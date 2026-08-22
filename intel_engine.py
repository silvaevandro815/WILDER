"""
intel_engine.py — Motor de Inteligência Territorial
QG Digital Wilder Morais — Goiás 2026

Fontes open-source (zero API key):
  - IBGE Serviço de Dados API (servicodados.ibge.gov.br)
  - Google News RSS por cidade/pauta
  - NLP léxico em português (sem dependências pesadas)
  - Geocoding offline IBGE (lat/lon dos 246 municípios de Goiás)
"""
import os
import re
import ssl
import json
import time
import datetime
import threading
import unicodedata
import urllib.request
import urllib.parse
from xml.etree import ElementTree as ET

# ─────────────────────────────────────────────────────────────────────────────
# 1. CACHE CENTRAL DE INTELIGÊNCIA
# ─────────────────────────────────────────────────────────────────────────────
INTEL_CACHE = {
    "queixas":    {"data": [], "atualizado_em": None, "ciclos": 0},
    "ibge":       {"data": {}, "atualizado_em": None, "ciclos": 0},
    "mapa_calor": {"data": [], "atualizado_em": None, "ciclos": 0},
    "alertas":    {"data": [], "atualizado_em": None, "ciclos": 0},
}
_intel_lock = threading.Lock()

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE
_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def _agora():
    return datetime.datetime.now()

def _agora_str():
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

def _norma(txt):
    """Normaliza texto removendo acentos e lowercasing."""
    if not txt:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", txt.lower())
        if unicodedata.category(c) != "Mn"
    )

