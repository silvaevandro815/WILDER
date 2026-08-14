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
                <p>● Central Unificada de Inteligência Eleitoral, Notícias & YouTube Real</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="/mapa_demandas" class="btn-nav btn-mapa">🗺️ Mapa & Gráficos Interativos</a>
            <a href="/radar_noticias" class="btn-nav btn-alert">🚨 Radar de Notícias & Links</a>
            <a href="/dashboard" class="btn-nav btn-dashboard">📊 Dashboard YouTube Real</a>
            <a href="/eventos" class="btn-nav btn-eventos">🎪 Radar de 150 Eventos</a>
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 PDF 360°</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg bot">
            <strong>🔰 MAPA INTERATIVO E GRÁFICOS VISUAIS DE QUEIXAS E BUSCAS ATIVADOS!</strong><br><br>
            Implementamos o <strong>Mapa Colorido por Pauta</strong> e <strong>3 Gráficos Visuais Interativos</strong> diretamente abaixo do mapa para analisar em detalhes os locais de queixas e buscas no Google!<br><br>
            <strong>Escolha uma área de análise:</strong>
            <div class="quick-actions">
                <span class="chip chip-mapa" onclick="window.location.href='/mapa_demandas'">🗺️ Abrir Mapa & Gráficos Interativos</span>
                <span class="chip" onclick="window.location.href='/radar_noticias'">📰 Notícias & Links dos Candidatos</span>
                <span class="chip" onclick="window.location.href='/dashboard'">📺 Dashboard YouTube Real</span>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Digite (ex: 'mapa', 'gráficos', 'queixas por cidade')..." onkeypress="if(event.key==='Enter') enviar()">
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
            if (pLower.includes('mapa') || pLower.includes('grafico') || pLower.includes('gráfico') || pLower.includes('queixa')) {
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

# MAPA TÁTICO INTERATIVO LEAFLET.JS + 3 GRÁFICOS VISUAIS IMPRESSIONANTES (CHART.JS)
HTML_MAPA_DEMANDAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa Tático Interativo & Gráficos de Queixas — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        
        .header { background: linear-gradient(135deg, #0b2214, #0284c7, #15803d); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        
        .container { max-width: 1340px; margin: 30px auto; padding: 0 20px; }

        .legend-bar { background: #0a1f12; border: 1px solid #164624; border-radius: 12px; padding: 16px; margin-bottom: 20px; display: flex; gap: 16px; flex-wrap: wrap; align-items: center; }
        .legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; }
        .dot-red { width: 14px; height: 14px; background: #ef4444; border-radius: 50%; display: inline-block; }
        .dot-orange { width: 14px; height: 14px; background: #f97316; border-radius: 50%; display: inline-block; }
        .dot-green { width: 14px; height: 14px; background: #22c55e; border-radius: 50%; display: inline-block; }
        .dot-blue { width: 14px; height: 14px; background: #3b82f6; border-radius: 50%; display: inline-block; }
        .dot-purple { width: 14px; height: 14px; background: #a855f7; border-radius: 50%; display: inline-block; }

        .map-section { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 22px; margin-bottom: 24px; }
        .card-title { font-size: 17px; font-weight: 800; color: #86efac; margin-bottom: 16px; border-left: 5px solid #0284c7; padding-left: 10px; display: flex; justify-content: space-between; align-items: center; }

        #map { width: 100%; height: 520px; border-radius: 12px; border: 1px solid #1e4028; background: #040e08; }

        /* GRÁFICOS DETALHADOS EMBAIXO DO MAPA */
        .charts-row-top { display: grid; grid-template-columns: 1.2fr 1fr; gap: 24px; margin-bottom: 24px; }
        .charts-row-bottom { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
        .chart-box { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 22px; }

        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13.5px; }
        th { background: #040e08; color: #86efac; padding: 12px; text-align: left; font-weight: 800; border-bottom: 2px solid #15803d; }
        td { padding: 12px; border-bottom: 1px solid #14351f; color: #e2e8f0; }

        .leaflet-popup-content-wrapper { background: #040e08; color: #f8fafc; border: 1px solid #22c55e; border-radius: 10px; }
        .leaflet-popup-tip { background: #040e08; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🗺️ MAPA TÁTICO & GRÁFICOS VISUAIS INTERATIVOS (GOIÁS)</h1>
            <p style="margin:4px 0 0 0;color:#fef08a;font-size:13px;">● Geolocalização de Queixas & Painel Gráfico Detalhado de Buscas e Problemas por Cidade</p>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>

    <div class="container">
        <!-- BARRA DE LEGENDA DAS CORES DO MAPA -->
        <div class="legend-bar">
            <span style="color:#fef08a;font-weight:800;font-size:14px;">🎨 CORES DAS PAUTAS NO MAPA:</span>
            <div class="legend-item"><span class="dot-red"></span> 🔴 Saúde & Filas SUS</div>
            <div class="legend-item"><span class="dot-orange"></span> 🟠 Transporte & Asfalto</div>
            <div class="legend-item"><span class="dot-green"></span> 🟢 Logística Agro & Pontes</div>
            <div class="legend-item"><span class="dot-blue"></span> 🔵 Emprego Jovem & DAIA</div>
            <div class="legend-item"><span class="dot-purple"></span> 🟣 Hospital Regional & Turismo</div>
        </div>

        <!-- 1. MAPA LEAFLET.JS -->
        <div class="map-section">
            <div class="card-title">
                <span>📍 MAPA DE GOIÁS COM MARCADORES COLORIDOS POR PAUTA (CLIQUE NOS PINOS)</span>
                <span style="font-size:12px;color:#38bdf8;font-weight:bold;">TECNOLOGIA LEAFLET.JS GIS</span>
            </div>
            <div id="map"></div>
        </div>

        <!-- 2. PAINEL DE GRÁFICOS VISUAIS INTERATIVOS DIRETAMENTE ABAIXO DO MAPA -->
        <div class="charts-row-top">
            <!-- GRÁFICO 1: BARRA POR CIDADE -->
            <div class="chart-box">
                <div class="card-title">
                    <span>📊 INTENSIDADE DE QUEIXAS POPULARES POR MUNICÍPIO POLO (%)</span>
                </div>
                <canvas id="chartCidades" height="230"></canvas>
            </div>

            <!-- GRÁFICO 2: DOUGHNUT POR SETOR -->
            <div class="chart-box">
                <div class="card-title">
                    <span>🍩 DISTRIBUIÇÃO DAS RECLAMAÇÕES POR CATEGORIA</span>
                </div>
                <canvas id="chartCategorias" height="230"></canvas>
            </div>
        </div>

        <div class="charts-row-bottom">
            <!-- GRÁFICO 3: BUSCAS NO GOOGLE TRENDS -->
            <div class="chart-box">
                <div class="card-title">
                    <span>🔍 GOOGLE TRENDS — TERMOS DE MAIOR BUSCA DOS GOIANOS</span>
                </div>
                <canvas id="chartGoogleTrends" height="220"></canvas>
            </div>

            <!-- GRÁFICO 4: RADAR DE URGÊNCIA POR REGIÃO -->
            <div class="chart-box">
                <div class="card-title">
                    <span>📈 NÍVEL DE URGÊNCIA DE ATENDIMENTO POR REGIÃO</span>
                </div>
                <canvas id="chartUrgencia" height="220"></canvas>
            </div>
        </div>

        <!-- 3. TABELA DETALHADA DAS CIDADES E QUEIXAS -->
        <div class="map-section">
            <div class="card-title">
                <span>📋 DETALHAMENTO DE CIDADES, ELEITORES TSE E DIRECIONAMENTO DE VÍDEOS</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Cidade Polo & Região</th>
                        <th>Pauta Prioritária</th>
                        <th>Eleitores TSE</th>
                        <th>Reclamação Específica dos Moradores</th>
                        <th>Vídeo Recomendado para Wilder</th>
                    </tr>
                </thead>
                <tbody>
                    {% for c in reclamacoes %}
                    <tr>
                        <td><strong style="color:#fef08a;font-size:15px;">📍 {{ c.cidade }}</strong><br><span style="font-size:12px;color:#94a3b8;">{{ c.regiao }}</span></td>
                        <td><strong style="color:#38bdf8;">{{ c.pauta_principal }}</strong></td>
                        <td><strong style="color:#86efac;">{{ c.eleitores }}</strong></td>
                        <td>{{ c.demanda_especifica }}</td>
                        <td><strong style="color:#eab308;">{{ c.video_recomendado }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // INICIALIZAÇÃO DO MAPA LEAFLET.JS
        const map = L.map('map').setView([-16.6789, -49.2539], 7);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: '© OpenStreetMap / Inteligência Eleitoral Wilder Morais'
        }).addTo(map);

        const dadosCidades = {{ reclamacoes|tojson }};

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
                html: `<div style="background-color:${colorHex};width:22px;height:22px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 12px ${colorHex};"></div>`,
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

        // --- GRÁFICOS VISUAIS INTERATIVOS DIRETAMENTE ABAIXO DO MAPA ---

        // GRÁFICO 1: BARRAS DE INTENSIDADE POR CIDADE
        new Chart(document.getElementById('chartCidades').getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Luziânia', 'Goiânia', 'Valparaíso', 'Aparecida', 'Anápolis', 'Rio Verde', 'Catalão', 'Itumbiara'],
                datasets: [{
                    label: '% de Queixas na Cidade',
                    data: [45, 42, 40, 38, 35, 30, 28, 25],
                    backgroundColor: ['#f97316', '#ef4444', '#f97316', '#ef4444', '#3b82f6', '#22c55e', '#3b82f6', '#a855f7']
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

        // GRÁFICO 2: DOUGHNUT DE SETORES DE RECLAMAÇÃO
        new Chart(document.getElementById('chartCategorias').getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Saúde & Filas SUS (42%)', 'Transporte & Asfalto (28%)', 'Logística Agro & Pontes (14%)', 'Emprego Jovem (9%)', 'Hospital & Turismo (7%)'],
                datasets: [{
                    data: [42, 28, 14, 9, 7],
                    backgroundColor: ['#ef4444', '#f97316', '#22c55e', '#3b82f6', '#a855f7']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#f8fafc' } } }
            }
        });

        // GRÁFICO 3: GOOGLE TRENDS BUSCAS
        new Chart(document.getElementById('chartGoogleTrends').getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Concurso Público', 'Saúde / Fila SUS', 'Primeiro Emprego', 'Asfalto Entorno', 'Crédito Jovem'],
                datasets: [{
                    label: 'Volume Mensal Estimado no Google',
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

        // GRÁFICO 4: RADAR DE URGÊNCIA POR REGIÃO
        new Chart(document.getElementById('chartUrgencia').getContext('2d'), {
            type: 'radar',
            data: {
                labels: ['Metropolitana', 'Entorno DF', 'Sudoeste Agro', 'Centro Goiano', 'Sul Goiano', 'Estrada do Ferro'],
                datasets: [{
                    label: 'Índice de Urgência de Resposta (0 a 100)',
                    data: [95, 90, 85, 80, 75, 70],
                    backgroundColor: 'rgba(234, 179, 8, 0.2)',
                    borderColor: '#eab308',
                    pointBackgroundColor: '#eab308'
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#f8fafc' } } },
                scales: {
                    r: {
                        angleLines: { color: '#164624' },
                        grid: { color: '#164624' },
                        pointLabels: { color: '#86efac' },
                        ticks: { backdropColor: 'transparent', color: '#f8fafc' }
                    }
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

# RADAR DE NOTÍCIAS
HTML_RADAR_NOTICIAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar Anti-Crise de Notícias — Todos os Candidatos</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #450a0a, #991b1b); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 10px 18px; border-radius: 8px; border: 1px solid #22c55e; }
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📰 RADAR DE NOTÍCIAS COMPLETO DOS CANDIDATOS</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>
    <div class="container">
        {% for item in noticias %}
        <div style="background:#0a1f12;border:1px solid #164624;padding:20px;border-radius:12px;margin-bottom:16px;">
            <strong style="color:#fef08a;">👤 {{ item.candidato }}</strong> &bull; <span style="color:#86efac;">{{ item.veiculo }}</span>
            <h3 style="color:#fff;margin:6px 0;">"{{ item.manchete }}"</h3>
            <a href="{{ item.url_noticia }}" target="_blank" style="color:#38bdf8;font-weight:bold;">📰 Ler Matéria Completa</a>
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

    # Roteador de Mapa e Gráficos Interativos
    if any(k in p_lower for k in ["mapa", "grafico", "gráfico", "queixa", "cidade"]):
        return jsonify({
            "resposta": f"🗺️ <strong>MAPA INTERATIVO & PAINEL DE 4 GRÁFICOS VISUAIS COMPLETO</strong><br><br>"
                        f"Abaixo do mapa, você encontrará 4 gráficos interativos em Chart.js detalhando o ranking de queixas por cidade, os setores mais cobrados, buscas do Google Trends e índice de urgência por região!<br><br>"
                        f"👉 <a href='/mapa_demandas' style='background:linear-gradient(135deg, #0284c7, #0369a1);color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #38bdf8;'>🗺️ ABRIR MAPA & PAINEL DE GRÁFICOS VISUAIS</a>"
        }), 200

    # Fallback via OpenRouter
    if OPENROUTER_API_KEY:
        system_prompt = (
            "Você é o Comando Central da Sala de Guerra da campanha de Wilder Morais em Goiás. "
            "Seu sistema agora conta com um Mapa Interativo Leaflet.js acompanhado de 4 gráficos visuais detalhados abaixo do mapa (Barras de Cidades, Rosca de Setores, Barras do Google Trends e Radar de Urgência por Região)."
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
                    f"Painel de Gráficos e Mapa Interativo ativos.<br><br>"
                    f"👉 <a href='/mapa_demandas' style='background:#0284c7;color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:800;display:inline-block;'>🗺️ ABRIR MAPA & GRÁFICOS</a>"
    }), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
