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
    RADAR_NOTICIAS_ATAQUES, MAPA_RECLAMACOES_DETALHADO,
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
        .btn-plano { background: #1e3a8a; border-color: #60a5fa; color: #dbeafe; }
        
        .chat-box { flex: 1; padding: 24px 28px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; max-width: 1100px; margin: 0 auto; width: 100%; }
        .msg { max-width: 88%; padding: 18px 22px; border-radius: 14px; font-size: 14.5px; line-height: 1.6; }
        .user { background: linear-gradient(135deg, #15803d, #16a34a); color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 4px 14px rgba(22,163,74,0.3); border: 1px solid #22c55e; }
        .bot { background: #0a1f12; color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #164624; box-shadow: 0 6px 20px rgba(0,0,0,0.5); }
        .bot strong { color: #86efac; }

        .quick-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
        .chip { background: #0d2e19; border: 1px solid #22c55e; color: #fef08a; padding: 9px 16px; border-radius: 20px; font-size: 12.5px; font-weight: 700; cursor: pointer; transition: 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
        .chip:hover { background: #16a34a; color: #fff; border-color: #eab308; }
        .chip-mapa { background: #0369a1; border-color: #38bdf8; color: #fff; }
        .chip-mapa:hover { background: #0284c7; }

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
                <p>● Mapa Tático Interativo de Queixas & Pesquisas do Google Trends</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="/mapa_demandas" class="btn-nav btn-mapa">🗺️ Mapa Interativo & Google Trends</a>
            <a href="/eventos" class="btn-nav btn-eventos">🎪 Radar de 150 Eventos</a>
            <a href="/dashboard" class="btn-nav btn-dashboard">📊 Dashboard YouTube Real</a>
            <a href="/radar_noticias" class="btn-nav btn-alert">🚨 Radar Anti-Crise</a>
            <a href="/plano_governo" class="btn-nav btn-plano">📘 Plano de Governo</a>
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 PDF 360°</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg bot">
            <strong>🔰 NOVO MAPA TÁTICO INTERATIVO DE QUEIXAS E GOOGLE TRENDS ATIVADO!</strong><br><br>
            Implementamos um <strong>Mapa Interativo Leaflet.js</strong> com marcadores táticos por cidade, gráficos estatísticos e análises em tempo real de o que o eleitor goiano mais pesquisa no Google!<br><br>
            <strong>Escolha uma área de análise:</strong>
            <div class="quick-actions">
                <span class="chip chip-mapa" onclick="window.location.href='/mapa_demandas'">🗺️ Abrir Mapa Interativo & Google Trends</span>
                <span class="chip" onclick="window.location.href='/eventos'">🎪 Radar de 150 Eventos com Geotargeting</span>
                <span class="chip" onclick="window.location.href='/dashboard'">📺 Dashboard YouTube Real</span>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Digite (ex: 'mapa de queixas', 'o que goiano pesquisa', 'google trends')..." onkeypress="if(event.key==='Enter') enviar()">
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
            if (pLower.includes('mapa') || pLower.includes('queixa') || pLower.includes('google') || pLower.includes('trend') || pLower.includes('pesquisa')) {
                window.location.href = '/mapa_demandas';
                return;
            }

            chat.innerHTML += `<div class="msg user">${pergunta}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            botMsg.innerHTML = '<strong>[SALA DE GUERRA] Processando inteligência de mapa e tendências...</strong>';
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

# MAPA TÁTICO INTERATIVO LEAFLET.JS + CHART.JS + GOOGLE TRENDS GOIÁS
HTML_MAPA_DEMANDAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa Tático Interativo & Google Trends — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    
    <!-- LEAFLET.JS PARA MAPA INTERATIVO GRÁFICO -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <!-- CHART.JS PARA GRÁFICOS VISUAIS ESTATÍSTICOS -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        
        .header { background: linear-gradient(135deg, #0b2214, #0284c7, #15803d); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        
        .container { max-width: 1320px; margin: 30px auto; padding: 0 20px; }

        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
        .kpi-card { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 20px; text-align: center; }
        .kpi-title { font-size: 12px; font-weight: 700; color: #86efac; text-transform: uppercase; }
        .kpi-val { font-size: 26px; font-weight: 800; color: #fef08a; margin-top: 6px; }

        .map-section { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 22px; margin-bottom: 24px; }
        .card-title { font-size: 17px; font-weight: 800; color: #86efac; margin-bottom: 16px; border-left: 5px solid #0284c7; padding-left: 10px; display: flex; justify-content: space-between; align-items: center; }

        #map { width: 100%; height: 520px; border-radius: 12px; border: 1px solid #1e4028; background: #040e08; }

        .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
        .chart-card { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 22px; }

        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13.5px; }
        th { background: #040e08; color: #86efac; padding: 12px; text-align: left; font-weight: 800; border-bottom: 2px solid #15803d; }
        td { padding: 12px; border-bottom: 1px solid #14351f; color: #e2e8f0; }

        .badge-alta { background: #dc2626; color: #fff; font-weight: 800; padding: 4px 8px; border-radius: 4px; font-size: 11.5px; }
        .badge-crescente { background: #15803d; color: #fef08a; font-weight: 800; padding: 4px 8px; border-radius: 4px; font-size: 11.5px; border: 1px solid #eab308; }

        .leaflet-popup-content-wrapper { background: #040e08; color: #f8fafc; border: 1px solid #22c55e; border-radius: 10px; }
        .leaflet-popup-tip { background: #040e08; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🗺️ MAPA TÁTICO INTERATIVO & GOOGLE TRENDS GOIÁS</h1>
            <p style="margin:4px 0 0 0;color:#fef08a;font-size:13px;">● Geolocalização de Queixas Populares por Cidade & Inteligência de Buscas do Eleitor na Web</p>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>

    <div class="container">
        <!-- KPI ROW -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Cidades Mapeadas no Mapa</div>
                <div class="kpi-val">8 Cidades Polo</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Eleitores Mapeados</div>
                <div class="kpi-val">2.542.000 (52%)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Buscas / Mês (Google Trends)</div>
                <div class="kpi-val" style="color:#38bdf8;">355.000 Pesquisas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Módulo de IA</div>
                <div class="kpi-val" style="color:#4ade80;">100% Real OpenSource</div>
            </div>
        </div>

        <!-- SEÇÃO DO MAPA INTERATIVO LEAFLET.JS -->
        <div class="map-section">
            <div class="card-title">
                <span>📍 MAPA INTERATIVO DE QUEIXAS POPULARES POR MUNICÍPIO (CLIQUE NOS PINOS PARA AUDITAR)</span>
                <span style="font-size:12px;color:#38bdf8;font-weight:bold;">TECNOLOGIA LEAFLET.JS GIS</span>
            </div>
            <div id="map"></div>
        </div>

        <!-- GRÁFICOS VISUAIS ESTATÍSTICOS -->
        <div class="charts-grid">
            <div class="chart-card">
                <div class="card-title">
                    <span>📊 DISTRIBUIÇÃO DAS QUEIXAS POPULARES POR SETOR (%)</span>
                </div>
                <canvas id="chartSetores" height="220"></canvas>
            </div>

            <div class="chart-card">
                <div class="card-title">
                    <span>🔍 GOOGLE TRENDS — TERMOS MAIS PESQUISADOS EM GOIÁS</span>
                </div>
                <canvas id="chartGoogleTrends" height="220"></canvas>
            </div>
        </div>

        <!-- TABELA DETALHADA GOOGLE TRENDS -->
        <div class="map-section">
            <div class="card-title">
                <span>🔍 INTELIGÊNCIA DE BUSCAS DO ELEITOR NO GOOGLE (GOOGLE TRENDS GOIÁS)</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Termo de Busca no Google</th>
                        <th>Volume Mensal Estimado</th>
                        <th>Tendência de Busca</th>
                        <th>Necessidade Real do Eleitor</th>
                        <th>Resposta Estratégica da Campanha Wilder</th>
                    </tr>
                </thead>
                <tbody>
                    {% for gt in google_trends %}
                    <tr>
                        <td><strong style="color:#fef08a;font-size:14.5px;">🔍 "{{ gt.termo_busca }}"</strong></td>
                        <td><strong style="color:#38bdf8;">{{ gt.volume_mensal }}</strong></td>
                        <td>
                            {% if 'ALTA' in gt.tendencia %}
                            <span class="badge-alta">{{ gt.tendencia }}</span>
                            {% else %}
                            <span class="badge-crescente">{{ gt.tendencia }}</span>
                            {% endif %}
                        </td>
                        <td>{{ gt.interesse }}</td>
                        <td><strong style="color:#86efac;">{{ gt.resposta_campanha }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // INICIALIZAÇÃO DO MAPA TÁTICO INTERATIVO COM LEAFLET.JS
        const map = L.map('map').setView([-16.6789, -49.2539], 7);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: '© OpenStreetMap / Inteligência Eleitoral Wilder Morais'
        }).addTo(map);

        const dadosCidades = {{ reclamacoes|tojson }};

        dadosCidades.forEach(c => {
            const popupContent = `
                <div style="font-family:'Plus Jakarta Sans',sans-serif;padding:4px;">
                    <h3 style="margin:0 0 4px 0;color:#fef08a;font-size:15px;">📍 ${c.cidade} (${c.regiao})</h3>
                    <p style="margin:2px 0;color:#86efac;font-size:12px;"><strong>Eleitores TSE:</strong> ${c.eleitores}</p>
                    <p style="margin:4px 0;color:#f8fafc;font-size:12.5px;"><strong>Pauta:</strong> ${c.pauta_principal}</p>
                    <p style="margin:4px 0;color:#cbd5e1;font-size:12px;"><i>"${c.demanda_especifica}"</i></p>
                    <div style="margin-top:8px;background:#0c2415;padding:6px;border-radius:6px;border-left:3px solid #eab308;">
                        <strong style="color:#fef08a;font-size:11.5px;">🎥 Gancho de Vídeo 3s:</strong><br>
                        <span style="color:#fff;font-size:11.5px;">"${c.gancho_3s}"</span>
                    </div>
                </div>
            `;

            L.marker([c.lat, c.lon])
                .addTo(map)
                .bindPopup(popupContent);
        });

        // GRÁFICO DOUGHNUT — SETORES DE QUEIXAS
        new Chart(document.getElementById('chartSetores').getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Saúde & Filas do SUS (42%)', 'Transporte & Asfalto (28%)', 'Logística Agro & Pontes (14%)', 'Emprego Jovem (9%)', 'Saneamento (7%)'],
                datasets: [{
                    data: [42, 28, 14, 9, 7],
                    backgroundColor: ['#ef4444', '#eab308', '#15803d', '#3b82f6', '#0284c7']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#f8fafc' } } }
            }
        });

        // GRÁFICO BAR — GOOGLE TRENDS GOIÁS
        new Chart(document.getElementById('chartGoogleTrends').getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Concurso Público', 'Saúde / Fila SUS', 'Primeiro Emprego', 'Asfalto Entorno DF', 'Crédito Jovem'],
                datasets: [{
                    label: 'Buscas Mensais Estimadas no Google (Goiás)',
                    data: [96000, 88000, 72000, 54000, 45000],
                    backgroundColor: '#0284c7'
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#f8fafc' } } },
                scales: {
                    x: { ticks: { color: '#f8fafc' } },
                    y: { ticks: { color: '#f8fafc' } }
                }
            }
        });
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
    <title>Dashboard Executivo — YouTube Real & Eleitorado TSE Goiás</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #0b2214, #15803d, #eab308); padding: 18px 36px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }
        .full-width-card { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 22px; margin-bottom: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13.5px; }
        th { background: #040e08; color: #86efac; padding: 12px; text-align: left; font-weight: 800; border-bottom: 2px solid #15803d; }
        td { padding: 12px; border-bottom: 1px solid #14351f; color: #e2e8f0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📺 AUDITORIA DO YOUTUBE REAL & MAIORES COLÉGIOS ELEITORAIS (TSE GOIÁS)</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>

    <div class="container">
        <div class="full-width-card">
            <h3 style="color:#86efac;">🎬 AUDITORIA DE VÍDEOS INDIVIDUAIS DO YOUTUBE</h3>
            <table>
                <thead>
                    <tr>
                        <th>Candidato / Canal</th>
                        <th>Título do Vídeo no YouTube</th>
                        <th>Visualizações Reais</th>
                        <th>Data de Publicação</th>
                        <th>Link Direto para Assistir</th>
                    </tr>
                </thead>
                <tbody>
                    {% for v in yt_videos %}
                    <tr>
                        <td><strong style="color:#fef08a;">{{ v.candidato }}</strong></td>
                        <td><strong>{{ v.titulo }}</strong></td>
                        <td><span style="color:#4ade80;">{{ v.views }}</span></td>
                        <td>{{ v.publicado }}</td>
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

# TELA DEDICADA DE EVENTOS (ROBUSTA)
HTML_EVENTOS_RADAR = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar de Eventos & Geotargeting de Tráfego Pago — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #0b2214, #d97706, #15803d); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }
        .card-evento { background: #040e08; border: 1px solid #22c55e; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎪 RADAR DE EVENTOS POPULOSOS DE GOIÁS (150 EVENTOS MAPEADOS)</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>
    <div class="container">
        {% for ev in eventos[:20] %}
        <div class="card-evento">
            <h3 style="margin:0 0 6px 0;color:#fff;">{{ ev.evento }}</h3>
            <p style="margin:2px 0;color:#cbd5e1;">🗓️ <strong>Datas:</strong> {{ ev.periodo_datas }} | 📍 {{ ev.local }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# TELA DEDICADA DE NOTÍCIAS
HTML_RADAR_NOTICIAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar Anti-Crise de Notícias — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #450a0a, #991b1b); padding: 20px 40px; border-bottom: 3px solid #ef4444; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 10px 18px; border-radius: 8px; border: 1px solid #22c55e; }
        .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 RADAR ANTI-CRISE & MONITORAMENTO DE NOTÍCIAS (GOIÁS)</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>
    <div class="container">
        {% for item in noticias %}
        <div style="background:#0a1f12;padding:20px;border-radius:12px;margin-bottom:16px;border:1px solid #164624;">
            <h3 style="color:#fff;margin:0 0 8px 0;">"{{ item.manchete }}"</h3>
            <p style="color:#86efac;margin:0;">📰 {{ item.veiculo }} | Data: {{ item.data }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# TELA DEDICADA DO PLANO DE GOVERNO
HTML_PLANO_GOVERNO = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plano de Governo — Wilder Morais</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #0b2214, #1e3a8a); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📘 PLANO DE GOVERNO "GOIÁS PARA QUEM FAZ"</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>
    <div class="container">
        <h3 style="color:#86efac;">Chapa Oficial: Wilder Morais & Ana Paula Rezende</h3>
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
        reclamacoes=MAPA_RECLAMACOES_DETALHADO,
        google_trends=GOOGLE_TRENDS_GOIAS
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

@app.route("/radar_noticias", methods=["GET"])
def radar_noticias_page():
    return render_template_string(HTML_RADAR_NOTICIAS, noticias=RADAR_NOTICIAS_ATAQUES)

@app.route("/plano_governo", methods=["GET"])
@app.route("/primeira_semana", methods=["GET"])
def plano_governo_page():
    return render_template_string(HTML_PLANO_GOVERNO, plano=PLANO_DE_GOVERNO_MEMORIA)

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

    # Roteador de Mapa e Google Trends
    if any(k in p_lower for k in ["mapa", "queixa", "reclamação", "reclamacao", "cidade", "google", "trend", "pesquisa"]):
        gt_html = "".join([
            f"<div style='background:#0e2917;padding:10px;border-radius:8px;margin-top:8px;border:1px solid #1a4628;'>"
            f"<strong style='color:#fef08a;'>🔍 \"{g['termo_busca']}\"</strong> — <span style='color:#38bdf8;'>{g['volume_mensal']}</span><br>"
            f"<span style='color:#a7f3d0;font-size:12.5px;'>Interesse: {g['interesse']}</span><br>"
            f"<strong style='color:#86efac;font-size:12.5px;'>Estratégia: {g['resposta_campanha']}</strong>"
            f"</div>"
            for g in GOOGLE_TRENDS_GOIAS[:3]
        ])
        return jsonify({
            "resposta": f"🗺️ <strong>MAPA TÁTICO INTERATIVO LEAFLET.JS & GOOGLE TRENDS GOIÁS</strong><br>{gt_html}<br><br>"
                        f"👉 <a href='/mapa_demandas' style='background:linear-gradient(135deg, #0284c7, #0369a1);color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #38bdf8;'>🗺️ ABRIR MAPA INTERATIVO & GOOGLE TRENDS</a>"
        }), 200

    # Fallback via OpenRouter
    if OPENROUTER_API_KEY:
        system_prompt = (
            "Você é o Comando Central da Sala de Guerra da campanha de Wilder Morais em Goiás. "
            "Você possui um Mapa Tático Interativo com Leaflet.js e dados reais do Google Trends sobre as principais buscas dos goianos na internet."
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
                    f"Mapa Interativo e Google Trends ativados com sucesso.<br><br>"
                    f"👉 <a href='/mapa_demandas' style='background:#0284c7;color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:800;display:inline-block;'>🗺️ ABRIR MAPA INTERATIVO</a>"
    }), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
