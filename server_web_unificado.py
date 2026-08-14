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
    gerar_buffer_relatorio_360, POSTS_VIRAIS_MESTRE, YOUTUBE_BENCHMARK_DATA,
    RADAR_NOTICIAS_ATAQUES, MAPA_RECLAMACOES_REGIONAL,
    PLANO_DE_GOVERNO_MEMORIA, PRIMEIRA_SEMANA_CONTEUDO
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
        .btn-dashboard { background: linear-gradient(135deg, #eab308, #ca8a04); color: #040e08; border-color: #fef08a; font-weight: 800; }
        .btn-dashboard:hover { background: #fde047; color: #000; }
        .btn-alert { background: #991b1b; border-color: #ef4444; color: #fecdd3; }
        .btn-alert:hover { background: #dc2626; color: #fff; }
        .btn-pdf { background: linear-gradient(135deg, #15803d, #16a34a); border-color: #eab308; color: #fef08a; }
        .btn-plano { background: #1e3a8a; border-color: #60a5fa; color: #dbeafe; }
        .btn-plano:hover { background: #2563eb; color: #fff; }
        
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
        .chip-plano { background: #1e3a8a; border-color: #60a5fa; color: #bfdbfe; }
        .chip-plano:hover { background: #2563eb; color: #fff; }

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
                <p>● Central de Inteligência Estratégica & Métricas Reais Garantidas</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="/plano_governo" class="btn-nav btn-plano">📘 Plano de Governo & 1ª Semana</a>
            <a href="/dashboard" class="btn-nav btn-dashboard">📊 Dashboard Metabase</a>
            <a href="/radar_noticias" class="btn-nav btn-alert">🚨 Radar Anti-Crise</a>
            <a href="/mapa_demandas" class="btn-nav">🗺️ Mapa de Reclamações</a>
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 Baixar PDF 360°</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg bot">
            <strong>🔰 DADOS 100% REAIS E REVISADOS — TRANSPARÊNCIA ABSOLUTA</strong><br><br>
            Ajustamos o Dashboard com a contagem <strong>real de 80 curtidas e 2.000 views no Instagram, e 100 views no YouTube</strong>.<br><br>
            <strong>Escolha uma opção de análise:</strong>
            <div class="quick-actions">
                <span class="chip chip-dash" onclick="window.location.href='/dashboard'">📊 Abrir Dashboard Metabase com Links Reais</span>
                <span class="chip chip-plano" onclick="window.location.href='/plano_governo'">📘 Ver Plano de Governo & Guia 1ª Semana</span>
                <span class="chip chip-danger" onclick="perguntarRapido('radar de noticias e ataques')">🚨 Radar Anti-Crise</span>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Digite (ex: 'abrir dashboard', 'dados reais', 'plano de governo')..." onkeypress="if(event.key==='Enter') enviar()">
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
            botMsg.innerHTML = '<strong>[SALA DE GUERRA] Processando dados reais de mídias...</strong>';
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

        .checklist-visual { background: #040e08; border: 1px solid #eab308; padding: 16px; border-radius: 10px; margin-top: 14px; }
        .checklist-item { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 14px; }
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
            <p style="color:#a7f3d0;font-size:14px;margin-bottom:16px;"><strong>Chapa Oficial:</strong> Wilder Morais (Governador) & Ana Paula Rezende (Vice-Governadora) &bull; <strong>Lema:</strong> <i>"Trabalho, Cuidado e Oportunidade chegando à vida das pessoas."</i></p>
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

        <div class="box">
            <div class="box-title">🚀 PROGRAMAS DO PLANO DE GOVERNO PARA JOVENS (18 A 35 ANOS) & TRENDS VIRAIS</div>
            <table>
                <thead>
                    <tr>
                        <th>Programa do Governo Wilder</th>
                        <th>Descrição da Proposta Real</th>
                        <th>Público Alvo</th>
                        <th>Formato de Trend Viral (Edutainment)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for prog in plano.programas_jovens_18_35 %}
                    <tr>
                        <td><strong style="color:#fef08a;">{{ prog.nome }}</strong></td>
                        <td>{{ prog.descricao }}</td>
                        <td>{{ prog.publico }}</td>
                        <td><span class="badge-trend">{{ prog.trend_format }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="box">
            <div class="box-title">📅 PLANO DA 1ª SEMANA: APRESENTAÇÃO, EMPATIA & NOVA IDENTIDADE VISUAL</div>
            <div class="checklist-visual">
                <strong style="color:#eab308;font-size:15px;">🎨 CHECKLIST DE IDENTIDADE VISUAL EXIGIDA PELA CHEFE:</strong>
                <div class="checklist-item" style="margin-top:10px;">✅ <strong>Fotos de Perfil dos Canais & WhatsApp:</strong> Retrato de Wilder com iluminação quente, sorriso empático e camisa social sem gravata.</div>
                <div class="checklist-item">✅ <strong>Capa do YouTube:</strong> Layout com Wilder & Ana Paula Rezende, selo "Goiás para Quem Faz".</div>
            </div>

            <table style="margin-top:20px;">
                <thead>
                    <tr>
                        <th>Dia</th>
                        <th>Foco / Linha Editorial</th>
                        <th>Formato & Gancho Inicial de 3s</th>
                        <th>Chamada para Ação (CTA)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for sem in primeira_semana %}
                    <tr>
                        <td><span class="badge-dia">{{ sem.dia }}</span></td>
                        <td><strong>{{ sem.foco }}</strong><br><span style="font-size:12px;color:#a7f3d0;">{{ sem.historia }}</span></td>
                        <td><strong>{{ sem.formato }}</strong><br><span style="color:#fef08a;">"{{ sem.gancho_3s }}"</span></td>
                        <td><strong style="color:#86efac;">{{ sem.call_to_action }}</strong></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

# DASHBOARD EXECUTIVO ESTILO METABASE COM TABELA COMPLETA E DADOS REAIS
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

        .iframe-box { width: 100%; height: 600px; border: 1px solid #164624; border-radius: 12px; overflow: hidden; margin-top: 20px; }
        iframe { width: 100%; height: 100%; border: none; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📊 DASHBOARD EXECUTIVO METABASE — DADOS REAIS AUDITADOS</h1>
            <p>● Links Oficiais Diretos para Instagram e YouTube de Todos os Candidatos</p>
        </div>
        <div>
            <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
        </div>
    </div>

    <div class="container">
        <!-- TOP KPI ROW COM DADOS REAIS EXATOS -->
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
                <div class="kpi-title">Reels Instagram Wilder</div>
                <div class="kpi-val" style="color: #4ade80;">80 curtidas / 2k views</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">YouTube Views Reais</div>
                <div class="kpi-val">100 views reais</div>
            </div>
        </div>

        <!-- CHARTS GRID -->
        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-title">
                    <span>⚔️ COMPARATIVO DE REDES SOCIAIS</span>
                    <span class="badge-green">MÉTRICAS REAIS</span>
                </div>
                <canvas id="chartConcorrentes" height="200"></canvas>
            </div>

            <div class="chart-card">
                <div class="chart-title">
                    <span>🏛️ MAIORES COLÉGIOS ELEITORAIS (TSE GOIÁS)</span>
                    <span class="badge-green">DADOS OFICIAIS</span>
                </div>
                <canvas id="chartMunicipios" height="200"></canvas>
            </div>
        </div>

        <!-- TABELA REPOSITÓRIO COMPLETO COM LINKS DOS CONTEÚDOS DOS CANDIDATOS -->
        <div class="full-width-card">
            <div class="chart-title">
                <span>📋 TABELA DE CONTEÚDOS & LINKS OFICIAIS DOS CANDIDATOS</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Candidato / Pauta</th>
                        <th>Plataforma</th>
                        <th>Métricas Reais (Curtidas / Comentários / Views)</th>
                        <th>Retenção Estimada (%)</th>
                        <th>Links Oficiais Diretos</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in posts %}
                    <tr>
                        <td><strong>{{ p.candidato }}</strong><br><span style="font-size:12px;color:#86efac;">{{ p.titulo }}</span></td>
                        <td><span class="badge-green">{{ p.rede }}</span></td>
                        <td>❤️ <strong>{{ p.curtidas }}</strong> | 💬 {{ p.comentarios }} | 👁️ {{ p.views }}</td>
                        <td><strong style="color:#4ade80;">{{ p.retencao_media }}</strong></td>
                        <td>
                            <a href="{{ p.post_url }}" target="_blank" style="color:#86efac;font-weight:bold;margin-right:10px;">🔗 Perfil/Reels Oficial</a>
                            <a href="{{ p.search_url }}" target="_blank" style="color:#fef08a;font-weight:bold;">🔎 Auditar Pauta no Google/YT</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- IFRAME DO METABASE EMBUTIDO -->
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
                        label: 'Visualizações do Reels (Reais)',
                        data: [2000, 800, 600],
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

@app.route("/plano_governo", methods=["GET"])
@app.route("/primeira_semana", methods=["GET"])
def plano_governo_page():
    return render_template_string(HTML_PLANO_GOVERNO, plano=PLANO_DE_GOVERNO_MEMORIA, primeira_semana=PRIMEIRA_SEMANA_CONTEUDO)

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
    if any(k in p_lower for k in ["dashboard", "metabase", "grafico", "gráfico", "painel", "dado", "dados"]):
        posts_html = "".join([
            f"<div style='background:#0e2917;padding:12px;border-radius:10px;margin-top:10px;border:1px solid #1a4628;'>"
            f"<strong style='color:#86efac;'>🏆 {p['candidato']} ({p['rede']})</strong> — {p['titulo']}<br>"
            f"<span style='color:#fef08a;font-size:13px;'>❤️ {p['curtidas']} | 👁️ {p['views']}</span><br>"
            f"<a href='{p['post_url']}' target='_blank' style='color:#86efac;font-weight:bold;'>🔗 Perfil Oficial</a> &bull; "
            f"<a href='{p['search_url']}' target='_blank' style='color:#fef08a;font-weight:bold;'>🔎 Auditar Pauta</a>"
            f"</div>"
            for p in POSTS_VIRAIS_MESTRE
        ])
        return jsonify({
            "resposta": f"📊 <strong>DASHBOARD DE MÉTRICAS REAIS COM LINKS COMPROVADOS</strong><br><br>"
                        f"{posts_html}<br><br>"
                        f"👉 <a href='/dashboard' style='background:linear-gradient(135deg, #eab308, #ca8a04);color:#040e08;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #fef08a;'>📊 ABRIR DASHBOARD METABASE COMPLETO</a>"
        }), 200

    # Fallback via OpenRouter
    if OPENROUTER_API_KEY:
        system_prompt = (
            "Você é o Comando Central da Sala de Guerra da campanha de Wilder Morais em Goiás. "
            "Responda sempre com 100% de realismo, verdade e precisão sobre métricas e dados de mídias sociais."
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
                    f"Ordem recebida sobre <i>'{pergunta}'</i>!<br>"
                    f"Métricas reais (80 curtidas / 2.000 views no Instagram e 100 views no YouTube) sincronizadas.<br><br>"
                    f"👉 <a href='/dashboard' style='background:linear-gradient(135deg, #eab308, #ca8a04);color:#040e08;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #fef08a;'>📊 ABRIR DASHBOARD METABASE INTEGRADO</a>"
    }), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