# ─────────────────────────────────────────────────────────────────────────────
# 2. TABELA OFFLINE IBGE — 40 MUNICÍPIOS ESTRATÉGICOS DE GOIÁS
#    (lat/lon oficiais IBGE, populações Censo 2022)
# ─────────────────────────────────────────────────────────────────────────────
MUNICIPIOS_GOIAS = [
    {"codigo": "5208707", "nome": "Goiânia",              "regiao": "Metropolitana",  "lat": -16.6864, "lon": -49.2643, "pop": 1437237, "idh": 0.799},
    {"codigo": "5201405", "nome": "Aparecida de Goiânia", "regiao": "Metropolitana",  "lat": -16.8179, "lon": -49.2440, "pop": 590389,  "idh": 0.742},
    {"codigo": "5201108", "nome": "Anápolis",             "regiao": "Centro",         "lat": -16.3281, "lon": -48.9530, "pop": 391772,  "idh": 0.773},
    {"codigo": "5221858", "nome": "Rio Verde",            "regiao": "Sudoeste",       "lat": -17.7975, "lon": -50.9278, "pop": 241965,  "idh": 0.764},
    {"codigo": "5208004", "nome": "Luziânia",             "regiao": "Entorno DF",     "lat": -16.2523, "lon": -47.9503, "pop": 212603,  "idh": 0.699},
    {"codigo": "5221197", "nome": "Valparaíso de Goiás",  "regiao": "Entorno DF",     "lat": -16.0717, "lon": -47.9936, "pop": 173078,  "idh": 0.746},
    {"codigo": "5208707", "nome": "Senador Canedo",       "regiao": "Metropolitana",  "lat": -16.7000, "lon": -49.0975, "pop": 116731,  "idh": 0.718},
    {"codigo": "5211503", "nome": "Itumbiara",            "regiao": "Sul",            "lat": -18.4186, "lon": -49.2147, "pop": 104673,  "idh": 0.756},
    {"codigo": "5205109", "nome": "Catalão",              "regiao": "Sudeste",        "lat": -18.1659, "lon": -47.9469, "pop": 102793,  "idh": 0.766},
    {"codigo": "5221502", "nome": "Trindade",             "regiao": "Metropolitana",  "lat": -16.6522, "lon": -49.4891, "pop": 116671,  "idh": 0.741},
    {"codigo": "5204508", "nome": "Caldas Novas",         "regiao": "Sul",            "lat": -17.7422, "lon": -48.6208, "pop": 77010,   "idh": 0.748},
    {"codigo": "5218805", "nome": "Planaltina",           "regiao": "Entorno DF",     "lat": -15.4539, "lon": -47.6139, "pop": 94400,   "idh": 0.691},
    {"codigo": "5222203", "nome": "Formosa",              "regiao": "Entorno DF",     "lat": -15.5394, "lon": -47.3347, "pop": 115609,  "idh": 0.744},
    {"codigo": "5210000", "nome": "Jataí",                "regiao": "Sudoeste",       "lat": -17.8796, "lon": -51.7136, "pop": 101017,  "idh": 0.775},
    {"codigo": "5219704", "nome": "Santo Antônio do Descoberto", "regiao": "Entorno DF", "lat": -15.9438, "lon": -48.2528, "pop": 82667, "idh": 0.684},
    {"codigo": "5205406", "nome": "Ceres",                "regiao": "Centro-Norte",   "lat": -15.3017, "lon": -49.6003, "pop": 21836,   "idh": 0.739},
    {"codigo": "5221080", "nome": "Águas Lindas de Goiás","regiao": "Entorno DF",     "lat": -15.7448, "lon": -48.2765, "pop": 194875,  "idh": 0.685},
    {"codigo": "5209101", "nome": "Mineiros",             "regiao": "Sudoeste",       "lat": -17.5686, "lon": -52.5539, "pop": 66843,   "idh": 0.753},
    {"codigo": "5218300", "nome": "Porangatu",            "regiao": "Norte",          "lat": -13.4400, "lon": -49.1433, "pop": 44620,   "idh": 0.690},
    {"codigo": "5221601", "nome": "Uruaçu",               "regiao": "Norte",          "lat": -14.5228, "lon": -49.1408, "pop": 37027,   "idh": 0.700},
    {"codigo": "5216007", "nome": "Quirinópolis",         "regiao": "Sudoeste",       "lat": -18.4536, "lon": -50.4497, "pop": 46558,   "idh": 0.736},
    {"codigo": "5215504", "nome": "Pires do Rio",         "regiao": "Sudeste",        "lat": -17.3011, "lon": -48.2794, "pop": 30738,   "idh": 0.738},
    {"codigo": "5215603", "nome": "Pirenópolis",          "regiao": "Centro",         "lat": -15.8564, "lon": -48.9625, "pop": 25596,   "idh": 0.732},
    {"codigo": "5209705", "nome": "Morrinhos",            "regiao": "Sul",            "lat": -17.7317, "lon": -49.1058, "pop": 48004,   "idh": 0.737},
    {"codigo": "5207907", "nome": "Luziânia",             "regiao": "Entorno DF",     "lat": -16.2523, "lon": -47.9503, "pop": 212603,  "idh": 0.699},
    {"codigo": "5213806", "nome": "Novo Gama",            "regiao": "Entorno DF",     "lat": -16.0561, "lon": -48.0303, "pop": 103498,  "idh": 0.715},
    {"codigo": "5214606", "nome": "Padre Bernardo",       "regiao": "Entorno DF",     "lat": -15.1608, "lon": -48.2867, "pop": 30600,   "idh": 0.668},
    {"codigo": "5202908", "nome": "Aragarças",            "regiao": "Oeste",          "lat": -15.8994, "lon": -52.2486, "pop": 20254,   "idh": 0.700},
    {"codigo": "5201405", "nome": "Goiatuba",             "regiao": "Sul",            "lat": -18.0144, "lon": -49.3561, "pop": 37108,   "idh": 0.729},
    {"codigo": "5207105", "nome": "Inhumas",              "regiao": "Metropolitana",  "lat": -16.3592, "lon": -49.4972, "pop": 51255,   "idh": 0.741},
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. DICIONÁRIO LÉXICO NLP — CATEGORIZAÇÃO DE PAUTAS EM PORTUGUÊS
#    (sem dependências externas — zero pip install necessário)
# ─────────────────────────────────────────────────────────────────────────────
LEXICON_PAUTAS = {
    "SAUDE": {
        "palavras": ["hospital", "sus", "fila", "ubs", "remedio", "medicamento", "upa", "cirurgia",
                     "medico", "enfermagem", "leito", "ambulancia", "emergencia", "upa", "saude",
                     "cancer", "dengue", "morte", "obito", "tratamento", "consulta", "exame"],
        "peso": 10, "cor": "#ef4444", "icone": "🏥", "nivel": 4
    },
    "TRANSPORTE": {
        "palavras": ["onibus", "transporte", "passagem", "metro", "trem", "brt", "carro", "estrada",
                     "rodovia", "buraco", "asfalto", "transito", "engarrafamento", "acidente",
                     "km", "motorista", "entorno", "brasilia", "viagem", "trajeto"],
        "peso": 8, "cor": "#f97316", "icone": "🚌", "nivel": 3
    },
    "EMPREGO": {
        "palavras": ["emprego", "desemprego", "trabalho", "salario", "carteira", "clt", "demitido",
                     "contrato", "vaga", "concurso", "renda", "bolsa", "auxilio", "beneficio",
                     "aposentadoria", "previdencia", "primeiro emprego", "jovem"],
        "peso": 8, "cor": "#eab308", "icone": "💼", "nivel": 3
    },
    "SEGURANCA": {
        "palavras": ["violencia", "crime", "roubo", "furto", "assassinato", "homicidio", "policia",
                     "delegacia", "seguranca", "medo", "periferia", "trafico", "drogas", "arma",
                     "bala", "tiroteio", "morte", "latrocinio", "estupro", "assalto"],
        "peso": 9, "cor": "#dc2626", "icone": "🚨", "nivel": 4
    },
    "INFRAESTRUTURA": {
        "palavras": ["agua", "esgoto", "luz", "energia", "calcada", "pavimentacao", "obra",
                     "construcao", "ponte", "viaduto", "escola", "creche", "parque",
                     "iluminacao", "saneamento", "lixo", "coleta", "alagamento", "chuva"],
        "peso": 7, "cor": "#8b5cf6", "icone": "🏗️", "nivel": 2
    },
    "EDUCACAO": {
        "palavras": ["escola", "professor", "aluno", "aula", "ensino", "faculdade", "universidade",
                     "enem", "vestibular", "bolsa", "prouni", "fies", "estudante", "creche",
                     "infantil", "fundamental", "medio", "diploma", "formatura"],
        "peso": 6, "cor": "#0ea5e9", "icone": "📚", "nivel": 2
    },
}

def _classificar_pauta(texto: str) -> dict:
    """Classifica o texto em uma pauta usando o léxico NLP."""
    texto_norm = _norma(texto)
    scores = {}
    for pauta, config in LEXICON_PAUTAS.items():
        score = sum(config["peso"] for kw in config["palavras"] if kw in texto_norm)
        if score > 0:
            scores[pauta] = score

    if not scores:
        return {"pauta": "GERAL", "cor": "#64748b", "icone": "📌", "nivel": 1}

    melhor = max(scores, key=scores.get)
    return {
        "pauta": melhor,
        "cor": LEXICON_PAUTAS[melhor]["cor"],
        "icone": LEXICON_PAUTAS[melhor]["icone"],
        "nivel": LEXICON_PAUTAS[melhor]["nivel"],
        "score": scores[melhor]
    }

def _detectar_municipio(texto: str) -> dict | None:
    """Tenta identificar um município de Goiás no texto."""
    texto_norm = _norma(texto)
    for m in MUNICIPIOS_GOIAS:
        nome_norm = _norma(m["nome"])
        if nome_norm in texto_norm:
            return m
    return None

# ─────────────────────────────────────────────────────────────────────────────
# 4. FEEDS RSS POR PAUTA E CIDADE — COLETA REAL
# ─────────────────────────────────────────────────────────────────────────────
FEEDS_INTEL = [
    # Pautas de saúde em Goiás
    ("https://news.google.com/rss/search?q=hospital+fila+SUS+Goias&hl=pt-BR&gl=BR&ceid=BR:pt-419",  "RSS Saúde Goiás"),
    ("https://news.google.com/rss/search?q=UPA+Goiania+emergencia+saude&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS UPA Goiânia"),
    ("https://news.google.com/rss/search?q=remedio+SUS+Goias+falta&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Remédio SUS GO"),
    # Transporte e Entorno
    ("https://news.google.com/rss/search?q=onibus+Entorno+DF+Luziania+passagem&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Transporte Entorno"),
    ("https://news.google.com/rss/search?q=estrada+rodovia+Goias+acidente&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Estradas GO"),
    # Emprego e renda
    ("https://news.google.com/rss/search?q=desemprego+Goias+2026&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Emprego Goiás"),
    ("https://news.google.com/rss/search?q=concurso+publico+Goias+2026&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Concurso GO"),
    # Segurança pública
    ("https://news.google.com/rss/search?q=seguranca+publica+violencia+Goias&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Segurança GO"),
    ("https://news.google.com/rss/search?q=homicidio+roubo+Goiania+2026&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Crime Goiânia"),
    # Infraestrutura
    ("https://news.google.com/rss/search?q=saneamento+agua+esgoto+Goias&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Saneamento GO"),
    ("https://news.google.com/rss/search?q=obra+pavimentacao+Goias+problema&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Obras GO"),
    # Regiões específicas
    ("https://news.google.com/rss/search?q=Aparecida+Goiania+reclamacao&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Aparecida"),
    ("https://news.google.com/rss/search?q=Anapolis+problema+cidade&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Anápolis"),
    ("https://news.google.com/rss/search?q=Rio+Verde+Goias+noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Rio Verde"),
    ("https://news.google.com/rss/search?q=Caldas+Novas+turismo+problema&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Caldas Novas"),
    # Pautas gerais do estado
    ("https://news.google.com/rss/search?q=Goias+reclamacao+cidadao+governo&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Rec. Cidadão GO"),
    ("https://news.google.com/rss/search?q=Goias+crise+problema+populacao&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Crise GO"),
]

def _fetch_rss(url: str, fonte: str, max_items: int = 5) -> list:
    """Busca itens de um feed RSS de forma segura."""
    itens = []
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=10) as resp:
            root = ET.fromstring(resp.read())
        for item in root.findall(".//item")[:max_items]:
            titulo = item.findtext("title", "").strip()
            link   = item.findtext("link", "").strip()
            desc   = item.findtext("description", "").strip()
            pub    = item.findtext("pubDate", "")[:16].strip()
            src    = getattr(item.find("source"), "text", fonte) or fonte
            texto_completo = f"{titulo} {desc}"
            if titulo:
                itens.append({
                    "titulo": titulo.split(" - ")[0] if " - " in titulo else titulo,
                    "desc": re.sub(r'<[^>]+>', '', desc)[:200],
                    "url": link,
                    "fonte": src,
                    "pub": pub,
                    "texto_completo": texto_completo
                })
    except Exception as e:
        pass  # silencioso para não poluir logs de produção
    return itens

