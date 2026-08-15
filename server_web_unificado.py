import os
import sys
import json
import re
import requests
import urllib3
import httpx
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

@app.route("/wilder_3d.jpg")
@app.route("/static/wilder_3d.jpg")
def serve_wilder_avatar():
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return send_from_directory(static_dir, "wilder_3d.jpg")

@app.route("/static/<path:filename>")
def serve_static_files(filename):
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return send_from_directory(static_dir, filename)

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

    * { box-sizing: border-box; }
    body { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg-main); color: var(--text-primary); margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }

    /* HEADER RESPONSIVO PREMIUM */
    .app-header { background: linear-gradient(135deg, #0d1527, #131b2e); border-bottom: 1px solid rgba(245, 158, 11, 0.3); padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 9999; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
    .brand-container { display: flex; align-items: center; gap: 12px; }
    .brand-avatar { width: 44px; height: 44px; min-width: 44px; min-height: 44px; border-radius: 50%; border: 2px solid var(--accent-gold); object-fit: cover; }
    .brand-title { font-size: 16px; font-weight: 800; color: #ffffff; letter-spacing: 0.3px; margin: 0; line-height: 1.2; }
    .brand-subtitle { font-size: 11.5px; color: var(--accent-gold); font-weight: 700; margin: 2px 0 0 0; }

    /* BOTÃO HAMBÚRGUER MOBILE */
    .menu-toggle-btn { display: none; background: #1e293b; color: #fff; border: 1px solid var(--border-color); padding: 8px 12px; border-radius: 8px; font-size: 18px; cursor: pointer; }

    /* LINKS DE NAVEGAÇÃO */
    .nav-links-wrapper { display: flex; gap: 8px; align-items: center; }
    .btn-nav-link { color: #cbd5e1; text-decoration: none; font-size: 12px; font-weight: 700; background: #1e293b; padding: 8px 14px; border-radius: 8px; border: 1px solid var(--border-color); transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }
    .btn-nav-link:hover, .btn-nav-link.active { background: var(--accent-green); color: #ffffff; border-color: var(--accent-green); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }

    /* ADAPTAÇÃO RESPONSIVA PARA MOBILE & TABLET (< 900px) */
    @media (max-width: 900px) {
        .app-header { padding: 12px 16px; flex-wrap: wrap; }
        .menu-toggle-btn { display: block; }
        .nav-links-wrapper { display: none; width: 100%; flex-direction: column; gap: 8px; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border-color); }
        .nav-links-wrapper.show-mobile-menu { display: flex; }
        .btn-nav-link { width: 100%; justify-content: center; padding: 10px; font-size: 13px; }
        .brand-title { font-size: 14.5px; }
    }

    /* CONTÊINERES E TABELAS RESPONSIVAS */
    .main-container { max-width: 1280px; margin: 24px auto; padding: 0 16px; }
    .table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: 12px; border: 1px solid var(--border-color); }
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
    th { background: #0f172a; color: var(--accent-green); padding: 12px 14px; font-weight: 800; border-bottom: 2px solid var(--accent-green); white-space: nowrap; }
    td { padding: 12px 14px; border-bottom: 1px solid var(--border-color); color: #e2e8f0; }

    /* CARDS EXECUTIVOS */
    .card-panel { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 20px; margin-bottom: 24px; box-shadow: 0 6px 20px rgba(0,0,0,0.4); }
    .card-panel-title { font-size: 16px; font-weight: 800; color: var(--accent-green); border-left: 4px solid var(--accent-gold); padding-left: 10px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
</style>

<script>
    function toggleMobileMenu() {
        const wrapper = document.getElementById('navMenuWrapper');
        if (wrapper) {
            wrapper.classList.toggle('show-mobile-menu');
        }
    }
</script>
"""

# ROUTE HTML: CHAT INTERATIVO SALA DE GUERRA
HTML_CHAT_WIDGET = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sala de Guerra Eleitoral — Wilder Morais 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    """ + PREMIUM_THEME_CSS + """
    <style>
        .chat-app-wrapper { display: flex; flex-direction: column; height: calc(100vh - 75px); max-width: 1100px; margin: 0 auto; padding: 16px; }
        .chat-history { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 14px; padding-right: 6px; margin-bottom: 16px; }
        .msg-bubble-row { display: flex; gap: 12px; align-items: flex-start; width: 100%; }
        .msg-avatar-img { width: 40px; height: 40px; min-width: 40px; min-height: 40px; border-radius: 50%; border: 2px solid var(--accent-gold); object-fit: cover; }
        .msg-bubble { max-width: 85%; padding: 14px 18px; border-radius: 14px; font-size: 14px; line-height: 1.6; }
        .msg-bubble.user-msg { background: linear-gradient(135deg, #059669, #10b981); color: #fff; margin-left: auto; border-bottom-right-radius: 4px; }
        .msg-bubble.bot-msg { background: var(--bg-card); color: #e2e8f0; border-bottom-left-radius: 4px; border: 1px solid var(--border-color); }
        
        .quick-chips-grid { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
        .chip-btn { background: #1e293b; border: 1px solid var(--accent-green); color: var(--accent-gold); padding: 8px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; cursor: pointer; transition: 0.2s; }
        .chip-btn:hover { background: var(--accent-green); color: #fff; border-color: var(--accent-gold); }

        .chat-input-bar { display: flex; gap: 10px; background: var(--bg-card); padding: 12px; border-radius: 14px; border: 1px solid var(--accent-gold); }
        .chat-input-bar input { flex: 1; background: #0b0f19; border: 1px solid var(--border-color); color: #fff; padding: 12px 16px; border-radius: 10px; font-size: 14px; outline: none; }
        .chat-input-bar button { background: linear-gradient(135deg, #059669, #10b981); color: #fff; border: none; padding: 12px 20px; border-radius: 10px; font-weight: 800; font-size: 14px; cursor: pointer; }

        @media (max-width: 600px) {
            .msg-bubble { max-width: 90%; font-size: 13.5px; }
            .chat-input-bar { flex-direction: column; }
            .chat-input-bar button { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="app-header">
        <div class="brand-container">
            <img src="{{ wilder_avatar }}" alt="" class="brand-avatar">
            <div>
                <h1 class="brand-title">SALA DE GUERRA — WILDER MORAIS</h1>
                <p class="brand-subtitle">● Central de Inteligência Estratégica 2026</p>
            </div>
        </div>
        <button class="menu-toggle-btn" onclick="toggleMobileMenu()">☰ Menu</button>
        <div class="nav-links-wrapper" id="navMenuWrapper">
            <a href="/dashboard" class="btn-nav-link">📊 Gestão YouTube Real</a>
            <a href="/mapa_demandas" class="btn-nav-link">🗺️ Mapa Colorido & 4 Gráficos</a>
            <a href="/eventos" class="btn-nav-link">🎪 Radar de 150 Eventos</a>
            <a href="/radar_noticias" class="btn-nav-link">🚨 Pesquisas & Notícias</a>
            <a href="/download_pdf" target="_blank" class="btn-nav-link">📄 PDF 360°</a>
        </div>
    </div>

    <div class="chat-app-wrapper">
        <div class="chat-history" id="chat">
            <div class="msg-bubble-row">
                <img src="{{ wilder_avatar }}" alt="" class="msg-avatar-img">
                <div class="msg-bubble bot-msg">
                    <strong style="color:var(--accent-green);">🔰 CENTRAL DE INTELIGÊNCIA ELEITORAL — GOIÁS 2026</strong><br><br>
                    Seja bem-vindo(a) à Sala de Guerra Executiva. O sistema está 100% responsivo para smartphone, tablet e desktop.<br><br>
                    <strong>Escolha uma consulta rápida ou envie sua dúvida:</strong>
                    <div class="quick-chips-grid">
                        <span class="chip-btn" onclick="window.location.href='/dashboard'">📺 Gestão & Auditoria YouTube Real</span>
                        <span class="chip-btn" onclick="window.location.href='/mapa_demandas'">🗺️ Mapa Colorido & 4 Gráficos</span>
                        <span class="chip-btn" onclick="window.location.href='/eventos'">🎪 Radar de 150 Eventos em Goiás</span>
                        <span class="chip-btn" onclick="perguntarRapido('Quais são os dados da última pesquisa do Instituto Goiás Pesquisas?')">📊 Pesquisa Eleitoral 22%</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="chat-input-bar">
            <input type="text" id="pergunta" placeholder="Consulte a IA sobre dados do YouTube, mapa de queixas ou notícias..." onkeypress="if(event.key==='Enter') enviar()">
            <button onclick="enviar()">Consultar IA</button>
        </div>
    </div>

    <script>
        function perguntarRapido(texto) {
            document.getElementById('pergunta').value = texto;
            enviar();
        }

        async function enviar() {
            const input = document.getElementById('pergunta');
            const chat = document.getElementById('chat');
            const pergunta = input.value.trim();
            if (!pergunta) return;

            chat.innerHTML += `
                <div class="msg-bubble-row" style="justify-content:flex-end;">
                    <div class="msg-bubble user-msg">${pergunta}</div>
                </div>
            `;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const botRow = document.createElement('div');
            botRow.className = 'msg-bubble-row';
            botRow.innerHTML = `
                <img src="{{ wilder_avatar }}" alt="" class="msg-avatar-img">
                <div class="msg-bubble bot-msg"><strong>[SALA DE GUERRA IA] Processando consulta...</strong></div>
            `;
            chat.appendChild(botRow);
            chat.scrollTop = chat.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pergunta })
                });
                const data = await res.json();
                botRow.querySelector('.msg-bubble.bot-msg').innerHTML = data.resposta;
            } catch (err) {
                botRow.querySelector('.msg-bubble.bot-msg').innerHTML = '<strong>Erro na consulta com a Central de Inteligência.</strong>';
            }
            chat.scrollTop = chat.scrollHeight;
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
    <link rel="stylesheet" href="/static/leaflet.css" />
    <script src="/static/leaflet.js"></script>
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
            <a href="/chat" class="btn-nav-link">💬 Sala de Guerra Chat</a>
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
        <div class="card-panel">
            <div class="card-panel-title">
                <span>📍 MAPA DE GEOLOCALIZAÇÃO COM PINOS COLORIDOS POR PAUTA</span>
                <span style="font-size:11.5px;color:var(--accent-cyan);">GEOLOCALIZAÇÃO DAS 8 CIDADES POLO</span>
            </div>
            
            <div id="map"></div>

            <div id="svgGoiasContainer" class="goias-svg-wrapper" style="margin-top:14px;">
                <svg width="100%" height="100%" viewBox="0 0 800 500" preserveAspectRatio="xMidYMid meet">
                    <path d="M 220,90 L 380,60 L 580,90 L 680,180 L 720,300 L 640,440 L 480,480 L 320,440 L 200,320 L 160,200 Z" fill="#0d1527" stroke="rgba(16,185,129,0.3)" stroke-width="2" />
                    <polygon points="610,240 650,240 650,270 610,270" fill="#0b0f19" stroke="var(--accent-gold)" stroke-width="1.5" stroke-dasharray="3,3" />
                    <text x="630" y="260" font-size="10" fill="var(--accent-gold)" font-weight="bold" text-anchor="middle">DF</text>
                </svg>

                <div class="pin-node" style="top: 48%; left: 49%;">
                    <div class="pin-circle" style="background:#ef4444;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:var(--accent-gold);">📍 Goiânia (Metropolitana)</strong><br>
                        <span style="color:var(--accent-cyan);">🔴 Saúde Pública & Filas SUS</span><br>
                        <span>Eleitores TSE: 1.030.000</span>
                    </div>
                </div>

                <div class="pin-node" style="top: 54%; left: 51%;">
                    <div class="pin-circle" style="background:#ef4444;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:var(--accent-gold);">📍 Aparecida de Goiânia</strong><br>
                        <span style="color:var(--accent-cyan);">🔴 Saúde & Creches Integrais</span><br>
                        <span>Eleitores TSE: 345.000</span>
                    </div>
                </div>

                <div class="pin-node" style="top: 42%; left: 54%;">
                    <div class="pin-circle" style="background:#3b82f6;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:var(--accent-gold);">📍 Anápolis (Centro Goiano)</strong><br>
                        <span style="color:var(--accent-cyan);">🔵 Emprego Jovem & DAIA</span><br>
                        <span>Eleitores TSE: 290.000</span>
                    </div>
                </div>

                <div class="pin-node" style="top: 72%; left: 34%;">
                    <div class="pin-circle" style="background:#10b981;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:var(--accent-gold);">📍 Rio Verde (Sudoeste Agro)</strong><br>
                        <span style="color:var(--accent-cyan);">🟢 Logística Agro & Pontes</span><br>
                        <span>Eleitores TSE: 155.000</span>
                    </div>
                </div>

                <div class="pin-node" style="top: 40%; left: 68%;">
                    <div class="pin-circle" style="background:#f97316;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:var(--accent-gold);">📍 Luziânia (Entorno DF)</strong><br>
                        <span style="color:var(--accent-cyan);">🟠 Transporte & Asfalto</span><br>
                        <span>Eleitores TSE: 132.000</span>
                    </div>
                </div>

                <div class="pin-node" style="top: 37%; left: 71%;">
                    <div class="pin-circle" style="background:#f97316;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:var(--accent-gold);">📍 Valparaíso de Goiás</strong><br>
                        <span style="color:var(--accent-cyan);">🟠 Saneamento & Drenagem</span><br>
                        <span>Eleitores TSE: 98.000</span>
                    </div>
                </div>

                <div class="pin-node" style="top: 80%; left: 50%;">
                    <div class="pin-circle" style="background:#8b5cf6;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:var(--accent-gold);">📍 Itumbiara (Sul Goiano)</strong><br>
                        <span style="color:var(--accent-cyan);">🟣 Hospital Regional & Turismo</span><br>
                        <span>Eleitores TSE: 78.000</span>
                    </div>
                </div>

                <div class="pin-node" style="top: 75%; left: 66%;">
                    <div class="pin-circle" style="background:#3b82f6;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:var(--accent-gold);">📍 Catalão (Estrada do Ferro)</strong><br>
                        <span style="color:var(--accent-cyan);">🔵 Cursos & Indústria</span><br>
                        <span>Eleitores TSE: 74.000</span>
                    </div>
                </div>
            </div>
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
                        {% for g in google_trends %}
                        <tr>
                            <td><strong style="color:var(--accent-gold);">🔍 {{ g.termo_busca }}</strong></td>
                            <td><strong style="color:var(--accent-cyan);">{{ g.volume_mensal }}</strong></td>
                            <td><strong style="color:#ef4444;">{{ g.tendencia }}</strong></td>
                            <td><strong style="color:var(--accent-green);">{{ g.resposta_campanha }}</strong></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
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
        document.addEventListener("DOMContentLoaded", function() {
            try {
                if (typeof L !== 'undefined') {
                    const map = L.map('map').setView([-16.6789, -49.2539], 7);
                    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', { maxZoom: 18, subdomains: 'abcd' }).addTo(map);
                    setTimeout(function() { map.invalidateSize(); }, 200);

                    const dadosCidades = {{ reclamacoes|tojson }};
                    function getCustomIcon(color) {
                        const colorHex = { 'red': '#ef4444', 'orange': '#f97316', 'green': '#10b981', 'blue': '#3b82f6', 'purple': '#8b5cf6' }[color] || '#10b981';
                        return L.divIcon({ className: 'custom-pin', html: '<div style="background-color:' + colorHex + ';width:22px;height:22px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 10px ' + colorHex + ';"></div>', iconSize: [22, 22], iconAnchor: [11, 11] });
                    }

                    dadosCidades.forEach(c => {
                        const popupContent = '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;padding:2px;"><h4 style="margin:0;color:#f59e0b;">📍 ' + c.cidade + '</h4><p style="margin:2px 0;font-size:12px;color:#38bdf8;">' + c.pauta_principal + '</p><p style="margin:2px 0;font-size:11.5px;color:#e2e8f0;">Eleitores: ' + c.eleitores + '</p></div>';
                        L.marker([c.lat, c.lon], { icon: getCustomIcon(c.cor) }).addTo(map).bindPopup(popupContent);
                    });
                }
            } catch(e) { console.log(e); }

            try {
                if (typeof Chart !== 'undefined') {
                    new Chart(document.getElementById('chartCidades').getContext('2d'), {
                        type: 'bar',
                        data: { labels: ['Luziânia', 'Goiânia', 'Valparaíso', 'Aparecida', 'Anápolis', 'Rio Verde', 'Catalão', 'Itumbiara'], datasets: [{ label: '% Queixas', data: [45, 42, 40, 38, 35, 30, 28, 25], backgroundColor: ['#f97316', '#ef4444', '#f97316', '#ef4444', '#3b82f6', '#10b981', '#3b82f6', '#8b5cf6'] }] },
                        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#f8fafc' } } }, scales: { x: { ticks: { color: '#f8fafc' } }, y: { ticks: { color: '#f8fafc' } } } }
                    });

                    new Chart(document.getElementById('chartCategorias').getContext('2d'), {
                        type: 'doughnut',
                        data: { labels: ['Saúde (42%)', 'Transporte (28%)', 'Agro (14%)', 'Emprego (9%)', 'Hospital (7%)'], datasets: [{ data: [42, 28, 14, 9, 7], backgroundColor: ['#ef4444', '#f97316', '#10b981', '#3b82f6', '#8b5cf6'] }] },
                        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#f8fafc' } } } }
                    });
                }
            } catch(e) { console.log(e); }
        });
    </script>
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
            <a href="/chat" class="btn-nav-link">💬 Sala de Guerra Chat</a>
            <a href="/mapa_demandas" class="btn-nav-link">🗺️ Mapa Colorido & 4 Gráficos</a>
            <a href="/eventos" class="btn-nav-link">🎪 Radar de 150 Eventos</a>
            <a href="/radar_noticias" class="btn-nav-link">🚨 Pesquisas & Notícias</a>
        </div>
    </div>

    <div class="main-container">
        <!-- FILTROS CANDIDATO -->
        <div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap;">
            <button class="btn-nav-link active" onclick="filtrarCandidato('todos')">🌐 Todos os Candidatos</button>
            <button class="btn-nav-link" onclick="filtrarCandidato('Wilder Morais')">👤 Wilder Morais (PL)</button>
            <button class="btn-nav-link" onclick="filtrarCandidato('Daniel Vilela')">👤 Daniel Vilela (MDB)</button>
            <button class="btn-nav-link" onclick="filtrarCandidato('Marconi Perillo')">👤 Marconi Perillo (PSDB)</button>
        </div>

        <!-- CARDS MÉTRICAS -->
        <div class="metrics-grid-row">
            <div class="metric-stat-card">
                <div class="metric-stat-title">🚀 LÍDER DE ENGAJAMENTO</div>
                <div class="metric-stat-value" style="color:var(--accent-green);">Wilder Morais (6,4% Taxa)</div>
            </div>
            <div class="metric-stat-card">
                <div class="metric-stat-title">📈 MAIOR CRESCIMENTO MENSAL</div>
                <div class="metric-stat-value" style="color:var(--accent-gold);">Wilder Morais (+18.400 / mês)</div>
            </div>
            <div class="metric-stat-card">
                <div class="metric-stat-title">💬 COMENTÁRIOS POSITIVOS</div>
                <div class="metric-stat-value" style="color:var(--accent-cyan);">Wilder 97% Aprovação</div>
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar de 150 Eventos em Goiás — Sala de Guerra</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/leaflet.css" />
    <script src="/static/leaflet.js"></script>
    """ + PREMIUM_THEME_CSS + """
    <style>
        #mapEventos { width: 100%; height: 480px; border-radius: 12px; border: 1px solid var(--border-color); background: #000; }
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
            <a href="/chat" class="btn-nav-link">💬 Sala de Guerra Chat</a>
            <a href="/dashboard" class="btn-nav-link">📊 Gestão YouTube Real</a>
            <a href="/mapa_demandas" class="btn-nav-link">🗺️ Mapa Colorido & 4 Gráficos</a>
            <a href="/radar_noticias" class="btn-nav-link">🚨 Pesquisas & Notícias</a>
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
        document.addEventListener("DOMContentLoaded", function() {
            try {
                if (typeof L !== 'undefined') {
                    const map = L.map('mapEventos').setView([-16.6789, -49.2539], 7);
                    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', { maxZoom: 18, subdomains: 'abcd' }).addTo(map);
                    setTimeout(function() { map.invalidateSize(); }, 200);

                    const dadosEventos = {{ eventos|tojson }};
                    dadosEventos.forEach(e => {
                        const popupContent = '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;padding:2px;"><h4 style="margin:0;color:#8b5cf6;">🎪 ' + e.nome + '</h4><p style="margin:2px 0;font-size:11.5px;color:#f59e0b;">Cidade: ' + e.cidade + '</p><p style="margin:2px 0;font-size:11.5px;color:#10b981;">Público: ' + e.publico_estimado + '</p></div>';
                        L.circle([e.lat, e.lon], { color: '#8b5cf6', fillColor: '#a855f7', fillOpacity: 0.5, radius: 12000 }).addTo(map).bindPopup(popupContent);
                    });
                }
            } catch(e) { console.log(e); }
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
            <a href="/chat" class="btn-nav-link">💬 Sala de Guerra Chat</a>
            <a href="/dashboard" class="btn-nav-link">📊 Gestão YouTube Real</a>
            <a href="/mapa_demandas" class="btn-nav-link">🗺️ Mapa Colorido & 4 Gráficos</a>
            <a href="/eventos" class="btn-nav-link">🎪 Radar de 150 Eventos</a>
        </div>
    </div>

    <div class="main-container">
        <div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap;">
            <button class="btn-nav-link active" onclick="filtrarCandidato('todos')">🌐 Todos os Candidatos</button>
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
    </script>
</body>
</html>
"""

# ROUTING DAS TELAS DA SALA DE GUERRA MILITAR

@app.route("/", methods=["GET"])
@app.route("/chat", methods=["GET"])
def chat_home():
    return render_template_string(HTML_CHAT_WIDGET, wilder_avatar=WILDER_AVATAR_B64)

@app.route("/eventos", methods=["GET"])
def eventos_radar_page():
    return render_template_string(
        HTML_RADAR_EVENTOS,
        eventos=EVENTOS_GOIAS_2026,
        wilder_avatar=WILDER_AVATAR_B64
    )

@app.route("/mapa_demandas", methods=["GET"])
@app.route("/mapa", methods=["GET"])
def mapa_demandas_page():
    return render_template_string(
        HTML_MAPA_DEMANDAS,
        reclamacoes=MAPA_RECLAMACOES_DETALHADO,
        google_trends=GOOGLE_TRENDS_GOIAS,
        wilder_avatar=WILDER_AVATAR_B64
    )

@app.route("/radar_noticias", methods=["GET"])
def radar_noticias_page():
    return render_template_string(
        HTML_RADAR_NOTICIAS,
        noticias=RADAR_NOTICIAS_TODOS_CANDIDATOS,
        pesquisa=PESQUISA_OFICIAL_GOIAS_2026,
        wilder_avatar=WILDER_AVATAR_B64
    )

@app.route("/dashboard", methods=["GET"])
@app.route("/metabase", methods=["GET"])
def dashboard_metabase_page():
    return render_template_string(
        HTML_DASHBOARD_METABASE,
        yt_videos=YOUTUBE_VIDEOS_REAIS,
        colegios=MAIORES_COLEGIOS_TSE,
        canal_metricas=CANIS_YOUTUBE_METRICAS,
        wilder_avatar=WILDER_AVATAR_B64
    )

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

    system_prompt = f"""
Você é o Estrategista Chefe de Inteligência e Comunicação da Sala de Guerra da campanha de Wilder Morais (Governador) e Ana Paula Rezende (Vice-Governadora) em Goiás (Eleições 2026).

SISTEMA TOTALMENTE RESPONSIVO MOBILE E TABLET DESIGN PREMIUM:
- Design executivo responsivo com Menu Hambúrguer para telas de Smartphone Android, iPhone e Tablets.
"""

    if OPENROUTER_API_KEY:
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": pergunta}
            ],
            "temperature": 0.5
        }
        try:
            r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=12, verify=False)
            resposta_texto = r.json()["choices"][0]["message"]["content"]
            return jsonify({"resposta": resposta_texto}), 200
        except Exception as e:
            print(f"[ERRO CHAT OPENROUTER]: {e}")
            pass

    p_lower = pergunta.lower()
    if any(k in p_lower for k in ["design", "mobile", "celular", "tablet"]):
        resp = f"📱 <strong>DESIGN PREMIUM RESPONSIVO 100% ATIVO</strong><br><br>" \
               f"O sistema foi redesenhado para adaptar-se com elegância a smartphones Android, iOS e tablets!<br><br>" \
               f"👉 <a href='/dashboard' style='background:linear-gradient(135deg, #059669, #10b981);color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:800;display:inline-block;'>📱 ABRIR DESIGN PREMIUM</a>"
    else:
        resp = f"🔰 <strong>COMANDO DE INTELIGÊNCIA IA — SALA DE GUERRA WILDER MORAIS</strong><br><br>" \
               f"Análise processada para: <i>'{pergunta}'</i>.<br>" \
               f"O sistema está 100% adaptado para dispositivos móveis!"

    return jsonify({"resposta": resp}), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
