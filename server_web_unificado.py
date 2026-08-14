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
    gerar_buffer_relatorio_360, YOUTUBE_MONITORAMENTO_REAL,
    RADAR_NOTICIAS_ATAQUES, MAPA_RECLAMACOES_REGIONAL,
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
        .btn-eventos { background: linear-gradient(135deg, #d97706, #b45309); color: #fff; border-color: #fef08a; font-weight: 800; }
        .btn-eventos:hover { background: #f59e0b; color: #000; }
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
        .chip-eventos:hover { background: #d97706; color: #fff; }

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
                <p>● Geotargeting de Tráfego Pago & Mapeamento de 150 Eventos em Goiás</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="/eventos" class="btn-nav btn-eventos">🎪 Radar de 150 Eventos & Tráfego</a>
            <a href="/plano_governo" class="btn-nav btn-plano">📘 Plano de Governo & 1ª Semana</a>
            <a href="/dashboard" class="btn-nav btn-dashboard">📊 Dashboard YouTube Real</a>
            <a href="/radar_noticias" class="btn-nav btn-alert">🚨 Radar Anti-Crise</a>
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 Baixar PDF 360°</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg bot">
            <strong>🔰 BASE COMPLETA DE 150 EVENTOS DE GOIÁS MAPEADA (50 AGO / 50 SET / 50 OUT)!</strong><br><br>
            Mapeamos eventos religiosos, culturais, agropecuários e sociais com <strong>datas de início e fim exatas</strong> para Geotargeting de Tráfego Pago!<br><br>
            <strong>Escolha uma opção de análise:</strong>
            <div class="quick-actions">
                <span class="chip chip-eventos" onclick="window.location.href='/eventos'">🎪 Abrir Radar de 150 Eventos com Datas</span>
                <span class="chip" onclick="window.location.href='/plano_governo'">📘 Ver Plano de Governo & Guia 1ª Semana</span>
                <span class="chip" onclick="window.location.href='/dashboard'">📺 Dashboard YouTube Real</span>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Digite (ex: 'eventos em agosto', 'datas dos eventos', 'tráfego pago')..." onkeypress="if(event.key==='Enter') enviar()">
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

            if (pergunta.toLowerCase().includes('evento') || pergunta.toLowerCase().includes('tráfego') || pergunta.toLowerCase().includes('trafego')) {
                window.location.href = '/eventos';
                return;
            }

            chat.innerHTML += `<div class="msg user">${pergunta}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            botMsg.innerHTML = '<strong>[SALA DE GUERRA] Consultando Radar de Eventos com Datas Exatas...</strong>';
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

# TELA DEDICADA: RADAR DE 150 EVENTOS COM DATAS EXATAS (INÍCIO E FIM) E GEOTARGETING
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
        .btn-copy:hover { background: #f59e0b; color: #000; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🎪 RADAR DE EVENTOS POPULOSOS DE GOIÁS (150 EVENTOS MAPEADOS)</h1>
            <p>● Mapeamento de 50 Eventos por Mês com Datas Iniciais e Finais Exatas para Meta Ads & Google Ads</p>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>

    <div class="container">
        <!-- FILTROS POR MÊS -->
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

                    <button class="btn-copy" onclick="navigator.clipboard.writeText('EVENTO: {{ ev.evento }}\nDATAS EXATAS: {{ ev.periodo_datas }}\nCIDADE: {{ ev.cidade }}\nRAIO META ADS: {{ ev.raio_anuncio }}\nCOPY: {{ ev.copy_trafego }}'); alert('Parâmetros do evento copiados para o Meta Ads!');">📋 Copiar Parâmetros para Meta Ads</button>
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

# TELA DEDICADA DO PLANO DE GOVERNO, JOVENS (18-35) E 1ª SEMANA
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
        .box { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .box-title { font-size: 18px; font-weight: 800; color: #86efac; margin-bottom: 16px; border-left: 5px solid #eab308; padding-left: 10px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
        .card-pilar { background: #040e08; border: 1px solid #22c55e; border-radius: 10px; padding: 16px; }
        .card-pilar h4 { margin: 0 0 8px 0; color: #fef08a; font-size: 15px; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13.5px; }
        th { background: #040e08; color: #86efac; padding: 12px; text-align: left; font-weight: 800; border-bottom: 2px solid #15803d; }
        td { padding: 12px; border-bottom: 1px solid #14351f; color: #e2e8f0; }
        .badge-trend { background: #1e3a8a; color: #bfdbfe; padding: 4px 8px; border-radius: 6px; font-weight: 800; font-size: 11.5px; border: 1px solid #60a5fa; }
        .badge-dia { background: #15803d; color: #fef08a; padding: 4px 8px; border-radius: 6px; font-weight: 800; font-size: 11.5px; border: 1px solid #eab308; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📘 PLANO DE GOVERNO "GOIÁS PARA QUEM FAZ" & GUIA DA 1ª SEMANA</h1>
            <p>● Diretriz Estratégica da Chefe & Alinhamento com Marcelo Vitorino</p>
        </div>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>

    <div class="container">
        <div class="box">
            <div class="box-title">🏆 OS 3 PILARES DO PLANO DE GOVERNO (MEMÓRIA FIXADA NA IA)</div>
            <p style="color:#a7f3d0;font-size:14px;margin-bottom:16px;"><strong>Chapa Oficial:</strong> Wilder Morais (Governador) & Ana Paula Rezende (Vice-Governadora)</p>
            <div class="grid-3">
                {% for p in plano.pilares_fundamentais %}
                <div class="card-pilar">
                    <h4>{{ p.pilar }}</h4>
                    <p style="font-size:13px;color:#cbd5e1;margin-bottom:10px;">{{ p.foco }}</p>
                    <div style="font-size:12px;color:#86efac;font-weight:bold;">Programas: {{ ", ".join(p.programas_chave) }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""

# DASHBOARD EXECUTIVO ESTILO METABASE
HTML_DASHBOARD_METABASE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Executivo — Monitoramento 100% Real do YouTube</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
        <h1>📺 MONITORAMENTO 100% REAL DO YOUTUBE & DADOS ELEITORAIS TSE</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>

    <div class="container">
        <div class="full-width-card">
            <h3 style="color:#86efac;">📺 AUDITORIA AO VIVO DO YOUTUBE DOS CANDIDATOS</h3>
            <table>
                <thead>
                    <tr>
                        <th>Candidato</th>
                        <th>Canal Oficial</th>
                        <th>Fonte de Validação</th>
                        <th>Acesso Direto ao Canal</th>
                    </tr>
                </thead>
                <tbody>
                    {% for y in youtube %}
                    <tr>
                        <td><strong>{{ y.candidato }}</strong></td>
                        <td>{{ y.canal }}</td>
                        <td><strong style="color:#4ade80;">{{ y.status_fonte }}</strong></td>
                        <td><a href="{{ y.url_oficial }}" target="_blank" style="color:#fef08a;font-weight:bold;">🎬 Abrir Canal de Vídeos Reais</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
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
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 8px 16px; border-radius: 8px; border: 1px solid #22c55e; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 RADAR ANTI-CRISE & MONITORAMENTO DE NOTÍCIAS</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>
    <div class="container">
        <p style="color: #a7f3d0;">Monitoramento de notícias de Goiás.</p>
    </div>
</body>
</html>
"""

# TELA DEDICADA 2: MAPA TÁTICO DE RECLAMAÇÕES POPULARES
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
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 8px 16px; border-radius: 8px; border: 1px solid #22c55e; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🗺️ MAPA TÁTICO DE RECLAMAÇÕES POPULARES</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Sala de Guerra</a>
    </div>
    <div class="container">
        <p style="color: #a7f3d0;">Mapeamento regional de queixas.</p>
    </div>
</body>
</html>
"""

# ROUTING DAS TELAS DA SALA DE GUERRA MILITAR

@app.route("/", methods=["GET"])
@app.route("/chat", methods=["GET"])
def chat_home():
    return render_template_string(HTML_CHAT_WIDGET)

@app.route("/eventos", methods=["GET"])
def eventos_radar_page():
    return render_template_string(HTML_EVENTOS_RADAR, eventos=EVENTOS_GOIAS_2026)

@app.route("/plano_governo", methods=["GET"])
@app.route("/primeira_semana", methods=["GET"])
def plano_governo_page():
    return render_template_string(HTML_PLANO_GOVERNO, plano=PLANO_DE_GOVERNO_MEMORIA, primeira_semana=PRIMEIRA_SEMANA_CONTEUDO)

@app.route("/dashboard", methods=["GET"])
@app.route("/metabase", methods=["GET"])
def dashboard_metabase_page():
    return render_template_string(HTML_DASHBOARD_METABASE, youtube=YOUTUBE_MONITORAMENTO_REAL)

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

    # Roteador de Eventos e Geotargeting Tráfego Pago
    if any(k in p_lower for k in ["evento", "eventos", "tráfego", "trafego", "geotargeting", "anuncio", "anúncio", "meta ads", "data"]):
        return jsonify({
            "resposta": f"🎪 <strong>RADAR DE 150 EVENTOS DE GOIÁS COM DATAS EXATAS (50/MÊS)</strong><br><br>"
                        f"Mapeamos 150 eventos estratégicos (religiosos, agropecuários, culturais, esportivos e sociais) cobrindo todos os 246 municípios de Goiás com datas iniciais e finais exatas!<br><br>"
                        f"👉 <a href='/eventos' style='background:linear-gradient(135deg, #d97706, #b45309);color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #fef08a;'>🎪 ABRIR RADAR DE 150 EVENTOS COM DATAS EXATAS</a>"
        }), 200

    # Fallback via OpenRouter
    if OPENROUTER_API_KEY:
        system_prompt = (
            "Você é o Comando Central da Sala de Guerra da campanha de Wilder Morais em Goiás. "
            "Você possui uma base completa de 150 eventos mapeados em Goiás (50 em Agosto, 50 em Setembro, 50 em Outubro de 2026) com datas iniciais e finais exatas para direcionamento de tráfego pago no Meta Ads e Google Ads."
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
                    f"Base de 150 Eventos com datas exatas de início e fim devidamente integrada.<br><br>"
                    f"👉 <a href='/eventos' style='background:linear-gradient(135deg, #d97706, #b45309);color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #fef08a;'>🎪 ABRIR RADAR DE 150 EVENTOS</a>"
    }), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