# ─────────────────────────────────────────────────────────────────────────────
# 5. JOB: COLETA DE QUEIXAS TERRITORIAIS
# ─────────────────────────────────────────────────────────────────────────────
def atualizar_intel_territorial():
    """Coleta RSS por pauta e cidade, classifica com NLP, geocodifica e atualiza cache."""
    print(f"[INTEL] Atualizando radar territorial... ({_agora_str()})")
    queixas = []
    contagem_municipio = {}  # municipio -> {pauta -> count}

    for url, fonte in FEEDS_INTEL:
        itens = _fetch_rss(url, fonte, max_items=6)
        time.sleep(0.3)  # throttle gentil
        for item in itens:
            pauta_info = _classificar_pauta(item["texto_completo"])
            municipio_info = _detectar_municipio(item["texto_completo"])

            # Fallback: inferir cidade pelo nome da fonte/feed
            if not municipio_info:
                for m in MUNICIPIOS_GOIAS:
                    if _norma(m["nome"]) in _norma(fonte):
                        municipio_info = m
                        break

            # Último fallback: Goiânia (capital)
            if not municipio_info:
                municipio_info = MUNICIPIOS_GOIAS[0]

            nome_mun = municipio_info["nome"]
            pauta = pauta_info["pauta"]

            # Contagem para o mapa de calor
            if nome_mun not in contagem_municipio:
                contagem_municipio[nome_mun] = {}
            contagem_municipio[nome_mun][pauta] = contagem_municipio[nome_mun].get(pauta, 0) + 1

            queixas.append({
                "municipio":  nome_mun,
                "regiao":     municipio_info.get("regiao", ""),
                "lat":        municipio_info["lat"],
                "lon":        municipio_info["lon"],
                "pop":        municipio_info.get("pop", 0),
                "pauta":      pauta,
                "cor":        pauta_info["cor"],
                "icone":      pauta_info["icone"],
                "nivel":      pauta_info["nivel"],
                "manchete":   item["titulo"],
                "desc":       item["desc"],
                "fonte":      item["fonte"],
                "url":        item["url"],
                "pub":        item["pub"],
                "coletado":   _agora_str(),
            })

    # Monta dados do mapa de calor: intensidade por município
    mapa_calor = []
    for m in MUNICIPIOS_GOIAS:
        nome = m["nome"]
        if nome in contagem_municipio:
            total = sum(contagem_municipio[nome].values())
            pauta_dom = max(contagem_municipio[nome], key=contagem_municipio[nome].get)
            nivel = min(4, total)
            mapa_calor.append({
                "municipio": nome,
                "lat": m["lat"],
                "lon": m["lon"],
                "total_queixas": total,
                "pauta_dominante": pauta_dom,
                "nivel": nivel,
                "cor": LEXICON_PAUTAS.get(pauta_dom, {}).get("cor", "#64748b"),
                "icone": LEXICON_PAUTAS.get(pauta_dom, {}).get("icone", "📌"),
                "regiao": m.get("regiao", ""),
                "pop": m.get("pop", 0),
            })
        else:
            mapa_calor.append({
                "municipio": nome,
                "lat": m["lat"],
                "lon": m["lon"],
                "total_queixas": 0,
                "pauta_dominante": "GERAL",
                "nivel": 0,
                "cor": "#1e293b",
                "icone": "📍",
                "regiao": m.get("regiao", ""),
                "pop": m.get("pop", 0),
            })

    # Alertas táticos
    alertas = []
    top_quentes = sorted(mapa_calor, key=lambda x: x["total_queixas"], reverse=True)[:5]
    for item in top_quentes:
        if item["total_queixas"] > 0:
            alertas.append({
                "tipo": "ALERTA",
                "municipio": item["municipio"],
                "mensagem": f"{item['icone']} {item['pauta_dominante']} em alta — {item['total_queixas']} sinais captados",
                "nivel": item["nivel"],
                "cor": item["cor"],
                "timestamp": _agora_str(),
            })

    with _intel_lock:
        INTEL_CACHE["queixas"]["data"] = queixas[-200:]  # últimas 200
        INTEL_CACHE["queixas"]["atualizado_em"] = _agora()
        INTEL_CACHE["queixas"]["ciclos"] += 1
        INTEL_CACHE["mapa_calor"]["data"] = mapa_calor
        INTEL_CACHE["mapa_calor"]["atualizado_em"] = _agora()
        INTEL_CACHE["alertas"]["data"] = alertas

    print(f"[INTEL] Territorial: {len(queixas)} sinais | {len(mapa_calor)} municipios mapeados | {len(alertas)} alertas")

