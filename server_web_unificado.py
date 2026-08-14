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
    PLANO_DE_GOVERNO_MEMORIA, PRIMEIRA_SEMANA_CONTEUDO,
    EVENTOS_GOIAS_2026
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
        .btn-mapa { background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; border-color: #38bdf8; font-weight: 800; }
        .btn-eventos { background: linear-gradient(135deg, #d97706, #b45309); color: #fff; border-color: #fef08a; font-weight: 800; }
        .btn-dashboard { background: linear-gradient(135deg, #eab308, #ca8a04); color: #040e08; border-color: #fef08a; font-weight: 800; }
        .btn-alert { background: #991b1b; border-color: #ef4444; color: #fecdd3; }
        .btn-pdf { background: linear-gradient(135deg, #15803d, #16a34a); border-color: #eab308; color: #fef08a; }
        
        .chat-box { flex: 1; padding: 24px 28px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; max-width: 1100px; margin: 0 auto; width: 100%; }
        .msg { max-width: 88%; padding: 18px 22px; border-radius: 14px; font-size: 14.5px; line-height: 1.6; }
        .user { background: linear-gradient(135deg, #15803d, #16a34a); color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 4px 14px rgba(22,163,74,0.3); border: 1px solid #22c55e; }
        .bot { background: #0a1f12; color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #164624; box-shadow: 0 6px 20px rgba(0,0,0,0.5); }
        .bot strong { color: #86efac; }

        .quick-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
        .chip { background: #0d2e19; border: 1px solid #22c55e; color: #fef08a; padding: 9px 16px; border-radius: 20px; font-size: 12.5px; font-weight: 700; cursor: pointer; transition: 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
        .chip:hover { background: #16a34a; color: #fff; border-color: #eab308; }
        .chip-mapa { background: #0369a1; border-color: #38bdf8; color: #fff; }
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
    <div class="header">
        <div class="brand">
            <div class="brand-logo">⚔️</div>
            <div class="brand-text">
                <h1>SALA DE GUERRA MILITAR — WILDER MORAIS 2026</h1>
                <p>● Mapa Colorido por Setor & Radar de Notícias de Todos os Candidatos com Links</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="/mapa_demandas" class="btn-nav btn-mapa">🗺️ Mapa Colorido & Queixas</a>
            <a href="/radar_noticias" class="btn-nav btn-alert">🚨 Radar de Notícias & Links</a>
            <a href="/dashboard" class="btn-nav btn-dashboard">📊 Dashboard YouTube Real</a>
            <a href="/eventos" class="btn-nav btn-eventos">🎪 Radar de 150 Eventos</a>
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 PDF 360°</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg bot">
            <strong>🔰 NOVO MAPA COLORIDO E RADAR DE NOTÍCIAS DE TODOS OS CANDIDATOS ATIVADO!</strong><br><br>
            Implementamos:<br>
            🎨 <strong>Mapa Colorido por Setor:</strong> Pinos coloridos em Leaflet.js para cada tipo de problema (🔴 Saúde, 🟠 Transporte, 🟢 Agro, 🔵 Emprego, 🟣 Hospital).<br>
            📰 <strong>Notícias de Wilder, Daniel Vilela e Marconi Perillo:</strong> Matérias positivas e críticas com <strong>links diretos para leitura nos portais</strong> (O Popular, Jornal Opção, Diário da Manhã, G1).<br><br>
            <strong>Escolha uma área de análise:</strong>
            <div class="quick-actions">
                <span class="chip chip-mapa" onclick="window.location.href='/mapa_demandas'">🗺️ Abrir Mapa Colorido por Setor</span>
                <span class="chip chip-alert" onclick="window.location.href='/radar_noticias'">📰 Notícias & Links de Todos os Candidatos</span>
                <span class="chip" onclick="window.location.href='/dashboard'">📺 Dashboard YouTube Real</span>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Digite (ex: 'notícias do daniel vilela', 'marconi perillo', 'mapa colorido')..." onkeypress="if(event.key==='Enter') enviar()">
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
            if (pLower.includes('noticia') || pLower.includes('notícia') || pLower.includes('daniel') || pLower.includes('marconi') || pLower.includes('wilder')) {
                window.location.href = '/radar_noticias';
                return;
            }
            if (pLower.includes('mapa') || pLower.includes('cor') || pLower.includes('cores') || pLower.includes('queixa')) {
                window.location.href = '/mapa_demandas';
                return;
            }

            chat.innerHTML += `<div class="msg user">${pergunta}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            botMsg.innerHTML = '<strong>[SALA DE GUERRA] Processando dados...</strong>';
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

# MAPA TÁTICO INTERATIVO COM PINOS COLORIDOS POR SETOR (RED, ORANGE, GREEN, BLUE, PURPLE)
HTML_MAPA_DEMANDAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa Colorido de Queixas por Setor — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        
        .header { background: linear-gradient(135deg, #0b2214, #0284c7, #15803d); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        
        .container { max-width: 1320px; margin: 30px auto; padding: 0 20px; }

        .legend-bar { background: #0a1f12; border: 1px solid #164624; border-radius: 12px; padding: 16px; margin-bottom: 20px; display: flex; gap: 16px; flex-wrap: wrap; align-items: center; }
        .legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; }
        .dot-red { width: 14px; height: 14px; background: #ef4444; border-radius: 50%; display: inline-block; }
        .dot-orange { width: 14px; height: 14px; background: #f97316; border-radius: 50%; display: inline-block; }
        .dot-green { width: 14px; height: 14px; background: #22c55e; border-radius: 50%; display: inline-block; }
        .dot-blue { width: 14px; height: 14px; background: #3b82f6; border-radius: 50%; display: inline-block; }
        .dot-purple { width: 14px; height: 14px; background: #a855f7; border-radius: 50%; display: inline-block; }

        .map-section { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 22px; margin-bottom: 24px; }
        .card-title { font-size: 17px; font-weight: 800; color: #86efac; margin-bottom: 16px; border-left: 5px solid #0284c7; padding-left: 10px; display: flex; justify-content: space-between; align-items: center; }

        #map { width: 100%; height: 540px; border-radius: 12px; border: 1px solid #1e4028; background: #040e08; }

        .leaflet-popup-content-wrapper { background: #040e08; color: #f8fafc; border: 1px solid #22c55e; border-radius: 10px; }
        .leaflet-popup-tip { background: #040e08; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🗺️ MAPA TÁTICO COLORIDO DE QUEIXAS POPULARES (GOIÁS)</h1>
            <p style="margin:4px 0 0 0;color:#fef08a;font-size:13px;">● Cores Diferenciadas por Tipo de Problema (Saúde, Transporte, Agro, Emprego, Hospital)</p>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>

    <div class="container">
        <!-- BARRA DE LEGENDA DAS CORES -->
        <div class="legend-bar">
            <span style="color:#fef08a;font-weight:800;font-size:14px;">🎨 LEGENDA DE CORES DO MAPA:</span>
            <div class="legend-item"><span class="dot-red"></span> 🔴 Saúde & Filas SUS</div>
            <div class="legend-item"><span class="dot-orange"></span> 🟠 Transporte & Asfalto</div>
            <div class="legend-item"><span class="dot-green"></span> 🟢 Logística Agro & Pontes</div>
            <div class="legend-item"><span class="dot-blue"></span> 🔵 Emprego Jovem & DAIA</div>
            <div class="legend-item"><span class="dot-purple"></span> 🟣 Hospital Regional & Turismo</div>
        </div>

        <!-- SEÇÃO DO MAPA INTERATIVO LEAFLET.JS -->
        <div class="map-section">
            <div class="card-title">
                <span>📍 MAPA DE GOIÁS COM PINOS COLORIDOS POR PAUTA (CLIQUE NOS PINOS)</span>
                <span style="font-size:12px;color:#38bdf8;font-weight:bold;">SALA DE GUERRA GIS</span>
            </div>
            <div id="map"></div>
        </div>
    </div>

    <script>
        const map = L.map('map').setView([-16.6789, -49.2539], 7);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: '© OpenStreetMap / Sala de Guerra Wilder Morais'
        }).addTo(map);

        const dadosCidades = {{ reclamacoes|tojson }};

        // ÍCONES COLORIDOS CUSTOMIZADOS DO LEAFLET.JS
        function getCustomIcon(color) {
            const colorHex = {
                'red': '#ef4444',
                'orange': '#f97316',
                'green': '#22c55e',
                'blue': '#3b82f6',
                'purple': '#a855f7'
            }[color] || '#22c55e';

            return L.divIcon({
                className: 'custom-pin',
                html: `<div style="background-color:${colorHex};width:22px;height:22px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 10px ${colorHex};"></div>`,
                iconSize: [22, 22],
                iconAnchor: [11, 11]
            });
        }

        dadosCidades.forEach(c => {
            const popupContent = `
                <div style="font-family:'Plus Jakarta Sans',sans-serif;padding:4px;">
                    <h3 style="margin:0 0 4px 0;color:#fef08a;font-size:15px;">📍 ${c.cidade} (${c.regiao})</h3>
                    <p style="margin:2px 0;color:#38bdf8;font-size:12px;"><strong>Pauta:</strong> ${c.cor_nome}</p>
                    <p style="margin:2px 0;color:#86efac;font-size:12px;"><strong>Eleitores TSE:</strong> ${c.eleitores}</p>
                    <p style="margin:4px 0;color:#f8fafc;font-size:12.5px;">${c.pauta_principal}</p>
                    <p style="margin:4px 0;color:#cbd5e1;font-size:12px;"><i>"${c.demanda_especifica}"</i></p>
                    <div style="margin-top:8px;background:#0c2415;padding:6px;border-radius:6px;border-left:3px solid #eab308;">
                        <strong style="color:#fef08a;font-size:11.5px;">🎥 Gancho de Vídeo 3s:</strong><br>
                        <span style="color:#fff;font-size:11.5px;">"${c.gancho_3s}"</span>
                    </div>
                </div>
            `;

            L.marker([c.lat, c.lon], { icon: getCustomIcon(c.cor) })
                .addTo(map)
                .bindPopup(popupContent);
        });
    </script>
</body>
</html>
"""

# RADAR DE NOTÍCIAS DE TODOS OS CANDIDATOS (WILDER, DANIEL VILELA, MARCONI) COM LINKS DIRETOS
HTML_RADAR_NOTICIAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar Anti-Crise de Notícias — Todos os Candidatos</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        
        .header { background: linear-gradient(135deg, #450a0a, #991b1b, #15803d); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 10px 18px; border-radius: 8px; border: 1px solid #22c55e; }
        
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }

        .card-noticia { background: #0a1f12; border: 1px solid #164624; border-radius: 12px; padding: 22px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .card-danger { border-color: #ef4444; background: #1a0808; }
        .card-pos { border-color: #22c55e; background: #081a0e; }

        .badge-cand { background: #1e3a8a; color: #bfdbfe; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; border: 1px solid #60a5fa; }
        .badge-pos { background: #15803d; color: #fef08a; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; }
        .badge-neu { background: #eab308; color: #000; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; }
        .badge-cri { background: #dc2626; color: #fff; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; }

        .btn-link-portal { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: 800; font-size: 13px; display: inline-block; margin-top: 10px; border: 1px solid #60a5fa; }
        .btn-link-portal:hover { background: #3b82f6; }

        .estrategia-box { background: #040e08; border-left: 4px solid #eab308; padding: 14px; margin-top: 14px; border-radius: 8px; font-size: 13.5px; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📰 RADAR DE NOTÍCIAS COMPLETO DOS CANDIDATOS (WILDER, DANIEL, MARCONI)</h1>
            <p style="margin:4px 0 0 0;color:#fef08a;font-size:13px;">● Varredura dos Maiores Portais (O Popular, Jornal Opção, Diário da Manhã, G1) com Links Diretos</p>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>

    <div class="container">
        {% for item in noticias %}
        <div class="card-noticia {% if 'POSITIVA' in item.tipo_noticia %}card-pos{% elif 'CRÍTICA' in item.tipo_noticia %}card-danger{% endif %}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span class="badge-cand">👤 {{ item.candidato }}</span>
                    <span style="font-weight: 800; color: #86efac; font-size: 15px;">📰 {{ item.veiculo }} &bull; <span style="color:#cbd5e1;font-size:13px;">{{ item.data }}</span></span>
                </div>
                <span>
                    {% if 'POSITIVA' in item.tipo_noticia %}
                    <span class="badge-pos">🟢 MATÉRIA POSITIVA</span>
                    {% elif 'CRÍTICA' in item.tipo_noticia %}
                    <span class="badge-cri">🔴 MATÉRIA CRÍTICA</span>
                    {% else %}
                    <span class="badge-neu">🟡 MATÉRIA NEUTRA</span>
                    {% endif %}
                </span>
            </div>
            
            <h3 style="margin: 0 0 8px 0; color: #fff; font-size: 18px;">"{{ item.manchete }}"</h3>
            
            <a href="{{ item.url_noticia }}" target="_blank" class="btn-link-portal">📰 Ler Matéria Completa no Portal Oficial (Link Direto)</a>
            
            <div class="estrategia-box">
                🛡️ <strong>ESTRATÉGIA DA SALA DE GUERRA / RESPOSTA DA IA:</strong><br>
                {{ item.estrategia_defesa }}
            </div>
        </div>
        {% endfor %}
    </div>
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
        .header { background: linear-gradient(135deg, #0b2214, #15803d, #eab308); padding: 18px 36px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13.5px; }
        th { background: #040e08; color: #86efac; padding: 12px; text-align: left; font-weight: 800; border-bottom: 2px solid #15803d; }
        td { padding: 12px; border-bottom: 1px solid #14351f; color: #e2e8f0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📺 AUDITORIA DO YOUTUBE REAL & MAIORES COLÉGIOS ELEITORAIS</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
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

# TELA DEDICADA DE EVENTOS
HTML_EVENTOS_RADAR = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar de Eventos — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #0b2214, #d97706); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎪 RADAR DE 150 EVENTOS POPULOSOS DE GOIÁS</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>
    <div class="container">
        {% for ev in eventos[:15] %}
        <div style="background:#040e08;border:1px solid #22c55e;padding:16px;border-radius:10px;margin-bottom:12px;">
            <h3 style="margin:0 0 4px 0;color:#fff;">{{ ev.evento }}</h3>
            <p style="margin:0;color:#cbd5e1;">🗓️ {{ ev.periodo_datas }} | 📍 {{ ev.local }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# ROUTING DAS TELAS DA SALA DE GUERRA MILITAR

@app.route("/", methods=["GET"])
@app.route("/chat", methods=["GET"])
def chat_home():
    return render_template_string(HTML_CHAT_WIDGET)

@app.route("/mapa_demandas", methods=["GET"])
@app.route("/mapa", methods=["GET"])
def mapa_demandas_page():
    return render_template_string(
        HTML_MAPA_DEMANDAS,
        reclamacoes=MAPA_RECLAMACOES_DETALHADO
    )

@app.route("/radar_noticias", methods=["GET"])
def radar_noticias_page():
    return render_template_string(
        HTML_RADAR_NOTICIAS,
        noticias=RADAR_NOTICIAS_TODOS_CANDIDATOS
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
    return render_template_string(HTML_EVENTOS_RADAR, eventos=EVENTOS_GOIAS_2026)

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

    # Roteador de Notícias
    if any(k in p_lower for k in ["noticia", "notícia", "noticias", "notícias", "daniel", "marconi", "wilder"]):
        return jsonify({
            "resposta": f"📰 <strong>RADAR DE NOTÍCIAS DOS CANDIDATOS (WILDER, DANIEL VILELA, MARCONI PERILLO)</strong><br><br>"
                        f"Mapeamos matérias positivas, neutras e críticas dos principais portais de Goiás com links diretos para leitura!<br><br>"
                        f"👉 <a href='/radar_noticias' style='background:#991b1b;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #ef4444;'>📰 ABRIR RADAR DE NOTÍCIAS COM LINKS DIRETOS</a>"
        }), 200

    # Roteador de Mapa Colorido
    if any(k in p_lower for k in ["mapa", "cor", "cores", "queixa", "cidade"]):
        return jsonify({
            "resposta": f"🗺️ <strong>MAPA COLORIDO POR SETOR DE RECLAMAÇÃO (LEAFLET.JS GIS)</strong><br><br>"
                        f"Pinos coloridos diferenciando cada tipo de problema (🔴 Saúde, 🟠 Transporte, 🟢 Agro, 🔵 Emprego, 🟣 Hospital) com dados do TSE!<br><br>"
                        f"👉 <a href='/mapa_demandas' style='background:linear-gradient(135deg, #0284c7, #0369a1);color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #38bdf8;'>🗺️ ABRIR MAPA COLORIDO INTERATIVO</a>"
        }), 200

    # Fallback via OpenRouter
    if OPENROUTER_API_KEY:
        system_prompt = (
            "Você é o Comando Central da Sala de Guerra da campanha de Wilder Morais em Goiás. "
            "Seu sistema agora possui Mapa Colorido em Leaflet.js (Vermelho=Saúde, Laranja=Transporte, Verde=Agro, Azul=Emprego, Roxo=Hospital) e Radar de Notícias cobrindo Wilder Morais, Daniel Vilela e Marconi Perillo com links diretos para os portais oficiais."
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
                    f"Mapa Colorido por Pauta e Notícias dos Candidatos com links operacionais.<br><br>"
                    f"👉 <a href='/mapa_demandas' style='background:#0284c7;color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:800;display:inline-block;'>🗺️ ABRIR MAPA COLORIDO</a>"
    }), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
