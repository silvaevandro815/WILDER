"""
live_engine.py — Motor de Monitoramento Autonomo do QG Digital Wilder Morais 2026
"""
import os, re, ssl, json, time, datetime, threading, urllib.request, urllib.parse
from xml.etree import ElementTree as ET

LIVE_CACHE = {
    "noticias":  {"data": [], "atualizado_em": None, "ciclos": 0},
    "yt_videos": {"data": [], "atualizado_em": None, "ciclos": 0},
    "yt_canais": {"data": [], "atualizado_em": None, "ciclos": 0},
    "tendencias":{"data": [], "atualizado_em": None, "ciclos": 0},
}
_cache_lock = threading.Lock()

_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"}
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

def _agora_str():
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

def _tempo_desde(ts):
    if not ts:
        return "nunca"
    delta = datetime.datetime.now() - ts
    mins = int(delta.total_seconds() / 60)
    if mins < 60:
        return f"ha {mins} min"
    return f"ha {mins // 60}h"

# ── JOB 1: NOTICIAS (30 min) ────────────────────────────────────
def atualizar_noticias():
    print(f"[MOTOR] Atualizando noticias... ({_agora_str()})")
    CANDIDATOS = [
        ("Wilder Morais",   "Wilder+Morais+Goias"),
        ("Daniel Vilela",   "Daniel+Vilela+Goias+governador"),
        ("Marconi Perillo", "Marconi+Perillo+Goias+2026"),
    ]
    POS = ["lidera","cresce","apoio","obras","entrega","avanco","vence","alianca","eleito","aprovacao","inauguracao","conquista","vitoria"]
    NEG = ["critica","aponta","investiga","oposicao","preso","denuncia","processo","atraso","crise","desgaste","escandalo","rejeicao","fraude","corrupcao","polemica"]

    todas = []
    for cand, query in CANDIDATOS:
        try:
            url = f"https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=_SSL_CTX, timeout=10) as resp:
                root = ET.fromstring(resp.read())
            for item in root.findall(".//item")[:7]:
                title = item.findtext("title","").strip()
                link  = item.findtext("link","").strip()
                pub   = item.findtext("pubDate","")[:16]
                src_tag = item.find("source")
                src   = src_tag.text if src_tag is not None else "Imprensa"
                titulo = title.split(" - ")[0] if " - " in title else title
                t_low = titulo.lower()
                import unicodedata
                t_norm = "".join(c for c in unicodedata.normalize("NFD", t_low) if unicodedata.category(c) != "Mn")
                tipo = "NEUTRA"
                nivel = "NEUTRO"
                if any(k in t_norm for k in NEG):
                    tipo = "CRITICA / ALERTA"; nivel = "ALERTA"
                elif any(k in t_norm for k in POS):
                    tipo = "POSITIVA"; nivel = "FAVORAVEL"
                todas.append({"candidato":cand,"veiculo":src,"manchete":titulo,
                              "data":pub,"tipo_noticia":tipo,"nivel_ameaca":nivel,
                              "estrategia_defesa":"","url_noticia":link,"url_google_news":link})
        except Exception as e:
            print(f"[MOTOR] RSS {cand}: {e}")

    if todas:
        with _cache_lock:
            LIVE_CACHE["noticias"]["data"] = todas
            LIVE_CACHE["noticias"]["atualizado_em"] = datetime.datetime.now()
            LIVE_CACHE["noticias"]["ciclos"] += 1
        print(f"[MOTOR] Noticias: {len(todas)} artigos.")

# ── JOB 2: YT VIDEOS (2h) ───────────────────────────────────────
def _fmt_num(n):
    try:
        n = int(n)
        if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
        if n >= 1_000: return f"{n/1_000:.1f}K"
        return str(n)
    except: return str(n)

def _scrape_video(vid):
    try:
        req = urllib.request.Request(f"https://www.youtube.com/watch?v={vid}", headers=_HEADERS)
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=10) as r:
            html = r.read().decode("utf-8","ignore")
        views = re.search(r'"viewCount":"(\d+)"', html)
        title = re.search(r'"title":\{"runs":\[\{"text":"([^"]+)"', html)
        likes = re.search(r'"label":"([\d,\.]+)\s*(?:likes|curtidas)"', html)
        return {
            "views":    _fmt_num(views.group(1)) + " visualizacoes" if views else "—",
            "curtidas": likes.group(1) + " curtidas" if likes else "—",
            "titulo":   title.group(1) if title else None,
        }
    except: return {"views":"—","curtidas":"—","titulo":None}