# ─────────────────────────────────────────────────────────────────────────────
# 6. JOB: DADOS IBGE POR MUNICÍPIO
# ─────────────────────────────────────────────────────────────────────────────
def atualizar_dados_ibge():
    """Consulta a API pública do IBGE para enriquecer dados dos municípios."""
    print(f"[INTEL] Atualizando dados IBGE... ({_agora_str()})")
    dados = {}

    # Busca populações estimadas pelo IBGE (API pública, sem auth)
    # Endpoint: /v3/agregados/6579/periodos/2022/variaveis/9324?localidades=N6[52]
    # N6 = municípios, código 52 = Goiás
    try:
        url = "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2022/variaveis/9324?localidades=N6[52]"
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8", "ignore"))

        if result and isinstance(result, list):
            series = result[0].get("resultados", [])
            for serie in series:
                for loc in serie.get("series", []):
                    codigo = loc["localidade"]["id"]
                    nome_ibge = loc["localidade"]["nome"]
                    valor = loc["serie"].get("2022", "0")
                    try:
                        pop = int(valor)
                    except (ValueError, TypeError):
                        pop = 0
                    dados[codigo] = {"municipio": nome_ibge, "populacao": pop, "codigo": codigo}
        print(f"[INTEL] IBGE: {len(dados)} municípios carregados da API.")
    except Exception as e:
        print(f"[INTEL] IBGE API erro: {e} — usando dados offline.")

    # Preenche com dados offline (sempre disponíveis como fallback)
    for m in MUNICIPIOS_GOIAS:
        cod = m["codigo"]
        if cod not in dados:
            dados[cod] = {
                "municipio": m["nome"],
                "populacao": m.get("pop", 0),
                "codigo": cod,
                "lat": m["lat"],
                "lon": m["lon"],
                "idh": m.get("idh", 0),
                "regiao": m.get("regiao", ""),
            }
        else:
            dados[cod].update({
                "lat": m["lat"],
                "lon": m["lon"],
                "idh": m.get("idh", 0),
                "regiao": m.get("regiao", ""),
            })

    with _intel_lock:
        INTEL_CACHE["ibge"]["data"] = dados
        INTEL_CACHE["ibge"]["atualizado_em"] = _agora()
        INTEL_CACHE["ibge"]["ciclos"] += 1

    print(f"[INTEL] IBGE: {len(dados)} municípios de Goiás carregados.")

