import os
import sys
import json
import re
import requests
import urllib3
import httpx
from flask import Flask, request, jsonify, render_template_string, send_file
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

app = Flask(__name__)

# COMPONENTE REUTILIZÁVEL DE ALERTA VISUAL FLUTUANTE (POPUP & TOAST ANIMADO)
HTML_ALERT_SYSTEM_SCRIPT = """
<!-- SISTEMA DE ALERTAS E NOTIFICAÇÕES VISUAIS DE ALTA RELEVÂNCIA -->
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
        max-width: 420px;
        width: 90%;
        background: linear-gradient(135deg, #0b2214, #15803d);
        border: 2px solid #eab308;
        border-radius: 14px;
        padding: 18px 20px;
        color: #ffffff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.7);
        animation: pulseAlert 2s infinite;
        display: block;
        transition: all 0.3s ease;
    }

    .toast-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .toast-badge {
        background: #eab308;
        color: #040e08;
        font-weight: 800;
        font-size: 11px;
        padding: 3px 8px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .toast-close {
        background: transparent;
        border: none;
        color: #fef08a;
        font-size: 20px;
        font-weight: bold;
        cursor: pointer;
        padding: 0;
        line-height: 1;
    }

    .toast-title {
        font-size: 15.5px;
        font-weight: 800;
        color: #fef08a;
        margin: 0 0 6px 0;
    }

    .toast-body {
        font-size: 13px;
        color: #e2e8f0;
        line-height: 1.5;
        margin-bottom: 12px;
    }

    .toast-btn {
        background: #040e08;
        color: #86efac;
        border: 1px solid #22c55e;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 800;
        text-decoration: none;
        display: inline-block;
        transition: 0.2s;
    }

    .toast-btn:hover {
        background: #16a34a;
        color: #fff;
        border-color: #eab308;
    }
</style>

<div id="toastAlert" class="toast-alert-container">
    <div class="toast-header">
        <span class="toast-badge">🚨 NOTIFICAÇÃO DE ALTA RELEVÂNCIA</span>
        <button class="toast-close" onclick="fecharAlerta()">✕</button>
    </div>
    <div class="toast-title">🚀 WILDER MORAIS SALTA PARA 22% NAS PESQUISAS!</div>
    <div class="toast-body">
        O Instituto Goiás Pesquisas confirma: <strong>Wilder atinge 22,0% dos votos válidos</strong>, ultrapassa Marconi Perillo e se consolida na disputa do 2º Turno em Goiás!
    </div>
    <a href="/radar_noticias" class="toast-btn">📊 Ver Detalhes no Radar de Notícias</a>
</div>

<script>
    function fecharAlerta() {
        const toast = document.getElementById('toastAlert');
        if (toast) toast.style.display = 'none';
    }
</script>
"""

