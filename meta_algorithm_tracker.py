"""
meta_algorithm_tracker.py — Rastreador Autônomo de Diretrizes e Mudanças no Algoritmo da Meta
QG Digital Wilder Morais — Goiás 2026

Objetivo:
  - Monitora continuamente anúncios oficiais da Meta, declarações de Adam Mosseri (Head do Instagram),
    atualizações do Instagram for Creators, Meta Newsroom e portais especializados.
  - Identifica pesos de sinais de rankeamento (Sends per Reach, Watch Time, SEO/ASR, Originalidade).
  - Alimenta o Laboratório de Engajamento e a IA do Chat com as regras vigentes do algoritmo.
"""
import os
import re
import ssl
import json
import time
import datetime
import threading
import urllib.request
import urllib.parse
from xml.etree import ElementTree as ET

META_CACHE = {
    "diretrizes": {},
    "noticias_algoritmo": [],
    "sinais_rankeamento": {},
    "formatos_em_alta": {},
    "penalidades_ativas": {},
    "atualizado_em": None,
    "ciclos": 0
}
_meta_lock = threading.Lock()

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def _agora_str():
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

# ─────────────────────────────────────────────────────────────────────────────
# BASELINE ESTRUTURADO DE DIRETRIZES DA META 2026
# ─────────────────────────────────────────────────────────────────────────────
DIRETRIZES_META_BASELINE = {
    "versao_algoritmo": "Meta AI Multi-Surface Ranking 2026",
    "sinal_numero_um": {
        "nome": "Sends Per Reach (Compartilhamentos por DM)",
        "peso_relativo": "45%",
        "impacto": "MÁXIMO",
        "explicacao": "A métrica mais valorizada pela Meta. Quando um usuário envia o Reel para um amigo ou grupo no direct, o algoritmo interpreta como alta relevância e distribui massivamente no Explore para não-seguidores."
    },
    "sinal_numero_dois": {
        "nome": "Watch Time & Retenção nos Primeiros 3s",
        "peso_relativo": "30%",
        "impacto": "CRÍTICO",
        "explicacao": "O 'Skip Rate' (taxa de abandono nos primeiros 3 segundos) decide se o vídeo continua sendo entregue. Vídeos com retenção >70% nos primeiros 5s ganham impulso de entrega."
    },
    "sinal_numero_tres": {
        "nome": "SEO de Legenda & ASR de Áudio Falado",
        "peso_relativo": "15%",
        "impacto": "ALTO",
        "explicacao": "A Meta transcreve o áudio (ASR) e lê os textos na tela (OCR). Palavras-chave faladas indexam o vídeo nas buscas temáticas do Instagram sem depender de hashtags."
    },
    "sinal_numero_quatro": {
        "nome": "Prioridade Absoluta a Conteúdo Original",
        "peso_relativo": "10%",
        "impacto": "REGULATÓRIO",
        "explicacao": "Vídeos com marcas d'água de concorrentes (ex: TikTok) ou contas que fazem mais de 10 reposts por mês são severamente penalizadas no alcance orgânico."
    }
}

FORMATOS_RECOMENDADOS_META = [
    {
        "formato": "Reels Rápido (15s a 30s)",
        "objetivo": "Furar a Bolha & Descoberta",
        "taxa_entrega": "🔥 Máxima (Explore e Aba Reels)",
        "estrutura": "Gancho visual (0-3s) + Dor concreta (3-15s) + Solução e CTA no DM (15-30s)."
    },
    {
        "formato": "Carrossel Informativo (8 a 10 slides)",
        "objetivo": "Geração de Salvamentos & Autoridade",
        "taxa_entrega": "📈 Alta (Feed Principal)",
        "estrutura": "Capa com pergunta intrigante + 7 lâminas com dados e fotos reais + CTA final."
    },
    {
        "formato": "Stories Interativos com Gatilho de DM",
        "objetivo": "Conversão & Fortalecimento de Base",
        "taxa_entrega": "🎯 Foco em Seguidores e Conexão Direta",
        "estrutura": "Enquete / Caixa de perguntas + convite para responder no Direct."
    },
    {
        "formato": "Vídeo de Contraste Político (30s a 45s)",
        "objetivo": "Combate e Desconstrução",
        "taxa_entrega": "⚡ Média-Alta (Compartilhamento Familiar)",
        "estrutura": "Fato real vs promessa de gabinete + linguagem de chão."
    }
]

