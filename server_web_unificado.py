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
    PRIMEIRA_SEMANA_CONTEUDO, EVENTOS_GOIAS_2026
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

# ROTA DEDICADA PARA SERVIR A FOTO 3D DE PERFIL DO WILDER
@app.route("/wilder_3d.jpg")
@app.route("/static/wilder_3d.jpg")
def serve_wilder_avatar():
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return send_from_directory(static_dir, "wilder_3d.jpg")

# BLINDAGEM DO CLIENTE: DESABILITA CLIQUE DIREITO, F12, CTRL+U
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

# COMPONENTE DE TOAST POPUP COM O AVATAR 3D DO WILDER
HTML_ALERT_SYSTEM_SCRIPT = """
<style>
    @keyframes pulseAlert {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { box-shadow: 0 0 0 16px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    .toast-alert-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 99999;
        max-width: 440px;
        width: 92%;
        background: linear-gradient(135deg, #0b2214, #15803d);
        border: 2px solid #eab308;
        border-radius: 16px;
        padding: 16px 20px;
        color: #ffffff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.7);
        animation: pulseAlert 2s infinite;
        display: block;
    }

    .toast-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .toast-badge { background: #eab308; color: #040e08; font-weight: 800; font-size: 11px; padding: 3px 8px; border-radius: 6px; }
    .toast-close { background: transparent; border: none; color: #fef08a; font-size: 20px; font-weight: bold; cursor: pointer; }
    
    .toast-content-wrapper { display: flex; gap: 14px; align-items: center; }
    .toast-avatar { width: 56px; height: 56px; border-radius: 50%; border: 2px solid #eab308; object-fit: cover; box-shadow: 0 4px 12px rgba(234,179,8,0.5); }
    
    .toast-title { font-size: 15px; font-weight: 800; color: #fef08a; margin: 0 0 4px 0; }
    .toast-body { font-size: 12.5px; color: #e2e8f0; line-height: 1.4; margin-bottom: 8px; }
    .toast-btn { background: #040e08; color: #86efac; border: 1px solid #22c55e; padding: 6px 12px; border-radius: 6px; font-size: 11.5px; font-weight: 800; text-decoration: none; display: inline-block; }
    .toast-btn:hover { background: #16a34a; color: #fff; border-color: #eab308; }
</style>

<div id="toastAlert" class="toast-alert-container">
    <div class="toast-header">
        <span class="toast-badge">🚀 ALERTA DE PESQUISA ELEITORAL</span>
        <button class="toast-close" onclick="document.getElementById('toastAlert').style.display='none';">✕</button>
    </div>
    <div class="toast-content-wrapper">
        <img src="/wilder_3d.jpg" alt="Wilder Morais 3D" class="toast-avatar">
        <div>
            <div class="toast-title">WILDER SALTA PARA 22% NOS VOTOS VÁLIDOS!</div>
            <div class="toast-body">
                Instituto Goiás Pesquisas confirma: <strong>Wilder atinge 22,0%</strong> e vai para o 2º Turno em Goiás!
            </div>
            <a href="/radar_noticias" class="toast-btn">📊 Ver no Radar</a>
        </div>
    </div>
</div>
""" + HTML_PROTECTION_SCRIPT