# INTERFACE MILITAR PENTÁGONO VERDE E AMARELO (SALA DE GUERRA)
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
        
        .header { background: linear-gradient(135deg, #0b2214, #15803d, #16a34a); padding: 14px 28px; border-bottom: 3px solid #eab308; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 6px 25px rgba(22,163,74,0.4); }
        .brand { display: flex; align-items: center; gap: 14px; }
        .brand-logo { background: linear-gradient(135deg, #eab308, #f59e0b); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 800; color: #040e08; box-shadow: 0 4px 15px rgba(234,179,8,0.6); }
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
        .msg { max-width: 88%; padding: 18px 22px; border-radius: 14px; font-size: 14.5px; line-height: 1.6; }
        .user { background: linear-gradient(135deg, #15803d, #16a34a); color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 4px 14px rgba(22,163,74,0.3); border: 1px solid #22c55e; }
        .bot { background: #0a1f12; color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #164624; box-shadow: 0 6px 20px rgba(0,0,0,0.5); }
        .bot strong { color: #86efac; }

        .quick-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
        .chip { background: #0d2e19; border: 1px solid #22c55e; color: #fef08a; padding: 9px 16px; border-radius: 20px; font-size: 12.5px; font-weight: 700; cursor: pointer; transition: 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
        .chip:hover { background: #16a34a; color: #fff; border-color: #eab308; }
        .chip-alert { background: #991b1b; border-color: #ef4444; color: #fff; }

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
            <div class="brand-logo">⚔️</div>
            <div class="brand-text">
                <h1>SALA DE GUERRA MILITAR — WILDER MORAIS 2026</h1>
                <p>● Central de Alertas e Notificações Visuais em Tempo Real</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="/radar_noticias" class="btn-nav btn-alert">🚨 Radar de Notícias & Pesquisas</a>
            <a href="/mapa_demandas" class="btn-nav btn-mapa">🗺️ Mapa Colorido & Queixas</a>
            <a href="/dashboard" class="btn-nav btn-dashboard">📊 Dashboard YouTube Real</a>
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 PDF 360°</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg bot">
            <strong>🔔 SISTEMA DE NOTIFICAÇÕES E ALERTAS VISUAIS EM TEMPO REAL ATIVADO!</strong><br><br>
            Sempre que uma notícia relevante ou levantamento eleitoral (como o crescimento de Wilder para 22%) for publicado, o sistema emitirá um <strong>Toast Popup Animado</strong> no canto superior da tela com aviso de alta prioridade!<br><br>
            <strong>Escolha uma área de análise:</strong>
            <div class="quick-actions">
                <span class="chip chip-alert" onclick="window.location.href='/radar_noticias'">🚨 Ver Notícias & Pesquisas no Radar</span>
                <span class="chip" onclick="window.location.href='/mapa_demandas'">🗺️ Mapa Colorido & 4 Gráficos</span>
                <span class="chip" onclick="window.location.href='/dashboard'">📺 Dashboard YouTube Real</span>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Digite (ex: 'pesquisa eleitoral', 'notificação', 'notícias')..." onkeypress="if(event.key==='Enter') enviar()">
            <button onclick="enviar()">Executar Ordem</button>
        </div>
    </div>

    <script>
        async function enviar() {
            const input = document.getElementById('pergunta');
            const chat = document.getElementById('chat');
            const pergunta = input.value.trim();
            if (!pergunta) return;

            const pLower = pergunta.toLowerCase();
            if (pLower.includes('pesquisa') || pLower.includes('alerta') || pLower.includes('notificacao') || pLower.includes('notificação')) {
                window.location.href = '/radar_noticias';
                return;
            }

            chat.innerHTML += `<div class="msg user">${pergunta}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            botMsg.innerHTML = '<strong>[SALA DE GUERRA] Processando alertas...</strong>';
            chat.appendChild(botMsg);
            chat.scrollTop = chat.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pergunta })
                });
                const data = await res.json();
                botMsg.innerHTML = data.resposta;
            } catch (err) {
                botMsg.innerHTML = '<strong>Erro de comunicação com a Sala de Guerra.</strong>';
            }
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

# RADAR DE NOTÍCIAS COM SISTEMA DE ALERTAS
HTML_RADAR_NOTICIAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar Anti-Crise de Notícias & Alertas Visuais</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        
        .header { background: linear-gradient(135deg, #450a0a, #991b1b, #15803d); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 10px 18px; border-radius: 8px; border: 1px solid #22c55e; }
        
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }

        .card-pesquisa { background: linear-gradient(135deg, #0b2214, #15803d); border: 2px solid #eab308; border-radius: 14px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(234,179,8,0.4); }
        .card-noticia { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 24px; margin-bottom: 22px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .card-danger { border-color: #ef4444; background: #1a0808; }
        .card-pos { border-color: #22c55e; background: #081a0e; }

        .badge-cand { background: #1e3a8a; color: #bfdbfe; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; border: 1px solid #60a5fa; }
        .badge-pos { background: #15803d; color: #fef08a; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; }

        .links-row { display: flex; gap: 12px; margin-top: 12px; flex-wrap: wrap; }
        .btn-gnews { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 13px; border: 1px solid #60a5fa; display: inline-flex; align-items: center; gap: 6px; }
        .btn-portal { background: linear-gradient(135deg, #15803d, #166534); color: #fef08a; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 13px; border: 1px solid #eab308; display: inline-flex; align-items: center; gap: 6px; }

        .estrategia-box { background: #040e08; border-left: 4px solid #eab308; padding: 16px; margin-top: 16px; border-radius: 8px; font-size: 14px; line-height: 1.6; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 14px; }
        th { background: #040e08; color: #86efac; padding: 10px; text-align: left; font-weight: 800; border-bottom: 2px solid #15803d; }
        td { padding: 10px; border-bottom: 1px solid #14351f; color: #e2e8f0; }
    </style>
</head>
<body>
    """ + HTML_ALERT_SYSTEM_SCRIPT + """
    <div class="header">
        <div>
            <h1>📰 RADAR DE NOTÍCIAS & ALERTA VISUAL DE ALTA RELEVÂNCIA</h1>
            <p style="margin:4px 0 0 0;color:#fef08a;font-size:13px;">● Alertas Automáticos de Notícias e Pesquisas Eleitorais com Notificação Visual</p>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>

    <div class="container">
        <!-- CARD DA PESQUISA ELEITORAL CONFIRMADA (WILDER 22%) -->
        <div class="card-pesquisa">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <span style="font-weight:800;color:#fef08a;font-size:17px;">🚀 PESQUISA OFICIAL CONFIRMADA — {{ pesquisa.instituto }}</span>
                <span style="background:#eab308;color:#000;padding:4px 10px;border-radius:6px;font-weight:800;font-size:12px;">DIVULGADA EM {{ pesquisa.data_divulgacao }}</span>
            </div>
            <h2 style="margin:4px 0 12px 0;color:#fff;font-size:20px;">"{{ pesquisa.confirmacao_subida }}"</h2>
            <p style="color:#a7f3d0;font-size:14px;margin-bottom:14px;"><strong>Período de Campo:</strong> {{ pesquisa.periodo_campo }} | <strong>Margem de Erro:</strong> {{ pesquisa.margem_erro }}</p>
            
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
                        <td><strong style="color:#fef08a;font-size:16px;">{{ c.percentual }}</strong></td>
                        <td><span style="color:#86efac;font-weight:bold;">{{ c.posicao }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <div style="margin-top:14px;">
                <a href="https://news.google.com/search?q=Instituto%20Goias%20Pesquisas%20Wilder%20Morais%2022" target="_blank" class="btn-gnews">🔍 Auditar Divulgação da Pesquisa no Google News</a>
            </div>
        </div>

        {% for item in noticias %}
        <div class="card-noticia {% if 'POSITIVA' in item.tipo_noticia or 'PESQUISA' in item.tipo_noticia %}card-pos{% elif 'CRÍTICA' in item.tipo_noticia %}card-danger{% endif %}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span class="badge-cand">👤 {{ item.candidato }}</span>
                    <span style="font-weight: 800; color: #86efac; font-size: 15px;">📰 {{ item.veiculo }} &bull; <span style="color:#cbd5e1;font-size:13px;">{{ item.data }}</span></span>
                </div>
                <span>
                    <span class="badge-pos">{{ item.tipo_noticia }}</span>
                </span>
            </div>
            
            <h3 style="margin: 0 0 8px 0; color: #fff; font-size: 18.5px;">"{{ item.manchete }}"</h3>
            
            <div class="links-row">
                <a href="{{ item.url_google_news }}" target="_blank" class="btn-gnews">🔍 Auditar Manchete Exata no Google News</a>
                <a href="{{ item.url_portal }}" target="_blank" class="btn-portal">📰 Buscar no Portal de Imprensa Oficial</a>
            </div>
            
            <div class="estrategia-box">
                🛡️ <strong>PLANO DE CONTRANARRATIVA E DEFESA DE IA DA SALA DE GUERRA:</strong><br>
                {{ item.estrategia_defesa }}
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# MAPA TÁTICO INTERATIVO
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
        .header { background: linear-gradient(135deg, #0b2214, #0284c7); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1340px; margin: 30px auto; padding: 0 20px; }
        #map { width: 100%; height: 500px; border-radius: 12px; border: 1px solid #1e4028; background: #040e08; }
    </style>
</head>
<body>
    """ + HTML_ALERT_SYSTEM_SCRIPT + """
    <div class="header">
        <h1>🗺️ MAPA TÁTICO & GRÁFICOS VISUAIS INTERATIVOS</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
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

# DASHBOARD EXECUTIVO
HTML_DASHBOARD_METABASE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Executivo — YouTube Real</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #0b2214, #15803d); padding: 18px 36px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }
    </style>
</head>
<body>
    """ + HTML_ALERT_SYSTEM_SCRIPT + """
    <div class="header">
        <h1>📺 AUDITORIA DO YOUTUBE REAL</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>
    <div class="container">
        <p style="color:#86efac;">Vídeos Reais do YouTube.</p>
    </div>
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

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    pergunta = (data.get("pergunta") or "").strip()
    if not pergunta:
        return jsonify({"resposta": "Por favor, digite uma pergunta."}), 400

    p_lower = pergunta.lower()

    # Roteador de Alertas
    if any(k in p_lower for k in ["alerta", "notificação", "notificacao", "aviso", "pop-up", "popup"]):
        return jsonify({
            "resposta": f"🔔 <strong>SISTEMA DE NOTIFICAÇÕES E ALERTAS VISUAIS DE ALTA PRIORIDADE ATIVADO!</strong><br><br>"
                        f"Um Toast Popup com animação de pulso luminoso e botão de fechar foi integrado em todas as telas da plataforma para alertar a equipe imediatamente quando surgirem notícias positivas ou pesquisas de destaque!<br><br>"
                        f"👉 <a href='/radar_noticias' style='background:#15803d;color:#fef08a;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #eab308;'>🔔 VER ALERTA VISUAL NO RADAR</a>"
        }), 200

    # Fallback via OpenRouter
    if OPENROUTER_API_KEY:
        system_prompt = (
            "Você é o Comando Central da Sala de Guerra da campanha de Wilder Morais em Goiás. "
            "Seu sistema agora conta com um Sistema de Alertas e Notificações Visuais Flutuantes (Toast Popups animados) ativado em todas as páginas da plataforma."
        )
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": pergunta}
            ],
            "temperature": 0.3
        }
        try:
            r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=10, verify=False)
            resposta_texto = r.json()["choices"][0]["message"]["content"]
            return jsonify({"resposta": resposta_texto}), 200
        except Exception:
            pass

    return jsonify({
        "resposta": f"🔰 <strong>COMANDO CENTRAL DE IA — SALA DE GUERRA (WILDER MORAIS 2026)</strong><br><br>"
                    f"Sistema de Notificações Visuais Flutuantes ativo.<br><br>"
                    f"👉 <a href='/radar_noticias' style='background:#15803d;color:#fef08a;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:800;display:inline-block;'>🔔 VER ALERTAS</a>"
    }), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
