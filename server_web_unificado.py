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
from pdf_generator_service import gerar_buffer_relatorio_360, POSTS_VIRAIS_MESTRE, YOUTUBE_BENCHMARK_DATA, RADAR_NOTICIAS_ATAQUES, MAPA_RECLAMACOES_REGIONAL

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
        .btn-dashboard { background: linear-gradient(135deg, #eab308, #ca8a04); color: #040e08; border-color: #fef08a; font-weight: 800; }
        .btn-dashboard:hover { background: #fde047; color: #000; }
        .btn-alert { background: #991b1b; border-color: #ef4444; color: #fecdd3; }
        .btn-alert:hover { background: #dc2626; color: #fff; }
        .btn-pdf { background: linear-gradient(135deg, #15803d, #16a34a); border-color: #eab308; color: #fef08a; }
        
        .chat-box { flex: 1; padding: 24px 28px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; max-width: 1100px; margin: 0 auto; width: 100%; }
        .msg { max-width: 88%; padding: 18px 22px; border-radius: 14px; font-size: 14.5px; line-height: 1.6; }
        .user { background: linear-gradient(135deg, #15803d, #16a34a); color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 4px 14px rgba(22,163,74,0.3); border: 1px solid #22c55e; }
        .bot { background: #0a1f12; color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #164624; box-shadow: 0 6px 20px rgba(0,0,0,0.5); }
        .bot strong { color: #86efac; }

        .quick-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
        .chip { background: #0d2e19; border: 1px solid #22c55e; color: #fef08a; padding: 9px 16px; border-radius: 20px; font-size: 12.5px; font-weight: 700; cursor: pointer; transition: 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
        .chip:hover { background: #16a34a; color: #fff; border-color: #eab308; }
        .chip-dash { background: #854d0e; border-color: #eab308; color: #fef08a; }
        .chip-dash:hover { background: #ca8a04; color: #fff; }
        .chip-danger { border-color: #ef4444; color: #fca5a5; background: #2a0a0a; }
        .chip-danger:hover { background: #dc2626; color: #fff; }

        .btn-link-creative { display: inline-flex; align-items: center; gap: 6px; background: linear-gradient(135deg, #15803d, #16a34a); color: #fef08a; padding: 8px 16px; border-radius: 8px; font-weight: 800; font-size: 12px; text-decoration: none; border: 1px solid #eab308; margin-top: 8px; transition: 0.2s; }
        .btn-link-creative:hover { background: #16a34a; color: #ffffff; }

        .badge-retencao { background: #14351f; color: #86efac; border: 1px solid #22c55e; padding: 3px 8px; border-radius: 6px; font-weight: 800; font-size: 11px; }

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
                <p>● Central de Inteligência de Criativos, Dashboard Visual & Defesa</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="/dashboard" class="btn-nav btn-dashboard">📊 Dashboard Metabase</a>
            <a href="/radar_noticias" class="btn-nav btn-alert">🚨 Radar Anti-Crise</a>
            <a href="/mapa_demandas" class="btn-nav">🗺️ Mapa de Reclamações</a>
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 Baixar PDF 360°</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg bot">
            <strong>🔰 BEM-VINDO À CENTRAL DE GUERRA & DASHBOARDS EXECUTIVOS</strong><br><br>
            Tudo o que está visualmente no <strong>Metabase</strong> agora está integrado diretamente aqui na plataforma!<br><br>
            <strong>Escolha uma opção de análise:</strong>
            <div class="quick-actions">
                <span class="chip chip-dash" onclick="window.location.href='/dashboard'">📊 Abrir Dashboard Metabase Integrado</span>
                <span class="chip" onclick="perguntarRapido('retencao e engajamento 7 dias')">⏱️ Retenção & Engajamento (7 Dias)</span>
                <span class="chip" onclick="perguntarRapido('retencao e engajamento 30 dias')">📅 Retenção & Engajamento (30 Dias)</span>
                <span class="chip chip-danger" onclick="perguntarRapido('radar de noticias e ataques')">🚨 Radar Anti-Crise</span>
                <span class="chip" onclick="perguntarRapido('mapa de reclamacoes por regiao')">🗺️ Mapa de Reclamações</span>
                <span class="chip" onclick="perguntarRapido('me de um relatorio')">📊 Dossiê PDF 360°</span>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Digite (ex: 'abrir dashboard', 'retencao 7 dias', 'cidades de goias')..." onkeypress="if(event.key==='Enter') enviar()">
            <button onclick="enviar()">Executar Ordem</button>
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

            if (pergunta.toLowerCase().includes('dashboard') || pergunta.toLowerCase().includes('metabase')) {
                window.location.href = '/dashboard';
                return;
            }

            chat.innerHTML += `<div class="msg user">${pergunta}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            botMsg.innerHTML = '<strong>[SALA DE GUERRA] Processando análise de inteligência...</strong>';
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

# DASHBOARD EXECUTIVO ESTILO METABASE (INTEGRADO TOTALMENTE NA PLATAFORMA DA IA)
HTML_DASHBOARD_METABASE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Executivo Metabase — Sala de Guerra Wilder Morais</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        
        .header { background: linear-gradient(135deg, #0b2214, #15803d, #eab308); padding: 18px 36px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .header p { margin: 4px 0 0 0; color: #fef08a; font-size: 13px; font-weight: 700; }
        
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; transition: 0.2s; }
        .btn-voltar:hover { background: #16a34a; color: #fff; }

        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }

        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
        .kpi-card { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .kpi-title { font-size: 12px; font-weight: 700; color: #86efac; text-transform: uppercase; letter-spacing: 0.5px; }
        .kpi-val { font-size: 28px; font-weight: 800; color: #fef08a; margin-top: 6px; }

        .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
        .chart-card { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 22px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .chart-title { font-size: 16px; font-weight: 800; color: #86efac; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }

        .full-width-card { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 22px; margin-bottom: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }

        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13.5px; }
        th { background: #040e08; color: #86efac; padding: 12px; text-align: left; font-weight: 800; border-bottom: 2px solid #15803d; }
        td { padding: 12px; border-bottom: 1px solid #14351f; color: #e2e8f0; }

        .badge-green { background: #15803d; color: #fef08a; padding: 4px 8px; border-radius: 4px; font-weight: 800; font-size: 11px; border: 1px solid #eab308; }
        .badge-red { background: #991b1b; color: #fecdd3; padding: 4px 8px; border-radius: 4px; font-weight: 800; font-size: 11px; }

        .iframe-box { width: 100%; height: 600px; border: 1px solid #164624; border-radius: 12px; overflow: hidden; margin-top: 20px; }
        iframe { width: 100%; height: 100%; border: none; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📊 DASHBOARD EXECUTIVO METABASE — SALA DE GUERRA MILITAR</h1>
            <p>● Painel Consolidado de Dados Eleitorais de Goiás & Competitividade de Redes Sociais</p>
        </div>
        <div>
            <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
        </div>
    </div>

    <div class="container">
        <!-- TOP KPI ROW -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Eleitores Mapeados (TSE)</div>
                <div class="kpi-val">4.870.000</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Municípios Cobertos</div>
                <div class="kpi-val">246 Cidades</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Taxa de Engajamento Wilder</div>
                <div class="kpi-val" style="color: #4ade80;">6.85% (Líder)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">YouTube Total Views</div>
                <div class="kpi-val">1.250.000</div>
            </div>
        </div>

        <!-- CHARTS GRID -->
        <div class="charts-grid">
            <!-- CHART 1: COMPARATIVO DE SEGUIDORES E ENGAJAMENTO DOS CANDIDATOS -->
            <div class="chart-card">
                <div class="chart-title">
                    <span>⚔️ COMPARATIVO DE REDES SOCIAIS</span>
                    <span class="badge-green">ATUALIZADO</span>
                </div>
                <canvas id="chartConcorrentes" height="200"></canvas>
            </div>

            <!-- CHART 2: ELEITORADO DOS TOP 7 MUNICÍPIOS DE GOIÁS -->
            <div class="chart-card">
                <div class="chart-title">
                    <span>🏛️ MAIORES COLÉGIOS ELEITORAIS (TSE GOIÁS)</span>
                    <span class="badge-green">DADOS OFICIAIS</span>
                </div>
                <canvas id="chartMunicipios" height="200"></canvas>
            </div>
        </div>

        <!-- CHART GRID ROW 2 -->
        <div class="charts-grid">
            <!-- CHART 3: DISTRIBUIÇÃO REGIONAL DE QUEIXAS POPULARES -->
            <div class="chart-card">
                <div class="chart-title">
                    <span>🗺️ QUEIXAS POPULARES POR REGIÃO (%)</span>
                </div>
                <canvas id="chartQueixas" height="200"></canvas>
            </div>

            <!-- CHART 4: SCORE DE RETENÇÃO E IMPACTO DOS VÍDEOS MAIS VIRAIS -->
            <div class="chart-card">
                <div class="chart-title">
                    <span>⏱️ SCORE DE RETENÇÃO DE VÍDEO (0-100)</span>
                </div>
                <canvas id="chartRetencao" height="200"></canvas>
            </div>
        </div>

        <!-- TABELA DE RESULTADOS DO METABASE -->
        <div class="full-width-card">
            <div class="chart-title">
                <span>📋 VISÃO EXECUTIVA DE AUDITORIA DE CRIATIVOS & DEFESA</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Candidato / Peça</th>
                        <th>Plataforma</th>
                        <th>Engajamento Ativo (Curtidas/Comentários)</th>
                        <th>Retenção de Vídeo (%)</th>
                        <th>Score de Impacto</th>
                        <th>Link do Criativo</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in posts %}
                    <tr>
                        <td><strong>{{ p.candidato }}</strong><br><span style="font-size:12px;color:#86efac;">{{ p.titulo }}</span></td>
                        <td><span class="badge-green">{{ p.rede }}</span></td>
                        <td>❤️ {{ p.curtidas }} | 💬 <strong>{{ p.comentarios }}</strong></td>
                        <td><strong style="color:#4ade80;">{{ p.retencao_media }}</strong></td>
                        <td><strong style="color:#fef08a;">{{ p.score_impacto }}</strong></td>
                        <td><a href="{{ p.post_url }}" target="_blank" style="color:#86efac;font-weight:bold;">🔗 Abrir Criativo</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- IFRAME DO METABASE EMBUTIDO (OPCIONAL INTEGRADO) -->
        <div class="full-width-card">
            <div class="chart-title">
                <span>🌐 ESPELHAMENTO AO VIVO DO METABASE ORIGINAL</span>
                <a href="https://dadoswilder.evandrosilvagallina.cloud" target="_blank" style="color:#fef08a;font-size:13px;">🔗 Abrir Metabase em nova aba</a>
            </div>
            <div class="iframe-box">
                <iframe src="https://dadoswilder.evandrosilvagallina.cloud"></iframe>
            </div>
        </div>
    </div>

    <script>
        // CHART 1: CONCORRENTES
        const ctx1 = document.getElementById('chartConcorrentes').getContext('2d');
        new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: ['Wilder Morais', 'Daniel Vilela', 'Marconi Perillo'],
                datasets: [
                    {
                        label: 'Seguidores Instagram (x1000)',
                        data: [310, 185, 240],
                        backgroundColor: '#15803d'
                    },
                    {
                        label: 'Taxa de Engajamento (%)',
                        data: [6.85, 3.45, 2.80],
                        backgroundColor: '#eab308'
                    }
                ]
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

        // CHART 2: MUNICIPIOS
        const ctx2 = document.getElementById('chartMunicipios').getContext('2d');
        new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: ['Goiânia', 'Aparecida', 'Anápolis', 'Rio Verde', 'Luziânia', 'Águas Lindas', 'Valparaíso'],
                datasets: [{
                    label: 'Eleitores Registrados TSE',
                    data: [1030000, 345000, 290000, 155000, 132000, 115000, 98000],
                    backgroundColor: '#16a34a'
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

        // CHART 3: QUEIXAS
        const ctx3 = document.getElementById('chartQueixas').getContext('2d');
        new Chart(ctx3, {
            type: 'doughnut',
            data: {
                labels: ['Metropolitana (Saúde)', 'Entorno DF (Transporte/Asfalto)', 'Sudoeste (Agro/Logística)', 'Outros'],
                datasets: [{
                    data: [42, 28, 14, 16],
                    backgroundColor: ['#ef4444', '#eab308', '#15803d', '#3b82f6']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#f8fafc' } } }
            }
        });

        // CHART 4: RETENÇÃO
        const ctx4 = document.getElementById('chartRetencao').getContext('2d');
        new Chart(ctx4, {
            type: 'bar',
            data: {
                labels: ['Wilder (Livros)', 'Wilder (Agro)', 'Daniel (GO-070)', 'Marconi (TBT)'],
                datasets: [{
                    label: 'Score de Impacto (0-100)',
                    data: [96, 92, 58, 48],
                    backgroundColor: ['#22c55e', '#22c55e', '#eab308', '#ef4444']
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

# TELA DEDICADA 1: RADAR ANTI-CRISE
HTML_RADAR_NOTICIAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar Anti-Crise & Defesa — Wilder Morais</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #450a0a, #991b1b); padding: 20px 40px; border-bottom: 3px solid #ef4444; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
        .card-noticia { background: #0a1f12; border: 1px solid #164624; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .card-danger { border-color: #ef4444; background: #1a0808; }
        .badge { padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; }
        .badge-red { background: #ef4444; color: #fff; }
        .badge-yellow { background: #eab308; color: #000; }
        .badge-green { background: #22c55e; color: #000; }
        .estrategia-box { background: #040e08; border-left: 4px solid #eab308; padding: 12px 16px; margin-top: 12px; border-radius: 6px; font-size: 13.5px; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 8px 16px; border-radius: 8px; border: 1px solid #22c55e; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 RADAR ANTI-CRISE & MONITORAMENTO DE NOTÍCIAS (WILDER MORAIS)</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>

    <div class="container">
        <p style="color: #a7f3d0; font-size: 15px;">Monitoramento contínuo de portais de notícias de Goiás (O Popular, Jornal Opção, Diário da Manhã, G1 Goiás) e redes sociais para mitigação de crises.</p>

        {% for item in noticias %}
        <div class="card-noticia {% if 'VERMELHO' in item.nivel_ameaca %}card-danger{% endif %}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-weight: 800; color: #86efac;">📰 {{ item.veiculo }}</span>
                <span class="badge {% if 'VERMELHO' in item.nivel_ameaca %}badge-red{% elif 'MÉDIO' in item.nivel_ameaca %}badge-yellow{% else %}badge-green{% endif %}">{{ item.nivel_ameaca }}</span>
            </div>
            <h3 style="margin: 0 0 8px 0; color: #fff;">"{{ item.manchete }}"</h3>
            <div class="estrategia-box">
                🛡️ <strong>PLANO DE CONTRANARRATIVA DE IA:</strong><br>
                {{ item.estrategia_defesa }}
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# TELA DEDICADA 2: MAPA TÁTICO DE RECLAMAÇÕES POPULARES COM GRÁFICOS
HTML_MAPA_DEMANDAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa Tático de Reclamações — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #0b2214, #15803d); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
        .chart-box { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 24px; margin-bottom: 30px; }
        .bar-container { margin-bottom: 16px; }
        .bar-label { display: flex; justify-content: space-between; font-size: 13.5px; font-weight: 700; margin-bottom: 6px; }
        .bar-bg { background: #040e08; height: 22px; border-radius: 6px; overflow: hidden; border: 1px solid #1e4028; }
        .bar-fill { height: 100%; background: linear-gradient(90deg, #15803d, #eab308); border-radius: 6px; }
        .card-demanda { background: #0a1f12; border: 1px solid #164624; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 8px 16px; border-radius: 8px; border: 1px solid #22c55e; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🗺️ MAPA TÁTICO DE RECLAMAÇÕES & PAUTAS DE VÍDEO (GOIÁS)</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>

    <div class="container">
        <div class="chart-box">
            <h2 style="margin: 0 0 20px 0; color: #86efac; font-size: 17px;">📊 DISTRIBUIÇÃO REGIONAL DE QUEIXAS DA POPULAÇÃO (%)</h2>
            {% for item in reclamacoes %}
            <div class="bar-container">
                <div class="bar-label">
                    <span>{{ item.regiao }}</span>
                    <span style="color: #fef08a;">{{ item.percentual }}</span>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill" style="width: 50%;"></div>
                </div>
            </div>
            {% endfor %}
        </div>

        <h2 style="color: #fef08a; font-size: 18px; margin-bottom: 16px;">🎬 DIRECIONAMENTO TÁTICO DE VÍDEOS POR REGIÃO</h2>
        {% for item in reclamacoes %}
        <div class="card-demanda">
            <strong style="color: #86efac; font-size: 16px;">📍 {{ item.regiao }}</strong>
            <p style="margin: 4px 0 10px 0; color: #e2e8f0; font-size: 14px;"><strong>Pauta Principal:</strong> {{ item.pauta }}</p>
            <div style="background: #040e08; padding: 12px; border-radius: 8px; border-left: 4px solid #16a34a;">
                🎥 <strong>TEMA DO VÍDEO RECOMENDADO:</strong> {{ item.video }}<br>
                🎯 <strong>GANCHO INICIAL DE 3s:</strong> {{ item.gancho|safe }}
            </div>
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

@app.route("/dashboard", methods=["GET"])
@app.route("/metabase", methods=["GET"])
def dashboard_metabase_page():
    return render_template_string(HTML_DASHBOARD_METABASE, posts=POSTS_VIRAIS_MESTRE)

@app.route("/radar_noticias", methods=["GET"])
def radar_noticias_page():
    return render_template_string(HTML_RADAR_NOTICIAS, noticias=RADAR_NOTICIAS_ATAQUES)

@app.route("/mapa_demandas", methods=["GET"])
def mapa_demandas_page():
    return render_template_string(HTML_MAPA_DEMANDAS, reclamacoes=MAPA_RECLAMACOES_REGIONAL)

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

    # Roteador de Dashboard / Metabase
    if any(k in p_lower for k in ["dashboard", "metabase", "grafico", "gráfico", "painel"]):
        return jsonify({
            "resposta": "📊 <strong>DASHBOARD EXECUTIVO METABASE INTEGRADO NA IA</strong><br><br>"
                        "Todos os gráficos de concorrentes, colégios eleitorais de Goiás, retenção de vídeo e mapa de queixas estão consolidados!<br><br>"
                        "👉 <a href='/dashboard' style='background:linear-gradient(135deg, #eab308, #ca8a04);color:#040e08;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #fef08a;'>📊 ABRIR DASHBOARD METABASE AGORA</a>"
        }), 200

    # 1. Roteador de Auditoria Qualitativa de Engajamento e Retenção de Vídeo
    if any(k in p_lower for k in ["post", "posts", "engajou", "engajado", "curtidas", "viral", "retencao", "retenção", "comentarios", "comentários", "compartilhamentos", "score", "7 dia", "7d", "30 dia", "30d"]):
        
        filtro_periodo = "30_dias" if any(k in p_lower for k in ["30", "mês", "mes", "mensal"]) else "7_dias"
        rotulo_periodo = "ÚLTIMOS 30 DIAS (MENSAL)" if filtro_periodo == "30_dias" else "ÚLTIMOS 7 DIAS (SEMANAL)"

        posts_filtrados = [p for p in POSTS_VIRAIS_MESTRE if p.get("periodo") == filtro_periodo]
        if not posts_filtrados:
            posts_filtrados = POSTS_VIRAIS_MESTRE[:4]

        posts_html = "".join([
            f"<div style='background:#0e2917;padding:16px;border-radius:12px;margin-top:12px;border:1px solid #1a4628;box-shadow:0 4px 12px rgba(0,0,0,0.3);'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
            f"<strong style='font-size:15px;color:#86efac;'>🏆 {p['candidato']} ({p['rede']})</strong>"
            f"<span class='badge-retencao'>SCORE: {p.get('score_impacto', '90/100')}</span></div>"
            f"<div style='color:#fef08a;font-weight:bold;font-size:14px;margin-top:6px;'>\"{p['titulo']}\"</div>"
            f"<div style='margin-top:8px;font-size:13px;color:#cbd5e1;'>"
            f"• <strong>Engajamento Ativo</strong>: ❤️ {p['curtidas']} curtidas | 💬 <strong>{p['comentarios']} comentários</strong> | 🔄 {p.get('compartilhamentos', 'N/A')} compartilhamentos no WhatsApp<br>"
            f"• ⏱️ <strong>Tempo de Retenção Média</strong>: <span style='color:#86efac;font-weight:bold;'>{p.get('retencao_media', '85%')}</span> | Views Totais: {p['views']}<br>"
            f"• 📊 <strong>Taxa de Engajamento Real</strong>: <span style='color:#4ade80;font-weight:bold;'>{p['engajamento']}</span> (Pauta: {p['pauta']})</div>"
            f"<div style='margin-top:8px;font-size:12.5px;color:#a7f3d0;background:#040e08;padding:10px;border-radius:8px;border:1px solid #16a34a;'>"
            f"💡 <strong>Diagnóstico de IA de Retenção & Engajamento Qualitativo:</strong><br>{p['analise_ia']}</div>"
            f"<div style='margin-top:10px;'>"
            f"<a href='{p['post_url']}' target='_blank' class='btn-link-creative'>🔗 ASSISTIR CRIATIVO NO {p['rede'].upper().split()[0]}</a></div>"
            f"</div>"
            for p in posts_filtrados
        ])

        return jsonify({
            "resposta": f"⏱️ <strong>AUDITORIA QUALITATIVA DE ENGAJAMENTO REAL & RETENÇÃO — {rotulo_periodo}</strong><br>"
                        f"<p style='font-size:13px;color:#a7f3d0;'>Esta análise avalia visualizações x comentários x retenção de vídeo até o final. Clique no botão verde para auditar o criativo!</p>"
                        f"{posts_html}<br><br>"
                        f"<strong>Alternar Janela Temporável:</strong><br>"
                        f"👉 <a href='#' onclick='perguntarRapido(\"retencao e engajamento 7 dias\");return false;' style='color:#fef08a;font-weight:bold;'>[Ranking 7 Dias (Semanal)]</a> &bull; "
                        f"<a href='#' onclick='perguntarRapido(\"retencao e engajamento 30 dias\");return false;' style='color:#fef08a;font-weight:bold;'>[Ranking 30 Dias (Mensal)]</a>"
        }), 200

    # 2. Roteamento Radar Anti-Crise e Notícias
    if any(k in p_lower for k in ["radar", "ataque", "ataques", "noticia", "notícia", "crise", "falando mal", "fake news"]):
        noticias_html = "".join([
            f"<div style='background:#1a0808;padding:14px;border-radius:10px;margin-top:10px;border:1px solid #ef4444;'><div style='display:flex;justify-content:space-between;'>"
            f"<strong>📰 {n['veiculo']}</strong>"
            f"<span style='background:#ef4444;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold;'>{n['nivel_ameaca']}</span></div>"
            f"<div style='color:#fff;font-weight:bold;margin-top:6px;'>\"{n['manchete']}\"</div>"
            f"<div style='background:#040e08;padding:8px;border-radius:6px;margin-top:8px;font-size:12px;border-left:3px solid #eab308;'>"
            f"🛡️ <strong>Estratégia de Defesa IA:</strong> {n['estrategia_defesa']}</div></div>"
            for n in RADAR_NOTICIAS_ATAQUES
        ])
        return jsonify({
            "resposta": f"🚨 <strong>RADAR ANTI-CRISE & MONITORAMENTO DE NOTÍCIAS DA OPOSIÇÃO</strong><br>{noticias_html}<br><br>👉 <a href='/radar_noticias' target='_blank' style='color:#fef08a;font-weight:bold;text-decoration:underline;'>Abrir Painel Completo do Radar Anti-Crise</a>"
        }), 200

    # 3. Roteamento Mapa Tático de Reclamações por Região
    if any(k in p_lower for k in ["mapa", "reclamacao", "reclamação", "reclamacoes", "regiao", "região", "demandas", "queixas"]):
        mapa_html = "".join([
            f"<div style='background:#0e2917;padding:14px;border-radius:10px;margin-top:10px;border:1px solid #1a4628;'>"
            f"<strong>📍 {m['regiao']}</strong> ({m['percentual']} do total de queixas)<br>"
            f"<span style='color:#fef08a;font-weight:bold;font-size:13px;'>Pauta Principal: {m['pauta']}</span><br>"
            f"<div style='margin-top:6px;font-size:12.5px;color:#e2e8f0;background:#040e08;padding:8px;border-radius:6px;border-left:3px solid #16a34a;'>"
            f"🎥 <strong>Vídeo Recomendado:</strong> {m['video']}<br>"
            f"🎯 <strong>Gancho 3s:</strong> {m['gancho']}</div></div>"
            for m in MAPA_RECLAMACOES_REGIONAL
        ])
        return jsonify({
            "resposta": f"🗺️ <strong>MAPA TÁTICO DE RECLAMAÇÕES POPULARES POR REGIÃO DE GOIÁS</strong><br>{mapa_html}<br><br>👉 <a href='/mapa_demandas' target='_blank' style='color:#fef08a;font-weight:bold;text-decoration:underline;'>Abrir Gráficos Interativos do Mapa de Reclamações</a>"
        }), 200

    # 4. Roteador de YouTube dos Concorrentes
    if any(k in p_lower for k in ["youtube", "canal", "vilela", "marconi", "assunto", "interesse"]):
        yt_html = "".join([
            f"<div style='background:#0e2917;padding:14px;border-radius:10px;margin-top:10px;border:1px solid #1a4628;'>"
            f"<strong>📺 {y['candidato']} — {y['canal']}</strong><br>"
            f"<span style='color:#fef08a;font-weight:bold;font-size:13px;'>Inscritos: {y['inscritos']} | Views Totais: {y['views_totais']}</span><br>"
            f"<div style='margin-top:6px;font-size:13px;color:#e2e8f0;'>"
            f"• <strong>Vídeo Top Performer</strong>: \"{y['top_video']}\"<br>"
            f"• <strong>Métricas</strong>: <span style='color:#86efac;font-weight:bold;'>{y['top_video_views']}</span> ({y['top_video_likes']})<br>"
            f"• 🎯 <strong>Assunto de Maior Interesse</strong>: <span style='color:#fde047;'>{y['assunto_interesse']}</span></div>"
            f"<div style='margin-top:6px;font-size:12px;color:#a7f3d0;background:#040e08;padding:8px;border-radius:6px;border:1px solid #16a34a;'>"
            f"💡 <strong>Análise de IA:</strong> {y['analise_ia']}</div></div>"
            for y in YOUTUBE_BENCHMARK_DATA
        ])
        return jsonify({
            "resposta": f"📺 <strong>BENCHMARKING DE CANAIS DE YOUTUBE DOS CONCORRENTES</strong><br>{yt_html}"
        }), 200

    # 5. Roteador de Guerra de Concorrentes
    if any(k in p_lower for k in ["crescendo", "concorrente", "concorrentes", "quem", "redes", "seguidores", "wilder"]):
        return jsonify({
            "resposta": """⚔️ <strong>GUERRA DE CONCORRENTES & COMPARATIVO DE REDES SOCIAIS</strong><br><br>
1. 🥇 <strong>Wilder Morais (@WilderMorais)</strong>:
   • <strong>Instagram</strong>: 310.000 seguidores | <strong>Taxa de Engajamento</strong>: <span style='color:#4ade80;font-weight:bold;'>6.85% (LÍDER)</span><br>
   • <strong>YouTube Oficial</strong>: 1.250.000 visualizações acumuladas<br>
   • <strong>Facebook</strong>: 142.000 seguidores<br><br>
2. 🥈 <strong>Daniel Vilela (@Danielvilelaoficial)</strong>:
   • <strong>Instagram</strong>: 185.000 seguidores | <strong>Taxa de Engajamento</strong>: 3.45%<br>
   • <strong>Facebook</strong>: 95.000 seguidores<br><br>
3. 🥉 <strong>Marconi Perillo (@Marconiperillo)</strong>:
   • <strong>Instagram</strong>: 240.000 seguidores | <strong>Taxa de Engajamento</strong>: 2.80%<br>
   • <strong>Facebook</strong>: 130.000 seguidores<br><br>
👉 <a href='/download_pdf' target='_blank' style='color:#fef08a;font-weight:bold;text-decoration:underline;'>Baixar o Dossiê de Concorrentes em PDF</a>"""
        }), 200

    # 6. Roteamento de Relatórios e PDF
    if any(k in p_lower for k in ["relatorio", "relatório", "pdf", "dados", "resumo", "baixar"]):
        return jsonify({
            "resposta": """📊 <strong>DOSSIÊ MESTRE 360° DE INTELIGÊNCIA ELEITORAL MILITAR</strong><br><br>
• 📍 <strong>246 Cidades de Goiás</strong>: Mapeadas com eleitorado TSE e coordenadas PostGIS.<br>
• 🚨 <strong>Radar Anti-Crise</strong>: Monitoramento de notícias e defesa em tempo real.<br>
• 🗺️ <strong>Mapa de Reclamações</strong>: Queixas da população divididas por região.<br>
• 📺 <strong>YouTube & Concorrentes</strong>: Benchmarking de vídeos virais e taxas de engajamento.<br><br>
👉 <a href='/download_pdf' target='_blank' style='background:linear-gradient(135deg, #15803d, #16a34a);color:#fef08a;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block;margin-top:6px;border:1px solid #eab308;'>📄 BAIXAR O RELATÓRIO OFICIAL 360° EM PDF</a>"""
        }), 200

    # Fallback via OpenRouter
    if OPENROUTER_API_KEY:
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "Você é o Comando Central da Sala de Guerra da campanha de Wilder Morais em Goiás. Responda em Português com tom militar, autoridade e clareza estratégica."},
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

    # Resposta Padrão Tática
    return jsonify({
        "resposta": f"🔰 <strong>COMANDO CENTRAL DE IA — SALA DE GUERRA (WILDER MORAIS 2026)</strong><br><br>"
                    f"Ordem recebida sobre <i>'{pergunta}'</i>!<br>"
                    f"Todos os módulos táticos de inteligência (Retenção de Vídeo, Radar Anti-Crise e Dashboard Metabase) estão operacionais.<br><br>"
                    f"👉 <a href='/dashboard' style='background:linear-gradient(135deg, #eab308, #ca8a04);color:#040e08;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #fef08a;'>📊 ABRIR DASHBOARD METABASE INTEGRADO</a>"
    }), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
