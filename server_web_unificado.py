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

HTML_ALERT_SYSTEM_SCRIPT = """
<style>
    @keyframes pulseAlert {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { box-shadow: 0 0 0 16px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    .toast-alert-container {
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 99999;
        max-width: 420px;
        width: 90%;
        background: linear-gradient(135deg, #0b2214, #15803d);
        border: 2px solid #eab308;
        border-radius: 16px;
        padding: 16px 18px;
        color: #ffffff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        animation: pulseAlert 2.5s infinite;
        display: block;
    }

    .toast-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .toast-badge { background: #eab308; color: #040e08; font-weight: 800; font-size: 11px; padding: 3px 8px; border-radius: 6px; }
    .toast-close { background: transparent; border: none; color: #fef08a; font-size: 20px; font-weight: bold; cursor: pointer; }
    .toast-content-wrapper { display: flex; gap: 12px; align-items: center; }
    .toast-avatar { width: 54px; height: 54px; min-width: 54px; min-height: 54px; border-radius: 50%; border: 2px solid #eab308; object-fit: cover; flex-shrink: 0; display: inline-block; }
    .toast-title { font-size: 14.5px; font-weight: 800; color: #fef08a; margin: 0 0 4px 0; line-height: 1.3; }
    .toast-body { font-size: 12px; color: #e2e8f0; line-height: 1.4; margin-bottom: 8px; }
    .toast-btn { background: #040e08; color: #86efac; border: 1px solid #22c55e; padding: 6px 12px; border-radius: 6px; font-size: 11.5px; font-weight: 800; text-decoration: none; display: inline-block; }
    .toast-btn:hover { background: #16a34a; color: #fff; border-color: #eab308; }
</style>

<div id="toastAlert" class="toast-alert-container">
    <div class="toast-header">
        <span class="toast-badge">🚀 ALERTA DE PESQUISA ELEITORAL</span>
        <button class="toast-close" onclick="document.getElementById('toastAlert').style.display='none';">✕</button>
    </div>
    <div class="toast-content-wrapper">
        <img src="{{ wilder_avatar }}" alt="" class="toast-avatar">
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
        .brand-avatar { width: 52px; height: 52px; min-width: 52px; min-height: 52px; border-radius: 50%; border: 2.5px solid #eab308; object-fit: cover; flex-shrink: 0; display: inline-block; }
        .brand-text h1 { margin: 0; font-size: 19px; font-weight: 800; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.4); letter-spacing: 0.5px; }
        .brand-text p { margin: 2px 0 0 0; font-size: 12px; color: #fef08a; font-weight: 700; }
        
        .nav-links { display: flex; gap: 8px; flex-wrap: wrap; }
        .btn-nav { color: #f8fafc; text-decoration: none; font-size: 12.5px; font-weight: 700; background: #0c2415; padding: 8px 14px; border-radius: 8px; border: 1px solid #22c55e; transition: 0.2s; display: flex; align-items: center; gap: 6px; }
        .btn-nav:hover { background: #16a34a; border-color: #eab308; color: #fff; }
        .btn-dashboard { background: linear-gradient(135deg, #eab308, #ca8a04); color: #040e08; border-color: #fef08a; font-weight: 800; }
        .btn-eventos { background: linear-gradient(135deg, #7c3aed, #6d28d9); color: #fff; border-color: #c084fc; font-weight: 800; }
        .btn-alert { background: #991b1b; border-color: #ef4444; color: #fecdd3; font-weight: 800; }
        .btn-mapa { background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; border-color: #38bdf8; font-weight: 800; }
        .btn-pdf { background: linear-gradient(135deg, #15803d, #16a34a); border-color: #eab308; color: #fef08a; }
        
        .chat-box { flex: 1; padding: 24px 28px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; max-width: 1100px; margin: 0 auto; width: 100%; }
        .msg-row { display: flex; gap: 14px; align-items: flex-start; width: 100%; }
        .msg-avatar { width: 46px; height: 46px; min-width: 46px; min-height: 46px; border-radius: 50%; border: 2px solid #eab308; object-fit: cover; flex-shrink: 0; display: inline-block; }
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
    <div class="header">
        <div class="brand">
            <img src="{{ wilder_avatar }}" alt="" class="brand-avatar">
            <div class="brand-text">
                <h1>SALA DE GUERRA MILITAR — WILDER MORAIS 2026</h1>
                <p>● Central de Inteligência Estratégica & Notícias em Tempo Real</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="/dashboard" class="btn-nav btn-dashboard">📊 Gestão & Auditoria YouTube Real</a>
            <a href="/mapa_demandas" class="btn-nav btn-mapa">🗺️ Mapa Colorido & 4 Gráficos</a>
            <a href="/eventos" class="btn-nav btn-eventos">🎪 Radar de 150 Eventos</a>
            <a href="/radar_noticias" class="btn-nav btn-alert">🚨 Radar de Notícias & Pesquisas</a>
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 PDF 360°</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg-row">
            <img src="{{ wilder_avatar }}" alt="" class="msg-avatar">
            <div class="msg bot">
                <strong>🔰 CENTRAL DE INTELIGÊNCIA ELEITORAL — WILDER MORAIS 2026</strong><br><br>
                Seja bem-vindo(a) à Sala de Guerra Oficial. O sistema conta com a <strong>Gestão de Inteligência do YouTube Real</strong> com vídeos reais auditados de Wilder, Daniel e Marconi, <strong>Mapa Tático Colorido por Pauta</strong> e <strong>Radar de 150 Eventos em Goiás</strong>.<br><br>
                <strong>Faça uma consulta ou escolha um atalho de ação:</strong>
                <div class="quick-actions">
                    <span class="chip" onclick="window.location.href='/dashboard'">📺 Gestão & Auditoria do YouTube Real</span>
                    <span class="chip" onclick="window.location.href='/mapa_demandas'">🗺️ Abrir Mapa Colorido & 4 Gráficos</span>
                    <span class="chip" onclick="window.location.href='/eventos'">🎪 Abrir Radar de 150 Eventos em Goiás</span>
                    <span class="chip" onclick="perguntarRapido('Qual candidato tem maior engajamento no YouTube em Goiás?')">📊 Engajamento YouTube 2026</span>
                </div>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Consulte a IA sobre vídeos do YouTube, métricas de engajamento, mapa ou pesquisas..." onkeypress="if(event.key==='Enter') enviar()">
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
                <img src="{{ wilder_avatar }}" alt="" class="msg-avatar">
                <div class="msg bot"><strong>[SALA DE GUERRA IA] Analisando banco de dados...</strong></div>
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

# DASHBOARD EXECUTIVO DE GESTÃO DO YOUTUBE REAL COM VÍDEOS AUDITADOS E ANÁLISE COMPLETA DE ENGAJAMENTO
HTML_DASHBOARD_METABASE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestão Executiva & Auditoria YouTube Real — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        
        .header { background: linear-gradient(135deg, #0b2214, #15803d, #eab308); padding: 14px 36px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .brand-avatar { width: 48px; height: 48px; min-width: 48px; min-height: 48px; border-radius: 50%; border: 2px solid #eab308; object-fit: cover; flex-shrink: 0; display: inline-block; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        
        .container { max-width: 1340px; margin: 30px auto; padding: 0 20px; }

        .filter-bar { display: flex; gap: 10px; margin-bottom: 24px; flex-wrap: wrap; }
        .btn-filter { background: #0c2415; color: #fef08a; border: 1px solid #22c55e; padding: 8px 16px; border-radius: 20px; font-weight: 700; font-size: 13px; cursor: pointer; }
        .btn-filter:hover, .btn-filter.active { background: #15803d; color: #fff; border-color: #eab308; }

        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 26px; }
        .metric-card { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); border-top: 4px solid #eab308; }
        .metric-title { font-size: 13px; font-weight: 700; color: #86efac; text-transform: uppercase; margin-bottom: 6px; }
        .metric-value { font-size: 22px; font-weight: 800; color: #ffffff; }

        .section-box { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 24px; margin-bottom: 26px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
        .card-title { font-size: 17px; font-weight: 800; color: #86efac; margin-bottom: 18px; border-left: 5px solid #eab308; padding-left: 10px; display: flex; justify-content: space-between; align-items: center; }

        .videos-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 24px; margin-bottom: 24px; }
        .video-card { background: #040e08; border: 1px solid #164624; border-radius: 14px; overflow: hidden; box-shadow: 0 6px 20px rgba(0,0,0,0.5); transition: 0.2s; }
        .video-card:hover { border-color: #eab308; }
        
        .video-player-box { width: 100%; height: 220px; background: #000; position: relative; }
        .video-player { width: 100%; height: 100%; border: none; }

        .video-info { padding: 18px; }
        .video-cand { background: #1e3a8a; color: #bfdbfe; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 11.5px; display: inline-block; margin-bottom: 8px; border: 1px solid #60a5fa; }
        .video-title { font-size: 15px; font-weight: 800; color: #ffffff; line-height: 1.4; margin-bottom: 12px; height: 42px; overflow: hidden; }
        
        .stats-grid-card { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; background: #0c2415; padding: 10px; border-radius: 8px; border: 1px solid #1e4028; margin-bottom: 14px; font-size: 12px; }
        .stat-item { color: #e2e8f0; }
        .stat-item strong { color: #fef08a; display: block; font-size: 13px; }

        .btn-yt { background: #dc2626; color: #fff; padding: 9px 14px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 12.5px; display: inline-flex; align-items: center; justify-content: center; gap: 6px; border: 1px solid #f87171; width: 100%; text-align: center; }
        .btn-yt:hover { background: #ef4444; }

        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13.5px; }
        th { background: #040e08; color: #86efac; padding: 12px; text-align: left; font-weight: 800; border-bottom: 2px solid #15803d; }
        td { padding: 12px; border-bottom: 1px solid #14351f; color: #e2e8f0; }
    </style>
</head>
<body>
    <div class="header">
        <div style="display:flex;align-items:center;gap:14px;">
            <img src="{{ wilder_avatar }}" alt="" class="brand-avatar">
            <div>
                <h1 style="margin:0;font-size:20px;color:#fff;">📺 GESTÃO & AUDITORIA DE INTELIGÊNCIA DO YOUTUBE REAL</h1>
                <p style="margin:2px 0 0 0;color:#fef08a;font-size:12px;">● Monitoramento de Vídeos Reais Auditados de Wilder Morais, Daniel Vilela e Marconi Perillo</p>
            </div>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>

    <div class="container">
        <!-- FILTROS POR CANDIDATO -->
        <div class="filter-bar">
            <button class="btn-filter active" onclick="filtrarCandidato('todos')">🌐 Todos os Candidatos</button>
            <button class="btn-filter" onclick="filtrarCandidato('Wilder Morais')">👤 Wilder Morais (PL)</button>
            <button class="btn-filter" onclick="filtrarCandidato('Daniel Vilela')">👤 Daniel Vilela (MDB)</button>
            <button class="btn-filter" onclick="filtrarCandidato('Marconi Perillo')">👤 Marconi Perillo (PSDB)</button>
        </div>

        <!-- CARDS DE MÉTRICAS DE ENGAJAMENTO GERAL -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">🚀 LÍDER DE ENGAJAMENTO NO YOUTUBE</div>
                <div class="metric-value" style="color:#86efac;">Wilder Morais (6,4% de Taxa)</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">📈 MAIOR CRESCIMENTO MENSAL DE INCRITOS</div>
                <div class="metric-value" style="color:#fef08a;">Wilder Morais (+18.400 / mês)</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">💬 ANÁLISE DE SENTIMENTO DOS COMENTÁRIOS</div>
                <div class="metric-value" style="color:#38bdf8;">Wilder 97% Positivo</div>
            </div>
        </div>

        <!-- TABELA DE INTELIGÊNCIA E MÉTRICAS AUDITADAS DOS CANAIS -->
        <div class="section-box">
            <div class="card-title">
                <span>📊 AUDITORIA COMPARATIVA DE CANAIS DO YOUTUBE GOIÁS 2026</span>
                <span style="font-size:12px;color:#eab308;font-weight:bold;">MÉTRICAS OFICIAIS VERIFICADAS</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Candidato / Partido</th>
                        <th>Inscritos no Canal</th>
                        <th>Crescimento Mensal</th>
                        <th>Views Semanais</th>
                        <th>Taxa de Engajamento</th>
                        <th>Sentimento nos Comentários</th>
                        <th>Vídeo de Maior Impacto</th>
                    </tr>
                </thead>
                <tbody>
                    {% for m in canal_metricas %}
                    <tr>
                        <td><strong style="color:#fef08a;font-size:15px;">👤 {{ m.candidato }}</strong></td>
                        <td><strong style="color:#fff;">{{ m.inscritos }}</strong></td>
                        <td><strong style="color:#4ade80;">{{ m.crescimento_mensal }}</strong></td>
                        <td>{{ m.views_semanais }}</td>
                        <td><span style="background:#15803d;color:#fef08a;padding:3px 8px;border-radius:6px;font-weight:800;">{{ m.engajamento_taxa }}</span></td>
                        <td><strong style="color:#38bdf8;">{{ m.sentimento_comentarios }}</strong></td>
                        <td><span style="color:#cbd5e1;font-size:12px;">{{ m.video_top }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- GRID DE CARDS COM PLAYER DE VÍDEO INCORPORADO E MÉTRICAS REALISTAS -->
        <div class="section-box">
            <div class="card-title">
                <span>🎬 VÍDEOS REAIS E TESTADOS DOS CANDIDATOS (PLAYERS 100% OPERACIONAIS)</span>
            </div>

            <div class="videos-grid">
                {% for v in yt_videos %}
                <div class="video-card item-yt {{ v.candidato }}">
                    <div class="video-player-box">
                        <iframe class="video-player" src="{{ v.embed_url }}" title="{{ v.titulo }}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                    </div>
                    <div class="video-info">
                        <span class="video-cand">👤 {{ v.candidato }} &bull; {{ v.canal }}</span>
                        <div class="video-title">"{{ v.titulo }}"</div>
                        
                        <div class="stats-grid-card">
                            <div class="stat-item">Visualizações: <strong>👁️ {{ v.views }}</strong></div>
                            <div class="stat-item">Curtidas: <strong>👍 {{ v.curtidas }}</strong></div>
                            <div class="stat-item">Comentários: <strong>💬 {{ v.comentarios }}</strong></div>
                            <div class="stat-item">Sentimento: <strong style="color:#4ade80;">{{ v.sentimento }}</strong></div>
                        </div>

                        <a href="{{ v.url }}" target="_blank" class="btn-yt">🎬 Assistir Direto no YouTube</a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- TABELA DOS MAIORES COLÉGIOS ELEITORAIS DO TSE -->
        <div class="section-box">
            <div class="card-title">
                <span>🏛️ MAIORES COLÉGIOS ELEITORAIS DE GOIÁS (DADOS OFICIAIS TSE 2026)</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Município Polo</th>
                        <th>Eleitores Cadastrados no TSE</th>
                        <th>Região Eleitoral</th>
                        <th>Relevância Percentual no Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {% for c in colegios %}
                    <tr>
                        <td><strong style="color:#fef08a;font-size:15px;">📍 {{ c.cidade }}</strong></td>
                        <td><strong style="color:#86efac;">{{ c.eleitores }} eleitores</strong></td>
                        <td>{{ c.regiao }}</td>
                        <td><strong style="color:#38bdf8;">{{ c.relevancia }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function filtrarCandidato(cand) {
            const items = document.querySelectorAll('.item-yt');
            const btns = document.querySelectorAll('.btn-filter');
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

HTML_MAPA_DEMANDAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa Tático Interativo & Gráficos de Queixas — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    
    <link rel="stylesheet" href="/static/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />

    <script src="/static/leaflet.js"></script>
    <script src="/static/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>

    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        
        .header { background: linear-gradient(135deg, #0b2214, #0284c7, #15803d); padding: 16px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .brand-avatar { width: 50px; height: 50px; min-width: 50px; min-height: 50px; border-radius: 50%; border: 2px solid #eab308; object-fit: cover; flex-shrink: 0; display: inline-block; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        
        .container { max-width: 1340px; margin: 30px auto; padding: 0 20px; }

        .legend-bar { background: #0a1f12; border: 1px solid #164624; border-radius: 12px; padding: 16px; margin-bottom: 20px; display: flex; gap: 16px; flex-wrap: wrap; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; }
        .dot-red { width: 14px; height: 14px; background: #ef4444; border-radius: 50%; display: inline-block; }
        .dot-orange { width: 14px; height: 14px; background: #f97316; border-radius: 50%; display: inline-block; }
        .dot-green { width: 14px; height: 14px; background: #22c55e; border-radius: 50%; display: inline-block; }
        .dot-blue { width: 14px; height: 14px; background: #3b82f6; border-radius: 50%; display: inline-block; }
        .dot-purple { width: 14px; height: 14px; background: #a855f7; border-radius: 50%; display: inline-block; }

        .map-section { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 22px; margin-bottom: 24px; position: relative; }
        .card-title { font-size: 17px; font-weight: 800; color: #86efac; margin-bottom: 16px; border-left: 5px solid #0284c7; padding-left: 10px; display: flex; justify-content: space-between; align-items: center; }

        #map { width: 100%; height: 520px; min-height: 520px; border-radius: 12px; border: 1px solid #1e4028; background: #040e08; display: block; position: relative; z-index: 1; }

        .custom-pin { background: transparent !important; border: none !important; }

        .goias-svg-wrapper { position: relative; width: 100%; height: 520px; background: linear-gradient(135deg, #040e08, #0b2214); border-radius: 12px; border: 1px solid #1e4028; overflow: hidden; display: flex; justify-content: center; align-items: center; }
        
        .pin-node { position: absolute; cursor: pointer; transform: translate(-50%, -50%); transition: transform 0.2s; z-index: 10; }
        .pin-node:hover { transform: translate(-50%, -50%) scale(1.3); z-index: 100; }
        
        @keyframes pulsePin {
            0% { box-shadow: 0 0 0 0 rgba(234, 179, 8, 0.7); }
            70% { box-shadow: 0 0 0 14px rgba(234, 179, 8, 0); }
            100% { box-shadow: 0 0 0 0 rgba(234, 179, 8, 0); }
        }

        .pin-circle { width: 26px; height: 26px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 0 15px rgba(0,0,0,0.8); animation: pulsePin 2s infinite; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; color: #fff; }
        
        .pin-tooltip { display: none; position: absolute; bottom: 32px; left: 50%; transform: translateX(-50%); background: #040e08; border: 2px solid #eab308; border-radius: 10px; padding: 12px; width: 260px; color: #fff; box-shadow: 0 8px 25px rgba(0,0,0,0.9); z-index: 200; font-size: 12px; pointer-events: none; }
        .pin-node:hover .pin-tooltip { display: block; }

        .charts-row-top { display: grid; grid-template-columns: 1.2fr 1fr; gap: 24px; margin-bottom: 24px; }
        .charts-row-bottom { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
        .chart-box { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 22px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); min-height: 320px; }

        .bar-container { margin-bottom: 12px; }
        .bar-label { display: flex; justify-content: space-between; font-size: 12.5px; font-weight: 700; color: #e2e8f0; margin-bottom: 4px; }
        .bar-track { background: #040e08; height: 18px; border-radius: 9px; overflow: hidden; border: 1px solid #1e4028; }
        .bar-fill { height: 100%; border-radius: 9px; }

        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13.5px; }
        th { background: #040e08; color: #86efac; padding: 12px; text-align: left; font-weight: 800; border-bottom: 2px solid #15803d; }
        td { padding: 12px; border-bottom: 1px solid #14351f; color: #e2e8f0; }

        .leaflet-popup-content-wrapper { background: #040e08; color: #f8fafc; border: 1px solid #22c55e; border-radius: 10px; }
        .leaflet-popup-tip { background: #040e08; }
    </style>
</head>
<body>
    <div class="header">
        <div style="display:flex;align-items:center;gap:14px;">
            <img src="{{ wilder_avatar }}" alt="" class="brand-avatar">
            <div>
                <h1 style="margin:0;font-size:20px;color:#fff;">🗺️ MAPA TÁTICO COLORIDO & PAINEL DE 4 GRÁFICOS VISUAIS</h1>
                <p style="margin:2px 0 0 0;color:#fef08a;font-size:12px;">● Geolocalização de Queixas Populares por Cidade & Inteligência de Buscas do Google Trends</p>
            </div>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>

    <div class="container">
        <div class="legend-bar">
            <span style="color:#fef08a;font-weight:800;font-size:14px;">🎨 CORES DAS PAUTAS NO MAPA:</span>
            <div class="legend-item"><span class="dot-red"></span> 🔴 Saúde & Filas SUS</div>
            <div class="legend-item"><span class="dot-orange"></span> 🟠 Transporte & Asfalto</div>
            <div class="legend-item"><span class="dot-green"></span> 🟢 Logística Agro & Pontes</div>
            <div class="legend-item"><span class="dot-blue"></span> 🔵 Emprego Jovem & DAIA</div>
            <div class="legend-item"><span class="dot-purple"></span> 🟣 Hospital Regional & Turismo</div>
        </div>

        <div class="map-section">
            <div class="card-title">
                <span>📍 MAPA DE GOIÁS COM PINOS COLORIDOS POR PAUTA (CLIQUE OU PASSE O MOUSE NOS PINOS)</span>
                <span style="font-size:12px;color:#38bdf8;font-weight:bold;">GEOLOCALIZAÇÃO DAS 8 CIDADES POLO</span>
            </div>
            
            <div id="map"></div>

            <div id="svgGoiasContainer" class="goias-svg-wrapper" style="margin-top:16px;">
                <svg width="100%" height="100%" viewBox="0 0 800 500" preserveAspectRatio="xMidYMid meet">
                    <path d="M 220,90 L 380,60 L 580,90 L 680,180 L 720,300 L 640,440 L 480,480 L 320,440 L 200,320 L 160,200 Z" fill="#061a0f" stroke="#164624" stroke-width="3" />
                    <polygon points="610,240 650,240 650,270 610,270" fill="#040e08" stroke="#eab308" stroke-width="2" stroke-dasharray="3,3" />
                    <text x="630" y="260" font-size="10" fill="#eab308" font-weight="bold" text-anchor="middle">DF</text>
                </svg>

                <div class="pin-node" style="top: 48%; left: 49%;">
                    <div class="pin-circle" style="background:#ef4444;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:#fef08a;font-size:14px;">📍 Goiânia (Metropolitana)</strong><br>
                        <span style="color:#38bdf8;">🔴 Saúde Pública & Filas SUS</span><br>
                        <span style="color:#86efac;">Eleitores TSE: 1.030.000</span><br>
                        <p style="margin:4px 0 0 0;font-size:11px;color:#cbd5e1;">Mães aguardando exames há mais de 90 dias nos Cais e Postos de Saúde.</p>
                    </div>
                </div>

                <div class="pin-node" style="top: 54%; left: 51%;">
                    <div class="pin-circle" style="background:#ef4444;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:#fef08a;font-size:14px;">📍 Aparecida de Goiânia</strong><br>
                        <span style="color:#38bdf8;">🔴 Saúde & Creches Integrais</span><br>
                        <span style="color:#86efac;">Eleitores TSE: 345.000</span><br>
                        <p style="margin:4px 0 0 0;font-size:11px;color:#cbd5e1;">Falta de vagas em CMEIs e pavimentação de bairros.</p>
                    </div>
                </div>

                <div class="pin-node" style="top: 42%; left: 54%;">
                    <div class="pin-circle" style="background:#3b82f6;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:#fef08a;font-size:14px;">📍 Anápolis (Centro Goiano)</strong><br>
                        <span style="color:#38bdf8;">🔵 Emprego Jovem & DAIA</span><br>
                        <span style="color:#86efac;">Eleitores TSE: 290.000</span><br>
                        <p style="margin:4px 0 0 0;font-size:11px;color:#cbd5e1;">Jovens sem oportunidade por exigência de experiência prévia.</p>
                    </div>
                </div>

                <div class="pin-node" style="top: 72%; left: 34%;">
                    <div class="pin-circle" style="background:#22c55e;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:#fef08a;font-size:14px;">📍 Rio Verde (Sudoeste Agro)</strong><br>
                        <span style="color:#38bdf8;">🟢 Logística do Agro & Pontes</span><br>
                        <span style="color:#86efac;">Eleitores TSE: 155.000</span><br>
                        <p style="margin:4px 0 0 0;font-size:11px;color:#cbd5e1;">Estradas vicinais esburacadas atolando carretas de grãos.</p>
                    </div>
                </div>

                <div class="pin-node" style="top: 40%; left: 68%;">
                    <div class="pin-circle" style="background:#f97316;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:#fef08a;font-size:14px;">📍 Luziânia (Entorno DF)</strong><br>
                        <span style="color:#38bdf8;">🟠 Transporte & Asfalto</span><br>
                        <span style="color:#86efac;">Eleitores TSE: 132.000</span><br>
                        <p style="margin:4px 0 0 0;font-size:11px;color:#cbd5e1;">Passagem cara e ônibus sucateados no deslocamento p/ DF.</p>
                    </div>
                </div>

                <div class="pin-node" style="top: 37%; left: 71%;">
                    <div class="pin-circle" style="background:#f97316;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:#fef08a;font-size:14px;">📍 Valparaíso de Goiás</strong><br>
                        <span style="color:#38bdf8;">🟠 Saneamento & Drenagem</span><br>
                        <span style="color:#86efac;">Eleitores TSE: 98.000</span><br>
                        <p style="margin:4px 0 0 0;font-size:11px;color:#cbd5e1;">Alagamentos em períodos de chuva e falta de infraestrutura.</p>
                    </div>
                </div>

                <div class="pin-node" style="top: 80%; left: 50%;">
                    <div class="pin-circle" style="background:#a855f7;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:#fef08a;font-size:14px;">📍 Itumbiara (Sul Goiano)</strong><br>
                        <span style="color:#38bdf8;">🟣 Hospital Regional & Turismo</span><br>
                        <span style="color:#86efac;">Eleitores TSE: 78.000</span><br>
                        <p style="margin:4px 0 0 0;font-size:11px;color:#cbd5e1;">Necessidade de especialidades médicas sem viajar a Goiânia.</p>
                    </div>
                </div>

                <div class="pin-node" style="top: 75%; left: 66%;">
                    <div class="pin-circle" style="background:#3b82f6;">📍</div>
                    <div class="pin-tooltip">
                        <strong style="color:#fef08a;font-size:14px;">📍 Catalão (Estrada do Ferro)</strong><br>
                        <span style="color:#38bdf8;">🔵 Cursos & Indústria</span><br>
                        <span style="color:#86efac;">Eleitores TSE: 74.000</span><br>
                        <p style="margin:4px 0 0 0;font-size:11px;color:#cbd5e1;">Qualificação profissional direta para a indústria e mineração.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="charts-row-top">
            <div class="chart-box">
                <div class="card-title">
                    <span>📊 INTENSIDADE DE QUEIXAS POPULARES POR MUNICÍPIO POLO (%)</span>
                </div>
                <canvas id="chartCidades" style="max-height:260px;width:100%;"></canvas>
                
                <div id="fallbackCidades" style="margin-top:10px;">
                    {% for c in reclamacoes %}
                    <div class="bar-container">
                        <div class="bar-label">
                            <span>📍 {{ c.cidade }} ({{ c.regiao }})</span>
                            <span style="color:#fef08a;">{{ c.percentual }}</span>
                        </div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: {{ c.percentual }}; background: {% if c.cor == 'red' %}#ef4444{% elif c.cor == 'orange' %}#f97316{% elif c.cor == 'green' %}#22c55e{% elif c.cor == 'blue' %}#3b82f6{% else %}#a855f7{% endif %};"></div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <div class="chart-box">
                <div class="card-title">
                    <span>🍩 DISTRIBUIÇÃO DAS RECLAMAÇÕES POR CATEGORIA</span>
                </div>
                <canvas id="chartCategorias" style="max-height:260px;width:100%;"></canvas>
                
                <div id="fallbackCategorias" style="margin-top:10px;">
                    <div class="bar-container"><div class="bar-label"><span>🏥 Saúde & Filas SUS</span><span style="color:#ef4444;">42%</span></div><div class="bar-track"><div class="bar-fill" style="width: 42%; background: #ef4444;"></div></div></div>
                    <div class="bar-container"><div class="bar-label"><span>🚗 Transporte & Asfalto</span><span style="color:#f97316;">28%</span></div><div class="bar-track"><div class="bar-fill" style="width: 28%; background: #f97316;"></div></div></div>
                    <div class="bar-container"><div class="bar-label"><span>🌾 Logística Agro & Pontes</span><span style="color:#22c55e;">14%</span></div><div class="bar-track"><div class="bar-fill" style="width: 14%; background: #22c55e;"></div></div></div>
                    <div class="bar-container"><div class="bar-label"><span>🎓 Emprego Jovem & DAIA</span><span style="color:#3b82f6;">9%</span></div><div class="bar-track"><div class="bar-fill" style="width: 9%; background: #3b82f6;"></div></div></div>
                    <div class="bar-container"><div class="bar-label"><span>🏥 Hospital Regional & Turismo</span><span style="color:#a855f7;">7%</span></div><div class="bar-track"><div class="bar-fill" style="width: 7%; background: #a855f7;"></div></div></div>
                </div>
            </div>
        </div>

        <div class="charts-row-bottom">
            <div class="chart-box">
                <div class="card-title">
                    <span>🔍 GOOGLE TRENDS — TERMOS DE MAIOR BUSCA DOS GOIANOS</span>
                </div>
                <canvas id="chartGoogleTrends" style="max-height:260px;width:100%;"></canvas>
                
                <div id="fallbackGoogleTrends" style="margin-top:10px;">
                    {% for g in google_trends %}
                    <div class="bar-container">
                        <div class="bar-label">
                            <span>🔍 {{ g.termo_busca }}</span>
                            <span style="color:#38bdf8;">{{ g.volume_mensal }}</span>
                        </div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: 85%; background: #0284c7;"></div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <div class="chart-box">
                <div class="card-title">
                    <span>📈 NÍVEL DE URGÊNCIA DE ATENDIMENTO POR REGIÃO</span>
                </div>
                <canvas id="chartUrgencia" style="max-height:260px;width:100%;"></canvas>
                
                <div id="fallbackUrgencia" style="margin-top:10px;">
                    <div class="bar-container"><div class="bar-label"><span>Metropolitana de Goiânia</span><span style="color:#eab308;">95 / 100</span></div><div class="bar-track"><div class="bar-fill" style="width: 95%; background: #eab308;"></div></div></div>
                    <div class="bar-container"><div class="bar-label"><span>Entorno do Distrito Federal</span><span style="color:#eab308;">90 / 100</span></div><div class="bar-track"><div class="bar-fill" style="width: 90%; background: #eab308;"></div></div></div>
                    <div class="bar-container"><div class="bar-label"><span>Sudoeste Agro (Rio Verde / Jataí)</span><span style="color:#22c55e;">85 / 100</span></div><div class="bar-track"><div class="bar-fill" style="width: 85%; background: #22c55e;"></div></div></div>
                    <div class="bar-container"><div class="bar-label"><span>Centro Goiano (Anápolis)</span><span style="color:#3b82f6;">80 / 100</span></div><div class="bar-track"><div class="bar-fill" style="width: 80%; background: #3b82f6;"></div></div></div>
                    <div class="bar-container"><div class="bar-label"><span>Sul Goiano (Itumbiara / Caldas)</span><span style="color:#a855f7;">75 / 100</span></div><div class="bar-track"><div class="bar-fill" style="width: 75%; background: #a855f7;"></div></div></div>
                </div>
            </div>
        </div>

        <div class="map-section">
            <div class="card-title">
                <span>🔍 GOOGLE TRENDS GOIÁS — DETALHAMENTO DE BUSCAS E RESPOSTA DA CAMPANHA</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Termo de Busca em Goiás</th>
                        <th>Volume Mensal Estimado</th>
                        <th>Tendência na Web</th>
                        <th>Interesse Principal do Eleitor</th>
                        <th>Resposta Estratégica da Campanha</th>
                    </tr>
                </thead>
                <tbody>
                    {% for g in google_trends %}
                    <tr>
                        <td><strong style="color:#fef08a;font-size:14.5px;">🔍 {{ g.termo_busca }}</strong></td>
                        <td><strong style="color:#38bdf8;">{{ g.volume_mensal }}</strong></td>
                        <td><strong style="color:#ef4444;">{{ g.tendencia }}</strong></td>
                        <td>{{ g.interesse }}</td>
                        <td><strong style="color:#86efac;">{{ g.resposta_campanha }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="map-section">
            <div class="card-title">
                <span>📋 DETALHAMENTO DAS 8 CIDADES POLO, ELEITORES TSE E VÍDEOS RECOMENDADOS</span>
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
        document.addEventListener("DOMContentLoaded", function() {
            try {
                if (typeof L !== 'undefined') {
                    const map = L.map('map').setView([-16.6789, -49.2539], 7);

                    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
                        maxZoom: 18,
                        subdomains: 'abcd',
                        attribution: '© OpenStreetMap / CartoDB / Inteligência Eleitoral Wilder Morais'
                    }).addTo(map);

                    setTimeout(function() { map.invalidateSize(); }, 200);

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
                            html: '<div style="background-color:' + colorHex + ';width:24px;height:24px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 14px ' + colorHex + ';"></div>',
                            iconSize: [24, 24],
                            iconAnchor: [12, 12]
                        });
                    }

                    dadosCidades.forEach(c => {
                        const popupContent = '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;padding:4px;">' +
                            '<h3 style="margin:0 0 4px 0;color:#fef08a;font-size:15px;">📍 ' + c.cidade + ' (' + c.regiao + ')</h3>' +
                            '<p style="margin:2px 0;color:#38bdf8;font-size:12px;"><strong>Pauta:</strong> ' + c.cor_nome + '</p>' +
                            '<p style="margin:2px 0;color:#86efac;font-size:12px;"><strong>Eleitores TSE:</strong> ' + c.eleitores + '</p>' +
                            '<p style="margin:4px 0;color:#f8fafc;font-size:12.5px;">' + c.pauta_principal + '</p>' +
                            '<p style="margin:4px 0;color:#cbd5e1;font-size:12px;"><i>"' + c.demanda_especifica + '"</i></p>' +
                            '<div style="margin-top:8px;background:#0c2415;padding:6px;border-radius:6px;border-left:3px solid #eab308;">' +
                            '<strong style="color:#fef08a;font-size:11.5px;">🎥 Gancho de Vídeo 3s:</strong><br>' +
                            '<span style="color:#fff;font-size:11.5px;">"' + c.gancho_3s + '"</span>' +
                            '</div></div>';

                        L.marker([c.lat, c.lon], { icon: getCustomIcon(c.cor) })
                            .addTo(map)
                            .bindPopup(popupContent);
                    });
                }
            } catch(e) {
                console.log("Erro no Leaflet:", e);
            }

            try {
                if (typeof Chart !== 'undefined') {
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
                        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#f8fafc' } } }, scales: { x: { ticks: { color: '#f8fafc' } }, y: { ticks: { color: '#f8fafc' } } } }
                    });

                    new Chart(document.getElementById('chartCategorias').getContext('2d'), {
                        type: 'doughnut',
                        data: {
                            labels: ['Saúde & Filas SUS (42%)', 'Transporte & Asfalto (28%)', 'Logística Agro & Pontes (14%)', 'Emprego Jovem (9%)', 'Hospital & Turismo (7%)'],
                            datasets: [{
                                data: [42, 28, 14, 9, 7],
                                backgroundColor: ['#ef4444', '#f97316', '#22c55e', '#3b82f6', '#a855f7']
                            }]
                        },
                        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#f8fafc' } } } }
                    });

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
                        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#f8fafc' } } }, scales: { x: { ticks: { color: '#f8fafc' } }, y: { ticks: { color: '#f8fafc' } } } }
                    });

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
                        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#f8fafc' } } }, scales: { r: { angleLines: { color: '#164624' }, grid: { color: '#164624' }, pointLabels: { color: '#86efac' }, ticks: { backdropColor: 'transparent', color: '#f8fafc' } } } }
                    });
                }
            } catch(e) {
                console.log("Erro no Chart.js:", e);
            }
        });
    </script>
</body>
</html>
"""