def atualizar_yt_videos():
    print(f"[MOTOR] Atualizando videos YouTube... ({_agora_str()})")
    try:
        from pdf_generator_service import YOUTUBE_VIDEOS_REAIS
        videos_live = []
        for v in YOUTUBE_VIDEOS_REAIS:
            real = _scrape_video(v["video_id"])
            time.sleep(0.6)
            videos_live.append({**v,"views":real["views"],"curtidas":real["curtidas"],
                                "titulo":real["titulo"] if real["titulo"] else v["titulo"]})
        if videos_live:
            with _cache_lock:
                LIVE_CACHE["yt_videos"]["data"] = videos_live
                LIVE_CACHE["yt_videos"]["atualizado_em"] = datetime.datetime.now()
                LIVE_CACHE["yt_videos"]["ciclos"] += 1
            print(f"[MOTOR] YT videos: {len(videos_live)} atualizados.")
    except Exception as e:
        print(f"[MOTOR] YT videos erro: {e}")

# ── JOB 3: YT CANAIS (6h) ───────────────────────────────────────
def _scrape_canal(handle):
    try:
        clean = handle.replace("@","").strip()
        req = urllib.request.Request(f"https://www.youtube.com/@{clean}", headers=_HEADERS)
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=10) as r:
            html = r.read().decode("utf-8","ignore")
        sub = re.search(r'"subscriberCountText":"([^"]+)"', html) or re.search(r'"(\d[\d\.,]*\s*(?:mil|M|K)?)\s*(?:subscribers|inscritos)"', html, re.I)
        return {"inscritos": sub.group(1) if sub else "—"}
    except: return {"inscritos":"—"}

def atualizar_yt_canais():
    print(f"[MOTOR] Atualizando canais YouTube... ({_agora_str()})")
    try:
        from pdf_generator_service import CANIS_YOUTUBE_METRICAS
        CANAIS = [("Wilder Morais (PL)","WilderMoraisGoias"),("Daniel Vilela (MDB)","danielvilela15"),("Marconi Perillo (PSDB)","marconiperillo")]
        live = []
        for cand, handle in CANAIS:
            ch = _scrape_canal(handle)
            time.sleep(1.2)
            fb = next((m for m in CANIS_YOUTUBE_METRICAS if cand in m["candidato"]),{})
            live.append({**fb,"candidato":cand,"inscritos":ch["inscritos"] if ch["inscritos"]!="—" else fb.get("inscritos","—"),"handle":handle})
        if any(m["inscritos"]!="—" for m in live):
            with _cache_lock:
                LIVE_CACHE["yt_canais"]["data"] = live
                LIVE_CACHE["yt_canais"]["atualizado_em"] = datetime.datetime.now()
                LIVE_CACHE["yt_canais"]["ciclos"] += 1
            print(f"[MOTOR] YT canais: {len(live)} atualizados.")
    except Exception as e:
        print(f"[MOTOR] YT canais erro: {e}")

# ── JOB 4: TENDENCIAS (4h) ──────────────────────────────────────
def atualizar_tendencias():
    print(f"[MOTOR] Atualizando tendencias... ({_agora_str()})")
    QUERIES = ["wilder morais","wilder morais governador goias","eleicao governador goias 2026","daniel vilela governador","pesquisa eleitoral goias 2026"]
    live = []
    for q in QUERIES:
        try:
            enc = urllib.parse.quote(q)
            req = urllib.request.Request(f"https://suggestqueries.google.com/complete/search?client=firefox&q={enc}&hl=pt-BR", headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, context=_SSL_CTX, timeout=8) as r:
                parsed = json.loads(r.read().decode("utf-8","ignore"))
            sugs = parsed[1] if len(parsed)>1 else []
            if sugs:
                live.append({"query_base":q,"sugestoes":sugs[:6],"colhido_em":_agora_str()})
            time.sleep(0.4)
        except Exception as e:
            print(f"[MOTOR] Tendencias '{q}': {e}")
    if live:
        with _cache_lock:
            LIVE_CACHE["tendencias"]["data"] = live
            LIVE_CACHE["tendencias"]["atualizado_em"] = datetime.datetime.now()
            LIVE_CACHE["tendencias"]["ciclos"] += 1
        print(f"[MOTOR] Tendencias: {sum(len(t['sugestoes']) for t in live)} sugestoes.")