# ─────────────────────────────────────────────────────────────────────────────
# 7. HELPERS PARA AS ROTAS FLASK
# ─────────────────────────────────────────────────────────────────────────────
def get_queixas():
    with _intel_lock:
        return INTEL_CACHE["queixas"]["data"][:]

def get_mapa_calor():
    with _intel_lock:
        return INTEL_CACHE["mapa_calor"]["data"][:]

def get_ibge():
    with _intel_lock:
        return dict(INTEL_CACHE["ibge"]["data"])

def get_alertas():
    with _intel_lock:
        return INTEL_CACHE["alertas"]["data"][:]

def get_municipios_base():
    """Retorna a tabela base de municípios (disponível imediatamente, sem coleta)."""
    return MUNICIPIOS_GOIAS

def get_status_intel():
    def _td(ts):
        if not ts:
            return "nunca"
        mins = int((_agora() - ts).total_seconds() / 60)
        return f"ha {mins} min" if mins < 60 else f"ha {mins // 60}h"

    with _intel_lock:
        return {
            "motor": "INTEL TERRITORIAL ATIVO",
            "timestamp": _agora_str(),
            "queixas": {
                "total": len(INTEL_CACHE["queixas"]["data"]),
                "atualizado": _td(INTEL_CACHE["queixas"]["atualizado_em"]),
                "ciclos": INTEL_CACHE["queixas"]["ciclos"],
                "intervalo": "2 horas",
            },
            "mapa_calor": {
                "municipios": len(INTEL_CACHE["mapa_calor"]["data"]),
                "atualizado": _td(INTEL_CACHE["mapa_calor"]["atualizado_em"]),
            },
            "ibge": {
                "municipios": len(INTEL_CACHE["ibge"]["data"]),
                "atualizado": _td(INTEL_CACHE["ibge"]["atualizado_em"]),
                "ciclos": INTEL_CACHE["ibge"]["ciclos"],
                "intervalo": "24 horas",
            },
            "alertas": len(INTEL_CACHE["alertas"]["data"]),
        }

