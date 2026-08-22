import os
import sys
import json
import re
import requests
import urllib3
import httpx
import urllib.request
from xml.etree import ElementTree as ET
from flask import Flask, request, jsonify, render_template_string, send_file, send_from_directory
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

load_dotenv()

from supabase import create_client, Client, ClientOptions
from pdf_generator_service import (
    gerar_buffer_relatorio_360, YOUTUBE_VIDEOS_REAIS,
    RADAR_NOTICIAS_TODOS_CANDIDATOS, MAPA_RECLAMACOES_DETALHADO,
    GOOGLE_TRENDS_GOIAS, MAIORES_COLEGIOS_TSE,
    PESQUISA_OFICIAL_GOIAS_2026, PLANO_DE_GOVERNO_MEMORIA,
    PRIMEIRA_SEMANA_CONTEUDO, EVENTOS_GOIAS_2026, WILDER_AVATAR_B64,
    CANIS_YOUTUBE_METRICAS
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
VERIFY_TOKEN = os.getenv("INSTAGRAM_VERIFY_TOKEN", "wilder_eleitoral_2026")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "google/gemini-2.5-flash"

# ─── BUSCA DE NOTÍCIAS REAIS VIA GOOGLE NEWS RSS ─────────────────────────────
def buscar_noticias_rss(queries=None):
    """Busca manchetes reais do Google News RSS sem precisar de API key."""
    if queries is None:
        queries = [
            "Wilder+Morais+Goiás+2026",
            "eleições+governador+Goiás+2026+pesquisa"
        ]
    manchetes = []
    headers_rss = {"User-Agent": "Mozilla/5.0 (compatible; RSS Reader)"}
    for q in queries:
        try:
            url = f"https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
            req = urllib.request.Request(url, headers=headers_rss)
            with urllib.request.urlopen(req, timeout=5) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            for item in root.findall(".//item")[:4]:
                title = item.findtext("title", "").strip()
                pub = item.findtext("pubDate", "")[:16].strip()
                if title:
                    manchetes.append(f"• {title} [{pub}]")
        except Exception:
            pass
    return "\n".join(manchetes[:8]) if manchetes else "Sem notícias recentes disponíveis no momento."

is_supabase_configurado = (
    SUPABASE_URL and SUPABASE_KEY and
    "your-supabase" not in SUPABASE_URL and
    "your-supabase" not in SUPABASE_KEY
)

supabase: Client = None
if is_supabase_configurado:
    try:
        options = ClientOptions(httpx_client=httpx.Client(verify=False))
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options=options)
    except Exception as e:
        print(f"[AVISO] Não foi possível inicializar cliente Supabase: {e}")
app = Flask(__name__, static_folder="static")

# Inicialização do Motor de Monitoramento Autônomo (APScheduler em background)
try:
    import live_engine
    live_engine.iniciar_scheduler()
except Exception as e:
    print(f"[AVISO] Falha ao iniciar live_engine: {e}")

@app.route("/wilder_3d.jpg")
@app.route("/static/wilder_3d.jpg")
def serve_wilder_avatar():
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return send_from_directory(static_dir, "wilder_3d.jpg")

@app.route("/static/<path:filename>")
def serve_static_files(filename):
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return send_from_directory(static_dir, filename)

@app.after_request
def add_caching_and_performance_headers(response):
    # Caching de imagens e arquivos estáticos no navegador por 24h
    if request.path.startswith('/static') or request.path.endswith(('.jpg', '.png', '.svg', '.webp', '.css', '.js', '.ico')):
        response.headers['Cache-Control'] = 'public, max-age=86400'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

HTML_PROTECTION_SCRIPT = """
<script>
    document.addEventListener('contextmenu', function(e) { e.preventDefault(); });
    document.addEventListener('keydown', function(e) {
        if (
            e.keyCode === 123 || 
            (e.ctrlKey && e.shiftKey && (e.keyCode === 73 || e.keyCode === 74 || e.keyCode === 67)) ||
            (e.ctrlKey && e.keyCode === 85)
        ) {
            e.preventDefault();
            return false;
        }
    });
</script>
"""

# GLOBAL PREMIM RESPONSIVE CSS & HEADER COMPONENT
PREMIUM_THEME_CSS = """
<style>
    :root {
        --bg-main: #0b0f19;
        --bg-card: #131b2e;
        --bg-card-hover: #1c2742;
        --border-color: rgba(255, 255, 255, 0.08);
        --accent-green: #10b981;
        --accent-gold: #f59e0b;
        --accent-cyan: #38bdf8;
        --accent-purple: #8b5cf6;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }

    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    html, body {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--bg-main);
        color: var(--text-primary);
        margin: 0; padding: 0;
        -webkit-font-smoothing: antialiased;
        min-height: 100vh;
        min-height: 100dvh;
    }

    /* HEADER RESPONSIVO PREMIUM */
    .app-header {
        background: linear-gradient(135deg, #0d1527, #131b2e);
        border-bottom: 1px solid rgba(245, 158, 11, 0.3);
        padding: 12px 20px;
        display: flex; justify-content: space-between; align-items: center;
        position: sticky; top: 0; z-index: 9999;
        box-shadow: 0 4px 20px rgba(0,0,0,0.6);
    }
    .brand-container { display: flex; align-items: center; gap: 12px; }
    .brand-avatar { width: 42px; height: 42px; min-width: 42px; min-height: 42px; border-radius: 50%; border: 2px solid var(--accent-gold); object-fit: cover; }
    .brand-title { font-size: 15.5px; font-weight: 800; color: #ffffff; letter-spacing: 0.3px; margin: 0; line-height: 1.2; }
    .brand-subtitle { font-size: 11px; color: var(--accent-gold); font-weight: 700; margin: 2px 0 0 0; }

    /* BOTÃO HAMBÚRGUER MOBILE */
    .menu-toggle-btn { display: none; background: #1e293b; color: #fff; border: 1px solid var(--border-color); padding: 8px 12px; border-radius: 8px; font-size: 18px; cursor: pointer; }

    /* LINKS DE NAVEGAÇÃO DESKTOP & TABLET */
    .nav-links-wrapper { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
    .btn-nav-link { color: #cbd5e1; text-decoration: none; font-size: 11.5px; font-weight: 700; background: #1e293b; padding: 7px 12px; border-radius: 8px; border: 1px solid var(--border-color); transition: all 0.15s ease; display: inline-flex; align-items: center; gap: 5px; white-space: nowrap; }
    .btn-nav-link:hover, .btn-nav-link.active { background: var(--accent-green); color: #ffffff; border-color: var(--accent-green); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }

    /* BARRA INFERIOR MOBILE NATIVA (ANDROID & IPHONE) */
    .mobile-bottom-nav {
        display: none; position: fixed; bottom: 0; left: 0; right: 0; height: 60px;
        background: rgba(6, 12, 24, 0.96); backdrop-filter: blur(16px);
        border-top: 1px solid rgba(0, 255, 136, 0.15); z-index: 10000;
        justify-content: space-around; align-items: center; padding: 0 4px;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.5);
    }
    .mobile-bottom-link {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        gap: 3px; color: #94a3b8; text-decoration: none; font-size: 10px; font-weight: 700;
        padding: 6px 8px; border-radius: 8px; transition: all 0.15s; flex: 1; text-align: center;
    }
    .mobile-bottom-link span.icon { font-size: 18px; line-height: 1; }
    .mobile-bottom-link.active, .mobile-bottom-link:hover { color: #00ff88; }

    /* ADAPTAÇÃO RESPONSIVA PARA TABLETS (< 1024px) E SMARTPHONES (< 768px) */
    @media (max-width: 1024px) {
        .main-container { max-width: 100%; margin: 16px auto; padding: 0 14px; }
        .btn-nav-link { font-size: 11px; padding: 6px 10px; }
    }

    @media (max-width: 768px) {
        body { padding-bottom: 68px !important; }
        .app-header { padding: 10px 14px; }
        .menu-toggle-btn { display: block; }
        .nav-links-wrapper { display: none; width: 100%; flex-direction: column; gap: 6px; margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-color); }
        .nav-links-wrapper.show-mobile-menu { display: flex; }
        .btn-nav-link { width: 100%; justify-content: center; padding: 10px; font-size: 12.5px; }
        .brand-title { font-size: 13.5px; }
        .brand-avatar { width: 36px; height: 36px; min-width: 36px; min-height: 36px; }
        .mobile-bottom-nav { display: flex; }
        .card-panel { padding: 14px; margin-bottom: 16px; border-radius: 12px; }
        .main-container { padding: 0 10px; margin: 12px auto; }
    }

    /* CONTÊINERES E TABELAS RESPONSIVAS */
    .main-container { max-width: 1280px; margin: 20px auto; padding: 0 16px; }
    .table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: 12px; border: 1px solid var(--border-color); }
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
    th { background: #0f172a; color: var(--accent-green); padding: 12px 14px; font-weight: 800; border-bottom: 2px solid var(--accent-green); white-space: nowrap; }
    td { padding: 12px 14px; border-bottom: 1px solid var(--border-color); color: #e2e8f0; }

    /* CARDS EXECUTIVOS */
    .card-panel { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 20px; margin-bottom: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.4); }
    .card-panel-title { font-size: 15.5px; font-weight: 800; color: var(--accent-green); border-left: 4px solid var(--accent-gold); padding-left: 10px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
</style>

<!-- ── PREFETCH INTELIGENTE & INSTANT NAVIGATION (0ms Latência) ── -->
<script>
    function toggleMobileMenu() {
        const wrapper = document.getElementById('navMenuWrapper');
        if (wrapper) {
            wrapper.classList.toggle('show-mobile-menu');
        }
    }

    // Pré-carrega páginas no toque ou hover para que abram instantaneamente
    (function() {
        const cacheLinks = new Set();
        function prefetch(url) {
            if (!url || cacheLinks.has(url) || url.startsWith('http') || url.startsWith('#')) return;
            cacheLinks.add(url);
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = url;
            document.head.appendChild(link);
        }

        document.addEventListener('pointerenter', function(e) {
            const a = e.target.closest('a');
            if (a && a.href && a.origin === location.origin) {
                prefetch(a.pathname);
            }
        }, true);

        document.addEventListener('touchstart', function(e) {
            const a = e.target.closest('a');
            if (a && a.href && a.origin === location.origin) {
                prefetch(a.pathname);
            }
        }, { passive: true, capture: true });
    })();
</script>

<!-- ── BARRA DE NAVEGAÇÃO INFERIOR PARA SMARTPHONES ANDROID / TABLETS ── -->
<div class="mobile-bottom-nav">
    <a href="/" class="mobile-bottom-link">
        <span class="icon">💬</span>
        <span>QG Chat</span>
    </a>
    <a href="/intel" class="mobile-bottom-link">
        <span class="icon">🎖️</span>
        <span>Intel 246</span>
    </a>
    <a href="/engajamento" class="mobile-bottom-link">
        <span class="icon">🚀</span>
        <span>Viral Lab</span>
    </a>
    <a href="/radar_noticias" class="mobile-bottom-link">
        <span class="icon">🚨</span>
        <span>Notícias</span>
    </a>
    <a href="/mapa_demandas" class="mobile-bottom-link">
        <span class="icon">🗺️</span>
        <span>Demandas</span>
    </a>
</div>
"""