# ── HELPERS PARA AS ROTAS FLASK ──────────────────────────────────
def get_noticias():
    with _cache_lock: data = LIVE_CACHE["noticias"]["data"][:]
    if data: return data
    try:
        from pdf_generator_service import RADAR_NOTICIAS_TODOS_CANDIDATOS
        return RADAR_NOTICIAS_TODOS_CANDIDATOS
    except: return []

def get_yt_videos():
    with _cache_lock: data = LIVE_CACHE["yt_videos"]["data"][:]
    if data: return data
    try:
        from pdf_generator_service import YOUTUBE_VIDEOS_REAIS
        return YOUTUBE_VIDEOS_REAIS
    except: return []

def get_yt_canais():
    with _cache_lock: data = LIVE_CACHE["yt_canais"]["data"][:]
    if data: return data
    try:
        from pdf_generator_service import CANIS_YOUTUBE_METRICAS
        return CANIS_YOUTUBE_METRICAS
    except: return []

def get_tendencias():
    with _cache_lock: return LIVE_CACHE["tendencias"]["data"][:]

def get_status():
    with _cache_lock:
        return {
            "motor":"ATIVO","timestamp_servidor":_agora_str(),
            "fontes":{
                "noticias":  {"total":len(LIVE_CACHE["noticias"]["data"]), "atualizado":_tempo_desde(LIVE_CACHE["noticias"]["atualizado_em"]),  "ciclos":LIVE_CACHE["noticias"]["ciclos"],  "intervalo":"30 min"},
                "yt_videos": {"total":len(LIVE_CACHE["yt_videos"]["data"]),"atualizado":_tempo_desde(LIVE_CACHE["yt_videos"]["atualizado_em"]), "ciclos":LIVE_CACHE["yt_videos"]["ciclos"], "intervalo":"2 horas"},
                "yt_canais": {"total":len(LIVE_CACHE["yt_canais"]["data"]),"atualizado":_tempo_desde(LIVE_CACHE["yt_canais"]["atualizado_em"]), "ciclos":LIVE_CACHE["yt_canais"]["ciclos"], "intervalo":"6 horas"},
                "tendencias":{"total":len(LIVE_CACHE["tendencias"]["data"]),"atualizado":_tempo_desde(LIVE_CACHE["tendencias"]["atualizado_em"]),"ciclos":LIVE_CACHE["tendencias"]["ciclos"],"intervalo":"4 horas"},
            }
        }

# ── INICIALIZAR SCHEDULER ────────────────────────────────────────
_scheduler_started = False

def iniciar_scheduler():
    global _scheduler_started
    if _scheduler_started:
        return

    # Proteção de worker unico via lock de arquivo
    lock_file = "/tmp/qg_motor.lock"
    try:
        if os.path.exists(lock_file):
            with open(lock_file) as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)
                print(f"[MOTOR] Scheduler ja rodando no PID {pid}. Pulando.")
                return
            except OSError:
                pass
        with open(lock_file,"w") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        import pytz
        tz = pytz.timezone("America/Sao_Paulo")

        scheduler = BackgroundScheduler(timezone=tz, job_defaults={"max_instances":1,"coalesce":True})

        scheduler.add_job(atualizar_noticias,   "interval", minutes=30, id="noticias",   name="Noticias RSS")
        scheduler.add_job(atualizar_yt_videos,  "interval", hours=2,    id="yt_videos",  name="YT Videos")
        scheduler.add_job(atualizar_yt_canais,  "interval", hours=6,    id="yt_canais",  name="YT Canais")
        scheduler.add_job(atualizar_tendencias, "interval", hours=4,    id="tendencias", name="Tendencias")

        scheduler.start()
        _scheduler_started = True

        print("=" * 55)
        print("MOTOR QG DIGITAL — APScheduler ATIVO!")
        print("  Noticias:    30 min")
        print("  YT Videos:  2 horas")
        print("  YT Canais:  6 horas")
        print("  Tendencias: 4 horas")
        print("=" * 55)

        # Coleta inicial imediata em threads paralelas
        threading.Thread(target=atualizar_noticias,   daemon=True, name="boot-noticias").start()
        threading.Thread(target=atualizar_tendencias, daemon=True, name="boot-tendencias").start()
        def _boot_yt():
            time.sleep(5)
            atualizar_yt_videos()
            time.sleep(3)
            atualizar_yt_canais()
        threading.Thread(target=_boot_yt, daemon=True, name="boot-yt").start()

    except ImportError:
        print("[MOTOR] APScheduler/pytz nao instalado. Instale com: pip install apscheduler pytz")
    except Exception as e:
        print(f"[MOTOR] Falha ao iniciar scheduler: {e}")