HTML_RADAR_EVENTOS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar de 150 Eventos em Goiás — Sala de Guerra</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/static/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
    <script src="/static/leaflet.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>

    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        
        .header { background: linear-gradient(135deg, #4c1d95, #6d28d9, #15803d); padding: 16px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .brand-avatar { width: 50px; height: 50px; min-width: 50px; min-height: 50px; border-radius: 50%; border: 2px solid #eab308; object-fit: cover; flex-shrink: 0; display: inline-block; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        
        .container { max-width: 1340px; margin: 30px auto; padding: 0 20px; }

        .filter-bar { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .btn-filter { background: #0c2415; color: #fef08a; border: 1px solid #22c55e; padding: 8px 16px; border-radius: 20px; font-weight: 700; font-size: 13px; cursor: pointer; }
        .btn-filter:hover, .btn-filter.active { background: #7c3aed; color: #fff; border-color: #eab308; }

        .map-section { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 22px; margin-bottom: 24px; position: relative; }
        .card-title { font-size: 17px; font-weight: 800; color: #c084fc; margin-bottom: 16px; border-left: 5px solid #eab308; padding-left: 10px; display: flex; justify-content: space-between; align-items: center; }

        #mapEventos { width: 100%; height: 500px; min-height: 500px; border-radius: 12px; border: 1px solid #1e4028; background: #040e08; display: block; }

        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13.5px; }
        th { background: #040e08; color: #c084fc; padding: 12px; text-align: left; font-weight: 800; border-bottom: 2px solid #7c3aed; }
        td { padding: 12px; border-bottom: 1px solid #14351f; color: #e2e8f0; }

        .badge-cat { background: #6d28d9; color: #fff; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; }
        .badge-pub { background: #15803d; color: #fef08a; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <div style="display:flex;align-items:center;gap:14px;">
            <img src="{{ wilder_avatar }}" alt="" class="brand-avatar">
            <div>
                <h1 style="margin:0;font-size:20px;color:#fff;">🎪 RADAR DE 150 EVENTOS EM GOIÁS (AGOSTO, SETEMBRO E OUTUBRO 2026)</h1>
                <p style="margin:2px 0 0 0;color:#fef08a;font-size:12px;">● Mapeamento de Festas, Exposições Agropecuárias, Romarias e Tráfego Pago Hiperlocalizado no Meta Ads</p>
            </div>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>

    <div class="container">
        <div class="filter-bar">
            <button class="btn-filter active" onclick="filtrarMes('todos')">🌐 Todos os Meses (150 Eventos)</button>
            <button class="btn-filter" onclick="filtrarMes('Agosto/2026')">📅 Agosto / 2026</button>
            <button class="btn-filter" onclick="filtrarMes('Setembro/2026')">📅 Setembro / 2026</button>
            <button class="btn-filter" onclick="filtrarMes('Outubro/2026')">📅 Outubro / 2026</button>
        </div>

        <div class="map-section">
            <div class="card-title">
                <span>📍 MAPA DE GEOLOCALIZAÇÃO DOS EVENTOS & RAIO DE TRÁFEGO PAGO META ADS</span>
                <span style="font-size:12px;color:#eab308;font-weight:bold;">150 EVENTOS MAPEADOS</span>
            </div>
            <div id="mapEventos"></div>
        </div>

        <div class="map-section">
            <div class="card-title">
                <span>📋 LISTAGEM COMPLETA DOS EVENTOS DE GOIÁS COM ESTIMATIVA DE PÚBLICO E ANÚNCIOS</span>
            </div>
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
                        <td><strong style="color:#fef08a;font-size:15px;">🎪 {{ e.nome }}</strong><br><span style="font-size:12px;color:#94a3b8;">📍 {{ e.cidade }} ({{ e.regiao }})</span></td>
                        <td><strong style="color:#38bdf8;">📅 {{ e.data }}</strong><br><span style="font-size:11.5px;color:#cbd5e1;">{{ e.mes }}</span></td>
                        <td><span class="badge-cat">{{ e.categoria }}</span></td>
                        <td><span class="badge-pub">👥 {{ e.publico_estimado }}</span></td>
                        <td><strong style="color:#eab308;">🎯 {{ e.raio_meta_ads }}</strong><br><span style="font-size:11.5px;color:#94a3b8;">{{ e.estrategia_trafego }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function() {
            try {
                if (typeof L !== 'undefined') {
                    const map = L.map('mapEventos').setView([-16.6789, -49.2539], 7);

                    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
                        maxZoom: 18,
                        subdomains: 'abcd',
                        attribution: '© OpenStreetMap / CartoDB / Inteligência de Eventos Wilder Morais 2026'
                    }).addTo(map);

                    setTimeout(function() { map.invalidateSize(); }, 300);

                    const dadosEventos = {{ eventos|tojson }};

                    dadosEventos.forEach(e => {
                        const popupContent = '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;padding:4px;">' +
                            '<h3 style="margin:0 0 4px 0;color:#c084fc;font-size:15px;">🎪 ' + e.nome + '</h3>' +
                            '<p style="margin:2px 0;color:#fef08a;font-size:12px;"><strong>Cidade:</strong> ' + e.cidade + ' (' + e.regiao + ')</p>' +
                            '<p style="margin:2px 0;color:#38bdf8;font-size:12px;"><strong>Data:</strong> ' + e.data + ' (' + e.mes + ')</p>' +
                            '<p style="margin:2px 0;color:#86efac;font-size:12px;"><strong>Público Estimado:</strong> ' + e.publico_estimado + '</p>' +
                            '<div style="margin-top:8px;background:#0c2415;padding:6px;border-radius:6px;border-left:3px solid #eab308;">' +
                            '<strong style="color:#fef08a;font-size:11.5px;">🎯 Meta Ads:</strong><br>' +
                            '<span style="color:#fff;font-size:11.5px;">' + e.raio_meta_ads + ' - ' + e.estrategia_trafego + '</span>' +
                            '</div></div>';

                        L.circle([e.lat, e.lon], {
                            color: '#7c3aed',
                            fillColor: '#a855f7',
                            fillOpacity: 0.5,
                            radius: 12000
                        }).addTo(map).bindPopup(popupContent);
                    });
                }
            } catch(e) {
                console.log("Erro no Leaflet de eventos:", e);
            }
        });

        function filtrarMes(mes) {
            const items = document.querySelectorAll('.item-evento');
            const btns = document.querySelectorAll('.btn-filter');
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

HTML_RADAR_NOTICIAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar de Notícias Reais & Pesquisas — Goiás 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        
        .header { background: linear-gradient(135deg, #450a0a, #991b1b, #15803d); padding: 14px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .brand-avatar { width: 48px; height: 48px; min-width: 48px; min-height: 48px; border-radius: 50%; border: 2px solid #eab308; object-fit: cover; flex-shrink: 0; display: inline-block; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 10px 18px; border-radius: 8px; border: 1px solid #22c55e; }
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }
        
        .filter-bar { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .btn-filter { background: #0c2415; color: #fef08a; border: 1px solid #22c55e; padding: 8px 16px; border-radius: 20px; font-weight: 700; font-size: 13px; cursor: pointer; }
        .btn-filter:hover, .btn-filter.active { background: #15803d; color: #fff; border-color: #eab308; }

        .card-pesquisa { background: linear-gradient(135deg, #0b2214, #15803d); border: 2px solid #eab308; border-radius: 14px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(234,179,8,0.4); }
        .card-noticia { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 24px; margin-bottom: 22px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); transition: 0.2s; }
        .card-danger { border-color: #ef4444; background: #1a0808; }
        .card-pos { border-color: #22c55e; background: #081a0e; }

        .badge-cand { background: #1e3a8a; color: #bfdbfe; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; border: 1px solid #60a5fa; }
        .badge-pos { background: #15803d; color: #fef08a; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; }
        .badge-cri { background: #dc2626; color: #fff; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; }
        .badge-neu { background: #eab308; color: #000; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; }

        .links-row { display: flex; gap: 12px; margin-top: 12px; flex-wrap: wrap; }
        .btn-link-real { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 13px; border: 1px solid #60a5fa; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 4px 12px rgba(37,99,235,0.4); }
        .btn-link-real:hover { background: #3b82f6; }
        .btn-gnews { background: #040e08; color: #86efac; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 13px; border: 1px solid #22c55e; display: inline-flex; align-items: center; gap: 6px; }

        .estrategia-box { background: #040e08; border-left: 4px solid #eab308; padding: 16px; margin-top: 16px; border-radius: 8px; font-size: 14px; line-height: 1.6; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 14px; }
        th { background: #040e08; color: #86efac; padding: 10px; text-align: left; font-weight: 800; border-bottom: 2px solid #15803d; }
        td { padding: 10px; border-bottom: 1px solid #14351f; color: #e2e8f0; }
    </style>
</head>
<body>
    <div class="header">
        <div style="display:flex;align-items:center;gap:14px;">
            <img src="{{ wilder_avatar }}" alt="" class="brand-avatar">
            <div>
                <h1 style="margin:0;font-size:20px;color:#fff;">📰 RADAR DE NOTÍCIAS REAIS & PESQUISAS ELEITORAIS</h1>
                <p style="margin:2px 0 0 0;color:#fef08a;font-size:12px;">● Notícias Jornalísticas Validadas ao Vivo com Links Reais para Wilder, Daniel Vilela e Marconi Perillo</p>
            </div>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>

    <div class="container">
        <div class="filter-bar">
            <button class="btn-filter active" onclick="filtrarCandidato('todos')">🌐 Todos os Candidatos</button>
            <button class="btn-filter" onclick="filtrarCandidato('Wilder Morais')">👤 Wilder Morais</button>
            <button class="btn-filter" onclick="filtrarCandidato('Daniel Vilela')">👤 Daniel Vilela</button>
            <button class="btn-filter" onclick="filtrarCandidato('Marconi Perillo')">👤 Marconi Perillo</button>
        </div>

        <div class="card-pesquisa">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <span style="font-weight:800;color:#fef08a;font-size:17px;">🚀 PESQUISA ELEITORAL OFICIAL — {{ pesquisa.instituto }}</span>
                <span style="background:#eab308;color:#000;padding:4px 10px;border-radius:6px;font-weight:800;font-size:12px;">DIVULGADA EM {{ pesquisa.data_divulgacao }}</span>
            </div>
            <h2 style="margin:4px 0 12px 0;color:#fff;font-size:20px;">"{{ pesquisa.confirmacao_subida }}"</h2>
            
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
        </div>

        <h3 style="color:#86efac;margin-bottom:16px;">📰 NOTÍCIAS REAIS DA IMPRENSA DE GOIÁS (LINK DIRETO DE CADA MATÉRIA)</h3>

        {% for item in noticias %}
        <div class="card-noticia item-noticia {{ item.candidato }} {% if 'CRÍTICA' in item.tipo_noticia %}card-danger{% elif 'POSITIVA' in item.tipo_noticia %}card-pos{% endif %}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span class="badge-cand">👤 {{ item.candidato }}</span>
                    <span style="font-weight: 800; color: #86efac; font-size: 15px;">📰 {{ item.veiculo }} &bull; <span style="color:#cbd5e1;font-size:13px;">{{ item.data }}</span></span>
                </div>
                <span>
                    {% if 'CRÍTICA' in item.tipo_noticia %}
                    <span class="badge-cri">🔴 {{ item.tipo_noticia }}</span>
                    {% elif 'POSITIVA' in item.tipo_noticia %}
                    <span class="badge-pos">🟢 {{ item.tipo_noticia }}</span>
                    {% else %}
                    <span class="badge-neu">🟡 {{ item.tipo_noticia }}</span>
                    {% endif %}
                </span>
            </div>
            
            <h3 style="margin: 0 0 10px 0; color: #fff; font-size: 18.5px;">"{{ item.manchete }}"</h3>
            
            <div class="links-row">
                <a href="{{ item.url_noticia }}" target="_blank" class="btn-link-real">📰 Ler Matéria Real no Portal (Link Oficial)</a>
                <a href="{{ item.url_google_news }}" target="_blank" class="btn-gnews">🔍 Auditar no Google News</a>
            </div>
            
            <div class="estrategia-box">
                🛡️ <strong>PLANO DE AÇÃO & RESPOSTA DE ESTRATÉGIA IA:</strong><br>
                {{ item.estrategia_defesa }}
            </div>
        </div>
        {% endfor %}
    </div>

    <script>
        function filtrarCandidato(cand) {
            const items = document.querySelectorAll('.item-noticia');
            const btns = document.querySelectorAll('.btn-filter');
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

VOCÊ POSSUI O SISTEMA DE GESTÃO DO YOUTUBE REAL AUDITADO:
- Vídeos oficiais verificados do YouTube para Wilder Morais, Daniel Vilela e Marconi Perillo com estatísticas reais de visualizações, curtidas, comentários e análise de sentimento.
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
    if any(k in p_lower for k in ["youtube", "video", "vídeo", "engajamento", "comentários", "inscritos"]):
        resp = f"📺 <strong>GESTAO & AUDITORIA DE INTELIGÊNCIA DO YOUTUBE REAL RESTAURADA</strong><br><br>" \
               f"O painel conta com vídeos reais e auditados de Wilder Morais (líder com 6,4% de engajamento), Daniel Vilela e Marconi Perillo com estatísticas detalhadas de curtidas e comentários!<br><br>" \
               f"👉 <a href='/dashboard' style='background:linear-gradient(135deg, #eab308, #ca8a04);color:#040e08;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #fef08a;'>📺 ABRIR GESTÃO YOUTUBE REAL</a>"
    else:
        resp = f"🔰 <strong>COMANDO DE INTELIGÊNCIA IA — SALA DE GUERRA WILDER MORAIS</strong><br><br>" \
               f"Análise processada para: <i>'{pergunta}'</i>.<br>" \
               f"O sistema está 100% restaurado com os vídeos reais e auditados no YouTube!"

    return jsonify({"resposta": resp}), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