# ROUTE HTML: CHAT INTERATIVO QG DIGITAL
HTML_CHAT_WIDGET = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>QG Digital — Wilder Morais 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    """ + PREMIUM_THEME_CSS + """
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background: #060c18;
            min-height: 100vh;
            font-family: 'Plus Jakarta Sans', sans-serif;
            display: flex;
            flex-direction: column;
        }

        /* ── TOP BAR ───────────────────────────────────────────── */
        .top-bar {
            position: sticky; top: 0; z-index: 100;
            background: rgba(6,12,24,0.92);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid rgba(16,185,129,0.15);
            padding: 10px 16px;
            display: flex; align-items: center; justify-content: space-between;
        }
        .top-bar-brand { display: flex; align-items: center; gap: 10px; }
        .top-bar-brand img { width: 38px; height: 38px; border-radius: 50%; border: 2px solid #10b981; object-fit: cover; }
        .top-bar-title { font-size: 14px; font-weight: 800; color: #f8fafc; line-height: 1.2; }
        .top-bar-sub   { font-size: 10px; color: #10b981; font-weight: 600; letter-spacing: .5px; }
        .live-dot {
            width: 8px; height: 8px; border-radius: 50%; background: #ef4444;
            box-shadow: 0 0 8px #ef4444;
            animation: blink 1.2s ease-in-out infinite;
            display: inline-block; margin-right: 4px;
        }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

        .top-bar-nav { display: flex; gap: 6px; }
        .nav-icon-btn {
            background: #131b2e; border: 1px solid #1e293b;
            color: #94a3b8; border-radius: 10px;
            padding: 7px 11px; font-size: 12px; font-weight: 700;
            text-decoration: none; cursor: pointer;
            transition: all .2s; white-space: nowrap;
        }
        .nav-icon-btn:hover { background: #10b981; color: #fff; border-color: #10b981; }
        .hamburger { display: none; background: #131b2e; border: 1px solid #1e293b; border-radius: 10px; padding: 8px 12px; color: #94a3b8; font-size: 16px; cursor: pointer; }

        /* ── STORIES / MÓDULOS ─────────────────────────────────── */
        .stories-bar {
            display: flex; gap: 12px;
            overflow-x: auto; padding: 14px 16px 10px;
            scrollbar-width: none;
        }
        .stories-bar::-webkit-scrollbar { display: none; }
        .story-item {
            display: flex; flex-direction: column; align-items: center; gap: 5px;
            cursor: pointer; min-width: 64px; text-decoration: none;
            flex-shrink: 0;
        }
        .story-ring {
            width: 58px; height: 58px; border-radius: 50%;
            padding: 2px;
            background: linear-gradient(135deg, #f59e0b, #10b981, #3b82f6);
            position: relative;
        }
        .story-ring-inner {
            width: 100%; height: 100%; border-radius: 50%;
            background: #060c18; border: 2px solid #060c18;
            display: flex; align-items: center; justify-content: center;
            font-size: 22px;
        }
        .story-label { font-size: 10px; font-weight: 700; color: #94a3b8; text-align: center; max-width: 64px; line-height: 1.2; }

        /* ── FEED DE CARDS ─────────────────────────────────────── */
        .feed-wrapper {
            flex: 1;
            overflow-y: auto;
            padding: 0 12px 160px;
        }
        .feed-section-title {
            font-size: 11px; font-weight: 800; color: #f59e0b;
            text-transform: uppercase; letter-spacing: 1px;
            padding: 14px 4px 8px;
            border-bottom: 1px solid #1e293b; margin-bottom: 12px;
        }

        /* cards de status / post */
        .post-card {
            background: #0d1525; border: 1px solid #1e293b;
            border-radius: 16px; margin-bottom: 12px;
            overflow: hidden; transition: border-color .2s;
        }
        .post-card:hover { border-color: #10b981; }
        .post-header {
            display: flex; align-items: center; gap: 10px;
            padding: 12px 14px 8px;
        }
        .post-avatar {
            width: 36px; height: 36px; border-radius: 50%;
            border: 2px solid #f59e0b; object-fit: cover; flex-shrink: 0;
        }
        .post-author { font-size: 13px; font-weight: 800; color: #f8fafc; }
        .post-time   { font-size: 11px; color: #64748b; }
        .post-badge {
            margin-left: auto; font-size: 10px; font-weight: 800;
            padding: 3px 8px; border-radius: 20px;
        }
        .badge-live { background: #ef44441a; color: #ef4444; border: 1px solid #ef444440; }
        .badge-new  { background: #10b9811a; color: #10b981; border: 1px solid #10b98140; }
        .badge-hot  { background: #f59e0b1a; color: #f59e0b; border: 1px solid #f59e0b40; }

        .post-body { padding: 4px 14px 12px; }
        .post-text { font-size: 13.5px; color: #cbd5e1; line-height: 1.6; margin-bottom: 10px; }
        .post-metric-row {
            display: flex; gap: 8px; flex-wrap: wrap;
        }
        .metric-pill {
            background: #131b2e; border: 1px solid #1e293b;
            border-radius: 8px; padding: 6px 10px;
            font-size: 11px; font-weight: 700;
        }
        .metric-pill .mp-val { color: #f8fafc; font-size: 14px; font-weight: 800; display: block; }
        .metric-pill .mp-lbl { color: #64748b; }

        /* Botão de ação do card */
        .post-action-btn {
            display: flex; align-items: center; justify-content: center; gap: 6px;
            margin: 4px 14px 14px;
            padding: 10px; border-radius: 10px; cursor: pointer;
            font-size: 12.5px; font-weight: 800; text-decoration: none;
            border: 1px solid #1e293b; background: #131b2e;
            color: #10b981; transition: all .2s;
        }
        .post-action-btn:hover { background: #10b981; color: #fff; border-color: #10b981; }

        /* ── QUICK ASK CHIPS (acima do chat bar) ────────────────── */
        .quick-ask-bar {
            position: fixed; bottom: 68px; left: 0; right: 0; z-index: 200;
            display: flex; gap: 7px; overflow-x: auto; padding: 8px 12px;
            background: linear-gradient(to top, rgba(6,12,24,1) 60%, transparent);
            scrollbar-width: none;
        }
        .quick-ask-bar::-webkit-scrollbar { display: none; }
        .qa-chip {
            background: #131b2e; border: 1px solid #10b98160;
            color: #10b981; font-size: 11.5px; font-weight: 700;
            padding: 7px 13px; border-radius: 20px; white-space: nowrap;
            cursor: pointer; flex-shrink: 0; transition: all .2s;
        }
        .qa-chip:hover { background: #10b981; color: #fff; }

        /* ── CHAT BAR (FIXO NO FUNDO como WhatsApp) ────────────── */
        .chat-bar-fixed {
            position: fixed; bottom: 0; left: 0; right: 0; z-index: 300;
            background: rgba(6,12,24,0.98);
            border-top: 1px solid rgba(16,185,129,0.25);
            padding: 10px 12px 14px;
            display: flex; align-items: center; gap: 8px;
        }
        .chat-bar-input {
            flex: 1; background: #131b2e;
            border: 1.5px solid #1e293b; color: #f8fafc;
            padding: 11px 16px; border-radius: 24px;
            font-size: 14px; outline: none;
            font-family: 'Plus Jakarta Sans', sans-serif;
            transition: border-color .2s;
        }
        .chat-bar-input:focus { border-color: #10b981; }
        .chat-bar-input::placeholder { color: #475569; }
        .chat-bar-send {
            width: 44px; height: 44px; border-radius: 50%;
            background: linear-gradient(135deg, #059669, #10b981);
            border: none; color: #fff; font-size: 18px;
            cursor: pointer; display: flex; align-items: center; justify-content: center;
            flex-shrink: 0; transition: transform .15s;
        }
        .chat-bar-send:hover { transform: scale(1.08); }

        /* ── CHAT MESSAGES OVERLAY ─────────────────────────────── */
        .chat-overlay {
            display: none;
            position: fixed; inset: 0; z-index: 400;
            background: rgba(6,12,24,0.97);
            flex-direction: column;
        }
        .chat-overlay.open { display: flex; }
        .chat-overlay-header {
            display: flex; align-items: center; gap: 10px;
            padding: 12px 16px;
            border-bottom: 1px solid #1e293b;
            background: #060c18;
        }
        .chat-back-btn {
            background: #131b2e; border: 1px solid #1e293b;
            color: #10b981; border-radius: 10px; padding: 7px 12px;
            font-size: 13px; font-weight: 800; cursor: pointer;
        }
        .chat-overlay-title { font-size: 14px; font-weight: 800; color: #f8fafc; }
        .chat-messages {
            flex: 1; overflow-y: auto;
            padding: 16px; display: flex; flex-direction: column; gap: 12px;
            padding-bottom: 80px;
        }
        .msg-row { display: flex; gap: 10px; align-items: flex-end; }
        .msg-row.user { justify-content: flex-end; }
        .msg-av { width: 32px; height: 32px; border-radius: 50%; border: 2px solid #f59e0b; object-fit: cover; flex-shrink: 0; }
        .msg-bbl {
            max-width: 88%; padding: 16px 20px; border-radius: 18px;
            font-size: 15px; line-height: 1.75; letter-spacing: 0.01em;
            word-break: break-word;
        }
        .msg-bbl.bot {
            background: linear-gradient(135deg, #091322, #0d1a2d);
            color: #f1f5f9; border: 1px solid rgba(0, 255, 136, 0.2);
            border-bottom-left-radius: 4px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.35);
        }
        .msg-bbl.usr {
            background: linear-gradient(135deg, #059669, #10b981);
            color: #fff; font-weight: 600;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 15px rgba(16,185,129,0.3);
        }

        /* ── ELEMENTOS MODERNOS DA IA (FORMATO VISUAL PROFISSIONAL) ── */
        .ai-title {
            font-size: 16.5px; font-weight: 800; color: #00ff88;
            margin: 14px 0 8px 0; display: flex; align-items: center; gap: 8px;
            letter-spacing: 0.03em; border-bottom: 1px solid rgba(0,255,136,0.15);
            padding-bottom: 4px;
        }
        .ai-title:first-child { margin-top: 0; }
        .ai-p {
            margin: 0 0 12px 0; color: #e2e8f0; font-size: 14.5px; line-height: 1.7;
        }
        .ai-p:last-child { margin-bottom: 0; }
        .ai-list {
            margin: 10px 0 14px 0; padding-left: 0; list-style: none;
            display: flex; flex-direction: column; gap: 8px;
        }
        .ai-list-item {
            padding: 10px 14px; background: rgba(255, 255, 255, 0.035);
            border-radius: 10px; border-left: 3px solid #38bdf8;
            color: #f1f5f9; font-size: 14px; line-height: 1.6;
        }
        .ai-card {
            background: rgba(15, 23, 42, 0.8);
            border-left: 3px solid #00ff88; border-radius: 10px;
            padding: 12px 16px; margin: 12px 0;
            color: #e2e8f0; font-size: 14px; line-height: 1.65;
        }
        .ai-card.gold {
            border-left-color: #f59e0b;
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-left: 4px solid #f59e0b;
        }
        .ai-card.purple {
            border-left-color: #a855f7;
            background: rgba(168, 85, 247, 0.08);
            border: 1px solid rgba(168, 85, 247, 0.25);
            border-left: 4px solid #a855f7;
        }
        .ai-highlight { color: #38bdf8; font-weight: 700; }
        .ai-badge {
            display: inline-block; background: rgba(0, 255, 136, 0.12);
            color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.3);
            padding: 2px 8px; border-radius: 6px; font-size: 12px;
            font-weight: 800; margin-right: 6px;
        }
        .chat-input-row {
            position: sticky; bottom: 0;
            display: flex; gap: 8px; padding: 10px 12px 14px;
            background: rgba(6,12,24,0.98); border-top: 1px solid #1e293b;
        }
        .ci-input {
            flex: 1; background: #131b2e; border: 1.5px solid #1e293b;
            color: #f8fafc; padding: 11px 16px; border-radius: 24px;
            font-size: 14px; outline: none; font-family: inherit;
        }
        .ci-input:focus { border-color: #10b981; }
        .ci-send {
            width: 44px; height: 44px; border-radius: 50%;
            background: linear-gradient(135deg, #059669, #10b981);
            border: none; color: #fff; font-size: 18px; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
        }

        /* ── MOBILE NAV (drawer) ───────────────────────────────── */
        .mobile-drawer {
            display: none; position: fixed; inset: 0; z-index: 500;
            background: rgba(0,0,0,.6);
        }
        .mobile-drawer.open { display: flex; justify-content: flex-end; }
        .drawer-panel {
            background: #0d1525; border-left: 1px solid #1e293b;
            width: 260px; padding: 20px 16px;
            display: flex; flex-direction: column; gap: 10px;
            animation: slideIn .2s ease;
        }
        @keyframes slideIn { from{transform:translateX(100%)} to{transform:translateX(0)} }
        .drawer-close {
            align-self: flex-end; background: none; border: none;
            color: #94a3b8; font-size: 22px; cursor: pointer; margin-bottom: 8px;
        }
        .drawer-link {
            display: flex; align-items: center; gap: 10px;
            padding: 12px 14px; border-radius: 12px; border: 1px solid #1e293b;
            background: #131b2e; color: #e2e8f0; text-decoration: none;
            font-size: 13.5px; font-weight: 700; transition: all .2s;
        }
        .drawer-link:hover { background: #10b981; color: #fff; border-color: #10b981; }

        @media (max-width: 768px) {
            .top-bar-nav { display: none; }
            .hamburger { display: block; }
        }
    </style>
</head>
<body>

    <!-- ── TOP BAR ──────────────────────────────────────────────────────── -->
    <div class="top-bar">
        <div class="top-bar-brand">
            <img src="{{ wilder_avatar }}" alt="Wilder">
            <div>
                <div class="top-bar-title">QG DIGITAL</div>
                <div class="top-bar-sub"><span class="live-dot"></span>WILDER MORAIS 2026 · AO VIVO</div>
            </div>
        </div>
        <nav class="top-bar-nav">
            <a href="/dashboard"    class="nav-icon-btn">📊 YouTube</a>
            <a href="/mapa_demandas" class="nav-icon-btn">🗺️ Mapa</a>
            <a href="/eventos"      class="nav-icon-btn">🎪 Eventos</a>
            <a href="/radar_noticias" class="nav-icon-btn">🚨 Notícias</a>
            <a href="/engajamento"  class="nav-icon-btn" style="background:linear-gradient(135deg,#7c3aed,#db2777);color:#fff;">🚀 Engajamento</a>
            <a href="/intel"      class="nav-icon-btn" style="background:linear-gradient(135deg,#0f172a,#1e3a4a);border:1px solid #00ff88;color:#00ff88;">🏖️ Intel</a>
            <a href="/download_pdf" target="_blank" class="nav-icon-btn">📄 PDF 360°</a>
        </nav>
        <button class="hamburger" onclick="toggleDrawer()">☰</button>
    </div>

    <!-- ── STORIES (módulos como Instagram) ─────────────────────────────── -->
    <div class="stories-bar">
        <a href="/dashboard" class="story-item">
            <div class="story-ring"><div class="story-ring-inner">📊</div></div>
            <span class="story-label">YouTube</span>
        </a>
        <a href="/mapa_demandas" class="story-item">
            <div class="story-ring" style="background:linear-gradient(135deg,#ef4444,#f97316)"><div class="story-ring-inner">🗺️</div></div>
            <span class="story-label">Mapa Goiás</span>
        </a>
        <a href="/eventos" class="story-item">
            <div class="story-ring" style="background:linear-gradient(135deg,#8b5cf6,#3b82f6)"><div class="story-ring-inner">🎪</div></div>
            <span class="story-label">150 Eventos</span>
        </a>
        <a href="/radar_noticias" class="story-item">
            <div class="story-ring" style="background:linear-gradient(135deg,#ef4444,#8b5cf6)"><div class="story-ring-inner">🚨</div></div>
            <span class="story-label">Notícias</span>
        </a>
        <a href="/plano_governo" class="story-item">
            <div class="story-ring" style="background:linear-gradient(135deg,#10b981,#06b6d4)"><div class="story-ring-inner">📋</div></div>
            <span class="story-label">Plano Gov.</span>
        </a>
        <a href="/download_pdf" target="_blank" class="story-item">
            <div class="story-ring" style="background:linear-gradient(135deg,#f59e0b,#ef4444)"><div class="story-ring-inner">📄</div></div>
            <span class="story-label">PDF 360°</span>
        </a>
        <a href="/engajamento" class="story-item">
            <div class="story-ring" style="background:linear-gradient(135deg,#7c3aed,#db2777)"><div class="story-ring-inner">🚀</div></div>
            <span class="story-label">Viral Lab</span>
        </a>
        <a href="/intel" class="story-item">
            <div class="story-ring" style="background:linear-gradient(135deg,#001a0a,#004d2a);border:2px solid #00ff88;box-shadow:0 0 12px #00ff8840;"><div class="story-ring-inner">🎖️</div></div>
            <span class="story-label">Intel</span>
        </a>
    </div>

    <!-- ── FEED ──────────────────────────────────────────────────────────── -->
    <div class="feed-wrapper" id="feedWrapper">

        <!-- CARD 0: STATUS DO MOTOR AO VIVO -->
        <div class="post-card" style="border: 1px solid rgba(16,185,129,0.35); background: linear-gradient(135deg, #0a1829, #0d1525);">
            <div class="post-header">
                <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#059669,#10b981);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">⚡</div>
                <div>
                    <div class="post-author" style="color:#10b981;">MOTOR AUTÔNOMO QG DIGITAL</div>
                    <div class="post-time">Auto-atualização ativa a cada 30 min • {{ status_motor.timestamp_servidor }}</div>
                </div>
                <span class="post-badge badge-new" style="background:#10b98125;color:#10b981;border-color:#10b98160;">🟢 100% ONLINE</span>
            </div>
            <div class="post-body">
                <div class="post-text">
                    📡 <strong style="color:#f8fafc;">Central de Inteligência Ativa:</strong> Robôs em background monitoram continuamente notícias da imprensa goiana, dados do YouTube e tendências do eleitorado sem necessidade de deploys manuais.
                </div>
                <div class="post-metric-row">
                    <div class="metric-pill"><span class="mp-val" style="color:#10b981;">{{ status_motor.fontes.noticias.total }}</span><span class="mp-lbl">Notícias RSS ({{ status_motor.fontes.noticias.atualizado }})</span></div>
                    <div class="metric-pill"><span class="mp-val" style="color:#ef4444;">{{ status_motor.fontes.yt_videos.total }}</span><span class="mp-lbl">Vídeos YT ({{ status_motor.fontes.yt_videos.atualizado }})</span></div>
                    <div class="metric-pill"><span class="mp-val" style="color:#f59e0b;">{{ status_motor.fontes.yt_canais.total }}</span><span class="mp-lbl">Canais ({{ status_motor.fontes.yt_canais.atualizado }})</span></div>
                    <div class="metric-pill"><span class="mp-val" style="color:#8b5cf6;">{{ status_motor.fontes.tendencias.total }}</span><span class="mp-lbl">Buscas ({{ status_motor.fontes.tendencias.atualizado }})</span></div>
                </div>
            </div>
            <div style="display:flex;gap:8px;padding:0 14px 14px;">
                <a href="/radar_noticias" class="post-action-btn" style="flex:1;margin:0;">📰 Ver {{ status_motor.fontes.noticias.total }} Notícias ao Vivo →</a>
                <a href="/api/status" target="_blank" class="post-action-btn" style="flex:0 0 auto;margin:0;background:#0b0f19;color:#94a3b8;border-color:#1e293b;">📊 API Status</a>
            </div>
        </div>

        <div class="feed-section-title">📡 INTELIGÊNCIA EM TEMPO REAL</div>

        <!-- Card 1: Pesquisa -->
        <div class="post-card">
            <div class="post-header">
                <img src="{{ wilder_avatar }}" class="post-avatar">
                <div>
                    <div class="post-author">QG Digital · Pesquisa</div>
                    <div class="post-time">Atualizado agora</div>
                </div>
                <span class="post-badge badge-live">🔴 AO VIVO</span>
            </div>
            <div class="post-body">
                <div class="post-text">
                    📊 <strong style="color:#f59e0b">Goiás Pesquisas / Mais Goiás:</strong> Daniel Vilela lidera com <strong style="color:#ef4444">37,2%</strong>. Wilder Morais e Marconi Perillo <strong style="color:#10b981">empatados em 2º lugar</strong> — janela real de crescimento para o segundo turno.
                </div>
                <div class="post-metric-row">
                    <div class="metric-pill"><span class="mp-val" style="color:#10b981">22%</span><span class="mp-lbl">Wilder Intenção</span></div>
                    <div class="metric-pill"><span class="mp-val" style="color:#ef4444">37%</span><span class="mp-lbl">Vilela Liderança</span></div>
                    <div class="metric-pill"><span class="mp-val" style="color:#f59e0b">+18K</span><span class="mp-lbl">Inscritos/mês YT</span></div>
                    <div class="metric-pill"><span class="mp-val" style="color:#8b5cf6">6.4%</span><span class="mp-lbl">Engajamento</span></div>
                </div>
            </div>
            <a href="/radar_noticias" class="post-action-btn">📊 Ver análise completa de pesquisas →</a>
        </div>

        <!-- Card 2: Mapa de Dores -->
        <div class="post-card">
            <div class="post-header">
                <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#ef4444,#f97316);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🗺️</div>
                <div>
                    <div class="post-author">Mapa de Demandas · 8 Cidades Polo</div>
                    <div class="post-time">246 municípios mapeados</div>
                </div>
                <span class="post-badge badge-hot">🔥 TOP</span>
            </div>
            <div class="post-body">
                <div class="post-text">
                    As <strong style="color:#f59e0b">8 cidades polo de Goiás</strong> estão mapeadas com suas dores principais: <strong style="color:#ef4444">Saúde &amp; Filas do SUS (42%)</strong>, <strong style="color:#f97316">Transporte &amp; Asfalto (28%)</strong>, Logística Agro e Emprego Jovem. Mapa interativo colorido por pauta.
                </div>
                <div class="post-metric-row">
                    <div class="metric-pill"><span class="mp-val">1.03M</span><span class="mp-lbl">Eleitores Goiânia</span></div>
                    <div class="metric-pill"><span class="mp-val">345K</span><span class="mp-lbl">Eleitores Aparecida</span></div>
                    <div class="metric-pill"><span class="mp-val">290K</span><span class="mp-lbl">Eleitores Anápolis</span></div>
                </div>
            </div>
            <a href="/mapa_demandas" class="post-action-btn">🗺️ Abrir mapa interativo de Goiás →</a>
        </div>

        <!-- Card 3: YouTube -->
        <div class="post-card">
            <div class="post-header">
                <div style="width:36px;height:36px;border-radius:50%;background:#dc2626;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">▶</div>
                <div>
                    <div class="post-author">Auditoria YouTube Real</div>
                    <div class="post-time">Dados buscados ao vivo</div>
                </div>
                <span class="post-badge badge-new">✨ REAL</span>
            </div>
            <div class="post-body">
                <div class="post-text">
                    Canal <strong style="color:#10b981">@WilderMoraisGoias</strong> monitorado em tempo real. Vídeo em destaque: <em style="color:#f59e0b">"PL confirma Wilder Morais &amp; Ana Paula"</em> com alto engajamento positivo no setor Agro e Entorno DF.
                </div>
                <div class="post-metric-row">
                    <div class="metric-pill"><span class="mp-val" style="color:#dc2626">124K</span><span class="mp-lbl">Inscritos Canal</span></div>
                    <div class="metric-pill"><span class="mp-val" style="color:#10b981">+18K</span><span class="mp-lbl">Crescimento/mês</span></div>
                    <div class="metric-pill"><span class="mp-val" style="color:#f59e0b">88K</span><span class="mp-lbl">Views Semanais</span></div>
                </div>
            </div>
            <a href="/dashboard" class="post-action-btn">📺 Ver auditoria completa dos candidatos →</a>
        </div>

        <!-- Card 4: Eventos -->
        <div class="post-card">
            <div class="post-header">
                <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#8b5cf6,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🎪</div>
                <div>
                    <div class="post-author">Radar de Eventos · Goiás 2026</div>
                    <div class="post-time">150 eventos mapeados</div>
                </div>
                <span class="post-badge badge-hot">🎯 ADS</span>
            </div>
            <div class="post-body">
                <div class="post-text">
                    <strong style="color:#8b5cf6">150 eventos estratégicos</strong> em Goiás com raio de Meta Ads calculado. Feiras agro, festividades regionais e eventos religiosos — janelas de impacto máximo para tráfego pago.
                </div>
                <div class="post-metric-row">
                    <div class="metric-pill"><span class="mp-val" style="color:#8b5cf6">150</span><span class="mp-lbl">Eventos Mapeados</span></div>
                    <div class="metric-pill"><span class="mp-val">246</span><span class="mp-lbl">Municípios</span></div>
                    <div class="metric-pill"><span class="mp-val" style="color:#10b981">Meta Ads</span><span class="mp-lbl">Raio Calculado</span></div>
                </div>
            </div>
            <a href="/eventos" class="post-action-btn">🎪 Ver radar de 150 eventos →</a>
        </div>

        <!-- Card 5: Plano de Governo -->
        <div class="post-card">
            <div class="post-header">
                <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#10b981,#06b6d4);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">📋</div>
                <div>
                    <div class="post-author">Plano de Governo Wilder</div>
                    <div class="post-time">Resumo Executivo 2026</div>
                </div>
                <span class="post-badge badge-new">📌 FIXADO</span>
            </div>
            <div class="post-body">
                <div class="post-text">
                    As principais propostas do plano de governo: <strong style="color:#10b981">Saúde</strong> — Hospitais Regionais e UPAs 24h. <strong style="color:#3b82f6">Emprego</strong> — Primeiro Emprego Jovem e incentivo ao DAIA. <strong style="color:#f59e0b">Agro</strong> — Logística e desburocratização. Acesse o plano completo integrado com IA.
                </div>
            </div>
            <a href="/plano_governo" class="post-action-btn">📋 Consultar plano de governo com IA →</a>
        </div>

        <div class="feed-section-title" style="margin-top:8px;">🤖 PERGUNTAS FREQUENTES AO QG</div>

        <!-- Card IA -->
        <div class="post-card" style="border-color:#10b98140;">
            <div class="post-header">
                <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#059669,#10b981);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🤖</div>
                <div>
                    <div class="post-author">IA do QG Digital</div>
                    <div class="post-time">Gemini Flash · Responde 24h</div>
                </div>
                <span class="post-badge badge-live">● ONLINE</span>
            </div>
            <div class="post-body">
                <div class="post-text" style="margin-bottom:12px;">
                    Pergunte qualquer coisa sobre a campanha, dados de pesquisa, YouTube, mapa de dores ou Google Trends de Goiás. A IA tem acesso a <strong style="color:#10b981">todo o contexto estratégico do QG Digital</strong>.
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:7px;">
                    <span class="qa-chip" style="position:static;padding:7px 12px;font-size:11.5px;" onclick="abrirChatComPergunta('Quais as propostas de Wilder para Saúde?')">💊 Propostas Saúde</span>
                    <span class="qa-chip" style="position:static;padding:7px 12px;font-size:11.5px;" onclick="abrirChatComPergunta('O que o goiano pesquisa sobre o Wilder no Google?')">🔍 Google Trends</span>
                    <span class="qa-chip" style="position:static;padding:7px 12px;font-size:11.5px;" onclick="abrirChatComPergunta('Qual a situação nas pesquisas eleitorais de Goiás?')">📊 Pesquisas</span>
                    <span class="qa-chip" style="position:static;padding:7px 12px;font-size:11.5px;" onclick="abrirChatComPergunta('Quais vídeos devemos gravar para o YouTube?')">🎬 Estratégia YT</span>
                </div>
            </div>
        </div>

    </div>

    <!-- ── QUICK CHIPS BARRA FLUTUANTE ───────────────────────────────────── -->
    <div class="quick-ask-bar">
        <span class="qa-chip" onclick="abrirChat()">💬 Consultar IA</span>
        <span class="qa-chip" onclick="abrirChatComPergunta('Situação atual das pesquisas?')">📊 Pesquisas</span>
        <span class="qa-chip" onclick="abrirChatComPergunta('Quais as principais dores do povo goiano?')">📍 Dores do Povo</span>
        <span class="qa-chip" onclick="abrirChatComPergunta('O que o goiano pesquisa sobre o Wilder no Google?')">🔍 Google Trends</span>
        <span class="qa-chip" onclick="abrirChatComPergunta('Quais eventos acontecem em Goiás nos próximos meses?')">🎪 Eventos</span>
    </div>

    <!-- ── CHAT BAR FIXO NO RODAPÉ ───────────────────────────────────────── -->
    <div class="chat-bar-fixed">
        <input class="chat-bar-input" id="chatBarInput" placeholder="Pergunte ao QG Digital..." onkeypress="if(event.key==='Enter') enviarRapido()" onclick="abrirChat()">
        <button class="chat-bar-send" onclick="enviarRapido()">➤</button>
    </div>

    <!-- ── CHAT OVERLAY (abre ao clicar) ────────────────────────────────── -->
    <div class="chat-overlay" id="chatOverlay">
        <div class="chat-overlay-header">
            <button class="chat-back-btn" onclick="fecharChat()">← Voltar</button>
            <img src="{{ wilder_avatar }}" style="width:32px;height:32px;border-radius:50%;border:2px solid #f59e0b;object-fit:cover;">
            <div class="chat-overlay-title">QG Digital IA · <span style="color:#10b981;">● Online</span></div>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="msg-row">
                <img src="{{ wilder_avatar }}" class="msg-av">
                <div class="msg-bbl bot">
                    <strong style="color:#10b981;">🔰 QG DIGITAL — INTELIGÊNCIA ELEITORAL</strong><br><br>
                    Olá! Sou a IA do QG Digital Eleitoral de Wilder Morais. Tenho acesso completo a dados de YouTube, mapa de demandas populares, Google Trends de Goiás, pesquisas eleitorais e muito mais.<br><br>
                    <strong>Como posso ajudar a campanha agora?</strong>
                </div>
            </div>
        </div>
        <div class="chat-input-row">
            <input class="ci-input" id="ciInput" placeholder="Digite sua pergunta..." onkeypress="if(event.key==='Enter') enviar()">
            <button class="ci-send" onclick="enviar()">➤</button>
        </div>
    </div>

    <!-- ── MOBILE DRAWER ─────────────────────────────────────────────────── -->
    <div class="mobile-drawer" id="mobileDrawer" onclick="if(event.target===this)fecharDrawer()">
        <div class="drawer-panel">
            <button class="drawer-close" onclick="fecharDrawer()">✕</button>
            <a href="/dashboard"      class="drawer-link">📊 Gestão YouTube Real</a>
            <a href="/mapa_demandas"  class="drawer-link">🗺️ Mapa Colorido &amp; Gráficos</a>
            <a href="/eventos"        class="drawer-link">🎪 Radar de 150 Eventos</a>
            <a href="/radar_noticias" class="drawer-link">🚨 Pesquisas &amp; Notícias</a>
            <a href="/plano_governo"  class="drawer-link">📋 Plano de Governo</a>
            <a href="/engajamento"    class="drawer-link" style="background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(219,39,119,0.1));border-color:#7c3aed;">🚀 Engajamento Viral Lab</a>
            <a href="/intel"          class="drawer-link" style="background:linear-gradient(135deg,rgba(0,255,136,0.08),rgba(0,100,50,0.05));border-color:#00ff8840;color:#00ff88;">🎖️ Centro de Inteligência</a>
            <a href="/download_pdf" target="_blank" class="drawer-link">📄 PDF 360° Completo</a>
        </div>
    </div>

    <script>
        const AVATAR = "{{ wilder_avatar }}";

        // ── Drawer mobile
        function toggleDrawer() { document.getElementById('mobileDrawer').classList.toggle('open'); }
        function fecharDrawer() { document.getElementById('mobileDrawer').classList.remove('open'); }

        // ── Chat overlay
        function abrirChat() { document.getElementById('chatOverlay').classList.add('open'); document.getElementById('ciInput').focus(); }
        function fecharChat() { document.getElementById('chatOverlay').classList.remove('open'); }

        function abrirChatComPergunta(texto) {
            abrirChat();
            document.getElementById('ciInput').value = texto;
            setTimeout(enviar, 200);
        }

        // ── Envio pelo chat bar fixo do feed
        function enviarRapido() {
            const val = document.getElementById('chatBarInput').value.trim();
            if (val) {
                abrirChat();
                document.getElementById('ciInput').value = val;
                document.getElementById('chatBarInput').value = '';
                setTimeout(enviar, 200);
            } else {
                abrirChat();
            }
        }

        // ── FORMATADOR MODERNO DE RESPOSTAS DA IA (PADRÃO CHATGPT / CLAUDE) ──
        function formatarRespostaModernaIA(textoBruto) {
            if (!textoBruto) return '';
            let txt = String(textoBruto);

            // 1. Quebra listas e tópicos inline que vieram sem quebra de linha
            txt = txt.replace(/(\\s+\\*\\s+\\*{1,3})/g, '\\n- ');
            txt = txt.replace(/(\\s+\\d+\\.\\s+\\*{0,3})/g, (match) => '\\n' + match.trim() + ' ');
            txt = txt.replace(/(\\s+\\*{2}Recomendação Estratégica:?\\*{2})/gi, '\\n\\n### 💡 Recomendação Estratégica:\\n');
            txt = txt.replace(/(\\s+\\*{2}Ação Prática:?\\*{2})/gi, '\\n\\n### 🚀 Ação Prática:\\n');

            // 2. Converte negritos e itálicos
            txt = txt.replace(/\\*\\*\\*(.*?)\\*\\*\\*/g, '<strong class="ai-highlight">$1</strong>');
            txt = txt.replace(/\\*\\*(.*?)\\*\\*/g, '<strong class="ai-highlight">$1</strong>');

            // 3. Processamento linha por linha
            const linhas = txt.split('\\n');
            let htmlFinal = '';
            let emLista = false;

            for (let i = 0; i < linhas.length; i++) {
                let linha = linhas[i].trim();
                if (!linha) {
                    if (emLista) { htmlFinal += '</ul>'; emLista = false; }
                    continue;
                }

                // Títulos e cabeçalhos de seção (###, ##, #)
                if (linha.startsWith('### ') || linha.startsWith('## ') || linha.startsWith('# ')) {
                    if (emLista) { htmlFinal += '</ul>'; emLista = false; }
                    const titulo = linha.replace(/^#+\\s*/, '');
                    htmlFinal += `<div class="ai-title">${titulo}</div>`;
                    continue;
                }

                // Cartões de recomendação / destaque
                if (linha.toLowerCase().includes('recomendação estratégica:') || linha.toLowerCase().includes('estratégia:') || linha.toLowerCase().includes('ação prática:')) {
                    if (emLista) { htmlFinal += '</ul>'; emLista = false; }
                    htmlFinal += `<div class="ai-card gold">${linha}</div>`;
                    continue;
                }

                // Itens de lista (1., 2., -, *, •)
                const matchLista = linha.match(/^(\\d+\\.|[-*•])\\s+(.*)/);
                if (matchLista) {
                    if (!emLista) { htmlFinal += '<ul class="ai-list">'; emLista = true; }
                    const numBadge = /^\\d+\\./.test(matchLista[1]) ? `<span class="ai-badge">${matchLista[1]}</span>` : '<span style="color:#38bdf8;margin-right:6px;">▪</span>';
                    htmlFinal += `<li class="ai-list-item">${numBadge}${matchLista[2]}</li>`;
                    continue;
                }

                // Linha de texto comum
                if (emLista) { htmlFinal += '</ul>'; emLista = false; }

                if (linha.startsWith('👉') || linha.startsWith('📊') || linha.startsWith('🚀') || linha.startsWith('🎖️') || linha.startsWith('💡')) {
                    htmlFinal += `<div class="ai-card">${linha}</div>`;
                } else {
                    htmlFinal += `<p class="ai-p">${linha}</p>`;
                }
            }

            if (emLista) { htmlFinal += '</ul>'; }
            return htmlFinal || txt;
        }

        // ── Envio da mensagem
        async function enviar() {
            const input = document.getElementById('ciInput');
            const msgs  = document.getElementById('chatMessages');
            const pergunta = input.value.trim();
            if (!pergunta) return;

            // Bubble do usuário
            const userRow = document.createElement('div');
            userRow.className = 'msg-row user';
            userRow.innerHTML = `<div class="msg-bbl usr">${pergunta}</div>`;
            msgs.appendChild(userRow);
            input.value = '';
            msgs.scrollTop = msgs.scrollHeight;

            // Bubble de loading
            const botRow = document.createElement('div');
            botRow.className = 'msg-row';
            botRow.innerHTML = `<img src="${AVATAR}" class="msg-av"><div class="msg-bbl bot"><em style="color:#64748b;">Processando...</em></div>`;
            msgs.appendChild(botRow);
            msgs.scrollTop = msgs.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pergunta })
                });
                const data = await res.json();
                botRow.querySelector('.msg-bbl.bot').innerHTML = formatarRespostaModernaIA(data.resposta);
            } catch(e) {
                botRow.querySelector('.msg-bbl.bot').innerHTML = '<strong>Erro na consulta com o QG Digital.</strong>';
            }
            msgs.scrollTop = msgs.scrollHeight;
        }
    </script>
</body>
</html>
"""


# ROUTE HTML: MAPA DEMANDAS COLORIDO & 4 GRÁFICOS
HTML_MAPA_DEMANDAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa Tático Interativo & Gráficos — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <!-- Leaflet CSS & JS - Cloudflare CDN (Mais Estável e sem bloqueio de integridade) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    <script src="/static/chart.js"></script>
    """ + PREMIUM_THEME_CSS + """
    <style>
        .legend-bar { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; display: flex; gap: 14px; flex-wrap: wrap; align-items: center; }
        .legend-item { display: flex; align-items: center; gap: 6px; font-size: 12.5px; font-weight: 700; }
        .dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }

        #map { width: 100%; height: 480px; border-radius: 12px; border: 1px solid var(--border-color); background: #000; }
        .custom-pin { background: transparent !important; border: none !important; }

        .goias-svg-wrapper { position: relative; width: 100%; height: 480px; background: linear-gradient(135deg, #0b0f19, #131b2e); border-radius: 12px; border: 1px solid var(--border-color); overflow: hidden; display: flex; justify-content: center; align-items: center; }
        .pin-node { position: absolute; cursor: pointer; transform: translate(-50%, -50%); transition: transform 0.2s; z-index: 10; }
        .pin-node:hover { transform: translate(-50%, -50%) scale(1.3); z-index: 100; }
        
        @keyframes pulsePin {
            0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7); }
            70% { box-shadow: 0 0 0 12px rgba(245, 158, 11, 0); }
            100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
        }

        .pin-circle { width: 24px; height: 24px; border-radius: 50%; border: 2px solid #ffffff; box-shadow: 0 0 12px rgba(0,0,0,0.8); animation: pulsePin 2s infinite; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 800; color: #fff; }
        .pin-tooltip { display: none; position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); background: #0d1527; border: 1.5px solid var(--accent-gold); border-radius: 10px; padding: 12px; width: 240px; color: #fff; box-shadow: 0 8px 25px rgba(0,0,0,0.9); z-index: 200; font-size: 11.5px; pointer-events: none; }
        .pin-node:hover .pin-tooltip { display: block; }

        .charts-grid-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-bottom: 24px; }
        .chart-box { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 18px; min-height: 300px; }

        .bar-container { margin-bottom: 10px; }
        .bar-label { display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: #e2e8f0; margin-bottom: 4px; }
        .bar-track { background: #0b0f19; height: 14px; border-radius: 7px; overflow: hidden; border: 1px solid var(--border-color); }
        .bar-fill { height: 100%; border-radius: 7px; }
    </style>
</head>
<body>
    <div class="app-header">
        <div class="brand-container">
            <img src="{{ wilder_avatar }}" alt="" class="brand-avatar">
            <div>
                <h1 class="brand-title">MAPA TÁTICO & 4 GRÁFICOS VISUAIS</h1>
                <p class="brand-subtitle">● Inteligência Eleitoral de Goiás 2026</p>
            </div>
        </div>
        <button class="menu-toggle-btn" onclick="toggleMobileMenu()">☰ Menu</button>
        <div class="nav-links-wrapper" id="navMenuWrapper">
            <a href="/chat" class="btn-nav-link">💬 QG Digital Chat</a>
            <a href="/dashboard" class="btn-nav-link">📊 Gestão YouTube Real</a>
            <a href="/eventos" class="btn-nav-link">🎪 Radar de 150 Eventos</a>
            <a href="/radar_noticias" class="btn-nav-link">🚨 Pesquisas & Notícias</a>
        </div>
    </div>

    <div class="main-container">
        <!-- LEGENDA -->
        <div class="legend-bar">
            <span style="color:var(--accent-gold);font-weight:800;font-size:13.5px;">🎨 CORES DAS PAUTAS:</span>
            <div class="legend-item"><span class="dot" style="background:#ef4444;"></span> 🔴 Saúde & Filas SUS</div>
            <div class="legend-item"><span class="dot" style="background:#f97316;"></span> 🟠 Transporte & Asfalto</div>
            <div class="legend-item"><span class="dot" style="background:#10b981;"></span> 🟢 Logística Agro & Pontes</div>
            <div class="legend-item"><span class="dot" style="background:#3b82f6;"></span> 🔵 Emprego Jovem & DAIA</div>
            <div class="legend-item"><span class="dot" style="background:#8b5cf6;"></span> 🟣 Hospital Regional & Turismo</div>
        </div>

        <!-- MAPA DUAL MODE -->
        <div class="card-panel" style="position: relative;">
            <div class="card-panel-title">
                <span>📍 MAPA INTERATIVO (ÁREAS COROPLÉTICAS)</span>
                <span style="font-size:11.5px;color:var(--accent-cyan);">GEOLOCALIZAÇÃO</span>
            </div>
            
            <!-- REGRA DE OURO 1: Altura e Largura estritas inline para evitar height:0 -->
            <div id="map" style="height: 500px; width: 100%; position: relative; display: block; background-color: #0b0f19; border-radius: 12px;"></div>
        </div>

        <!-- 4 GRÁFICOS VISUAIS -->
        <div class="charts-grid-row">
            <div class="chart-box">
                <div class="card-panel-title"><span>📊 QUEIXAS POR MUNICÍPIO POLO (%)</span></div>
                <canvas id="chartCidades" style="max-height:240px;width:100%;"></canvas>
                <div id="fallbackCidades">
                    {% for c in reclamacoes %}
                    <div class="bar-container">
                        <div class="bar-label"><span>📍 {{ c.cidade }}</span><span style="color:var(--accent-gold);">{{ c.percentual }}</span></div>
                        <div class="bar-track"><div class="bar-fill" style="width: {{ c.percentual }}; background: {% if c.cor == 'red' %}#ef4444{% elif c.cor == 'orange' %}#f97316{% elif c.cor == 'green' %}#10b981{% elif c.cor == 'blue' %}#3b82f6{% else %}#8b5cf6{% endif %};"></div></div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <div class="chart-box">
                <div class="card-panel-title"><span>🍩 CATEGORIAS DE RECLAMAÇÕES</span></div>
                <canvas id="chartCategorias" style="max-height:240px;width:100%;"></canvas>
                <div id="fallbackCategorias">
                    <div class="bar-container"><div class="bar-label"><span>🏥 Saúde & Filas SUS</span><span style="color:#ef4444;">42%</span></div><div class="bar-track"><div class="bar-fill" style="width: 42%; background: #ef4444;"></div></div></div>
                    <div class="bar-container"><div class="bar-label"><span>🚗 Transporte & Asfalto</span><span style="color:#f97316;">28%</span></div><div class="bar-track"><div class="bar-fill" style="width: 28%; background: #f97316;"></div></div></div>
                    <div class="bar-container"><div class="bar-label"><span>🌾 Logística Agro</span><span style="color:#10b981;">14%</span></div><div class="bar-track"><div class="bar-fill" style="width: 14%; background: #10b981;"></div></div></div>
                </div>
            </div>
        </div>

        <!-- TABELAS RESPONSIVAS -->
        <div class="card-panel">
            <div class="card-panel-title"><span>🔍 GOOGLE TRENDS GOIÁS — DETALHAMENTO DE BUSCAS</span></div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Termo de Busca em Goiás</th>
                            <th>Volume Mensal Estimado</th>
                            <th>Tendência na Web</th>
                            <th>Resposta Estratégica da Campanha</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for t in google_trends %}
                        <tr>
                            <td><strong style="color:var(--accent-cyan);">{{ t.termo_busca }}</strong></td>
                            <td><strong style="color:var(--accent-gold);">{{ t.volume_mensal }}</strong></td>
                            <td>{{ t.tendencia }}</td>
                            <td><span style="color:var(--text-secondary);font-size:12px;">{{ t.resposta_campanha }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            {% if noticias_pesquisas %}
            <div style="margin-top:16px;padding-top:14px;border-top:1px dashed rgba(245,158,11,0.35);">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <span style="width:8px;height:8px;border-radius:50%;background:var(--accent-gold);box-shadow:0 0 8px var(--accent-gold);display:inline-block;animation:blink 1.2s infinite;"></span>
                    <span style="font-size:12px;font-weight:800;color:var(--accent-gold);letter-spacing:0.06em;text-transform:uppercase;">SONDAGENS & NOTÍCIAS DE PESQUISAS DETECTADAS AO VIVO:</span>
                </div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px;">
                    {% for np in noticias_pesquisas %}
                    <a href="{{ np.url }}" target="_blank" style="background:#0b0f19;border:1px solid #1e293b;border-radius:10px;padding:10px 14px;text-decoration:none;display:block;transition:all 0.2s;" onmouseenter="this.style.borderColor='var(--accent-gold)'" onmouseleave="this.style.borderColor='#1e293b'">
                        <div style="font-size:12.5px;font-weight:700;color:#f8fafc;line-height:1.4;">{{ np.manchete }}</div>
                        <div style="font-size:11px;color:#64748b;margin-top:6px;">📰 {{ np.veiculo }} · {{ np.data }}</div>
                    </a>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </div>

        <div class="card-panel">
            <div class="card-panel-title"><span>📋 DETALHAMENTO DAS 8 CIDADES POLO E ELEITORES TSE</span></div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Cidade Polo & Região</th>
                            <th>Pauta Prioritária</th>
                            <th>Eleitores TSE</th>
                            <th>Reclamação Específica</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for c in reclamacoes %}
                        <tr>
                            <td><strong style="color:var(--accent-gold);">📍 {{ c.cidade }}</strong><br><span style="font-size:11px;color:var(--text-secondary);">{{ c.regiao }}</span></td>
                            <td><strong style="color:var(--accent-cyan);">{{ c.pauta_principal }}</strong></td>
                            <td><strong style="color:var(--accent-green);">{{ c.eleitores }}</strong></td>
                            <td>{{ c.demanda_especifica }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {

            // ── MAPA DE DEMANDAS ────────────────────────────────────────────────
            var mapEl = document.getElementById('map');
            if (!mapEl) { console.error('DIV #map nao encontrada'); return; }
            if (typeof L === 'undefined') { console.error('Leaflet nao carregou'); return; }

            var map = L.map('map', { zoomControl: true, scrollWheelZoom: true }).setView([-16.6789, -49.2539], 7);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 18,
                subdomains: ['a','b','c'],
                attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
            }).addTo(map);

            var dadosCidades = {{ reclamacoes|tojson }};
            var colorMap = { 'red': '#ef4444', 'orange': '#f97316', 'green': '#10b981', 'blue': '#3b82f6', 'purple': '#8b5cf6' };

            // Carrega GeoJSON simplificado via fetch (arquivo local /static/goias_min.geojson)
            fetch('/static/goias_min.geojson')
                .then(function(r) {
                    if (!r.ok) throw new Error('GeoJSON status ' + r.status);
                    return r.json();
                })
                .then(function(geo) {
                    L.geoJSON(geo, {
                        style: function(f) {
                            var nome = (f.properties.name || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
                            var corFill = '#1e293b', opac = 0.15, w = 0.5;
                            dadosCidades.forEach(function(c) {
                                var cNome = (c.cidade || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
                                if (nome === cNome) { corFill = colorMap[c.cor] || '#10b981'; opac = 0.6; w = 2; }
                            });
                            return { fillColor: corFill, weight: w, opacity: 1, color: '#475569', fillOpacity: opac };
                        },
                        onEachFeature: function(f, layer) {
                            var nome = f.properties.name || '';
                            dadosCidades.forEach(function(c) {
                                var cNome = (c.cidade || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
                                var fNome = nome.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
                                if (fNome === cNome) {
                                    layer.bindPopup('<div style="font-family:sans-serif;min-width:180px"><b style="color:#f59e0b">📍 ' + c.cidade + '</b><br><span style="color:#38bdf8">' + c.pauta_principal + '</span><br><small style="color:#10b981"><b>Eleitores: ' + c.eleitores + '</b></small><br><small style="color:#94a3b8">' + c.demanda_especifica + '</small></div>');
                                }
                            });
                        }
                    }).addTo(map);
                    setTimeout(function() { map.invalidateSize(true); }, 300);
                })
                .catch(function(e) { console.error('Erro GeoJSON demandas:', e); });

            // Pins animados sobre o mapa
            dadosCidades.forEach(function(c) {
                if (!c.lat || !c.lon) return;
                var cor = colorMap[c.cor] || '#10b981';
                var icon = L.divIcon({
                    className: '',
                    html: '<div style="width:16px;height:16px;border-radius:50%;background:' + cor + ';border:2px solid #fff;box-shadow:0 0 8px ' + cor + ';"></div>',
                    iconSize: [16, 16], iconAnchor: [8, 8]
                });
                var popup = '<div style="font-family:sans-serif;min-width:180px"><b style="color:#f59e0b">📍 ' + c.cidade + '</b><br><span style="color:#38bdf8">' + c.pauta_principal + '</span><br><b style="color:#10b981">Eleitores: ' + c.eleitores + '</b></div>';
                L.marker([c.lat, c.lon], { icon: icon }).addTo(map).bindPopup(popup);
            });

            setTimeout(function() { map.invalidateSize(true); }, 200);
            setTimeout(function() { map.invalidateSize(true); }, 1000);

            // ── GRÁFICOS CHART.JS ───────────────────────────────────────────────
            try {
                if (typeof Chart !== 'undefined') {
                    Chart.defaults.color = '#94a3b8';
                    Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

                    // GRÁFICO 1 — Barras Queixas por Cidade
                    var elCidades = document.getElementById('chartCidades');
                    if (elCidades) {
                        elCidades.style.height = '240px';
                        var ctx1 = elCidades.getContext('2d');
                        var grad1 = ctx1.createLinearGradient(0, 0, 0, 240);
                        grad1.addColorStop(0, 'rgba(245,158,11,0.9)');
                        grad1.addColorStop(1, 'rgba(245,158,11,0.2)');

                        new Chart(ctx1, {
                            type: 'bar',
                            data: {
                                labels: ['Luziânia', 'Goiânia', 'Valparaíso', 'Aparecida', 'Anápolis', 'Rio Verde', 'Catalão', 'Itumbiara'],
                                datasets: [{
                                    label: '% Queixas Populares',
                                    data: [45, 42, 40, 38, 35, 30, 28, 25],
                                    backgroundColor: ['#f97316','#ef4444','#f97316','#ef4444','#3b82f6','#10b981','#3b82f6','#8b5cf6'],
                                    borderRadius: 6,
                                    borderSkipped: false
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                animation: { duration: 1200, easing: 'easeInOutQuart' },
                                plugins: {
                                    legend: { labels: { color: '#f8fafc', font: { weight: '700' } } },
                                    tooltip: { backgroundColor: '#131b2e', borderColor: '#f59e0b', borderWidth: 1, titleColor: '#f59e0b', bodyColor: '#e2e8f0', padding: 10 }
                                },
                                scales: {
                                    x: { ticks: { color: '#94a3b8', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,0.05)' } },
                                    y: { ticks: { color: '#94a3b8', callback: function(v) { return v + '%'; } }, grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: true }
                                }
                            }
                        });
                        if (document.getElementById('fallbackCidades')) document.getElementById('fallbackCidades').style.display = 'none';
                    }

                    // GRÁFICO 2 — Donut Categorias
                    var elCat = document.getElementById('chartCategorias');
                    if (elCat) {
                        elCat.style.height = '240px';
                        new Chart(elCat.getContext('2d'), {
                            type: 'doughnut',
                            data: {
                                labels: ['Saúde/SUS (42%)', 'Transporte (28%)', 'Agro/Pontes (14%)', 'Emprego Jovem (9%)', 'Hospital Regional (7%)'],
                                datasets: [{
                                    data: [42, 28, 14, 9, 7],
                                    backgroundColor: ['#ef4444','#f97316','#10b981','#3b82f6','#8b5cf6'],
                                    borderWidth: 2,
                                    borderColor: '#0b0f19',
                                    hoverOffset: 8
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                animation: { animateRotate: true, duration: 1400 },
                                cutout: '62%',
                                plugins: {
                                    legend: { position: 'bottom', labels: { color: '#f8fafc', padding: 12, font: { size: 11, weight: '700' } } },
                                    tooltip: { backgroundColor: '#131b2e', borderColor: '#f59e0b', borderWidth: 1, titleColor: '#f59e0b', bodyColor: '#e2e8f0', padding: 10 }
                                }
                            }
                        });
                        if (document.getElementById('fallbackCategorias')) document.getElementById('fallbackCategorias').style.display = 'none';
                    }
                }
            } catch(err) {
                console.warn('[Charts]', err);
            }
        });
    </script>
    <style>
        @keyframes pingMap {
            0% { transform: scale(1); opacity: 0.5; }
            75%, 100% { transform: scale(2.4); opacity: 0; }
        }
        .leaflet-container { background: #0b0f19 !important; }
        #map { height: 500px !important; width: 100% !important; display: block !important; position: relative; }
    </style>
</body>
</html>
"""

# ROUTE HTML: DASHBOARD YOUTUBE REAL AUDITADO
HTML_DASHBOARD_METABASE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestão & Auditoria YouTube Real — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    """ + PREMIUM_THEME_CSS + """
    <style>
        .metrics-grid-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .metric-stat-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 18px; border-top: 4px solid var(--accent-gold); box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .metric-stat-title { font-size: 12px; font-weight: 700; color: var(--accent-green); text-transform: uppercase; margin-bottom: 4px; }
        .metric-stat-value { font-size: 20px; font-weight: 800; color: #ffffff; }

        .videos-responsive-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-bottom: 24px; }
        .video-item-card { background: #0b0f19; border: 1px solid var(--border-color); border-radius: 14px; overflow: hidden; box-shadow: 0 6px 20px rgba(0,0,0,0.5); transition: transform 0.2s; }
        .video-item-card:hover { border-color: var(--accent-gold); transform: translateY(-2px); }

        /* EMBED 100% RESPONSIVO PARA SMARTPHONE / TABLET */
        .responsive-embed-box { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; background: #000; }
        .responsive-embed-box iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; }

        .video-card-body { padding: 16px; }
        .cand-badge { background: #1e293b; color: var(--accent-cyan); font-weight: 800; padding: 3px 8px; border-radius: 6px; font-size: 11px; display: inline-block; margin-bottom: 8px; border: 1px solid var(--border-color); }
        .video-card-title { font-size: 14.5px; font-weight: 800; color: #ffffff; line-height: 1.4; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

        .video-stats-pill-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; background: #131b2e; padding: 10px; border-radius: 8px; border: 1px solid var(--border-color); margin-bottom: 12px; font-size: 11.5px; }
        .btn-watch-yt { background: #dc2626; color: #fff; padding: 9px 14px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 12px; display: flex; align-items: center; justify-content: center; gap: 6px; border: 1px solid #f87171; width: 100%; }
        .btn-watch-yt:hover { background: #ef4444; }
    </style>
</head>
<body>
    <div class="app-header">
        <div class="brand-container">
            <img src="{{ wilder_avatar }}" alt="" class="brand-avatar">
            <div>
                <h1 class="brand-title">GESTÃO & AUDITORIA YOUTUBE REAL</h1>
                <p class="brand-subtitle">● Análise de Engajamento e Vídeos Reais</p>
            </div>
        </div>
        <button class="menu-toggle-btn" onclick="toggleMobileMenu()">☰ Menu</button>
        <div class="nav-links-wrapper" id="navMenuWrapper">
            <a href="/chat" class="btn-nav-link">💬 QG Digital Chat</a>
            <a href="/mapa_demandas" class="btn-nav-link">🗺️ Mapa Colorido & 4 Gráficos</a>
            <a href="/eventos" class="btn-nav-link">🎪 Radar de 150 Eventos</a>
            <a href="/radar_noticias" class="btn-nav-link">🚨 Pesquisas & Notícias</a>
        </div>
    </div>

    <div class="main-container">
        <!-- BANNER MOTOR AO VIVO -->
        <div style="background:linear-gradient(135deg, rgba(220,38,38,0.15), rgba(16,185,129,0.1));border:1px solid rgba(220,38,38,0.3);border-radius:14px;padding:14px 18px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="width:10px;height:10px;border-radius:50%;background:#ef4444;box-shadow:0 0 10px #ef4444;display:inline-block;animation:blink 1.2s infinite;"></span>
                <div>
                    <span style="font-weight:800;color:#f87171;font-size:13.5px;">AUDITORIA YOUTUBE AO VIVO — MOTOR AUTÔNOMO</span>
                    <div style="font-size:11.5px;color:#94a3b8;">Vídeos atualizados: <strong style="color:#10b981;">{{ status_motor.fontes.yt_videos.atualizado }}</strong> • Canais: <strong style="color:#f59e0b;">{{ status_motor.fontes.yt_canais.atualizado }}</strong> • <strong style="color:#38bdf8;">{{ yt_videos|length }} vídeos monitorados</strong></div>
                </div>
            </div>
            <div style="display:flex;gap:8px;">
                <button onclick="forcarAtualizacaoYT(this)" style="background:#dc2626;color:#fff;border:none;padding:8px 16px;border-radius:8px;font-weight:800;font-size:12px;cursor:pointer;display:inline-flex;align-items:center;gap:6px;transition:0.2s;">
                    🔄 Auditar Agora
                </button>
                <a href="/api/status" target="_blank" style="background:#131b2e;color:#94a3b8;border:1px solid #1e293b;padding:8px 12px;border-radius:8px;font-weight:700;font-size:12px;text-decoration:none;display:inline-flex;align-items:center;gap:4px;">
                    📊 Status JSON
                </a>
            </div>
        </div>

        <!-- FILTROS CANDIDATO -->
        <div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap;">
            <button class="btn-nav-link active" onclick="filtrarCandidato('todos')">🌐 Todos os Candidatos ({{ yt_videos|length }})</button>
            <button class="btn-nav-link" onclick="filtrarCandidato('Wilder Morais')">👤 Wilder Morais (PL)</button>
            <button class="btn-nav-link" onclick="filtrarCandidato('Daniel Vilela')">👤 Daniel Vilela (MDB)</button>
            <button class="btn-nav-link" onclick="filtrarCandidato('Marconi Perillo')">👤 Marconi Perillo (PSDB)</button>
        </div>

        <!-- CARDS MÉTRICAS AUDITADAS E NEUTRAS -->
        <div class="metrics-grid-row">
            <div class="metric-stat-card">
                <div class="metric-stat-title">🏛️ MAIOR CANAL (INSCRITOS REAIS)</div>
                <div class="metric-stat-value" style="color:var(--accent-cyan);">Marconi Perillo (2.130 inscritos)</div>
            </div>
            <div class="metric-stat-card">
                <div class="metric-stat-title">📊 VÍDEO COM MAIOR AUDIÊNCIA</div>
                <div class="metric-stat-value" style="color:var(--accent-gold);">Debate BandNews (9.565 visualizações)</div>
            </div>
            <div class="metric-stat-card">
                <div class="metric-stat-title">🎯 CANAIS OFICIAIS MONITORADOS</div>
                <div class="metric-stat-value" style="color:var(--accent-green);">Wilder: 711 • Daniel: 976 • Marconi: 2.130</div>
            </div>
        </div>

        <!-- TABELA CANAIS AUDITADOS -->
        <div class="card-panel">
            <div class="card-panel-title">
                <span>📊 AUDITORIA COMPARATIVA DE CANAIS GOIÁS 2026</span>
            </div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Candidato / Partido</th>
                            <th>Inscritos</th>
                            <th>Crescimento Mensal</th>
                            <th>Views Semanais</th>
                            <th>Taxa Engajamento</th>
                            <th>Sentimento Comentários</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for m in canal_metricas %}
                        <tr>
                            <td><strong style="color:var(--accent-gold);">👤 {{ m.candidato }}</strong></td>
                            <td>{{ m.inscritos }}</td>
                            <td><strong style="color:var(--accent-green);">{{ m.crescimento_mensal }}</strong></td>
                            <td>{{ m.views_semanais }}</td>
                            <td><span style="background:var(--accent-green);color:#fff;padding:2px 8px;border-radius:6px;font-weight:800;font-size:11px;">{{ m.engajamento_taxa }}</span></td>
                            <td><strong style="color:var(--accent-cyan);">{{ m.sentimento_comentarios }}</strong></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- GRID DE CARDS COM EMBED VÍDEO RESPONSIVO -->
        <div class="card-panel">
            <div class="card-panel-title">
                <span>🎬 VÍDEOS REAIS AUDITADOS (PLAYERS EMBED 100% OPERACIONAIS)</span>
            </div>

            <div class="videos-responsive-grid">
                {% for v in yt_videos %}
                <div class="video-item-card item-yt {{ v.candidato }}">
                    <div class="responsive-embed-box">
                        <iframe src="{{ v.embed_url }}" title="{{ v.titulo }}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                    </div>
                    <div class="video-card-body">
                        <span class="cand-badge">👤 {{ v.candidato }} &bull; {{ v.canal }}</span>
                        <div class="video-card-title">"{{ v.titulo }}"</div>
                        
                        <div class="video-stats-pill-grid">
                            <div>Views: <strong style="color:var(--accent-green);">👁️ {{ v.views }}</strong></div>
                            <div>Curtidas: <strong style="color:var(--accent-gold);">👍 {{ v.curtidas }}</strong></div>
                            <div>Comentários: <strong>💬 {{ v.comentarios }}</strong></div>
                            <div>Sentimento: <strong style="color:var(--accent-cyan);">{{ v.sentimento }}</strong></div>
                        </div>

                        <a href="{{ v.url }}" target="_blank" class="btn-watch-yt">🎬 Assistir Direto no YouTube</a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        function filtrarCandidato(cand) {
            const items = document.querySelectorAll('.item-yt');
            const btns = document.querySelectorAll('.btn-nav-link');
            btns.forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');

            items.forEach(item => {
                if (cand === 'todos' || item.classList.contains(cand)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        async function forcarAtualizacaoYT(btn) {
            const originalText = btn.innerHTML;
            btn.innerHTML = '⏳ Auditando...';
            btn.disabled = true;
            try {
                const res = await fetch('/api/forcar_atualizacao', { method: 'POST' });
                const data = await res.json();
                btn.innerHTML = '✅ Auditado!';
                setTimeout(() => { window.location.reload(); }, 1500);
            } catch(e) {
                btn.innerHTML = '❌ Erro ao auditar';
                setTimeout(() => { btn.innerHTML = originalText; btn.disabled = false; }, 3000);
            }
        }
    </script>
</body>
</html>
"""

# ROUTE HTML: RADAR DE 150 EVENTOS EM GOIÁS
HTML_RADAR_EVENTOS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <title>Radar de 150 Eventos em Goiás — QG Digital</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <!-- Leaflet CSS & JS - Cloudflare CDN (Mais Estável e sem bloqueio de integridade) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    """ + PREMIUM_THEME_CSS + """
    <style>
        /* REGRA DE OURO 1 NO CSS GLOBAL: Forçando block e altura mínima rigorosa */
        #mapEventos { width: 100% !important; height: 500px !important; display: block !important; border-radius: 12px; border: 1px solid var(--border-color); background-color: #0b0f19 !important; }
        .badge-cat { background: var(--accent-purple); color: #fff; font-weight: 800; padding: 3px 8px; border-radius: 6px; font-size: 11px; }
        .badge-pub { background: var(--accent-green); color: #fff; font-weight: 800; padding: 3px 8px; border-radius: 6px; font-size: 11px; }
    </style>
</head>
<body>
    <div class="app-header">
        <div class="brand-container">
            <img src="{{ wilder_avatar }}" alt="" class="brand-avatar">
            <div>
                <h1 class="brand-title">RADAR DE 150 EVENTOS EM GOIÁS</h1>
                <p class="brand-subtitle">● Mapeamento Agro, Romarias & Meta Ads</p>
            </div>
        </div>
        <button class="menu-toggle-btn" onclick="toggleMobileMenu()">☰ Menu</button>
        <div class="nav-links-wrapper" id="navMenuWrapper">
            <a href="/" class="btn-nav-link">🏠 Home QG</a>
            <a href="/dashboard" class="btn-nav-link">📊 YouTube</a>
            <a href="/mapa_demandas" class="btn-nav-link">🗺️ Demandas</a>
            <a href="/radar_noticias" class="btn-nav-link">🚨 Notícias</a>
            <a href="/engajamento" class="btn-nav-link" style="background:linear-gradient(135deg,#7c3aed,#db2777);color:#fff;border-color:#7c3aed;">🚀 Viral Lab</a>
            <a href="/intel" class="btn-nav-link" style="background:linear-gradient(135deg,#0f172a,#1e3a4a);border-color:#00ff88;color:#00ff88;">🎖️ Intel</a>
        </div>
    </div>

    <div class="main-container">
        <div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap;">
            <button class="btn-nav-link active" onclick="filtrarMes('todos')">🌐 Todos os Meses (150 Eventos)</button>
            <button class="btn-nav-link" onclick="filtrarMes('Agosto/2026')">📅 Agosto / 2026</button>
            <button class="btn-nav-link" onclick="filtrarMes('Setembro/2026')">📅 Setembro / 2026</button>
            <button class="btn-nav-link" onclick="filtrarMes('Outubro/2026')">📅 Outubro / 2026</button>
        </div>

        <div class="card-panel">
            <div class="card-panel-title">
                <span>📍 GEOLOCALIZAÇÃO DOS EVENTOS & RAIO META ADS</span>
                <span style="font-size:11.5px;color:var(--accent-gold);">150 EVENTOS MAPEADOS</span>
            </div>
            <div id="mapEventos"></div>
        </div>

        <div class="card-panel">
            <div class="card-panel-title">
                <span>📋 LISTAGEM COMPLETA DOS EVENTOS DE GOIÁS</span>
            </div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Nome do Evento & Cidade</th>
                            <th>Data & Mês</th>
                            <th>Categoria</th>
                            <th>Público Estimado</th>
                            <th>Tráfego Pago Meta Ads</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for e in eventos %}
                        <tr class="item-evento {{ e.mes }}">
                            <td><strong style="color:var(--accent-gold);">🎪 {{ e.nome }}</strong><br><span style="font-size:11px;color:var(--text-secondary);">📍 {{ e.cidade }} ({{ e.regiao }})</span></td>
                            <td><strong style="color:var(--accent-cyan);">📅 {{ e.data }}</strong></td>
                            <td><span class="badge-cat">{{ e.categoria }}</span></td>
                            <td><span class="badge-pub">👥 {{ e.publico_estimado }}</span></td>
                            <td><strong style="color:var(--accent-gold);">🎯 {{ e.raio_meta_ads }}</strong><br><span style="font-size:11px;color:var(--text-secondary);">{{ e.estrategia_trafego }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {

            // ── MAPA DE EVENTOS ─────────────────────────────────────────────────
            var mapEvEl = document.getElementById('mapEventos');
            if (!mapEvEl) { console.error('DIV #mapEventos nao encontrada'); return; }
            if (typeof L === 'undefined') { console.error('Leaflet nao carregou'); return; }

            var mapEv = L.map('mapEventos', { zoomControl: true }).setView([-16.6789, -49.2539], 7);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 18,
                subdomains: ['a','b','c'],
                attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
            }).addTo(mapEv);

            var dadosEventos = {{ eventos|tojson }};

            // Carrega GeoJSON simplificado via fetch
            fetch('/static/goias_min.geojson')
                .then(function(r) {
                    if (!r.ok) throw new Error('GeoJSON status ' + r.status);
                    return r.json();
                })
                .then(function(geo) {
                    L.geoJSON(geo, {
                        style: function(f) {
                            var nome = (f.properties.name || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
                            var hasEvent = dadosEventos.some(function(e) {
                                return (e.cidade || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase() === nome;
                            });
                            return {
                                fillColor: hasEvent ? '#8b5cf6' : '#1e293b',
                                weight: hasEvent ? 2 : 0.5,
                                opacity: 1,
                                color: '#475569',
                                fillOpacity: hasEvent ? 0.45 : 0.15
                            };
                        }
                    }).addTo(mapEv);
                    setTimeout(function() { mapEv.invalidateSize(true); }, 300);
                })
                .catch(function(e) { console.error('Erro GeoJSON eventos:', e); });

            // Circles nos eventos
            dadosEventos.forEach(function(e) {
                if (!e.lat || !e.lon) return;
                var popup = '<div style="font-family:sans-serif;min-width:180px"><b style="color:#8b5cf6">🎪 ' + e.nome + '</b><br><b style="color:#f59e0b">📍 ' + e.cidade + '</b> (' + e.regiao + ')<br><span style="color:#38bdf8">📅 ' + e.data + ' — ' + e.mes + '</span><br><b style="color:#10b981">👥 ' + e.publico_estimado + '</b></div>';
                L.circle([e.lat, e.lon], {
                    color: '#8b5cf6', fillColor: '#a855f7', fillOpacity: 0.4, weight: 2, radius: 8000
                }).addTo(mapEv).bindPopup(popup);
            });

            setTimeout(function() { mapEv.invalidateSize(true); }, 200);
            setTimeout(function() { mapEv.invalidateSize(true); }, 1000);
        });

        function filtrarMes(mes) {
            const items = document.querySelectorAll('.item-evento');
            const btns = document.querySelectorAll('.btn-nav-link');
            btns.forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');

            items.forEach(item => {
                if (mes === 'todos' || item.classList.contains(mes)) {
                    item.style.display = 'table-row';
                } else {
                    item.style.display = 'none';
                }
            });
        }
    </script>
    <style>
        .leaflet-container { background: #0b0f19 !important; }
        #mapEventos { height: 500px !important; width: 100% !important; display: block !important; position: relative; }
    </style>
</body>
</html>
"""



# ════════════════════════════════════════════════════════════════════════════
# INTELIGÊNCIA TERRITORIAL MILITAR — Monitoramento Real dos Goianos
# ════════════════════════════════════════════════════════════════════════════
HTML_INTELIGENCIA_TERRITORIAL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎖️ Intel Territorial — Centro de Comando | QG Wilder 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css"/>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.heat/0.2.0/leaflet-heat.js"></script>
    """ + PREMIUM_THEME_CSS + """
    <style>
        /* ── MILITAR OVERRIDE ────────────────────────────────────────────── */
        :root {
            --mil-green:   #00ff88;
            --mil-red:     #ff2244;
            --mil-amber:   #ffbb00;
            --mil-blue:    #00ccff;
            --mil-purple:  #aa44ff;
            --mil-bg:      #020811;
            --mil-panel:   #050e1a;
            --mil-border:  rgba(0,255,136,0.2);
        }
        body { background: var(--mil-bg) !important; }
        .mil-scan-line {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,136,0.015) 2px, rgba(0,255,136,0.015) 4px);
            pointer-events: none; z-index: 0;
        }
        .mil-content { position: relative; z-index: 1; }

        /* ── HEADER MILITAR ──────────────────────────────────────────────── */
        .mil-header {
            background: linear-gradient(135deg, #050e1a, #020811);
            border-bottom: 1px solid var(--mil-green);
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            box-shadow: 0 0 20px rgba(0,255,136,0.15);
        }
        .mil-brand {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .mil-brand img {
            width: 46px;
            height: 46px;
            border-radius: 50%;
            border: 2px solid var(--mil-green);
            box-shadow: 0 0 12px rgba(0,255,136,0.4);
        }
        .mil-title-block {}
        .mil-title-main {
            font-size: clamp(13px,2vw,18px);
            font-weight: 900;
            color: var(--mil-green);
            letter-spacing: 0.15em;
            text-transform: uppercase;
        }
        .mil-title-sub {
            font-size: 10.5px;
            color: #4a5568;
            letter-spacing: 0.08em;
        }
        .mil-status-pill {
            background: rgba(0,255,136,0.08);
            border: 1px solid var(--mil-green);
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 11.5px;
            font-weight: 800;
            color: var(--mil-green);
            letter-spacing: 0.06em;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .mil-live-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            background: var(--mil-green);
            box-shadow: 0 0 8px var(--mil-green);
            animation: blink 1s infinite;
        }
        .mil-nav {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .mil-nav-btn {
            background: rgba(0,255,136,0.05);
            border: 1px solid rgba(0,255,136,0.2);
            color: #94a3b8;
            padding: 6px 12px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 12px;
            font-weight: 700;
            transition: all 0.2s;
        }
        .mil-nav-btn:hover, .mil-nav-btn.active {
            background: rgba(0,255,136,0.15);
            border-color: var(--mil-green);
            color: var(--mil-green);
        }
        .mil-nav-btn.hot {
            background: linear-gradient(135deg,rgba(124,58,237,0.2),rgba(219,39,119,0.15));
            border-color: #7c3aed;
            color: #c4b5fd;
        }

        /* ── METRICS BAR ─────────────────────────────────────────────────── */
        .mil-metrics-bar {
            background: var(--mil-panel);
            border-bottom: 1px solid var(--mil-border);
            padding: 10px 20px;
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
            align-items: center;
        }
        .mil-metric {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .mil-metric-label {
            font-size: 9.5px;
            font-weight: 800;
            color: #4a5568;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .mil-metric-value {
            font-size: 18px;
            font-weight: 900;
            color: var(--mil-green);
            line-height: 1;
        }
        .mil-metric-value.red    { color: var(--mil-red); }
        .mil-metric-value.amber  { color: var(--mil-amber); }
        .mil-metric-value.blue   { color: var(--mil-blue); }
        .mil-sep { width: 1px; height: 40px; background: var(--mil-border); flex-shrink: 0; }

        /* ── LAYOUT ──────────────────────────────────────────────────────── */
        .mil-body {
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 0;
            height: calc(100vh - 130px);
            height: calc(100dvh - 130px);
            overflow: hidden;
        }
        @media (max-width: 900px) {
            .mil-body { grid-template-columns: 1fr; height: auto; overflow: auto; padding-bottom: 70px; }
            #milMap { height: 380px !important; min-height: 380px !important; }
            .mil-metrics-bar { gap: 10px; padding: 8px 12px; }
            .mil-metric { min-width: 45%; }
            .mil-sep { display: none; }
            .mil-legend { bottom: 10px; left: 8px; padding: 8px 10px; font-size: 10px; }
        }

        /* ── MAPA ────────────────────────────────────────────────────────── */
        .mil-map-area {
            position: relative;
            background: var(--mil-bg);
            border-right: 1px solid var(--mil-border);
        }
        #milMap {
            height: 100%;
            width: 100%;
            min-height: 400px;
        }
        .mil-map-controls {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .mil-ctrl-btn {
            background: rgba(5,14,26,0.92);
            border: 1px solid var(--mil-border);
            color: var(--mil-green);
            padding: 7px 13px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 800;
            cursor: pointer;
            letter-spacing: 0.05em;
            backdrop-filter: blur(4px);
            transition: all 0.2s;
        }
        .mil-ctrl-btn:hover { background: rgba(0,255,136,0.12); }
        .mil-ctrl-btn.active { background: rgba(0,255,136,0.2); border-color: var(--mil-green); }
        .mil-legend {
            position: absolute;
            bottom: 20px;
            left: 10px;
            z-index: 1000;
            background: rgba(5,14,26,0.92);
            border: 1px solid var(--mil-border);
            border-radius: 10px;
            padding: 12px 16px;
            backdrop-filter: blur(4px);
        }
        .mil-legend-title { font-size: 10px; font-weight: 800; color: var(--mil-green); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 8px; }
        .mil-legend-item { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; font-size: 11px; color: #94a3b8; }
        .mil-legend-dot { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }

        /* ── PAINEL LATERAL ──────────────────────────────────────────────── */
        .mil-side-panel {
            background: var(--mil-panel);
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }
        .mil-panel-tabs {
            display: flex;
            border-bottom: 1px solid var(--mil-border);
            background: var(--mil-bg);
            flex-shrink: 0;
        }
        .mil-tab {
            flex: 1;
            padding: 10px 6px;
            text-align: center;
            font-size: 10.5px;
            font-weight: 800;
            color: #4a5568;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .mil-tab.active {
            color: var(--mil-green);
            border-bottom-color: var(--mil-green);
            background: rgba(0,255,136,0.04);
        }
        .mil-tab-content { display: none; flex: 1; overflow-y: auto; }
        .mil-tab-content.active { display: block; }

        /* Alertas */
        .mil-alert-item {
            padding: 12px 16px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            display: flex;
            gap: 10px;
            align-items: flex-start;
        }
        .mil-alert-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            margin-top: 5px;
            flex-shrink: 0;
            box-shadow: 0 0 6px currentColor;
        }
        .mil-alert-mun { font-size: 12.5px; font-weight: 800; color: #f8fafc; }
        .mil-alert-msg { font-size: 11.5px; color: #64748b; margin-top: 3px; line-height: 1.4; }
        .mil-alert-ts  { font-size: 10px; color: #334155; margin-top: 4px; }

        /* Feed de queixas */
        .mil-queixa-item {
            padding: 11px 16px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
        }
        .mil-queixa-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
        }
        .mil-queixa-mun { font-size: 11px; font-weight: 800; color: #94a3b8; }
        .mil-queixa-badge {
            font-size: 9.5px;
            font-weight: 800;
            padding: 2px 8px;
            border-radius: 12px;
            letter-spacing: 0.05em;
        }
        .mil-queixa-text { font-size: 12px; color: #e2e8f0; line-height: 1.45; }
        .mil-queixa-meta { font-size: 10.5px; color: #334155; margin-top: 4px; }

        /* Ranking */
        .mil-rank-item {
            padding: 10px 16px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .mil-rank-num {
            font-size: 20px;
            font-weight: 900;
            color: #1e293b;
            min-width: 28px;
            text-align: right;
        }
        .mil-rank-bar-wrap { flex: 1; }
        .mil-rank-city { font-size: 12.5px; font-weight: 800; color: #f8fafc; }
        .mil-rank-reg  { font-size: 10.5px; color: #64748b; }
        .mil-rank-bar-bg { height: 5px; border-radius: 3px; background: #0f172a; margin-top: 5px; overflow: hidden; }
        .mil-rank-bar-fill { height: 100%; border-radius: 3px; transition: width 1.5s ease; }
        .mil-rank-count { font-size: 15px; font-weight: 900; min-width: 28px; text-align: right; }

        /* IBGE stats */
        .mil-ibge-card {
            margin: 10px 14px;
            background: rgba(0,255,136,0.04);
            border: 1px solid var(--mil-border);
            border-radius: 10px;
            padding: 14px;
        }
        .mil-ibge-city { font-size: 13px; font-weight: 800; color: var(--mil-green); margin-bottom: 8px; }
        .mil-ibge-row { display: flex; justify-content: space-between; font-size: 11.5px; margin-bottom: 4px; }
        .mil-ibge-key { color: #4a5568; }
        .mil-ibge-val { color: #e2e8f0; font-weight: 700; }

        /* Leaflet dark tiles */
        .leaflet-tile { filter: brightness(0.55) saturate(0.3) hue-rotate(180deg) !important; }
        .leaflet-container { background: #020811 !important; }
        .leaflet-popup-content-wrapper {
            background: #050e1a;
            border: 1px solid rgba(0,255,136,0.3);
            border-radius: 10px;
            color: #e2e8f0;
            box-shadow: 0 0 20px rgba(0,255,136,0.15);
        }
        .leaflet-popup-tip { background: #050e1a; }

        /* Animações */
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
        @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }
        .mil-pulse { animation: pulse 2s infinite; }

        /* Scrollbar estilizada */
        .mil-side-panel::-webkit-scrollbar,
        .mil-tab-content::-webkit-scrollbar { width: 4px; }
        .mil-side-panel::-webkit-scrollbar-track,
        .mil-tab-content::-webkit-scrollbar-track { background: transparent; }
        .mil-side-panel::-webkit-scrollbar-thumb,
        .mil-tab-content::-webkit-scrollbar-thumb { background: rgba(0,255,136,0.2); border-radius: 2px; }

        /* Nível de alarme */
        .nivel-0 { color: #1e293b; }
        .nivel-1 { color: #22c55e; }
        .nivel-2 { color: #eab308; }
        .nivel-3 { color: #f97316; }
        .nivel-4 { color: #ef4444; box-shadow: 0 0 8px #ef4444; }
    </style>
</head>
<body>
<div class="mil-scan-line"></div>
<div class="mil-content">

    <!-- HEADER MILITAR -->
    <div class="mil-header">
        <div class="mil-brand">
            <img src="{{ wilder_avatar }}" alt="Wilder">
            <div class="mil-title-block">
                <div class="mil-title-main">🎖️ Intel Territorial — Centro de Comando</div>
                <div class="mil-title-sub">MONITORAMENTO REAL • DADOS IBGE • RSS AO VIVO • NLP EM PORTUGUÊS • QG WILDER MORAIS 2026</div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
            <div class="mil-status-pill">
                <span class="mil-live-dot"></span>
                SISTEMA OPERACIONAL
            </div>
            <div class="mil-nav">
                <a href="/"              class="mil-nav-btn">🏠 Home</a>
                <a href="/mapa_demandas" class="mil-nav-btn">🗺️ Demandas</a>
                <a href="/radar_noticias" class="mil-nav-btn">🚨 Notícias</a>
                <a href="/dashboard"     class="mil-nav-btn">📊 YouTube</a>
                <a href="/engajamento"   class="mil-nav-btn hot">🚀 Viral Lab</a>
                <a href="/intel"         class="mil-nav-btn active">🎖️ Intel</a>
            </div>
        </div>
    </div>

    <!-- METRICS BAR -->
    <div class="mil-metrics-bar" id="metricsBar">
        <div class="mil-metric">
            <span class="mil-metric-label">Sinais Captados</span>
            <span class="mil-metric-value" id="metTotalSinais">—</span>
        </div>
        <div class="mil-sep"></div>
        <div class="mil-metric">
            <span class="mil-metric-label">Município mais Quente</span>
            <span class="mil-metric-value amber" id="metCidadeQuente">—</span>
        </div>
        <div class="mil-sep"></div>
        <div class="mil-metric">
            <span class="mil-metric-label">Pauta Dominante</span>
            <span class="mil-metric-value red" id="metPautaDom">—</span>
        </div>
        <div class="mil-sep"></div>
        <div class="mil-metric">
            <span class="mil-metric-label">Alertas Ativos</span>
            <span class="mil-metric-value" id="metAlertas">—</span>
        </div>
        <div class="mil-sep"></div>
        <div class="mil-metric">
            <span class="mil-metric-label">Municípios Monitorados</span>
            <span class="mil-metric-value blue" id="metMunicipios">246 <span style="font-size:11px;color:#00ff88;">(100% GO)</span></span>
        </div>
        <div class="mil-sep"></div>
        <div class="mil-metric">
            <span class="mil-metric-label">Última Coleta</span>
            <span class="mil-metric-value" id="metUltimaColeta" style="font-size:12px;color:#64748b;">Aguardando...</span>
        </div>
        <div style="margin-left:auto;">
            <button onclick="forcarColeta(this)" style="background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);color:#00ff88;padding:8px 16px;border-radius:6px;font-size:12px;font-weight:800;cursor:pointer;letter-spacing:0.05em;">
                🔄 ATUALIZAR INTEL
            </button>
        </div>
    </div>

    <!-- CORPO PRINCIPAL: MAPA + PAINEL LATERAL -->
    <div class="mil-body">

        <!-- MAPA TÁTICO -->
        <div class="mil-map-area">
            <div id="milMap"></div>

            <!-- Controles do mapa -->
            <div class="mil-map-controls">
                <button class="mil-ctrl-btn active" id="btnModoCalor" onclick="toggleModoCalor(this)">🔥 CALOR</button>
                <button class="mil-ctrl-btn" id="btnModoMarcadores" onclick="toggleModoMarcadores(this)">📍 PINS</button>
                <button class="mil-ctrl-btn" id="btnModoRegioes" onclick="toggleModoRegioes(this)">🗺️ REGIÕES</button>
            </div>

            <!-- Legenda -->
            <div class="mil-legend">
                <div class="mil-legend-title">INTENSIDADE DE QUEIXAS</div>
                <div class="mil-legend-item"><div class="mil-legend-dot" style="background:#ef4444;"></div> CRÍTICO — Saúde / Segurança</div>
                <div class="mil-legend-item"><div class="mil-legend-dot" style="background:#f97316;"></div> ALTO — Transporte / Emprego</div>
                <div class="mil-legend-item"><div class="mil-legend-dot" style="background:#eab308;"></div> MÉDIO — Infraestrutura</div>
                <div class="mil-legend-item"><div class="mil-legend-dot" style="background:#22c55e;"></div> BAIXO — Monitorado</div>
                <div class="mil-legend-item"><div class="mil-legend-dot" style="background:#1e293b;border:1px solid #334155;"></div> SEM DADOS</div>
            </div>
        </div>

        <!-- PAINEL LATERAL -->
        <div class="mil-side-panel">
            <div class="mil-panel-tabs">
                <div class="mil-tab active" onclick="trocarTab('alertas',this)">⚡ ALERTAS</div>
                <div class="mil-tab" onclick="trocarTab('queixas',this)">📡 FEED</div>
                <div class="mil-tab" onclick="trocarTab('ranking',this)">🏆 RANKING</div>
                <div class="mil-tab" onclick="trocarTab('ibge',this)">📊 IBGE</div>
            </div>

            <!-- Tab: Alertas Táticos -->
            <div class="mil-tab-content active" id="tab-alertas">
                <div id="listaAlertas" style="color:#4a5568;padding:20px;font-size:12px;">Carregando alertas...</div>
            </div>

            <!-- Tab: Feed de Queixas -->
            <div class="mil-tab-content" id="tab-queixas">
                <div style="padding:10px 16px;">
                    <select id="filtroQueixa" onchange="renderQueixas()" style="width:100%;background:#060a14;border:1px solid #1e293b;color:#94a3b8;padding:7px 10px;border-radius:7px;font-size:12px;margin-bottom:2px;">
                        <option value="">Todas as pautas</option>
                        <option value="SAUDE">🏥 Saúde</option>
                        <option value="TRANSPORTE">🚌 Transporte</option>
                        <option value="EMPREGO">💼 Emprego</option>
                        <option value="SEGURANCA">🚨 Segurança</option>
                        <option value="INFRAESTRUTURA">🏗️ Infraestrutura</option>
                        <option value="EDUCACAO">📚 Educação</option>
                    </select>
                </div>
                <div id="listaQueixas" style="color:#4a5568;padding:20px;font-size:12px;">Carregando feed...</div>
            </div>

            <!-- Tab: Ranking de Cidades -->
            <div class="mil-tab-content" id="tab-ranking">
                <div id="listaRanking" style="color:#4a5568;padding:20px;font-size:12px;">Carregando ranking...</div>
            </div>

            <!-- Tab: Dados IBGE -->
            <div class="mil-tab-content" id="tab-ibge">
                <div style="padding:10px 16px;border-bottom:1px solid rgba(0,255,136,0.08);">
                    <div style="font-size:11px;color:#4a5568;margin-bottom:6px;">Fonte: IBGE Censo 2022 + 246 Municípios Oficiais de Goiás</div>
                    <input type="text" id="buscaIbge" oninput="filtrarIbge()" placeholder="🔍 Buscar entre os 246 municípios..." style="width:100%;background:#060a14;border:1px solid #1e293b;color:#00ff88;padding:7px 10px;border-radius:7px;font-size:12px;outline:none;">
                </div>
                <div id="listaIbge" style="color:#4a5568;padding:12px;font-size:12px;">Carregando dados IBGE...</div>
            </div>
        </div>
    </div>

</div><!-- /mil-content -->

<script>
// ── DADOS GLOBAIS ──────────────────────────────────────────────────────────
let G_QUEIXAS   = [];
let G_MAPA_CALOR = [];
let G_ALERTAS   = [];
let G_RANKING   = [];
let G_IBGE      = {};
let G_STATUS    = {};

// ── MAPA LEAFLET ──────────────────────────────────────────────────────────
const map = L.map('milMap', {
    center: [-16.0, -49.5],
    zoom: 7,
    zoomControl: false,
    attributionControl: false
});
L.control.zoom({ position: 'bottomright' }).addTo(map);

// Tile layer escuro (CartoDB Dark)
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CartoDB',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);

let heatLayer = null;
let markerLayer = L.layerGroup().addTo(map);
let modoAtivo = 'calor';

function getNivelColor(nivel) {
    const cores = { 0:'#1e293b', 1:'#22c55e', 2:'#eab308', 3:'#f97316', 4:'#ef4444' };
    return cores[nivel] || '#1e293b';
}

function renderMapa(dados) {
    // Limpar camadas
    if (heatLayer) { map.removeLayer(heatLayer); heatLayer = null; }
    markerLayer.clearLayers();

    if (!dados || dados.length === 0) return;
    const maxQueixas = Math.max(...dados.map(d => d.total_queixas || 0)) || 1;

    if (modoAtivo === 'calor') {
        // Heatmap
        const pontos = dados
            .filter(d => d.total_queixas > 0)
            .map(d => [d.lat, d.lon, d.total_queixas / maxQueixas]);
        if (pontos.length > 0) {
            heatLayer = L.heatLayer(pontos, {
                radius: 35,
                blur: 22,
                maxZoom: 10,
                gradient: { 0.0: '#1e293b', 0.25: '#22c55e', 0.5: '#eab308', 0.75: '#f97316', 1.0: '#ef4444' }
            }).addTo(map);
        }
    }

    // Marcadores sempre visíveis (círculos)
    dados.forEach(d => {
        if (!d.lat || !d.lon) return;
        const cor = d.total_queixas > 0 ? getNivelColor(d.nivel) : '#1e293b';
        const radius = modoAtivo === 'pins' ? Math.max(4, d.total_queixas * 3 + 4) : Math.max(5, d.total_queixas * 2 + 5);

        const popupHtml = `
            <div style="font-family:'Plus Jakarta Sans',sans-serif;min-width:200px;padding:4px;">
                <div style="font-size:14px;font-weight:900;color:#00ff88;margin-bottom:6px;">
                    ${d.icone || '📍'} ${d.municipio}
                </div>
                <div style="font-size:11px;color:#64748b;margin-bottom:8px;">${d.regiao || ''}</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:11.5px;">
                    <div><span style="color:#4a5568;">Queixas:</span> <strong style="color:${cor};">${d.total_queixas}</strong></div>
                    <div><span style="color:#4a5568;">Pauta:</span> <strong style="color:${cor};">${d.pauta_dominante}</strong></div>
                    <div><span style="color:#4a5568;">Pop:</span> <strong style="color:#94a3b8;">${d.pop ? d.pop.toLocaleString('pt-BR') : '—'}</strong></div>
                    <div><span style="color:#4a5568;">Região:</span> <strong style="color:#94a3b8;">${d.regiao || '—'}</strong></div>
                </div>
                ${d.total_queixas > 0 ? '<div style="margin-top:8px;font-size:10.5px;color:#334155;">Clique para ver queixas desta cidade</div>' : ''}
            </div>`;

        const isAtivo = d.total_queixas > 0;
        const circle = L.circleMarker([d.lat, d.lon], {
            radius: isAtivo ? Math.max(7, d.total_queixas * 2.5 + 5) : 4,
            fillColor: isAtivo ? cor : '#0e3a5a',
            color: isAtivo ? cor : '#00ff8840',
            weight: isAtivo ? 2 : 1,
            opacity: isAtivo ? 1.0 : 0.6,
            fillOpacity: isAtivo ? 0.8 : 0.35
        }).bindPopup(popupHtml, { maxWidth: 260 })
          .on('click', () => filtrarCidade(d.municipio));

        markerLayer.addLayer(circle);

        // Label para cidades com queixas
        if (d.total_queixas > 0 && modoAtivo !== 'calor') {
            const label = L.divIcon({
                className: '',
                html: `<div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:10px;font-weight:800;color:${cor};text-shadow:0 0 8px #000,0 0 4px #000;white-space:nowrap;">${d.municipio}</div>`,
                iconAnchor: [-4, 6]
            });
            L.marker([d.lat, d.lon], { icon: label }).addTo(markerLayer);
        }
    });
}

function toggleModoCalor(btn) {
    modoAtivo = 'calor';
    document.querySelectorAll('.mil-ctrl-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderMapa(G_MAPA_CALOR);
}
function toggleModoMarcadores(btn) {
    modoAtivo = 'pins';
    document.querySelectorAll('.mil-ctrl-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderMapa(G_MAPA_CALOR);
}
function toggleModoRegioes(btn) {
    modoAtivo = 'regioes';
    document.querySelectorAll('.mil-ctrl-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderMapa(G_MAPA_CALOR);
}

// ── TABS ───────────────────────────────────────────────────────────────────
function trocarTab(id, el) {
    document.querySelectorAll('.mil-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.mil-tab-content').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('tab-' + id).classList.add('active');
}

// ── RENDER ALERTAS ─────────────────────────────────────────────────────────
function renderAlertas(alertas) {
    const el = document.getElementById('listaAlertas');
    if (!alertas || alertas.length === 0) {
        el.innerHTML = '<div style="padding:20px;font-size:12px;color:#1e293b;">Coletando dados... aguarde o primeiro ciclo.</div>';
        return;
    }
    el.innerHTML = alertas.map(a => `
        <div class="mil-alert-item">
            <div class="mil-alert-dot" style="background:${a.cor || '#ef4444'};color:${a.cor || '#ef4444'};"></div>
            <div>
                <div class="mil-alert-mun">${a.municipio}</div>
                <div class="mil-alert-msg">${a.mensagem}</div>
                <div class="mil-alert-ts">⏱️ ${a.timestamp}</div>
            </div>
        </div>`).join('');
}

// ── RENDER QUEIXAS ─────────────────────────────────────────────────────────
let _cidadeAtiva = '';
function filtrarCidade(cidade) {
    _cidadeAtiva = cidade;
    trocarTab('queixas', document.querySelector('.mil-tab:nth-child(2)'));
    renderQueixas();
}

function renderQueixas() {
    const el = document.getElementById('listaQueixas');
    const filtro = document.getElementById('filtroQueixa').value;
    let queixas = G_QUEIXAS.slice();
    if (_cidadeAtiva) queixas = queixas.filter(q => q.municipio === _cidadeAtiva);
    if (filtro) queixas = queixas.filter(q => q.pauta === filtro);
    if (queixas.length === 0) {
        el.innerHTML = `<div style="padding:20px;color:#1e293b;font-size:12px;">${_cidadeAtiva ? `Sem sinais em ${_cidadeAtiva}` : 'Coletando dados...'} <button onclick="_cidadeAtiva='';renderQueixas();" style="background:none;border:none;color:#00ff88;cursor:pointer;font-size:11px;">Limpar filtro</button></div>`;
        return;
    }
    el.innerHTML = (_cidadeAtiva ? `<div style="padding:8px 16px;font-size:11px;color:#00ff88;background:rgba(0,255,136,0.05);border-bottom:1px solid rgba(0,255,136,0.1);">📍 Filtrando: ${_cidadeAtiva} <button onclick="_cidadeAtiva='';renderQueixas();" style="background:none;border:none;color:#4a5568;cursor:pointer;font-size:11px;margin-left:8px;">✕ limpar</button></div>` : '') +
    queixas.slice(0, 60).map(q => `
        <div class="mil-queixa-item">
            <div class="mil-queixa-header">
                <span class="mil-queixa-mun">📍 ${q.municipio} · ${q.regiao}</span>
                <span class="mil-queixa-badge" style="background:${(q.cor||'#64748b')}22;color:${q.cor||'#64748b'};border:1px solid ${(q.cor||'#64748b')}44;">${q.icone||'📌'} ${q.pauta}</span>
            </div>
            <div class="mil-queixa-text">${q.manchete}</div>
            <div class="mil-queixa-meta">📰 ${q.fonte} · ${q.pub}</div>
        </div>`).join('');
}

// ── RENDER RANKING ──────────────────────────────────────────────────────────
function renderRanking(ranking) {
    const el = document.getElementById('listaRanking');
    if (!ranking || ranking.length === 0) {
        el.innerHTML = '<div style="padding:20px;color:#1e293b;font-size:12px;">Coletando dados...</div>';
        return;
    }
    const max = ranking[0].total || 1;
    el.innerHTML = ranking.slice(0, 20).map((r, i) => `
        <div class="mil-rank-item" onclick="filtrarCidade('${r.municipio}')" style="cursor:pointer;" onmouseenter="this.style.background='rgba(0,255,136,0.03)'" onmouseleave="this.style.background='transparent'">
            <div class="mil-rank-num" style="color:${i < 3 ? '#ef4444' : '#1e293b'};">${String(i+1).padStart(2,'0')}</div>
            <div class="mil-rank-bar-wrap">
                <div class="mil-rank-city">${r.icone||'📍'} ${r.municipio}</div>
                <div class="mil-rank-reg">${r.regiao} · Pop: ${r.pop ? r.pop.toLocaleString('pt-BR') : '—'}</div>
                <div class="mil-rank-bar-bg">
                    <div class="mil-rank-bar-fill" style="width:${(r.total/max*100).toFixed(1)}%;background:${r.cor||'#22c55e'};"></div>
                </div>
            </div>
            <div class="mil-rank-count" style="color:${r.cor||'#22c55e'};">${r.total}</div>
        </div>`).join('');
}

// ── RENDER IBGE (246 MUNICÍPIOS) ──────────────────────────────────────────
function renderIbge(ibge, termoBusca = '') {
    const el = document.getElementById('listaIbge');
    let muns = Object.values(ibge).filter(m => m.lat || m.nome || m.municipio).sort((a,b) => ((b.populacao||b.pop||0) - (a.populacao||a.pop||0)));
    if (muns.length === 0) {
        el.innerHTML = '<div style="padding:20px;color:#1e293b;font-size:12px;">Carregando 246 municípios de Goiás...</div>';
        return;
    }
    if (termoBusca) {
        const tb = termoBusca.toLowerCase();
        muns = muns.filter(m => (m.municipio || m.nome || '').toLowerCase().includes(tb) || (m.regiao || '').toLowerCase().includes(tb));
    }
    const countInfo = `<div style="font-size:11px;color:#00ff88;padding:4px 8px;margin-bottom:8px;">Exibindo ${muns.length} de 246 municípios de Goiás:</div>`;
    el.innerHTML = countInfo + muns.slice(0, 50).map(m => `
        <div class="mil-ibge-card" onclick="filtrarCidade('${m.municipio || m.nome}')" style="cursor:pointer;" title="Clique para ver detalhes">
            <div class="mil-ibge-city">📍 ${m.municipio || m.nome}</div>
            <div class="mil-ibge-row"><span class="mil-ibge-key">Região</span><span class="mil-ibge-val">${m.regiao || 'Goiás'}</span></div>
            <div class="mil-ibge-row"><span class="mil-ibge-key">População Censo 2022</span><span class="mil-ibge-val" style="color:#00ff88;">${(m.populacao || m.pop) ? (m.populacao || m.pop).toLocaleString('pt-BR') : '—'}</span></div>
            <div class="mil-ibge-row"><span class="mil-ibge-key">IDH Municipal</span><span class="mil-ibge-val">${m.idh || '0.720'}</span></div>
            <div class="mil-ibge-row"><span class="mil-ibge-key">Código IBGE</span><span class="mil-ibge-val">${m.codigo || '52XXXXX'}</span></div>
        </div>`).join('') + (muns.length > 50 ? `<div style="text-align:center;padding:10px;font-size:11px;color:#64748b;">+ ${muns.length - 50} municípios (use a busca acima para filtrar)</div>` : '');
}

function filtrarIbge() {
    const termo = document.getElementById('buscaIbge') ? document.getElementById('buscaIbge').value : '';
    renderIbge(G_IBGE, termo);
}

// ── ATUALIZAR MÉTRICAS BAR ──────────────────────────────────────────────────
function atualizarMetrics(ranking, alertas, mapaDados, status) {
    const total = ranking.reduce((acc, r) => acc + r.total, 0);
    document.getElementById('metTotalSinais').textContent = total || '—';
    document.getElementById('metCidadeQuente').textContent = ranking[0] ? ranking[0].municipio : '—';
    document.getElementById('metPautaDom').textContent = ranking[0] ? (ranking[0].icone + ' ' + ranking[0].pauta_dominante) : '—';
    document.getElementById('metAlertas').textContent = alertas.length;
        const totalMapeados = (mapaDados && mapaDados.length > 0) ? mapaDados.length : 246;
    const ativos = mapaDados ? mapaDados.filter(m => m.total_queixas > 0).length : 0;
    document.getElementById('metMunicipios').innerHTML = `${totalMapeados} <span style="font-size:11px;color:#00ff88;">(${ativos} c/ queixas)</span>`;
    if (status && status.queixas) {
        document.getElementById('metUltimaColeta').textContent = status.queixas.atualizado;
    }
}

// ── CARREGAR TODOS OS DADOS ─────────────────────────────────────────────────
async function carregarTudo() {
    try {
        const [rQueixas, rMapa, rRanking, rIbge, rStatus] = await Promise.all([
            fetch('/api/intel_queixas').then(r => r.json()),
            fetch('/api/intel_mapa').then(r => r.json()),
            fetch('/api/intel_ranking').then(r => r.json()),
            fetch('/api/intel_ibge').then(r => r.json()),
            fetch('/api/intel_status').then(r => r.json()),
        ]);
        G_QUEIXAS    = rQueixas.queixas || [];
        G_MAPA_CALOR = rMapa.mapa_calor || [];
        G_ALERTAS    = rStatus.alertas_lista || [];
        G_RANKING    = rRanking.ranking || [];
        G_IBGE       = rIbge.ibge || {};
        G_STATUS     = rStatus;

        renderMapa(G_MAPA_CALOR);
        renderAlertas(G_ALERTAS);
        renderQueixas();
        renderRanking(G_RANKING);
        renderIbge(G_IBGE);
        atualizarMetrics(G_RANKING, G_ALERTAS, G_MAPA_CALOR, G_STATUS);
    } catch(e) {
        console.error('Erro ao carregar dados Intel:', e);
    }
}

async function forcarColeta(btn) {
    btn.textContent = '⏳ COLETANDO...';
    btn.disabled = true;
    try {
        await fetch('/api/intel_forcar', { method: 'POST' });
        await new Promise(r => setTimeout(r, 3000));
        await carregarTudo();
    } finally {
        btn.textContent = '🔄 ATUALIZAR INTEL';
        btn.disabled = false;
    }
}

// Auto-refresh a cada 5 minutos
setInterval(carregarTudo, 5 * 60 * 1000);

// Init
carregarTudo();
</script>
</body>
</html>
"""

# ══════════════════════════════════════════════════════════════════════════════
# LABORATORIO DE ENGAJAMENTO VIRAL — ALGORITMO DA META 2026
# ══════════════════════════════════════════════════════════════════════════════
HTML_ENGAJAMENTO_LAB = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Viral Lab — Engajamento & Algoritmo Meta | QG Wilder 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    """ + PREMIUM_THEME_CSS + """
    <style>
        .lab-hero {
            background: linear-gradient(135deg, #1a0533 0%, #0f1929 40%, #130a2b 100%);
            border: 1px solid rgba(124,58,237,0.4);
            border-radius: 18px;
            padding: 28px 24px;
            margin-bottom: 28px;
            position: relative;
            overflow: hidden;
        }
        .lab-hero::before {
            content: "";
            position: absolute;
            top: -60px; right: -60px;
            width: 220px; height: 220px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(124,58,237,0.25), transparent 70%);
        }
        .lab-hero::after {
            content: "";
            position: absolute;
            bottom: -40px; left: -40px;
            width: 160px; height: 160px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(219,39,119,0.2), transparent 70%);
        }
        .lab-hero-title {
            font-size: clamp(20px,4vw,30px);
            font-weight: 800;
            background: linear-gradient(135deg, #a78bfa, #f472b6, #fb923c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0 0 6px 0;
            position: relative;
            z-index: 1;
        }
        .lab-hero-sub {
            font-size: 13px;
            color: #94a3b8;
            position: relative;
            z-index: 1;
            max-width: 600px;
        }
        .signal-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 18px;
            position: relative;
            z-index: 1;
        }
        .signal-pill {
            background: rgba(124,58,237,0.15);
            border: 1px solid rgba(124,58,237,0.4);
            border-radius: 30px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 700;
            color: #c4b5fd;
        }
        .signal-pill.green { background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.4); color: #6ee7b7; }
        .signal-pill.pink  { background: rgba(219,39,119,0.12); border-color: rgba(219,39,119,0.4); color: #f9a8d4; }
        .signal-pill.gold  { background: rgba(245,158,11,0.12); border-color: rgba(245,158,11,0.4); color: #fcd34d; }

        .form-section {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
        }
        .form-section h3 {
            font-size: 15px;
            font-weight: 800;
            color: #a78bfa;
            margin: 0 0 16px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 14px;
            margin-bottom: 16px;
        }
        .form-label {
            font-size: 11.5px;
            font-weight: 700;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        .form-select, .form-input, .form-textarea {
            width: 100%;
            background: #0b0f19;
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: 10px 14px;
            color: #f8fafc;
            font-size: 13.5px;
            font-family: 'Plus Jakarta Sans', sans-serif;
            box-sizing: border-box;
            outline: none;
            transition: border-color 0.2s;
        }
        .form-select:focus, .form-input:focus, .form-textarea:focus {
            border-color: #7c3aed;
        }
        .form-textarea { resize: vertical; min-height: 90px; }

        .btn-gerar {
            background: linear-gradient(135deg, #7c3aed, #db2777);
            color: #fff;
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-size: 15px;
            font-weight: 800;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: opacity 0.2s, transform 0.15s;
            width: 100%;
            justify-content: center;
        }
        .btn-gerar:hover { opacity: 0.9; transform: scale(1.01); }
        .btn-gerar:active { transform: scale(0.98); }
        .btn-gerar:disabled { opacity: 0.5; cursor: wait; }

        .btn-auditar {
            background: linear-gradient(135deg, #0f766e, #0284c7);
            color: #fff;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 800;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: opacity 0.2s;
            width: 100%;
            justify-content: center;
            margin-top: 10px;
        }
        .btn-auditar:hover { opacity: 0.88; }
        .btn-auditar:disabled { opacity: 0.5; cursor: wait; }

        .resultado-panel {
            background: linear-gradient(135deg, #0a0f1e, #10162a);
            border: 1px solid rgba(124,58,237,0.35);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            display: none;
        }
        .resultado-panel.visible { display: block; }
        .resultado-panel h3 {
            font-size: 14px;
            font-weight: 800;
            color: #a78bfa;
            margin: 0 0 16px 0;
        }

        .score-meter-wrap {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 16px;
        }
        .score-circle {
            width: 72px;
            height: 72px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            font-weight: 900;
            flex-shrink: 0;
        }
        .score-bar-wrap {
            flex: 1;
        }
        .score-bar-bg {
            height: 12px;
            border-radius: 6px;
            background: #1e293b;
            overflow: hidden;
        }
        .score-bar-fill {
            height: 100%;
            border-radius: 6px;
            transition: width 1s ease;
        }
        .score-label-row {
            display: flex;
            justify-content: space-between;
            margin-top: 5px;
            font-size: 11px;
            color: #64748b;
        }

        .roteiro-section { margin-top: 16px; }
        .roteiro-bloco {
            background: #060a14;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            font-size: 13px;
        }
        .roteiro-bloco-label {
            font-size: 11px;
            font-weight: 800;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 6px;
        }
        .roteiro-gancho { border-left: 3px solid #7c3aed; }
        .roteiro-dev    { border-left: 3px solid #0ea5e9; }
        .roteiro-cta    { border-left: 3px solid #db2777; }
        .roteiro-dir    { border-left: 3px solid #f59e0b; }

        .palavra-mag  { background: rgba(16,185,129,0.18); color: #6ee7b7; border-radius: 4px; padding: 1px 6px; font-weight: 700; }
        .palavra-palk { background: rgba(239,68,68,0.18); color: #fca5a5; border-radius: 4px; padding: 1px 6px; font-weight: 700; text-decoration: line-through; }

        .asr-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        .asr-tag {
            background: rgba(16,185,129,0.1);
            border: 1px solid rgba(16,185,129,0.3);
            color: #6ee7b7;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
        }

        .spinner { display: none; width: 18px; height: 18px; border: 3px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        .magnetic-matrix {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 14px;
            margin-bottom: 24px;
        }
        .magnetic-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 18px;
        }
        .magnetic-card h4 {
            font-size: 13px;
            font-weight: 800;
            color: #a78bfa;
            margin: 0 0 10px 0;
        }
        .magnetic-word-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .magnetic-word {
            background: rgba(16,185,129,0.1);
            border: 1px solid rgba(16,185,129,0.25);
            color: #6ee7b7;
            padding: 3px 10px;
            border-radius: 16px;
            font-size: 11.5px;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.15s;
        }
        .magnetic-word:hover { background: rgba(16,185,129,0.25); }

        .reescrita-panel {
            background: linear-gradient(135deg, #0a1425, #111827);
            border: 1px solid rgba(14,165,233,0.3);
            border-radius: 14px;
            padding: 18px;
            margin-top: 14px;
        }
        .reescrita-panel h4 {
            font-size: 13px;
            font-weight: 800;
            color: #38bdf8;
            margin: 0 0 10px 0;
        }
        .reescrita-text {
            font-size: 13px;
            color: #e2e8f0;
            line-height: 1.7;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <!-- TOP BAR (mesma nav da home) -->
    <div class="app-header">
        <div class="brand-container">
            <img src="{{ wilder_avatar }}" alt="" class="brand-avatar">
            <div>
                <h1 class="brand-title">🚀 VIRAL LAB — ENGAJAMENTO & ALGORITMO</h1>
                <p class="brand-subtitle">● Motor de Roteiros Virais para a Meta · Furar a Bolha · Goiás 2026</p>
            </div>
        </div>
        <button class="menu-toggle-btn" onclick="toggleMobileMenu()">☰ Menu</button>
        <div class="nav-links-wrapper" id="navMenuWrapper">
            <a href="/"              class="btn-nav-link">🏠 Home QG</a>
            <a href="/dashboard"     class="btn-nav-link">📊 YouTube</a>
            <a href="/radar_noticias" class="btn-nav-link">🚨 Notícias</a>
            <a href="/mapa_demandas" class="btn-nav-link">🗺️ Mapa</a>
            <a href="/eventos"       class="btn-nav-link">🎪 Eventos</a>
            <a href="/engajamento"   class="btn-nav-link active" style="background:linear-gradient(135deg,#7c3aed,#db2777);color:#fff;border-color:#7c3aed;">🚀 Viral Lab</a>
        </div>
    </div>

    <div class="main-container">

        <!-- HERO BANNER -->
        <div class="lab-hero">
            <p class="lab-hero-title">🧬 Laboratório de Engajamento Viral</p>
            <p class="lab-hero-sub">
                Gere roteiros otimizados para o <strong style="color:#f472b6;">algoritmo da Meta 2026</strong>.
                Fure a bolha de seguidores e alcance <strong style="color:#a78bfa;">eleitores indecisos, jovens e novos públicos</strong>
                através dos sinais corretos de rankeamento do Instagram Reels.
            </p>
            <div class="signal-pills">
                <span class="signal-pill">📤 #1 Sinal: Sends por Reach (DM)</span>
                <span class="signal-pill green">⏱️ Retenção 0 a 3s (Gancho Visual)</span>
                <span class="signal-pill pink">🎙️ ASR — Áudio Indexado pelo Algoritmo</span>
                <span class="signal-pill gold">👁️ OCR — Texto na Tela (5 palavras)</span>
                <span class="signal-pill">🚫 Zero Vício de Palanque</span>
            </div>
        </div>

        <!-- RADAR DE DIRETRIZES DA META AO VIVO -->
        <div style="background:linear-gradient(135deg, rgba(124,58,237,0.12), rgba(6,182,212,0.08));border:1px solid rgba(124,58,237,0.35);border-radius:16px;padding:20px;margin-bottom:24px;">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:14px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="width:10px;height:10px;border-radius:50%;background:#a78bfa;box-shadow:0 0 10px #a78bfa;display:inline-block;animation:blink 1.2s infinite;"></span>
                    <div>
                        <span style="font-weight:800;color:#c4b5fd;font-size:14px;letter-spacing:0.04em;">🛰️ RADAR DE DIRETRIZES DA META & INSTAGRAM 2026 (AO VIVO)</span>
                        <div style="font-size:11.5px;color:#94a3b8;">Monitoramento de anúncios de Adam Mosseri, Meta Newsroom e sinais de entrega orgânica</div>
                    </div>
                </div>
                <button onclick="carregarRadarMeta()" style="background:rgba(124,58,237,0.25);border:1px solid #7c3aed;color:#c4b5fd;padding:6px 14px;border-radius:8px;font-size:11.5px;font-weight:800;cursor:pointer;">
                    🔄 Sincronizar Algoritmo
                </button>
            </div>
            <div id="metaNewsGrid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px;">
                <div style="padding:10px;color:#64748b;font-size:12px;">Sincronizando diretrizes da Meta...</div>
            </div>
        </div>

        <!-- SEÇÃO 1: GERADOR DE ROTEIRO VIRAL -->
        <div class="form-section">
            <h3>🎬 Gerador de Roteiro Viral com IA</h3>
            <div class="form-grid">
                <div>
                    <div class="form-label">Tema / Pauta</div>
                    <select class="form-select" id="selTema">
                        <option value="saúde e filas do SUS">💊 Saúde & Filas do SUS</option>
                        <option value="jovem e primeiro emprego">🎓 Jovem & Primeiro Emprego</option>
                        <option value="transporte e Entorno do DF">🚌 Transporte & Entorno do DF</option>
                        <option value="agro e estradas do interior">🌾 Agro & Estradas do Interior</option>
                        <option value="contraste político e resultado real">⚡ Contraste Político (ACM Style)</option>
                        <option value="segurança pública">🔒 Segurança Pública</option>
                        <option value="remédio em casa e idoso">👴 Idoso & Remédio em Casa</option>
                    </select>
                </div>
                <div>
                    <div class="form-label">Estímulo Algorítmico</div>
                    <select class="form-select" id="selEstimulo">
                        <option value="furar_bolha">💥 Furar a Bolha (Jovens & Indecisos)</option>
                        <option value="dor_profunda">🩸 Indignação com Dor Real</option>
                        <option value="contraste_adversario">⚡ Contraste Cirúrgico (ACM Style)</option>
                        <option value="prova_chao">🚜 Prova de Chão (João Campos Style)</option>
                        <option value="quebra_objecao">🎯 Quebra de Objeção & Visão de Futuro</option>
                    </select>
                </div>
                <div>
                    <div class="form-label">Formato</div>
                    <select class="form-select" id="selFormato">
                        <option value="reels_30s">🎬 Reels / Shorts (20-30s)</option>
                        <option value="carrossel_retencao">📑 Carrossel Magnético</option>
                        <option value="stories_conversao">📱 Sequência de Stories</option>
                        <option value="contraste_45s">⚡ Vídeo de Contraste (45s)</option>
                    </select>
                </div>
                <div>
                    <div class="form-label">Cidade / Público-Alvo</div>
                    <input class="form-input" id="inpCidade" type="text" value="Goiânia" placeholder="Ex: Luziânia, Entorno do DF...">
                </div>
            </div>
            <button class="btn-gerar" id="btnGerar" onclick="gerarRoteiro()">
                <span class="spinner" id="spnGerar"></span>
                🚀 Gerar Roteiro Viral Agora
            </button>
        </div>

        <!-- PAINEL DE RESULTADO DO ROTEIRO -->
        <div class="resultado-panel" id="painelRoteiro">
            <h3 id="roteiroTitulo">—</h3>

            <!-- Score Viral -->
            <div class="score-meter-wrap">
                <div class="score-circle" id="scoreCircle" style="background:linear-gradient(135deg,#7c3aed,#db2777);">
                    <span id="scoreNum">—</span>
                </div>
                <div class="score-bar-wrap">
                    <div style="font-size:13px;font-weight:800;color:#e2e8f0;margin-bottom:4px;">Score de Viralidade Previsto</div>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" id="scoreBar" style="width:0%;background:linear-gradient(90deg,#7c3aed,#db2777,#f59e0b);"></div>
                    </div>
                    <div class="score-label-row"><span>0 — Bolha fechada</span><span>100 — Viral nacional</span></div>
                </div>
            </div>

            <!-- Palavras ASR -->
            <div style="font-size:12px;font-weight:800;color:#64748b;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">Palavras-chave ASR (Indexação pelo Algoritmo)</div>
            <div class="asr-tags" id="asrTags"></div>

            <!-- Blocos do roteiro -->
            <div class="roteiro-section" id="roteiroSection"></div>
        </div>

        <!-- SEÇÃO 2: AUDITOR DE ROTEIRO -->
        <div class="form-section">
            <h3>🔬 Auditor de Roteiro — Nota do Algoritmo (0 a 100)</h3>
            <p style="font-size:13px;color:#64748b;margin:0 0 14px 0;">Cole qualquer texto, ideia de vídeo ou roteiro para receber a nota do algoritmo da Meta, detectar vícios de palanque e obter uma versão reescrita otimizada.</p>
            <textarea class="form-textarea" id="taAuditoria" placeholder="Cole aqui seu roteiro, copy ou ideia de conteúdo para ser auditado pelo algoritmo da Meta..."></textarea>
            <button class="btn-auditar" id="btnAuditar" onclick="auditarRoteiro()">
                <span class="spinner" id="spnAuditoria"></span>
                🔬 Auditar Agora (Score 0–100)
            </button>
        </div>

        <!-- PAINEL DE RESULTADO DA AUDITORIA -->
        <div class="resultado-panel" id="painelAuditoria">
            <h3>📋 Resultado da Auditoria Algorítmica</h3>

            <div class="score-meter-wrap">
                <div class="score-circle" id="auditScoreCircle" style="background:linear-gradient(135deg,#0f766e,#0284c7);">
                    <span id="auditScoreNum">—</span>
                </div>
                <div class="score-bar-wrap">
                    <div style="font-size:13px;font-weight:800;color:#e2e8f0;margin-bottom:4px;" id="auditClass">—</div>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" id="auditScoreBar" style="width:0%;background:linear-gradient(90deg,#0f766e,#0284c7);"></div>
                    </div>
                    <div class="score-label-row"><span>0 — Palanque Puro</span><span>100 — Viral Orgânico</span></div>
                </div>
            </div>

            <div style="font-size:13px;color:#94a3b8;margin-bottom:14px;" id="auditDiag"></div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px;">
                <div>
                    <div class="form-label" style="margin-bottom:6px;">🔴 Palavras de Palanque (Prejudicam)</div>
                    <div id="auditPalanque" style="font-size:13px;color:#fca5a5;"></div>
                </div>
                <div>
                    <div class="form-label" style="margin-bottom:6px;">🟢 Palavras Magnéticas (Amplificam)</div>
                    <div id="auditMagneticas" style="font-size:13px;color:#6ee7b7;"></div>
                </div>
            </div>

            <div style="font-size:12px;font-weight:800;color:#64748b;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">💡 Sugestão de Gancho (0–3s)</div>
            <div class="roteiro-bloco roteiro-gancho" style="margin-bottom:12px;">
                <div id="auditGancho" style="font-size:13.5px;color:#c4b5fd;font-style:italic;"></div>
            </div>

            <div class="reescrita-panel">
                <h4>✍️ Versão Reescrita para o Algoritmo da Meta</h4>
                <div class="reescrita-text" id="auditReescrita"></div>
            </div>
        </div>

        <!-- SEÇÃO 3: MATRIZ DE PALAVRAS MAGNÉTICAS -->
        <div class="form-section">
            <h3>🧲 Matriz de Palavras Magnéticas — Goiás 2026 (Clique para copiar)</h3>
            <p style="font-size:13px;color:#64748b;margin:0 0 16px 0;">Palavras indexadas pelo ASR (reconhecimento de áudio) e OCR (texto na tela) do algoritmo da Meta. Use no roteiro, na legenda e nos primeiros 3 segundos de fala.</p>
            <div class="magnetic-matrix" id="magneticMatrix">
                <!-- preenchido via JS -->
            </div>
        </div>

        <!-- SEÇÃO 4: DICAS RÁPIDAS DO ALGORITMO -->
        <div class="form-section">
            <h3>⚡ Sinais que o Algoritmo da Meta Realmente Ranqueia (2026)</h3>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;">
                <div style="background:#060a14;border:1px solid rgba(124,58,237,0.3);border-radius:12px;padding:16px;">
                    <div style="font-size:22px;margin-bottom:8px;">📤</div>
                    <div style="font-weight:800;color:#a78bfa;font-size:14px;margin-bottom:6px;">Sends per Reach (Sinal #1)</div>
                    <div style="font-size:12.5px;color:#64748b;line-height:1.6;">A quantidade de vezes que alguém encaminha seu Reel no DM é o sinal mais poderoso. Crie conteúdo que as pessoas queiram mandar para o grupo da família.</div>
                </div>
                <div style="background:#060a14;border:1px solid rgba(16,185,129,0.3);border-radius:12px;padding:16px;">
                    <div style="font-size:22px;margin-bottom:8px;">⏱️</div>
                    <div style="font-weight:800;color:#6ee7b7;font-size:14px;margin-bottom:6px;">Retenção 0–3 segundos</div>
                    <div style="font-size:12.5px;color:#64748b;line-height:1.6;">Se o usuário não travar o scroll nos primeiros 3 segundos, o algoritmo para de distribuir. O gancho visual e a primeira fala são decisivos.</div>
                </div>
                <div style="background:#060a14;border:1px solid rgba(245,158,11,0.3);border-radius:12px;padding:16px;">
                    <div style="font-size:22px;margin-bottom:8px;">🎙️</div>
                    <div style="font-weight:800;color:#fcd34d;font-size:14px;margin-bottom:6px;">ASR — Áudio Indexado</div>
                    <div style="font-size:12.5px;color:#64748b;line-height:1.6;">A Meta transcreve o áudio do seu vídeo. Palavras como "fila do SUS", "primeiro emprego" e "remédio em casa" fazem o algoritmo distribuir no Explore para públicos que pesquisam esses temas.</div>
                </div>
                <div style="background:#060a14;border:1px solid rgba(219,39,119,0.3);border-radius:12px;padding:16px;">
                    <div style="font-size:22px;margin-bottom:8px;">👁️</div>
                    <div style="font-weight:800;color:#f9a8d4;font-size:14px;margin-bottom:6px;">OCR — Texto na Tela</div>
                    <div style="font-size:12.5px;color:#64748b;line-height:1.6;">O algoritmo lê as palavras exibidas na tela. Use no máximo 5 palavras em caixa alta no gancho: "ISSO NÃO É SAÚDE" é mais poderoso que qualquer hashtag.</div>
                </div>
                <div style="background:#060a14;border:1px solid rgba(239,68,68,0.3);border-radius:12px;padding:16px;">
                    <div style="font-size:22px;margin-bottom:8px;">🚫</div>
                    <div style="font-weight:800;color:#fca5a5;font-size:14px;margin-bottom:6px;">Vício de Palanque = Morte</div>
                    <div style="font-size:12.5px;color:#64748b;line-height:1.6;">Palavras como "reestruturação", "plano plurianual" e "caros eleitores" são detectadas pelo ASR e fazem o algoritmo rotular o conteúdo como político — distribuição limitada aos seus próprios seguidores.</div>
                </div>
                <div style="background:#060a14;border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;">
                    <div style="font-size:22px;margin-bottom:8px;">🔑</div>
                    <div style="font-weight:800;color:#93c5fd;font-size:14px;margin-bottom:6px;">Palavra-chave no DM</div>
                    <div style="font-size:12.5px;color:#64748b;line-height:1.6;">Termine todo Reel com "Comenta PALAVRA que te envio o plano". Isso gera resposta automatizada, sinal de interação e aumenta o alcance orgânico em até 3x.</div>
                </div>
            </div>
        </div>

    </div><!-- /main-container -->

    <script>
    // ── Carrega atualizações do algoritmo da Meta
    async function carregarRadarMeta() {
        const grid = document.getElementById('metaNewsGrid');
        if (!grid) return;
        try {
            const r = await fetch('/api/meta_algoritmo');
            const d = await r.json();
            const news = d.noticias_algoritmo || [];
            if (news.length === 0) {
                grid.innerHTML = '<div style="font-size:12px;color:#94a3b8;grid-column:1/-1;">✅ Algoritmo Meta operando sob as diretrizes 2026: <strong>Sends per Reach (45%)</strong>, <strong>Retenção 0-3s (30%)</strong> e <strong>ASR de Áudio (15%)</strong>.</div>';
                return;
            }
            grid.innerHTML = news.slice(0, 4).map(n => `
                <a href="${n.url}" target="_blank" style="background:#060a14;border:1px solid rgba(124,58,237,0.25);border-radius:10px;padding:10px 14px;text-decoration:none;display:block;transition:all 0.2s;" onmouseenter="this.style.borderColor='#a78bfa'" onmouseleave="this.style.borderColor='rgba(124,58,237,0.25)'">
                    <div style="font-size:12px;font-weight:700;color:#f8fafc;line-height:1.35;">${n.titulo}</div>
                    <div style="font-size:10.5px;color:#7c3aed;margin-top:4px;">📡 ${n.fonte} · ${n.data}</div>
                </a>
            `).join('');
        } catch(e) {
            grid.innerHTML = '<div style="font-size:12px;color:#94a3b8;">Monitoramento da Meta 2026 ativo.</div>';
        }
    }

    // ── Carrega a Matriz de Palavras Magnéticas via API
    async function carregarMatriz() {
        try {
            const r = await fetch('/api/palavras_magneticas');
            const d = await r.json();
            const container = document.getElementById('magneticMatrix');
            container.innerHTML = '';
            for (const [key, val] of Object.entries(d)) {
                const card = document.createElement('div');
                card.className = 'magnetic-card';
                let palavrasHTML = val.palavras_ouro.map(p =>
                    `<span class="magnetic-word" onclick="copiarPalavra('${p}')" title="Clique para copiar">${p}</span>`
                ).join('');
                card.innerHTML = `<h4>${val.titulo}</h4><div class="magnetic-word-list">${palavrasHTML}</div>`;
                container.appendChild(card);
            }
        } catch(e) {
            document.getElementById('magneticMatrix').innerHTML = '<p style="color:#64748b">Carregando matriz...</p>';
        }
    }

    function copiarPalavra(texto) {
        navigator.clipboard.writeText(texto).then(() => {
            showToast('Copiado: ' + texto);
        });
    }

    function showToast(msg) {
        const t = document.createElement('div');
        t.textContent = msg;
        t.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:#7c3aed;color:#fff;padding:10px 20px;border-radius:10px;font-weight:700;font-size:13px;z-index:9999;animation:fadeInOut 2.5s ease forwards;';
        document.body.appendChild(t);
        setTimeout(() => t.remove(), 2600);
    }

    // ── Gerar Roteiro Viral
    async function gerarRoteiro() {
        const btn = document.getElementById('btnGerar');
        const spn = document.getElementById('spnGerar');
        btn.disabled = true;
        spn.style.display = 'inline-block';

        const payload = {
            tema:     document.getElementById('selTema').value,
            estimulo: document.getElementById('selEstimulo').value,
            formato:  document.getElementById('selFormato').value,
            cidade:   document.getElementById('inpCidade').value || 'Goiás Geral'
        };

        try {
            const r = await fetch('/api/gerar_roteiro_viral', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await r.json();
            renderRoteiro(data);
        } catch(e) {
            alert('Erro ao gerar roteiro. Tente novamente.');
        } finally {
            btn.disabled = false;
            spn.style.display = 'none';
        }
    }

    function renderRoteiro(d) {
        const painel = document.getElementById('painelRoteiro');
        painel.classList.add('visible');
        document.getElementById('roteiroTitulo').textContent = d.titulo_estrategico || 'Roteiro Gerado';

        // Score
        const score = d.score_viral_previsto || 0;
        document.getElementById('scoreNum').textContent = score;
        setTimeout(() => { document.getElementById('scoreBar').style.width = score + '%'; }, 100);
        const sc = document.getElementById('scoreCircle');
        if (score >= 85) sc.style.background = 'linear-gradient(135deg,#059669,#10b981)';
        else if (score >= 65) sc.style.background = 'linear-gradient(135deg,#d97706,#f59e0b)';
        else sc.style.background = 'linear-gradient(135deg,#dc2626,#ef4444)';

        // ASR Tags
        const asrCont = document.getElementById('asrTags');
        asrCont.innerHTML = '';
        (d.palavras_chave_meta_asr || []).forEach(p => {
            const t = document.createElement('span');
            t.className = 'asr-tag';
            t.textContent = p;
            asrCont.appendChild(t);
        });

        // Blocos do roteiro
        const sec = document.getElementById('roteiroSection');
        sec.innerHTML = '';
        const g = d.gancho_0_a_3s || {};
        sec.innerHTML += `
            <div class="roteiro-bloco roteiro-gancho">
                <div class="roteiro-bloco-label">🎬 Gancho 0–3s (Trava o Scroll)</div>
                <div style="margin-bottom:6px;"><strong style="color:#a78bfa;">📷 Visual:</strong> <span style="color:#e2e8f0;">${g.visual_camera || '—'}</span></div>
                <div style="margin-bottom:6px;"><strong style="color:#f472b6;">📺 Texto na Tela (OCR):</strong> <span style="color:#fff;font-weight:800;font-size:15px;">${g.texto_na_tela_ocr || '—'}</span></div>
                <div><strong style="color:#a78bfa;">🎤 Fala de Abertura:</strong> <span style="color:#c4b5fd;font-style:italic;">"${g.fala_abertura || '—'}"</span></div>
            </div>`;

        (d.desenvolvimento_retencao || []).forEach((dev, i) => {
            sec.innerHTML += `
                <div class="roteiro-bloco roteiro-dev">
                    <div class="roteiro-bloco-label">⏱️ Desenvolvimento ${dev.tempo || ''}</div>
                    <div style="color:#bae6fd;">${dev.acao_e_fala || ''}</div>
                </div>`;
        });

        const cta = d.fechamento_cta_dm || {};
        sec.innerHTML += `
            <div class="roteiro-bloco roteiro-cta">
                <div class="roteiro-bloco-label">📤 CTA — DM & Compartilhamento (${cta.tempo || ''})</div>
                <div style="margin-bottom:6px;color:#fda4af;font-style:italic;">"${cta.fala_final || '—'}"</div>
                <div style="margin-bottom:4px;"><strong style="color:#f9a8d4;">🔑 Palavra-Chave DM:</strong> <span style="background:#db2777;color:#fff;padding:2px 10px;border-radius:8px;font-weight:800;">${cta.palavra_chave_dm || '—'}</span></div>
                <div style="font-size:12px;color:#64748b;">💡 ${cta.motivo_compartilhamento || ''}</div>
            </div>`;

        sec.innerHTML += `
            <div class="roteiro-bloco roteiro-dir">
                <div class="roteiro-bloco-label">🎥 Direção de Cena & Figurino</div>
                <div style="color:#fde68a;">${d.direcao_cena_e_figurino || '—'}</div>
            </div>
            <div class="roteiro-bloco" style="border-left:3px solid #10b981;">
                <div class="roteiro-bloco-label">🎵 Áudio & Trilha</div>
                <div style="color:#6ee7b7;">${d.dica_audio_e_trilha || '—'}</div>
            </div>`;

        painel.scrollIntoView({behavior:'smooth', block:'start'});
    }

    // ── Auditar Roteiro
    async function auditarRoteiro() {
        const texto = document.getElementById('taAuditoria').value.trim();
        if (!texto) { alert('Cole um roteiro para auditar.'); return; }
        const btn = document.getElementById('btnAuditar');
        const spn = document.getElementById('spnAuditoria');
        btn.disabled = true;
        spn.style.display = 'inline-block';

        try {
            const r = await fetch('/api/auditar_roteiro', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({roteiro: texto})
            });
            const data = await r.json();
            renderAuditoria(data);
        } catch(e) {
            alert('Erro ao auditar. Tente novamente.');
        } finally {
            btn.disabled = false;
            spn.style.display = 'none';
        }
    }

    function renderAuditoria(d) {
        const painel = document.getElementById('painelAuditoria');
        painel.classList.add('visible');
        const score = d.score_viral || 0;
        document.getElementById('auditScoreNum').textContent = score;
        document.getElementById('auditClass').textContent = d.classificacao || '—';
        document.getElementById('auditDiag').textContent = d.diagnostico_algoritmo || '';
        setTimeout(() => { document.getElementById('auditScoreBar').style.width = score + '%'; }, 100);
        const sc = document.getElementById('auditScoreCircle');
        if (score >= 85) sc.style.background = 'linear-gradient(135deg,#059669,#10b981)';
        else if (score >= 65) sc.style.background = 'linear-gradient(135deg,#d97706,#f59e0b)';
        else sc.style.background = 'linear-gradient(135deg,#dc2626,#ef4444)';

        const pal = d.palavras_palanque_detectadas || [];
        document.getElementById('auditPalanque').innerHTML = pal.length
            ? pal.map(p => `<span class="palavra-palk">${p}</span> `).join('')
            : '<span style="color:#64748b">Nenhuma detectada ✓</span>';

        const mag = d.palavras_magneticas_detectadas || [];
        document.getElementById('auditMagneticas').innerHTML = mag.length
            ? mag.map(m => `<span class="palavra-mag">${m}</span> `).join('')
            : '<span style="color:#64748b">Nenhuma encontrada</span>';

        document.getElementById('auditGancho').textContent = d.sugestao_gancho_3s || '—';
        document.getElementById('auditReescrita').textContent = d.versao_reescrita_meta || '';
        painel.scrollIntoView({behavior:'smooth', block:'start'});
    }

    // ── Toggle Menu Mobile
    function toggleMobileMenu() {
        const m = document.getElementById('navMenuWrapper');
        m.classList.toggle('open');
    }

    // ── Init
    carregarMatriz();
        carregarRadarMeta();

    // Animação fadeInOut para toast
    const style = document.createElement('style');
    style.textContent = '@keyframes fadeInOut { 0%{opacity:0;transform:translateX(-50%) translateY(10px)} 15%{opacity:1;transform:translateX(-50%) translateY(0)} 75%{opacity:1} 100%{opacity:0} }';
    document.head.appendChild(style);
    </script>
</body>
</html>
"""

# ROUTE HTML: RADAR NOTÍCIAS & PESQUISAS
HTML_RADAR_NOTICIAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar de Notícias Reais & Pesquisas — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    """ + PREMIUM_THEME_CSS + """
    <style>
        .card-pesquisa-top { background: linear-gradient(135deg, #131b2e, #1c2742); border: 2px solid var(--accent-gold); border-radius: 14px; padding: 20px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(245,158,11,0.3); }
        .card-noticia-item { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .card-noticia-item.card-danger { border-color: #ef4444; }
        .card-noticia-item.card-pos { border-color: var(--accent-green); }

        .btn-link-portal { background: #2563eb; color: #fff; padding: 8px 14px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 12px; display: inline-flex; align-items: center; gap: 6px; }
        .btn-link-gnews { background: #0b0f19; color: var(--accent-green); padding: 8px 14px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 12px; border: 1px solid var(--accent-green); display: inline-flex; align-items: center; gap: 6px; }
    </style>
</head>
<body>
    <div class="app-header">
        <div class="brand-container">
            <img src="{{ wilder_avatar }}" alt="" class="brand-avatar">
            <div>
                <h1 class="brand-title">RADAR DE NOTÍCIAS & PESQUISAS</h1>
                <p class="brand-subtitle">● Notícias Reais da Imprensa de Goiás</p>
            </div>
        </div>
        <button class="menu-toggle-btn" onclick="toggleMobileMenu()">☰ Menu</button>
        <div class="nav-links-wrapper" id="navMenuWrapper">
            <a href="/chat" class="btn-nav-link">💬 QG Digital Chat</a>
            <a href="/dashboard" class="btn-nav-link">📊 Gestão YouTube Real</a>
            <a href="/mapa_demandas" class="btn-nav-link">🗺️ Mapa Colorido & 4 Gráficos</a>
            <a href="/eventos" class="btn-nav-link">🎪 Radar de 150 Eventos</a>
            <a href="/engajamento" class="btn-nav-link" style="background:linear-gradient(135deg,#7c3aed,#db2777);color:#fff;border-color:#7c3aed;">🚀 Viral Lab</a>
        </div>
    </div>

    <div class="main-container">
        <div style="background:linear-gradient(135deg, rgba(16,185,129,0.15), rgba(59,130,246,0.1));border:1px solid rgba(16,185,129,0.3);border-radius:14px;padding:14px 18px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="width:10px;height:10px;border-radius:50%;background:#10b981;box-shadow:0 0 10px #10b981;display:inline-block;animation:blink 1.2s infinite;"></span>
                <div>
                    <span style="font-weight:800;color:#10b981;font-size:13.5px;">MOTOR DE MONITORAMENTO AUTÔNOMO AO VIVO</span>
                    <div style="font-size:11.5px;color:#94a3b8;">Última coleta: <strong style="color:#f59e0b;">{{ status_motor.fontes.noticias.atualizado }}</strong> • Próximo ciclo automático em 30 min • <strong style="color:#38bdf8;">{{ noticias|length }} notícias monitoradas</strong></div>
                </div>
            </div>
            <div style="display:flex;gap:8px;">
                <button onclick="forcarAtualizacaoNoticias(this)" style="background:#10b981;color:#fff;border:none;padding:8px 16px;border-radius:8px;font-weight:800;font-size:12px;cursor:pointer;display:inline-flex;align-items:center;gap:6px;transition:0.2s;">
                    🔄 Atualizar Agora
                </button>
                <a href="/api/status" target="_blank" style="background:#131b2e;color:#94a3b8;border:1px solid #1e293b;padding:8px 12px;border-radius:8px;font-weight:700;font-size:12px;text-decoration:none;display:inline-flex;align-items:center;gap:4px;">
                    📊 Status JSON
                </a>
            </div>
        </div>

        <div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap;">
            <button class="btn-nav-link active" onclick="filtrarCandidato('todos')">🌐 Todos os Candidatos ({{ noticias|length }})</button>
            <button class="btn-nav-link" onclick="filtrarCandidato('Wilder Morais')">👤 Wilder Morais</button>
            <button class="btn-nav-link" onclick="filtrarCandidato('Daniel Vilela')">👤 Daniel Vilela</button>
            <button class="btn-nav-link" onclick="filtrarCandidato('Marconi Perillo')">👤 Marconi Perillo</button>
        </div>

        <div class="card-pesquisa-top">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
                <span style="font-weight:800;color:var(--accent-gold);font-size:15px;">🚀 PESQUISA ELEITORAL OFICIAL — {{ pesquisa.instituto }}</span>
                <span style="background:var(--accent-gold);color:#000;padding:3px 8px;border-radius:6px;font-weight:800;font-size:11px;">DIVULGADA EM {{ pesquisa.data_divulgacao }}</span>
            </div>
            <h2 style="margin:4px 0 12px 0;color:#fff;font-size:18px;">"{{ pesquisa.confirmacao_subida }}"</h2>
            
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Candidato</th>
                            <th>Votos Válidos (%)</th>
                            <th>Posição & Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for c in pesquisa.cenario_votos_validos %}
                        <tr>
                            <td><strong>{{ c.candidato }}</strong></td>
                            <td><strong style="color:var(--accent-gold);font-size:15px;">{{ c.percentual }}</strong></td>
                            <td><span style="color:var(--accent-green);font-weight:bold;">{{ c.posicao }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <h3 style="color:var(--accent-green);margin-bottom:16px;">📰 NOTÍCIAS REAIS DA IMPRENSA DE GOIÁS</h3>

        {% for item in noticias %}
        <div class="card-noticia-item item-noticia {{ item.candidato }} {% if 'CRÍTICA' in item.tipo_noticia %}card-danger{% elif 'POSITIVA' in item.tipo_noticia %}card-pos{% endif %}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
                <span style="background:#1e293b;color:var(--accent-cyan);font-weight:800;padding:3px 8px;border-radius:6px;font-size:11px;">👤 {{ item.candidato }}</span>
                <span style="font-weight:800;color:var(--accent-green);font-size:14px;">📰 {{ item.veiculo }} &bull; <span style="color:var(--text-secondary);font-size:12px;">{{ item.data }}</span></span>
            </div>
            
            <h3 style="margin:0 0 12px 0;color:#fff;font-size:16.5px;line-height:1.4;">"{{ item.manchete }}"</h3>
            
            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px;">
                <a href="{{ item.url_noticia }}" target="_blank" class="btn-link-portal">📰 Ler Matéria Oficial</a>
                <a href="{{ item.url_google_news }}" target="_blank" class="btn-link-gnews">🔍 Auditar Google News</a>
            </div>
            
            <div style="background:#0b0f19;border-left:3px solid var(--accent-gold);padding:12px;border-radius:6px;font-size:13px;line-height:1.5;">
                🛡️ <strong>RESPOSTA IA:</strong> {{ item.estrategia_defesa }}
            </div>
        </div>
        {% endfor %}
    </div>

    <script>
        function filtrarCandidato(cand) {
            const items = document.querySelectorAll('.item-noticia');
            const btns = document.querySelectorAll('.btn-nav-link');
            btns.forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');

            items.forEach(item => {
                if (cand === 'todos' || item.classList.contains(cand)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        async function forcarAtualizacaoNoticias(btn) {
            const originalText = btn.innerHTML;
            btn.innerHTML = '⏳ Coletando...';
            btn.disabled = true;
            try {
                const res = await fetch('/api/forcar_atualizacao', { method: 'POST' });
                const data = await res.json();
                btn.innerHTML = '✅ Atualizado!';
                setTimeout(() => { window.location.reload(); }, 1500);
            } catch(e) {
                btn.innerHTML = '❌ Erro ao atualizar';
                setTimeout(() => { btn.innerHTML = originalText; btn.disabled = false; }, 3000);
            }
        }
    </script>
</body>
</html>
"""

# ROUTING DAS TELAS DA QG DIGITAL MILITAR

@app.route("/", methods=["GET"])
@app.route("/chat", methods=["GET"])
def chat_home():
    status_motor = live_engine.get_status()
    noticias_vivas = live_engine.get_noticias()
    return render_template_string(
        HTML_CHAT_WIDGET,
        wilder_avatar=WILDER_AVATAR_B64,
        status_motor=status_motor,
        noticias_vivas=noticias_vivas
    )

@app.route("/eventos", methods=["GET"])
def eventos_radar_page():
    eventos_vivos = live_engine.get_eventos()
    return render_template_string(
        HTML_RADAR_EVENTOS,
        eventos=eventos_vivos,
        wilder_avatar=WILDER_AVATAR_B64
    )

@app.route("/mapa_demandas", methods=["GET"])
@app.route("/mapa", methods=["GET"])
def route_mapa():
    from pdf_generator_service import MAPA_RECLAMACOES_DETALHADO
    return render_template_string(
        HTML_MAPA_DEMANDAS,
        reclamacoes=MAPA_RECLAMACOES_DETALHADO,
        google_trends=GOOGLE_TRENDS_GOIAS,
        wilder_avatar=WILDER_AVATAR_B64
    )

@app.route("/radar_noticias", methods=["GET"])
def radar_noticias_page():
    noticias_vivas = live_engine.get_noticias()
    pesquisas_vivas = live_engine.get_pesquisas()
    status_motor = live_engine.get_status()
    return render_template_string(
        HTML_RADAR_NOTICIAS,
        noticias=noticias_vivas,
        pesquisa=pesquisas_vivas.get("consolidado", PESQUISA_OFICIAL_GOIAS_2026),
        noticias_pesquisas=pesquisas_vivas.get("noticias", []),
        wilder_avatar=WILDER_AVATAR_B64,
        status_motor=status_motor
    )

@app.route("/dashboard", methods=["GET"])
@app.route("/metabase", methods=["GET"])
def dashboard_metabase_page():
    yt_videos_vivos = live_engine.get_yt_videos()
    canal_metricas_vivas = live_engine.get_yt_canais()
    status_motor = live_engine.get_status()
    return render_template_string(
        HTML_DASHBOARD_METABASE,
        yt_videos=yt_videos_vivos,
        colegios=MAIORES_COLEGIOS_TSE,
        canal_metricas=canal_metricas_vivas,
        wilder_avatar=WILDER_AVATAR_B64,
        status_motor=status_motor
    )

# ─── ROTAS DE API DO MOTOR AUTÔNOMO ──────────────────────────────────────────
@app.route("/api/status", methods=["GET"])
def api_status_motor():
    return jsonify(live_engine.get_status())

@app.route("/api/noticias", methods=["GET"])
def api_noticias_ao_vivo():
    noticias = live_engine.get_noticias()
    return jsonify({"noticias": noticias, "total": len(noticias)})

@app.route("/api/pesquisas", methods=["GET"])
def api_pesquisas_ao_vivo():
    return jsonify(live_engine.get_pesquisas())

@app.route("/api/eventos_grandes", methods=["GET"])
def api_eventos_grandes_ao_vivo():
    eventos = live_engine.get_eventos()
    return jsonify({"eventos": eventos, "total": len(eventos)})

@app.route("/api/tendencias", methods=["GET"])
def api_tendencias_ao_vivo():
    tendencias = live_engine.get_tendencias()
    detalhadas = live_engine.get_tendencias_detalhadas()
    return jsonify({
        "tendencias": tendencias,
        "categorizadas": detalhadas,
        "total": len(tendencias)
    })

@app.route("/api/forcar_atualizacao", methods=["POST", "GET"])
def api_forcar_atualizacao():
    import threading
    threading.Thread(target=live_engine.atualizar_noticias, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_pesquisas_eleitorais, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_tendencias, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_eventos_grandes, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_yt_videos, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_yt_canais, daemon=True).start()
    try:
        import intel_engine
        threading.Thread(target=intel_engine.atualizar_intel_territorial, daemon=True).start()
    except Exception:
        pass
    return jsonify({
        "status": "sucesso",
        "mensagem": "Ciclo militar completo de atualização disparado (Notícias, Pesquisas, Tendências, Eventos +500, YouTube, Intel)!",
        "timestamp": live_engine._agora_str()
    })

@app.route("/plano_governo", methods=["GET"])
@app.route("/primeira_semana", methods=["GET"])
def plano_governo_page():
    return jsonify({"status": "ok", "plano": PLANO_DE_GOVERNO_MEMORIA})

@app.route("/busca_drive", methods=["GET"])
@app.route("/busca", methods=["GET"])
def busca_drive_home():
    try:
        from busca_drive_ia import HTML_BUSCA_DRIVE
        return render_template_string(HTML_BUSCA_DRIVE)
    except Exception:
        return jsonify({"status": "ok", "mensagem": "Busca Drive IA pronta."})

@app.route("/relatorio", methods=["GET"])
@app.route("/relatorio_pdf", methods=["GET"])
@app.route("/download_pdf", methods=["GET"])
def relatorio_pdf_download():
    try:
        pdf_buffer = gerar_buffer_relatorio_360()
        return send_file(
            pdf_buffer,
            mimetype='text/html',
            as_attachment=True,
            download_name='Dossie_Mestre_360_Wilder_Morais.html'
        )
    except Exception as e:
        print(f"[ERRO DOWNLOAD PDF] Falha ao gerar buffer: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    pergunta = (data.get("pergunta") or "").strip()
    if not pergunta:
        return jsonify({"resposta": "Por favor, digite uma pergunta."}), 400

    # Busca notícias reais ao vivo
    noticias_ao_vivo = buscar_noticias_rss()

    # Lê o plano de governo na memória
    plano_governo_texto = ""
    try:
        if os.path.exists('plano_governo_texto.txt'):
            with open('plano_governo_texto.txt', 'r', encoding='utf-8', errors='ignore') as f:
                plano_governo_texto = f.read(5000) # Primeiros 5000 caracteres como contexto principal
    except Exception:
        pass

    # Coleta inteligência da Meta e do motor territorial
    meta_info_txt = ""
    try:
        import meta_algorithm_tracker as mat
        m_data = mat.get_meta_intelligence()
        meta_info_txt = json.dumps(m_data.get("diretrizes", {}), ensure_ascii=False)
    except Exception:
        meta_info_txt = "Foco em Sends per Reach (DM), Retenção 0-3s e ASR áudio falado."

    system_prompt = f"""Você é Paulo, Diretor e Analista Chefe de Inteligência Estratégica, Algoritmos e Dados da campanha Wilder Morais (PL) — Governador de Goiás 2026.

CONSCIÊNCIA TOTAL DO PROJETO & MÓDULOS DISPONÍVEIS:
1. 🎖️ CENTRO DE INTELIGÊNCIA MILITAR (/intel): Monitoramento territorial em tempo real dos 246 municípios de Goiás, mapa de calor Leaflet com dados abertos do IBGE e queixas com classificação NLP (Saúde, Transporte, Emprego, Segurança, Infraestrutura).
2. 🚀 LABORATÓRIO DE ENGAJAMENTO & VIRALIZAÇÃO (/engajamento): Motor de roteiros virais e auditoria algorítmica (score 0-100) calibrado pelas diretrizes oficiais da Meta 2026 (Instagram Reels/Explore).
3. 🚨 RADAR DE PESQUISAS & NOTÍCIAS (/radar_noticias): Monitoramento minuto a minuto dos 3 candidatos (Wilder, Daniel Vilela, Marconi Perillo) e sondagens de institutos de pesquisa.
4. 🗺️ MAPA DE DEMANDAS REGIONAIS (/mapa_demandas): Dores populares por cidade e tendências do Google Trends.
5. 🎪 RADAR DE 150 GRANDES EVENTOS (/eventos): Eventos com +500 pessoas em Goiás com cálculo de raio para Meta Ads e pautas de discurso.
6. 📊 DASHBOARD METABASE & YOUTUBE (/dashboard): Auditoria de canais e vídeos com visualizações reais.
7. 📄 DOSSIÊ EXECUTIVO 360° (/download_pdf): Relatório completo para tomada de decisão da coordenação.

DIRETRIZES DO ALGORITMO DA META 2026 (PARA FURAR A BOLHA):
• SINAL #1 (45% do peso): Sends per Reach (Compartilhamentos por DM). O eleitor precisa pensar: "Vou mandar isso no grupo da família ou pro meu amigo".
• SINAL #2 (30% do peso): Retenção nos Primeiros 3 Segundos (Gancho visual de quebra de padrão + texto em caixa alta na tela de até 5 palavras).
• SINAL #3 (15% do peso): ASR (Reconhecimento de Áudio). A Meta escuta o áudio; fale palavras-chave da dor do povo ("fila do SUS", "primeiro emprego", "remédio em casa").
• REGRA DE OURO: ZERO VÍCIO DE PALANQUE. Elimine jargões burocráticos ("aparato", "plano plurianual"). Wilder deve falar como Engenheiro prático e homem do Agro que constrói e resolve.

FORMATO VISUAL OBRIGATÓRIO (MODERNO, SEPARADO E ELEGANTE):
- NUNCA responda em um único bloco de texto corrido ou amontoado.
- Use SEMPRE títulos de seção com marcadores (Ex: ### 📊 Análise do Cenário, ### 🔍 Perguntas Mais Frequentes, ### 💡 Recomendação Prática).
- Separe CADA pergunta ou ponto em itens de lista destacados (1., 2., 3. ou - ).
- Deixe linha em branco entre cada parágrafo e entre cada tópico.
- Destaque termos-chave e nomes em **negrito**.
- Seja direto, moderno e focado em tomada de decisão da campanha.

═══════════════════════════════════════════
DADOS ELEITORAIS — Instituto Goiás Pesquisas (14/08/2026):
• Daniel Vilela (MDB): 43,5% — Liderança Isolada
• Wilder Morais (PL): 22,0% — Empate técnico pelo 2º lugar
• Marconi Perillo (PSDB): 21,9% — Empate técnico pelo 2º lugar
• Luis Cesar Bueno (PT): 10,5%
• Luciana Amorim (UP): 2,1%

═══════════════════════════════════════════
YOUTUBE — MÉTRICAS AUDITADAS REAIS DOS CANAIS:
• Wilder Morais: 711 inscritos (Canal oficial em fase inicial de crescimento) | Vídeo da Convenção: 103 views, 6 curtidas | Recado Agro: 3,4k views
• Daniel Vilela: 976 inscritos | Convenção: 3,9k views, 117 curtidas
• Marconi Perillo: 2.130 inscritos | Melhores momentos debate: 3,1k views, 55 curtidas
DIAGNÓSTICO CRÍTICO: No YouTube todos os candidatos possuem canais de baixo alcance orgânico direto (< 2,5 mil inscritos). Por isso, a prioridade máxima é FURAR A BOLHA pelo Instagram Reels / Meta Ads / Direct Shares!

═══════════════════════════════════════════
MAPEAMENTO DE QUEIXAS POPULARES E DEMOGRAFIA (Jovens e 35 a 70 anos):
• Luziânia: 45% reclamam de exaustão no transporte para o DF (adultos) e falta de lazer (jovens).
• Goiânia: 42% sofrem com cirurgias eletivas e falta de remédios (40-70 anos), além da busca pelo 1º emprego (jovens).
• Valparaíso: 40% cobram obras de drenagem (adultos) e prevenção criminal para juventude nas periferias.
• Aparecida de Goiânia: 38% pedem segurança patrimonial (adultos) e creches para mães jovens.
• Anápolis: 35% reclamam de barreiras no 1º emprego (jovens) e dificuldade de recolocação nas indústrias (40+).
• Rio Verde: 30% cobram médicos especialistas locais (50+) e tecnologia agrotech para reter jovens.

═══════════════════════════════════════════
COMPORTAMENTO DIGITAL NO GOOGLE TRENDS (O que os Goianos mais pesquisam):
1. Buscas Gerais da População: "Fila do SUS demora quanto tempo?", "Vagas Primeiro Emprego Jovem Aprendiz", "Remédio de Alto Custo", "Preço passagem Entorno DF".
2. Perguntas MAIS FEITAS sobre Wilder Morais no Google:
   - "Quais as propostas de Wilder Morais para Saúde e Emprego?"
   - "Quem é Ana Paula Rezende, a vice de Wilder?"
   - "Qual a porcentagem de Wilder nas pesquisas de 2026?"
   - "Wilder Morais apoia o agronegócio e a indústria?"
   - "Qual o patrimônio e a profissão (Engenheiro) de Wilder Morais?"

═══════════════════════════════════════════
PLANO DE GOVERNO (RESUMO BASEADO NO PDF OFICIAL):
{plano_governo_texto}

═══════════════════════════════════════════
MANCHETES EM TEMPO REAL (Google News):
{noticias_ao_vivo}
═══════════════════════════════════════════

Responda sobre: {pergunta}"""

    if OPENROUTER_API_KEY:
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": pergunta}
            ],
            "temperature": 0.4,
            "max_tokens": 600
        }
        try:
            r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15, verify=False)
            resposta_texto = r.json()["choices"][0]["message"]["content"]
            return jsonify({"resposta": resposta_texto}), 200
        except Exception as e:
            print(f"[ERRO CHAT OPENROUTER]: {e}")

    # FALLBACK LOCAL COM DADOS REAIS
    p_lower = pergunta.lower()
    if any(k in p_lower for k in ["pesquisa", "porcentagem", "votos", "eleição", "eleições", "sondagem", "resultado", "pesquisas"]):
        resp = ("📊 <strong>Cenário Eleitoral — 14/08/2026:</strong><br><br>"
                "Daniel Vilela lidera isolado com 43,5%. Wilder Morais (22,0%) e Marconi Perillo (21,9%) estão em empate técnico "
                "disputando a vaga para o 2º turno. O cenário mostra forte competição no eleitorado de centro-direita.<br><br>"
                "👉 <a href='/radar_noticias' style='color:#10b981;font-weight:800;'>Ver análise completa no Radar de Notícias</a>")
    elif any(k in p_lower for k in ["youtube", "vídeo", "video", "engajamento", "canal", "inscritos"]):
        resp = ("📺 <strong>Métricas Reais Auditadas do YouTube (Goiás 2026):</strong><br><br>"
                "• <strong>Wilder Morais (PL):</strong> 711 inscritos no canal oficial. Vídeo da Convenção Estadual com 103 visualizações e 6 curtidas. Recado ao Agro com 3.464 visualizações.<br>"
                "• <strong>Daniel Vilela (MDB):</strong> 976 inscritos. Convenção com 3.906 visualizações e 117 curtidas.<br>"
                "• <strong>Marconi Perillo (PSDB):</strong> 2.130 inscritos. Debate Band com 3.132 visualizações e 55 curtidas.<br><br>"
                "💡 <em>Diagnóstico Estratégico:</em> O alcance direto no YouTube é restrito para todos os candidatos. A estratégia mestra para furar a bolha é a distribuição no Instagram/Meta Ads.<br><br>"
                "👉 <a href='/dashboard' style='color:#10b981;font-weight:800;'>Ver auditoria completa do YouTube</a>")
    elif any(k in p_lower for k in ["google", "trends", "perguntas", "internet", "goiano", "pesquisam"]):
        resp = ("🔍 <strong>Comportamento no Google Trends:</strong><br><br>"
                "As perguntas mais frequentes no Google sobre o candidato são:<br>"
                "1. Quais as propostas de Wilder para Saúde e Emprego?<br>"
                "2. Quem é Ana Paula Rezende (vice)?<br>"
                "3. Qual a porcentagem de Wilder nas pesquisas?<br>"
                "4. Relação com o Agro e Profissão (Engenheiro).<br><br>"
                "Já nas buscas gerais, os goianos procuram massivamente por 'Fila do SUS', '1º Emprego Jovem' e 'Remédio de Alto Custo'.")
    elif any(k in p_lower for k in ["mapa", "cidade", "queixa", "saúde", "sus", "transporte", "jovem", "emprego", "velho", "idoso", "remédio", "segurança", "idade"]):
        resp = ("🗺️ <strong>Dores Populares (Jovens e 35-70 anos):</strong><br><br>"
                "Luziânia (45%): exaustão no trânsito p/ Brasília. Goiânia (42%): cirurgias eletivas, remédios de alto custo e busca por 1º emprego. "
                "Aparecida (38%): vagas em creches e segurança pública. Anápolis (35%): moradia e barreiras de recolocação para 40+.<br><br>"
                "👉 <a href='/mapa_demandas' style='color:#10b981;font-weight:800;'>Ver mapa interativo completo</a>")
    elif any(k in p_lower for k in ["evento", "festa", "agro", "romaria", "cavalgada", "exposição"]):
        resp = ("🎪 <strong>150 eventos mapeados em Goiás (Ago-Out 2026):</strong><br><br>"
                "O sistema identifica eventos agro, religiosos, culturais e políticos com público estimado e raio de tráfego pago no Meta Ads. "
                "É possível filtrar por mês e visualizar no mapa interativo.<br><br>"
                "👉 <a href='/eventos' style='color:#10b981;font-weight:800;'>Abrir Radar de 150 Eventos</a>")
    elif any(k in p_lower for k in ["algoritmo", "meta", "instagram", "reels", "viral", "engajamento", "furar a bolha", "sinal", "sinais", "dm"]):
        resp = ("🚀 <strong>Diretrizes do Algoritmo da Meta (Instagram 2026):</strong><br><br>"
                "• <strong>Sinal #1 (45% do peso):</strong> <em>Sends per Reach</em> (Compartilhamentos por DM). Crie vídeos que façam o eleitor encaminhar no grupo da família.<br>"
                "• <strong>Sinal #2 (30% do peso):</strong> <em>Retenção 0-3 segundos</em>. O gancho visual e o texto em caixa alta na tela travam o scroll.<br>"
                "• <strong>Sinal #3 (15% do peso):</strong> <em>ASR (Áudio Falado)</em>. O algoritmo indexa palavras magnéticas de dor real.<br>"
                "• <strong>Zero Vício de Palanque:</strong> Discursos de político tradicional limitam o alcance aos mesmos seguidores de sempre.<br><br>"
                "👉 <a href='/engajamento' style='color:#7c3aed;font-weight:800;'>Acessar o Laboratório de Engajamento &amp; Roteiros Virais</a>")
    elif any(k in p_lower for k in ["intel", "militar", "territorial", "calor", "ibge", "municípios", "municipio", "segurança", "comando"]):
        resp = ("🎖️ <strong>Centro de Inteligência Territorial Militar:</strong><br><br>"
                "O sistema monitora em tempo real os 246 municípios de Goiás através de mapa de calor Leaflet com dados do IBGE, "
                "classificando queixas populares em 6 categorias de alarme (Saúde, Transporte, Emprego, Segurança, Infraestrutura e Educação).<br><br>"
                "👉 <a href='/intel' style='color:#00ff88;font-weight:800;'>Abrir o Centro de Comando Militar (/intel)</a>")
    elif any(k in p_lower for k in ["plano", "governo", "proposta", "propostas"]):
        resp = ("📄 <strong>Plano de Governo:</strong><br><br>"
                "As propostas abrangem: 'Fila Visível' e 'Remédio em Casa' (foco em adultos e idosos), 'Primeiro Salário' e 'Curso com Vaga' (jovens), "
                "e 'Cartão Creche' para mães. O foco é resolver problemas reais de todas as idades.<br><br>"
                "👉 <a href='/plano_governo' style='color:#10b981;font-weight:800;'>Acessar base de dados</a>")
    else:
        resp = (f"🔰 <strong>Análise Estratégica: \"{pergunta}\"</strong><br><br>"
                f"Daniel Vilela lidera as pesquisas (43,5%), enquanto Wilder Morais (22%) e Marconi Perillo (21,9%) disputam o 2º turno. "
                f"O desafio central é unificar a mensagem de geração de 1º emprego (jovens) com a resolução de saúde e segurança (público 35 a 70 anos).<br><br>"
                f"Para detalhes específicos, consulte o <a href='/radar_noticias' style='color:#10b981;font-weight:800;'>Radar de Notícias</a> ou o <a href='/mapa_demandas' style='color:#10b981;font-weight:800;'>Mapa de Demandas</a>.")

    return jsonify({"resposta": resp}), 200


# ─── LABORATÓRIO DE ENGAJAMENTO VIRAL ────────────────────────────────────────

# ─── INTELIGÊNCIA TERRITORIAL MILITAR ─────────────────────────────────────────
@app.route("/intel", methods=["GET"])
@app.route("/inteligencia", methods=["GET"])
def intel_page():
    return render_template_string(HTML_INTELIGENCIA_TERRITORIAL, wilder_avatar=WILDER_AVATAR_B64)

@app.route("/api/intel_queixas", methods=["GET"])
def api_intel_queixas():
    try:
        import intel_engine
        return jsonify({"queixas": intel_engine.get_queixas(), "total": len(intel_engine.get_queixas())}), 200
    except Exception as e:
        return jsonify({"queixas": [], "total": 0, "erro": str(e)}), 200

@app.route("/api/intel_mapa", methods=["GET"])
def api_intel_mapa():
    try:
        import intel_engine
        return jsonify({"mapa_calor": intel_engine.get_mapa_calor()}), 200
    except Exception as e:
        return jsonify({"mapa_calor": [], "erro": str(e)}), 200

@app.route("/api/intel_ibge", methods=["GET"])
def api_intel_ibge():
    try:
        import intel_engine
        ibge_data = intel_engine.get_ibge()
        # Se ainda vazio, retorna tabela base offline
        if not ibge_data:
            muns = intel_engine.get_municipios_base()
            ibge_data = {m["codigo"]: m for m in muns}
        return jsonify({"ibge": ibge_data, "total": len(ibge_data)}), 200
    except Exception as e:
        return jsonify({"ibge": {}, "erro": str(e)}), 200

@app.route("/api/intel_ranking", methods=["GET"])
def api_intel_ranking():
    try:
        import intel_engine
        return jsonify({"ranking": intel_engine.get_ranking_cidades()}), 200
    except Exception as e:
        return jsonify({"ranking": [], "erro": str(e)}), 200

@app.route("/api/intel_status", methods=["GET"])
def api_intel_status():
    try:
        import intel_engine
        status = intel_engine.get_status_intel()
        status["alertas_lista"] = intel_engine.get_alertas()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"motor": "INICIALIZANDO", "erro": str(e)}), 200

@app.route("/api/intel_forcar", methods=["POST", "GET"])
def api_intel_forcar():
    try:
        import intel_engine
        import threading
        threading.Thread(target=intel_engine.atualizar_intel_territorial, daemon=True).start()
        return jsonify({"status": "ok", "mensagem": "Coleta de inteligência territorial disparada!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/engajamento", methods=["GET"])
def engajamento_lab_page():
    return render_template_string(HTML_ENGAJAMENTO_LAB, wilder_avatar=WILDER_AVATAR_B64)


@app.route("/api/meta_algoritmo", methods=["GET"])
def api_meta_algoritmo():
    try:
        import meta_algorithm_tracker as mat
        return jsonify(mat.get_meta_intelligence()), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route("/api/gerar_roteiro_viral", methods=["POST"])
def api_gerar_roteiro_viral():
    try:
        import engajamento_service as es
        data = request.json or {}
        tema     = data.get("tema", "saúde e filas do SUS")
        estimulo = data.get("estimulo", "furar_bolha")
        formato  = data.get("formato", "reels_30s")
        cidade   = data.get("cidade", "Goiás Geral")
        resultado = es.gerar_roteiro_viral_ia(tema, estimulo, formato, cidade)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/api/auditar_roteiro", methods=["POST"])
def api_auditar_roteiro():
    try:
        import engajamento_service as es
        data = request.json or {}
        texto = (data.get("roteiro") or data.get("texto") or "").strip()
        if not texto:
            return jsonify({"erro": "Envie o campo 'roteiro' com o texto para auditoria."}), 400
        resultado = es.auditar_roteiro_ia(texto)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/api/palavras_magneticas", methods=["GET"])
def api_palavras_magneticas():
    try:
        import engajamento_service as es
        return jsonify(es.PALAVRAS_MAGNETICAS_GOIAS), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 QG Digital Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