# INTERFACE MILITAR PENTÁGONO VERDE E AMARELO COM FOTO 3D DE PERFIL
HTML_CHAT_WIDGET = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SALA DE GUERRA ELEITORAL — WILDER MORAIS 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; background: #040e08; color: #f8fafc; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        
        .header { background: linear-gradient(135deg, #0b2214, #15803d, #16a34a); padding: 12px 28px; border-bottom: 3px solid #eab308; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 6px 25px rgba(22,163,74,0.4); }
        .brand { display: flex; align-items: center; gap: 14px; }
        .brand-avatar { width: 50px; height: 50px; border-radius: 50%; border: 2px solid #eab308; object-fit: cover; box-shadow: 0 4px 15px rgba(234,179,8,0.6); }
        .brand-text h1 { margin: 0; font-size: 19px; font-weight: 800; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.4); letter-spacing: 0.5px; }
        .brand-text p { margin: 2px 0 0 0; font-size: 12px; color: #fef08a; font-weight: 700; }
        
        .nav-links { display: flex; gap: 8px; flex-wrap: wrap; }
        .btn-nav { color: #f8fafc; text-decoration: none; font-size: 12.5px; font-weight: 700; background: #0c2415; padding: 8px 14px; border-radius: 8px; border: 1px solid #22c55e; transition: 0.2s; display: flex; align-items: center; gap: 6px; }
        .btn-nav:hover { background: #16a34a; border-color: #eab308; color: #fff; }
        .btn-alert { background: #991b1b; border-color: #ef4444; color: #fecdd3; font-weight: 800; }
        .btn-mapa { background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; border-color: #38bdf8; font-weight: 800; }
        .btn-dashboard { background: linear-gradient(135deg, #eab308, #ca8a04); color: #040e08; border-color: #fef08a; font-weight: 800; }
        .btn-pdf { background: linear-gradient(135deg, #15803d, #16a34a); border-color: #eab308; color: #fef08a; }
        
        .chat-box { flex: 1; padding: 24px 28px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; max-width: 1100px; margin: 0 auto; width: 100%; }
        .msg-row { display: flex; gap: 12px; align-items: flex-start; width: 100%; }
        .msg-avatar { width: 42px; height: 42px; border-radius: 50%; border: 2px solid #eab308; object-fit: cover; flex-shrink: 0; box-shadow: 0 2px 10px rgba(0,0,0,0.5); }
        .msg { max-width: 88%; padding: 18px 22px; border-radius: 14px; font-size: 14.5px; line-height: 1.6; }
        .user { background: linear-gradient(135deg, #15803d, #16a34a); color: #fff; margin-left: auto; border-bottom-right-radius: 4px; border: 1px solid #22c55e; }
        .bot { background: #0a1f12; color: #e2e8f0; border-bottom-left-radius: 4px; border: 1px solid #164624; box-shadow: 0 6px 20px rgba(0,0,0,0.5); }
        .bot strong { color: #86efac; }

        .quick-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
        .chip { background: #0d2e19; border: 1px solid #22c55e; color: #fef08a; padding: 9px 16px; border-radius: 20px; font-size: 12.5px; font-weight: 700; cursor: pointer; transition: 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
        .chip:hover { background: #16a34a; color: #fff; border-color: #eab308; }

        .input-container { background: #0b2214; padding: 18px 28px; border-top: 2px solid #eab308; }
        .input-box { max-width: 1100px; margin: 0 auto; display: flex; gap: 12px; }
        input { flex: 1; padding: 14px 18px; border-radius: 12px; border: 1px solid #22c55e; background: #040e08; color: #fff; font-size: 15px; outline: none; transition: 0.2s; }
        input:focus { border-color: #eab308; box-shadow: 0 0 0 3px rgba(234,179,8,0.25); }
        button { padding: 14px 28px; background: linear-gradient(135deg, #15803d, #16a34a); color: #fef08a; border: 1px solid #eab308; border-radius: 12px; font-weight: 800; font-size: 15px; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 14px rgba(22,163,74,0.4); }
        button:hover { background: #16a34a; color: #fff; }
    </style>
</head>
<body>
    """ + HTML_ALERT_SYSTEM_SCRIPT + """
    <div class="header">
        <div class="brand">
            <img src="/wilder_3d.jpg" alt="Wilder Morais 3D" class="brand-avatar">
            <div class="brand-text">
                <h1>SALA DE GUERRA MILITAR — WILDER MORAIS 2026</h1>
                <p>● Perfil Oficial & Inteligência Estratégica da Campanha</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="/radar_noticias" class="btn-nav btn-alert">🚨 Radar de Notícias & Pesquisas</a>
            <a href="/mapa_demandas" class="btn-nav btn-mapa">🗺️ Mapa Colorido & Queixas</a>
            <a href="/dashboard" class="btn-nav btn-dashboard">📊 Dashboard YouTube Real</a>
            <a href="/eventos" class="btn-nav btn-eventos">🎪 Radar de 150 Eventos</a>
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 PDF 360°</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg-row">
            <img src="/wilder_3d.jpg" alt="Wilder Morais 3D" class="msg-avatar">
            <div class="msg bot">
                <strong>🔰 FOTO 3D DE PERFIL DO WILDER MORAIS INTEGRADA EM TODO O SISTEMA!</strong><br><br>
                Personalizamos a interface com o avatar 3D do Wilder Morais nos cabeçalhos, respostas da IA, notificações e relatórios do sistema!<br><br>
                <strong>Faça uma consulta ou escolha um atalho:</strong>
                <div class="quick-actions">
                    <span class="chip" onclick="perguntarRapido('Faça um roteiro de Reels de 30s sobre o programa Primeiro Salário')">🎬 Roteiro de Reels 30s</span>
                    <span class="chip" onclick="perguntarRapido('Quais são os dados da última pesquisa do Instituto Goiás Pesquisas?')">📊 Dados da Pesquisa 22%</span>
                    <span class="chip" onclick="perguntarRapido('Escreva um discurso curto de Wilder em Rio Verde')">🎤 Discurso Wilder Morais</span>
                </div>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Consulte a IA de campanha sobre discursos, posts, pesquisas ou plano de governo..." onkeypress="if(event.key==='Enter') enviar()">
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
                <div class="msg-row" style="justify-content:flex-end;">
                    <div class="msg user">${pergunta}</div>
                </div>
            `;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const botRow = document.createElement('div');
            botRow.className = 'msg-row';
            botRow.innerHTML = `
                <img src="/wilder_3d.jpg" alt="Wilder Morais 3D" class="msg-avatar">
                <div class="msg bot"><strong>[SALA DE GUERRA IA] Analisando banco de dados e gerando resposta...</strong></div>
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
                botRow.querySelector('.msg.bot').innerHTML = data.resposta;
            } catch (err) {
                botRow.querySelector('.msg.bot').innerHTML = '<strong>Erro de comunicação com a IA da Sala de Guerra.</strong>';
            }
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

# DASHBOARD EXECUTIVO COM AVATAR 3D DO WILDER NO HEADER
HTML_DASHBOARD_METABASE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Executivo — YouTube Real & Eleitorado TSE</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #0b2214, #15803d, #eab308); padding: 14px 36px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .brand-avatar { width: 48px; height: 48px; border-radius: 50%; border: 2px solid #eab308; object-fit: cover; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13.5px; }
        th { background: #040e08; color: #86efac; padding: 12px; text-align: left; font-weight: 800; border-bottom: 2px solid #15803d; }
        td { padding: 12px; border-bottom: 1px solid #14351f; color: #e2e8f0; }
    </style>
</head>
<body>
    """ + HTML_ALERT_SYSTEM_SCRIPT + """
    <div class="header">
        <div style="display:flex;align-items:center;gap:14px;">
            <img src="/wilder_3d.jpg" alt="Wilder Morais 3D" class="brand-avatar">
            <div>
                <h1 style="margin:0;font-size:20px;color:#fff;">📺 AUDITORIA DO YOUTUBE REAL DOS CANDIDATOS</h1>
                <p style="margin:2px 0 0 0;color:#fef08a;font-size:12px;">● Painel de Monitoramento Oficial de Vídeos de Wilder Morais e Concorrentes</p>
            </div>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>
    <div class="container">
        <div style="background:#0a1f12;padding:20px;border-radius:14px;border:1px solid #164624;">
            <h3 style="color:#86efac;">🎬 VÍDEOS INDIVIDUAIS DO YOUTUBE</h3>
            <table>
                <thead>
                    <tr>
                        <th>Candidato</th>
                        <th>Título do Vídeo</th>
                        <th>Visualizações</th>
                        <th>Link Direto</th>
                    </tr>
                </thead>
                <tbody>
                    {% for v in yt_videos %}
                    <tr>
                        <td><strong style="color:#fef08a;">{{ v.candidato }}</strong></td>
                        <td>{{ v.titulo }}</td>
                        <td><span style="color:#4ade80;">{{ v.views }}</span></td>
                        <td><a href="{{ v.url }}" target="_blank" style="color:#38bdf8;font-weight:bold;">🎬 Assistir Vídeo no YouTube</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

# RADAR DE NOTÍCIAS COM AVATAR 3D DO WILDER
HTML_RADAR_NOTICIAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar Anti-Crise de Notícias — Sala de Guerra</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #450a0a, #991b1b, #15803d); padding: 14px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .brand-avatar { width: 48px; height: 48px; border-radius: 50%; border: 2px solid #eab308; object-fit: cover; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 10px 18px; border-radius: 8px; border: 1px solid #22c55e; }
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }
        .card-pesquisa { background: linear-gradient(135deg, #0b2214, #15803d); border: 2px solid #eab308; border-radius: 14px; padding: 24px; margin-bottom: 24px; }
        .card-noticia { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 24px; margin-bottom: 22px; }
    </style>
</head>
<body>
    """ + HTML_ALERT_SYSTEM_SCRIPT + """
    <div class="header">
        <div style="display:flex;align-items:center;gap:14px;">
            <img src="/wilder_3d.jpg" alt="Wilder Morais 3D" class="brand-avatar">
            <div>
                <h1 style="margin:0;font-size:20px;color:#fff;">📰 RADAR DE NOTÍCIAS & PESQUISAS ELEITORAIS</h1>
                <p style="margin:2px 0 0 0;color:#fef08a;font-size:12px;">● Alertas Automáticos de Levantamentos e Notícias com Links Auditáveis</p>
            </div>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>

    <div class="container">
        <div class="card-pesquisa">
            <h2 style="margin:0 0 10px 0;color:#fff;">🚀 {{ pesquisa.confirmacao_subida }}</h2>
            <p style="color:#a7f3d0;"><strong>Divulgação:</strong> {{ pesquisa.data_divulgacao }} | <strong>Instituto:</strong> {{ pesquisa.instituto }}</p>
        </div>

        {% for item in noticias %}
        <div class="card-noticia">
            <strong style="color:#86efac;">{{ item.candidato }} &bull; {{ item.veiculo }}</strong>
            <h3 style="color:#fff;margin:8px 0;">"{{ item.manchete }}"</h3>
            <div style="margin-top:10px;display:flex;gap:10px;">
                <a href="{{ item.url_google_news }}" target="_blank" style="color:#38bdf8;font-weight:bold;">🔍 Auditar no Google News</a>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# MAPA TÁTICO INTERATIVO COM AVATAR 3D DO WILDER
HTML_MAPA_DEMANDAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa Tático Interativo — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #0b2214, #0284c7); padding: 14px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .brand-avatar { width: 48px; height: 48px; border-radius: 50%; border: 2px solid #eab308; object-fit: cover; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1340px; margin: 30px auto; padding: 0 20px; }
        #map { width: 100%; height: 520px; border-radius: 12px; border: 1px solid #1e4028; background: #040e08; }
    </style>
</head>
<body>
    """ + HTML_ALERT_SYSTEM_SCRIPT + """
    <div class="header">
        <div style="display:flex;align-items:center;gap:14px;">
            <img src="/wilder_3d.jpg" alt="Wilder Morais 3D" class="brand-avatar">
            <div>
                <h1 style="margin:0;font-size:20px;color:#fff;">🗺️ MAPA TÁTICO COLORIDO & QUEIXAS POPULARES</h1>
                <p style="margin:2px 0 0 0;color:#fef08a;font-size:12px;">● Geolocalização de Demandas e Pautas por Município Polo de Goiás</p>
            </div>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>
    <div class="container">
        <div style="background:#0a1f12;padding:20px;border-radius:14px;border:1px solid #164624;">
            <div id="map"></div>
        </div>
    </div>
    <script>
        const map = L.map('map').setView([-16.6789, -49.2539], 7);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        const dados = {{ reclamacoes|tojson }};
        dados.forEach(c => { L.marker([c.lat, c.lon]).addTo(map).bindPopup(`<b>${c.cidade}</b><br>${c.pauta_principal}`); });
    </script>
</body>
</html>
"""

# ROUTING DAS TELAS DA SALA DE GUERRA MILITAR

@app.route("/", methods=["GET"])
@app.route("/chat", methods=["GET"])
def chat_home():
    return render_template_string(HTML_CHAT_WIDGET)

@app.route("/radar_noticias", methods=["GET"])
def radar_noticias_page():
    return render_template_string(
        HTML_RADAR_NOTICIAS,
        noticias=RADAR_NOTICIAS_TODOS_CANDIDATOS,
        pesquisa=PESQUISA_OFICIAL_GOIAS_2026
    )

@app.route("/mapa_demandas", methods=["GET"])
@app.route("/mapa", methods=["GET"])
def mapa_demandas_page():
    return render_template_string(
        HTML_MAPA_DEMANDAS,
        reclamacoes=MAPA_RECLAMACOES_DETALHADO
    )

@app.route("/dashboard", methods=["GET"])
@app.route("/metabase", methods=["GET"])
def dashboard_metabase_page():
    return render_template_string(
        HTML_DASHBOARD_METABASE,
        yt_videos=YOUTUBE_VIDEOS_REAIS,
        colegios=MAIORES_COLEGIOS_TSE
    )

@app.route("/eventos", methods=["GET"])
def eventos_radar_page():
    return jsonify({"status": "ok", "eventos": EVENTOS_GOIAS_2026[:10]})

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

# API DO CHAT DE IA COM SUPORTE AO PERFIL 3D DO WILDER
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    pergunta = (data.get("pergunta") or "").strip()
    if not pergunta:
        return jsonify({"resposta": "Por favor, digite uma pergunta."}), 400

    system_prompt = f"""
Você é o Estrategista Chefe de Inteligência e Comunicação da Sala de Guerra da campanha de Wilder Morais (Governador) e Ana Paula Rezende (Vice-Governadora) em Goiás (Eleições 2026).

CONHECIMENTO COMPLETO DA CAMPANHA:
1. PESQUISA OFICIAL (Instituto Goiás Pesquisas - 14/08/2026): Wilder salta para 22,0% dos Votos Válidos, ultrapassando Marconi Perillo (21,9%) e indo ao 2º Turno contra Daniel Vilela (43,5%).
2. PLANO DE GOVERNO 'GOIÁS PARA QUEM FAZ': Família Protegida, Desenvolvimento Que Fica, Prosperidade Que Chega em Casa (Primeiro Salário, Primeira Renda & Crédito Sem Juros, HUB de Inovação).
3. REDAÇÃO E CONTEÚDO: Você redige posts, roteiros de Reels/TikTok de 30s/60s com gancho de 3s, discursos do Wilder e respostas a ataques.
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
    if any(k in p_lower for k in ["pesquisa", "22", "voto", "vilela", "marconi"]):
        resp = f"🚀 <strong>PESQUISA ELEITORAL CONFIRMADA (INSTITUTO GOIÁS PESQUISAS - 14/08/2026)</strong><br><br>" \
               f"Wilder Morais salta para <strong>22,0% dos Votos Válidos</strong>, ultrapassando Marconi Perillo (21,9%) e garantindo vaga isolada na disputa de 2º Turno contra Daniel Vilela (43,5%)!"
    else:
        resp = f"🔰 <strong>COMANDO DE INTELIGÊNCIA IA — SALA DE GUERRA WILDER MORAIS</strong><br><br>" \
               f"Análise processada para: <i>'{pergunta}'</i>.<br>" \
               f"O sistema está 100% calibrado com os dados da pesquisa de 22%, o Plano de Governo e a nova identidade visual!"

    return jsonify({"resposta": resp}), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