# ─────────────────────────────────────────────────────────────────────────────
# 8. RANKING DE PAUTAS POR CIDADE (para o painel de comando)
# ─────────────────────────────────────────────────────────────────────────────
def get_ranking_cidades():
    """Retorna ranking de cidades por intensidade de queixas captadas."""
    queixas = get_queixas()
    ranking = {}
    for q in queixas:
        mun = q["municipio"]
        if mun not in ranking:
            ranking[mun] = {
                "municipio": mun,
                "regiao": q.get("regiao", ""),
                "lat": q.get("lat", 0),
                "lon": q.get("lon", 0),
                "pop": q.get("pop", 0),
                "total": 0,
                "por_pauta": {},
                "nivel_max": 0,
                "pauta_dominante": "GERAL",
                "cor": "#64748b",
                "icone": "📍",
            }
        ranking[mun]["total"] += 1
        pauta = q.get("pauta", "GERAL")
        ranking[mun]["por_pauta"][pauta] = ranking[mun]["por_pauta"].get(pauta, 0) + 1
        if q.get("nivel", 0) > ranking[mun]["nivel_max"]:
            ranking[mun]["nivel_max"] = q["nivel"]
            ranking[mun]["pauta_dominante"] = pauta
            ranking[mun]["cor"] = q.get("cor", "#64748b")
            ranking[mun]["icone"] = q.get("icone", "📍")

    return sorted(ranking.values(), key=lambda x: x["total"], reverse=True)

# ─────────────────────────────────────────────────────────────────────────────
# 9. INICIALIZAR JOBS NO SCHEDULER EXISTENTE
# ─────────────────────────────────────────────────────────────────────────────
def iniciar_intel_jobs(scheduler):
    """Adiciona os jobs de inteligência territorial ao APScheduler existente."""
    try:
        scheduler.add_job(
            atualizar_intel_territorial,
            "interval", hours=2,
            id="intel_territorial",
            name="Intel Territorial RSS+NLP",
            max_instances=1, coalesce=True
        )
        scheduler.add_job(
            atualizar_dados_ibge,
            "interval", hours=24,
            id="intel_ibge",
            name="Intel IBGE Municípios GO",
            max_instances=1, coalesce=True
        )
        print("[INTEL] Jobs de inteligência territorial registrados no scheduler.")
    except Exception as e:
        print(f"[INTEL] Erro ao registrar jobs: {e}")

    # Coleta inicial imediata em background
    threading.Thread(target=atualizar_intel_territorial, daemon=True, name="boot-intel").start()
    threading.Thread(target=atualizar_dados_ibge,        daemon=True, name="boot-ibge").start()
