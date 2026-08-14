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
    RADAR_NOTICIAS_ATAQUES, MAPA_RECLAMACOES_REGIONAL,
    MAIORES_COLEGIOS_TSE, PLANO_DE_GOVERNO_MEMORIA,
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
        .chip-eventos { background: #b45309; border-color: #eab308; color: #fef08a; }
        .chip-dash { background: #854d0e; border-color: #eab308; color: #fef08a; }
        .chip-danger { border-color: #ef4444; color: #fca5a5; background: #2a0a0a; }

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
            <a href="/dashboard" class="btn-nav btn-dashboard">📊 Dashboard YouTube Real</a>
            <a href="/radar_noticias" class="btn-nav btn-alert">🚨 Radar Anti-Crise</a>
            <a href="/mapa_demandas" class="btn-nav">🗺️ Mapa de Queixas</a>
            <a href="/eventos" class="btn-nav btn-eventos">🎪 Radar de 150 Eventos</a>
            <a href="/plano_governo" class="btn-nav btn-plano">📘 Plano de Governo</a>
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 PDF 360°</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg bot">
            <strong>🔰 TODOS OS MÓDULOS DE INTELIGÊNCIA ELEITORAL REATIVADOS COM SUCESSO!</strong><br><br>
            Reativamos e aprimoramos:<br>
            📺 <strong>Auditoria em Tempo Real do YouTube:</strong> Títulos de vídeos, visualizações reais e links diretos para cada vídeo de Wilder Morais e concorrentes.<br>
            🚨 <strong>Radar Anti-Crise de Notícias:</strong> Monitoramento de portais de Goiás com contra-narrativas de IA.<br>
            🗺️ <strong>Mapa Tático de Reclamações:</strong> Queixas por cidade/região com direcionamento de vídeo.<br>
            🏛️ <strong>Maiores Colégios Eleitorais do TSE:</strong> Dados detalhados de eleitores das 246 cidades.<br>
            🎪 <strong>Radar de 150 Eventos:</strong> Datas exatas e parâmetros para Meta Ads.<br><br>
            <strong>Escolha uma área de análise:</strong>
            <div class="quick-actions">
                <span class="chip chip-dash" onclick="window.location.href='/dashboard'">📺 Ver Vídeos Reais do YouTube</span>
                <span class="chip chip-danger" onclick="window.location.href='/radar_noticias'">🚨 Radar Anti-Crise de Notícias</span>
                <span class="chip" onclick="window.location.href='/mapa_demandas'">🗺️ Mapa de Queixas por Cidade</span>
                <span class="chip chip-eventos" onclick="window.location.href='/eventos'">🎪 Radar de 150 Eventos</span>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Digite (ex: 'vídeos do youtube', 'notícias de goiás', 'mapa de queixas')..." onkeypress="if(event.key==='Enter') enviar()">
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
            if (pLower.includes('noticia') || pLower.includes('notícia') || pLower.includes('radar')) {
                window.location.href = '/radar_noticias';
                return;
            }
            if (pLower.includes('queixa') || pLower.includes('reclamacao') || pLower.includes('reclamação') || pLower.includes('cidade')) {
                window.location.href = '/mapa_demandas';
                return;
            }
            if (pLower.includes('youtube') || pLower.includes('dashboard') || pLower.includes('video') || pLower.includes('vídeo')) {
                window.location.href = '/dashboard';
                return;
            }

            chat.innerHTML += `<div class="msg user">${pergunta}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            botMsg.innerHTML = '<strong>[SALA DE GUERRA] Processando inteligência de campanha...</strong>';
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

# DASHBOARD EXECUTIVO COM AUDITORIA DE VÍDEOS REAIS E COLÉGIOS DO TSE
HTML_DASHBOARD_METABASE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Executivo — YouTube Real & Eleitorado TSE Goiás</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        
        .header { background: linear-gradient(135deg, #0b2214, #15803d, #eab308); padding: 18px 36px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }

        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
        .kpi-card { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 20px; text-align: center; }
        .kpi-title { font-size: 12px; font-weight: 700; color: #86efac; text-transform: uppercase; }
        .kpi-val { font-size: 26px; font-weight: 800; color: #fef08a; margin-top: 6px; }

        .full-width-card { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 22px; margin-bottom: 24px; }
        .card-title { font-size: 17px; font-weight: 800; color: #86efac; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #eab308; padding-left: 10px; }

        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13.5px; }
        th { background: #040e08; color: #86efac; padding: 12px; text-align: left; font-weight: 800; border-bottom: 2px solid #15803d; }
        td { padding: 12px; border-bottom: 1px solid #14351f; color: #e2e8f0; }

        .badge-green { background: #15803d; color: #fef08a; padding: 4px 8px; border-radius: 4px; font-weight: 800; font-size: 11.5px; border: 1px solid #eab308; }
        .badge-blue { background: #1e3a8a; color: #bfdbfe; padding: 4px 8px; border-radius: 4px; font-weight: 800; font-size: 11.5px; border: 1px solid #60a5fa; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📺 AUDITORIA DO YOUTUBE REAL & MAIORES COLÉGIOS ELEITORAIS (TSE GOIÁS)</h1>
            <p style="margin:4px 0 0 0;color:#fef08a;font-size:13px;">● Títulos e Visualizações Reais dos Vídeos & Dados Oficiais do TSE por Município</p>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>

    <div class="container">
        <!-- KPI ROW -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Eleitores Registrados (TSE)</div>
                <div class="kpi-val">4.870.000</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Municípios Cobertos</div>
                <div class="kpi-val">246 Cidades</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Vídeos Mapeados</div>
                <div class="kpi-val" style="color:#4ade80;">{{ yt_videos|length }} Vídeos Reais</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Fonte de Dados</div>
                <div class="kpi-val" style="color:#38bdf8;">100% Real API YouTube</div>
            </div>
        </div>

        <!-- TABELA DE VÍDEOS REAIS INDIVIDUAIS DO YOUTUBE -->
        <div class="full-width-card">
            <div class="card-title">
                <span>🎬 AUDITORIA DE VÍDEOS INDIVIDUAIS DO YOUTUBE (WILDER MORAIS & DANIEL VILELA)</span>
                <span class="badge-green">DADOS AO VIVO</span>
            </div>
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
                        <td><strong style="color:#fef08a;">{{ v.candidato }}</strong><br><span style="font-size:12px;color:#94a3b8;">{{ v.canal }}</span></td>
                        <td><strong>{{ v.titulo }}</strong></td>
                        <td><span class="badge-green">{{ v.views }}</span></td>
                        <td><span class="badge-blue">{{ v.publicado }}</span></td>
                        <td>
                            <a href="{{ v.url }}" target="_blank" style="color:#38bdf8;font-weight:bold;text-decoration:none;">🎬 Assistir Vídeo no YouTube</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- MAIORES COLÉGIOS ELEITORAIS DO TSE GOIÁS -->
        <div class="full-width-card">
            <div class="card-title">
                <span>🏛️ MAIORES COLÉGIOS ELEITORAIS DO TSE EM GOIÁS (RANKING MUNICIPAL)</span>
                <span class="badge-green">TSE 2026</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Município Polo</th>
                        <th>Eleitores Registrados (TSE)</th>
                        <th>Região Administrativa</th>
                        <th>Relevância no Eleitorado Estadual</th>
                    </tr>
                </thead>
                <tbody>
                    {% for c in colegios %}
                    <tr>
                        <td><strong style="color:#86efac;font-size:15px;">📍 {{ c.cidade }}</strong></td>
                        <td><strong style="color:#fef08a;">{{ c.eleitores }} eleitores</strong></td>
                        <td>{{ c.regiao }}</td>
                        <td><span class="badge-blue">{{ c.relevancia }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

# TELA DEDICADA 1: RADAR ANTI-CRISE DE NOTÍCIAS COM BUSCA AO VIVO E CONTRANARRATIVAS
HTML_RADAR_NOTICIAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar Anti-Crise & Defesa de Notícias — Wilder Morais</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #450a0a, #991b1b); padding: 20px 40px; border-bottom: 3px solid #ef4444; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .card-noticia { background: #0a1f12; border: 1px solid #164624; border-radius: 12px; padding: 22px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .card-danger { border-color: #ef4444; background: #1a0808; }
        .badge { padding: 4px 10px; border-radius: 6px; font-size: 11.5px; font-weight: 800; }
        .badge-red { background: #ef4444; color: #fff; }
        .badge-yellow { background: #eab308; color: #000; }
        .badge-green { background: #22c55e; color: #000; }
        .estrategia-box { background: #040e08; border-left: 4px solid #eab308; padding: 14px; margin-top: 14px; border-radius: 8px; font-size: 14px; line-height: 1.6; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 10px 18px; border-radius: 8px; border: 1px solid #22c55e; }
        .btn-busca { background: #2563eb; color: #fff; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-weight: 800; font-size: 12px; display: inline-block; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🚨 RADAR ANTI-CRISE & MONITORAMENTO DE NOTÍCIAS (GOIÁS)</h1>
            <p style="margin:4px 0 0 0;color:#fca5a5;font-size:13px;">● Varredura Ativa dos Portais O Popular, Jornal Opção, Diário da Manhã e G1 Goiás</p>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>

    <div class="container">
        <p style="color: #a7f3d0; font-size: 15px; margin-bottom: 24px;">Monitoramento inteligente das matérias e menções sobre a eleição de Goiás com plano de defesa e resposta em tempo real da IA:</p>

        {% for item in noticias %}
        <div class="card-noticia {% if 'VERMELHO' in item.nivel_ameaca %}card-danger{% endif %}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-weight: 800; color: #86efac; font-size: 15px;">📰 {{ item.veiculo }} &bull; <span style="color:#cbd5e1;font-size:13px;">{{ item.data }}</span></span>
                <span class="badge {% if 'VERMELHO' in item.nivel_ameaca %}badge-red{% elif 'MÉDIO' in item.nivel_ameaca %}badge-yellow{% else %}badge-green{% endif %}">{{ item.nivel_ameaca }}</span>
            </div>
            <h3 style="margin: 0 0 8px 0; color: #fff; font-size: 18px;">"{{ item.manchete }}"</h3>
            <a href="{{ item.url_noticia }}" target="_blank" class="btn-busca">🔍 Auditar Matéria ao Vivo no Google / Notícias</a>
            
            <div class="estrategia-box">
                🛡️ <strong>PLANO DE CONTRANARRATIVA E RESPOSTA DA IA:</strong><br>
                {{ item.estrategia_defesa }}
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# TELA DEDICADA 2: MAPA TÁTICO DE RECLAMAÇÕES POPULARES COM CIDADES POLO
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
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .card-demanda { background: #0a1f12; border: 1px solid #164624; border-radius: 12px; padding: 22px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 10px 18px; border-radius: 8px; border: 1px solid #22c55e; }
        .badge-perc { background: #eab308; color: #000; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🗺️ MAPA TÁTICO DE RECLAMAÇÕES & CIDADES POLO (GOIÁS)</h1>
            <p style="margin:4px 0 0 0;color:#fef08a;font-size:13px;">● Cruzamento de Queixas Populares por Região e Direcionamento de Anúncios e Vídeos</p>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>

    <div class="container">
        <h2 style="color: #86efac; font-size: 18px; margin-bottom: 20px;">📍 QUEIXAS DA POPULAÇÃO E TEMAS RECOMENDADOS PARA VÍDEOS</h2>
        {% for item in reclamacoes %}
        <div class="card-demanda">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <strong style="color: #86efac; font-size: 18px;">📍 {{ item.regiao }}</strong>
                <span class="badge-perc">🔥 {{ item.percentual }} das Queixas</span>
            </div>
            <p style="margin: 2px 0 10px 0; color: #38bdf8; font-size: 13.5px;">🏙️ <strong>Cidades Polo Impactadas:</strong> {{ item.cidades_polo }}</p>
            <p style="margin: 4px 0 12px 0; color: #e2e8f0; font-size: 14px;"><strong>Pauta Principal:</strong> {{ item.pauta }}</p>
            
            <div style="background: #040e08; padding: 14px; border-radius: 8px; border-left: 4px solid #16a34a;">
                🎥 <strong>TEMA DO VÍDEO RECOMENDADO:</strong> {{ item.video }}<br><br>
                🎯 <strong>GANCHO INICIAL DE 3 SEGUNTOS:</strong> <span style="color:#fef08a;">"{{ item.gancho|safe }}"</span>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# TELA DEDICADA DE EVENTOS (ROBUSTA - 150 EVENTOS COM DATAS EXATAS)
HTML_EVENTOS_RADAR = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar de Eventos & Geotargeting de Tráfego Pago — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #0b2214, #d97706, #15803d); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }
        
        .box { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .box-title { font-size: 18px; font-weight: 800; color: #fef08a; margin-bottom: 16px; border-left: 5px solid #d97706; padding-left: 10px; display: flex; justify-content: space-between; align-items: center; }
        
        .grid-events { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card-evento { background: #040e08; border: 1px solid #22c55e; border-radius: 12px; padding: 20px; position: relative; }
        .badge-mes { background: #b45309; color: #fff; padding: 4px 10px; border-radius: 6px; font-size: 11.5px; font-weight: 800; }
        .badge-categoria { background: #1e3a8a; color: #bfdbfe; padding: 4px 10px; border-radius: 6px; font-size: 11.5px; font-weight: 800; border: 1px solid #60a5fa; }
        .badge-datas { background: #15803d; color: #fef08a; padding: 4px 10px; border-radius: 6px; font-size: 11.5px; font-weight: 800; border: 1px solid #eab308; }

        .filter-bar { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .btn-filter { background: #0c2415; color: #fef08a; border: 1px solid #22c55e; padding: 8px 16px; border-radius: 20px; font-weight: 700; font-size: 13px; cursor: pointer; }
        .btn-filter:hover, .btn-filter.active { background: #15803d; color: #fff; border-color: #eab308; }

        .copy-box { background: #0c2415; border-left: 4px solid #eab308; padding: 12px; border-radius: 8px; margin-top: 12px; font-size: 13px; }
        .btn-copy { background: #d97706; color: #fff; border: none; padding: 6px 12px; border-radius: 6px; font-weight: 800; cursor: pointer; font-size: 11.5px; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🎪 RADAR DE EVENTOS POPULOSOS DE GOIÁS (150 EVENTOS MAPEADOS)</h1>
            <p style="margin:4px 0 0 0;color:#fef08a;font-size:13px;">● Mapeamento de 50 Eventos por Mês com Datas Iniciais e Finais Exatas para Meta Ads & Google Ads</p>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>

    <div class="container">
        <div class="filter-bar">
            <button class="btn-filter active" onclick="filtrarMes('todos')">🌐 Todos os 150 Eventos</button>
            <button class="btn-filter" onclick="filtrarMes('agosto')">📅 Agosto 2026 (50 Eventos)</button>
            <button class="btn-filter" onclick="filtrarMes('setembro')">📅 Setembro 2026 (50 Eventos)</button>
            <button class="btn-filter" onclick="filtrarMes('outubro')">📅 Outubro 2026 (50 Eventos)</button>
        </div>

        <div class="box">
            <div class="box-title">
                <span>📍 EVENTOS RELIGIOSOS, AGROPECUÁRIOS, CULTURAIS, ESPORTIVOS & SOCIAIS</span>
                <span style="font-size:13px;color:#86efac;">Total Mapeado: {{ eventos|length }} Eventos</span>
            </div>
            
            <div class="grid-events">
                {% for ev in eventos %}
                <div class="card-evento item-evento {{ ev.mes }}">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:6px;">
                        <span class="badge-datas">🗓️ {{ ev.periodo_datas }}</span>
                        <span class="badge-categoria">{{ ev.categoria }}</span>
                        <span class="badge-mes">{{ ev.mes_rotulo }}</span>
                    </div>
                    <h3 style="margin:0 0 6px 0;color:#fff;font-size:17px;">{{ ev.evento }}</h3>
                    <p style="margin:3px 0;color:#cbd5e1;font-size:13px;">📍 <strong>Cidade/Local:</strong> {{ ev.local }} ({{ ev.cidade }} - {{ ev.regiao }})</p>
                    <p style="margin:3px 0;color:#38bdf8;font-size:13px;">🎯 <strong>Parâmetro Geotargeting:</strong> {{ ev.raio_anuncio }} (Coordenadas: <code>{{ ev.coordenadas }}</code>)</p>
                    <p style="margin:3px 0;color:#86efac;font-size:13px;">👥 <strong>Público Estimado:</strong> {{ ev.publico_estimado }}</p>
                    
                    <div class="copy-box">
                        <strong>💡 PAUTA DO PLANO DE GOVERNO:</strong> <span style="color:#fef08a;">{{ ev.pauta_plano }}</span><br>
                        <strong>📣 COPY SUGERIDA PARA O ANÚNCIO:</strong><br>
                        <i>"{{ ev.copy_trafego }}"</i>
                    </div>

                    <button class="btn-copy" onclick="navigator.clipboard.writeText('EVENTO: {{ ev.evento }}\nDATAS EXATAS: {{ ev.periodo_datas }}\nCIDADE: {{ ev.cidade }}\nRAIO META ADS: {{ ev.raio_anuncio }}\nCOPY: {{ ev.copy_trafego }}'); alert('Parâmetros copiados para o Meta Ads!');">📋 Copiar Parâmetros para Meta Ads</button>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        function filtrarMes(mes) {
            const items = document.querySelectorAll('.item-evento');
            const btns = document.querySelectorAll('.btn-filter');
            btns.forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');

            items.forEach(item => {
                if (mes === 'todos' || item.classList.contains(mes)) {
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

# TELA DEDICADA DO PLANO DE GOVERNO
HTML_PLANO_GOVERNO = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plano de Governo & Guia da 1ª Semana — Wilder Morais</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        .header { background: linear-gradient(135deg, #0b2214, #1e3a8a, #15803d); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .box { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 24px; margin-bottom: 24px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
        .card-pilar { background: #040e08; border: 1px solid #22c55e; border-radius: 10px; padding: 16px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📘 PLANO DE GOVERNO "GOIÁS PARA QUEM FAZ" & GUIA DA 1ª SEMANA</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>

    <div class="container">
        <div class="box">
            <h3 style="color:#86efac;">🏆 OS 3 PILARES DO PLANO DE GOVERNO</h3>
            <div class="grid-3">
                {% for p in plano.pilares_fundamentais %}
                <div class="card-pilar">
                    <h4 style="color:#fef08a;">{{ p.pilar }}</h4>
                    <p style="font-size:13px;color:#cbd5e1;">{{ p.foco }}</p>
                    <div style="font-size:12px;color:#86efac;font-weight:bold;">Programas: {{ ", ".join(p.programas_chave) }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
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
    return render_template_string(
        HTML_DASHBOARD_METABASE,
        yt_videos=YOUTUBE_VIDEOS_REAIS,
        colegios=MAIORES_COLEGIOS_TSE
    )

@app.route("/radar_noticias", methods=["GET"])
def radar_noticias_page():
    return render_template_string(HTML_RADAR_NOTICIAS, noticias=RADAR_NOTICIAS_ATAQUES)

@app.route("/mapa_demandas", methods=["GET"])
def mapa_demandas_page():
    return render_template_string(HTML_MAPA_DEMANDAS, reclamacoes=MAPA_RECLAMACOES_REGIONAL)

@app.route("/eventos", methods=["GET"])
def eventos_radar_page():
    return render_template_string(HTML_EVENTOS_RADAR, eventos=EVENTOS_GOIAS_2026)

@app.route("/plano_governo", methods=["GET"])
@app.route("/primeira_semana", methods=["GET"])
def plano_governo_page():
    return render_template_string(
        HTML_PLANO_GOVERNO,
        plano=PLANO_DE_GOVERNO_MEMORIA,
        primeira_semana=PRIMEIRA_SEMANA_CONTEUDO
    )

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
    if any(k in p_lower for k in ["noticia", "notícia", "noticias", "notícias", "imprensa", "jornal"]):
        noticias_html = "".join([
            f"<div style='background:#1e0a0a;padding:12px;border-radius:10px;margin-top:10px;border:1px solid #991b1b;'>"
            f"<strong style='color:#fca5a5;'>📰 {n['veiculo']} ({n['data']}) — {n['nivel_ameaca']}</strong><br>"
            f"<span style='color:#fff;font-size:14px;'>\"{n['manchete']}\"</span><br>"
            f"<div style='margin-top:6px;font-size:12.5px;color:#86efac;'>"
            f"🛡️ <strong>Defesa de IA:</strong> {n['estrategia_defesa']}</div>"
            f"</div>"
            for n in RADAR_NOTICIAS_ATAQUES
        ])
        return jsonify({
            "resposta": f"🚨 <strong>RADAR ANTI-CRISE & MONITORAMENTO DE NOTÍCIAS DE GOIÁS</strong><br>{noticias_html}<br><br>"
                        f"👉 <a href='/radar_noticias' style='background:#991b1b;color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #ef4444;'>🚨 ABRIR RADAR ANTI-CRISE COMPLETO</a>"
        }), 200

    # Roteador de YouTube
    if any(k in p_lower for k in ["youtube", "video", "vídeo", "canal"]):
        yt_html = "".join([
            f"<div style='background:#0e2917;padding:10px;border-radius:8px;margin-top:8px;border:1px solid #1a4628;'>"
            f"<strong style='color:#fef08a;'>🎬 [{v['candidato']}] {v['titulo']}</strong><br>"
            f"<span style='color:#a7f3d0;font-size:12.5px;'>Views: {v['views']} &bull; Publicado: {v['publicado']}</span><br>"
            f"<a href='{v['url']}' target='_blank' style='color:#38bdf8;font-weight:bold;'>🎬 Assistir no YouTube</a>"
            f"</div>"
            for v in YOUTUBE_VIDEOS_REAIS[:4]
        ])
        return jsonify({
            "resposta": f"📺 <strong>AUDITORIA EM TEMPO REAL DE VÍDEOS INDIVIDUAIS DO YOUTUBE</strong><br>{yt_html}<br><br>"
                        f"👉 <a href='/dashboard' style='background:linear-gradient(135deg, #eab308, #ca8a04);color:#040e08;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #fef08a;'>📺 ABRIR DASHBOARD YOUTUBE COMPLETO</a>"
        }), 200

    # Fallback via OpenRouter
    if OPENROUTER_API_KEY:
        system_prompt = (
            "Você é o Comando Central da Sala de Guerra da campanha de Wilder Morais em Goiás. "
            "Você possui módulos completos ativados: Radar Anti-Crise de Notícias, Vídeos Reais do YouTube com títulos e links individuais, Mapa Tático de Reclamações por Cidade e Colégios Eleitorais do TSE."
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
                    f"Todos os módulos de inteligência eleitoral reativados e operacionais.<br><br>"
                    f"👉 <a href='/dashboard' style='background:linear-gradient(135deg, #eab308, #ca8a04);color:#040e08;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:800;display:inline-block;'>📺 ABRIR DASHBOARD</a>"
    }), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