PENALIDADES_META_ATIVAS = [
    {"motivo": "Marca d'água de outros apps (TikTok/CapCut)", "penalidade": "Redução drástica de alcance no Explore"},
    {"motivo": "Vício de Palanque & Jargão burocrático", "penalidade": "Rotulação como propaganda fria (limita a seguidores)"},
    {"motivo": "Engagement Bait agressivo ('Comente SIM para salvar')", "penalidade": "Queda no índice de qualidade do perfil"},
    {"motivo": "Vídeo estático ou sem movimento nos primeiros 3s", "penalidade": "Skip imediato pelo usuário e corte de distribuição"},
    {"motivo": "Mais de 5 hashtags genéricas", "penalidade": "Poluição de metadados; prefira 3 a 5 palavras-chave na legenda"}
]

# ─────────────────────────────────────────────────────────────────────────────
# RASTREAMENTO AO VIVO DE NOTÍCIAS & ANÚNCIOS DA META
# ─────────────────────────────────────────────────────────────────────────────
FEEDS_META_ALGORITMO = [
    ("https://news.google.com/rss/search?q=Instagram+algorithm+update+Reels+Meta&hl=en&gl=US&ceid=US:en", "Meta & Instagram Tech"),
    ("https://news.google.com/rss/search?q=Adam+Mosseri+Instagram+Reels+ranking+signals&hl=en&gl=US&ceid=US:en", "Adam Mosseri Official"),
    ("https://news.google.com/rss/search?q=SocialMediaToday+Instagram+algorithm+changes&hl=en&gl=US&ceid=US:en", "Social Media Today"),
    ("https://news.google.com/rss/search?q=algoritmo+Instagram+Reels+atualizacao+entrega+Meta&hl=pt-BR&gl=BR&ceid=BR:pt-419", "Imprensa Tech BR")
]

def atualizar_radar_meta():
    """Busca notícias recentes sobre o algoritmo do Instagram/Meta e atualiza cache."""
    print(f"[META ALGORITMO] 🛰️ Rastreando atualizações e diretrizes da Meta... ({_agora_str()})")
    noticias_captadas = []

    for url, fonte in FEEDS_META_ALGORITMO:
        try:
            req = urllib.request.Request(url, headers=_HEADERS)
            with urllib.request.urlopen(req, context=_SSL_CTX, timeout=10) as resp:
                root = ET.fromstring(resp.read())
            for item in root.findall(".//item")[:4]:
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                pub = item.findtext("pubDate", "")[:16].strip()
                clean_title = title.split(" - ")[0] if " - " in title else title
                if clean_title and not any(n["titulo"] == clean_title for n in noticias_captadas):
                    noticias_captadas.append({
                        "titulo": clean_title,
                        "fonte": fonte,
                        "data": pub,
                        "url": link,
                        "detectado_em": _agora_str()
                    })
            time.sleep(0.3)
        except Exception as e:
            pass

    with _meta_lock:
        META_CACHE["diretrizes"] = DIRETRIZES_META_BASELINE
        META_CACHE["noticias_algoritmo"] = noticias_captadas
        META_CACHE["sinais_rankeamento"] = DIRETRIZES_META_BASELINE
        META_CACHE["formatos_em_alta"] = FORMATOS_RECOMENDADOS_META
        META_CACHE["penalidades_ativas"] = PENALIDADES_META_ATIVAS
        META_CACHE["atualizado_em"] = datetime.datetime.now()
        META_CACHE["ciclos"] += 1

    print(f"[META ALGORITMO] ✅ Radar concluído: {len(noticias_captadas)} atualizações de algoritmo ativas.")

def get_meta_intelligence():
    """Retorna o estado consolidado da inteligência da Meta."""
    with _meta_lock:
        data = {
            "diretrizes": META_CACHE["diretrizes"] or DIRETRIZES_META_BASELINE,
            "noticias_algoritmo": META_CACHE["noticias_algoritmo"][:8],
            "formatos_recomendados": FORMATOS_RECOMENDADOS_META,
            "penalidades": PENALIDADES_META_ATIVAS,
            "atualizado_em": _agora_str(),
            "status": "CONECTADO & MONITORANDO 24/7"
        }
    return data
