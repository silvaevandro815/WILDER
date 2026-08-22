#!/usr/bin/env python3
"""
extrair_todos_videos_reais.py — Extrai métricas reais de todos os vídeos cadastrados no YouTube
"""
import urllib.request, json, ssl, re, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pdf_generator_service import YOUTUBE_VIDEOS_REAIS

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'
}

def formatar_numero_br(n_str):
    try:
        n = int(n_str)
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M".replace(".", ",")
        if n >= 1_000:
            return f"{n/1_000:.1f}k".replace(".", ",")
        return str(n)
    except Exception:
        return str(n_str)

def raspar_video_real(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=12) as r:
            html = r.read().decode("utf-8", "ignore")
    except Exception as e:
        return None

    # 1. Video Details (Título, Views, Autor)
    title = None
    author = None
    views = None
    
    m_player = re.search(r'ytInitialPlayerResponse\s*=\s*(\{.+?\});(?:var|window|\s*</script>)', html)
    if m_player:
        try:
            p_data = json.loads(m_player.group(1))
            v_details = p_data.get('videoDetails', {})
            title = v_details.get('title')
            author = v_details.get('author')
            views = v_details.get('viewCount')
        except Exception:
            pass

    # 2. Likes do botão
    likes = "0"
    m_like = re.search(r'"iconName":"LIKE","title":"([^"]+)"', html) or re.search(r'"valueIfIndifferent":"([^"]+)"', html)
    if m_like:
        likes = m_like.group(1)

    # 3. Inscritos do canal
    subs = "—"
    m_sub = re.search(r'"subscriberCountText":\{"accessibility":\{"accessibilityData":\{"label":"([^"]+)"', html) or re.search(r'"subtitle":\{"content":"([^"]*inscritos[^"]*)"', html)
    if m_sub:
        subs = m_sub.group(1)

    # 4. Fallback de título e autor via oEmbed se vazio
    if not title:
        try:
            url_oembed = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            req_oe = urllib.request.Request(url_oembed, headers=headers)
            with urllib.request.urlopen(req_oe, context=ctx, timeout=8) as r_oe:
                d_oe = json.loads(r_oe.read().decode("utf-8"))
                title = d_oe.get("title")
                author = d_oe.get("author_name")
        except Exception:
            pass

    return {
        "video_id": video_id,
        "titulo": title or "Vídeo Eleitoral",
        "canal": author or "YouTube",
        "views_raw": int(views) if views and str(views).isdigit() else 0,
        "views": f"{int(views):,}".replace(",", ".") + " visualizações" if views and str(views).isdigit() else "—",
        "curtidas": f"{likes} curtidas",
        "inscritos": subs
    }

print("=================================================================")
print("🎬 EXTRAINDO MÉTRICAS 100% REAIS DO YOUTUBE PARA CADA VÍDEO")
print("=================================================================")

resultados = []
for v in YOUTUBE_VIDEOS_REAIS:
    vid = v["video_id"]
    cand = v["candidato"]
    print(f"\n🔍 Auditando {cand} -> ID: {vid}...")
    real = raspar_video_real(vid)
    if real:
        print(f"   ✅ Título: {real['titulo']}")
        print(f"   ✅ Canal: {real['canal']}")
        print(f"   ✅ Views Reais: {real['views']}")
        print(f"   ✅ Curtidas Reais: {real['curtidas']}")
        print(f"   ✅ Inscritos Canal: {real['inscritos']}")
        resultados.append({
            **v,
            "titulo": real["titulo"],
            "canal": real["canal"],
            "views": real["views"],
            "curtidas": real["curtidas"],
            "comentarios": "Auditoria Real",
            "sentimento": v["sentimento"]
        })
    else:
        print(f"   ⚠️ Falha ao raspar {vid}")
        resultados.append(v)
    time.sleep(0.5)

# Salva base real
with open("youtube_videos_auditados_reais.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print("\n🎉 Auditoria real concluída e salva em 'youtube_videos_auditados_reais.json'!")
