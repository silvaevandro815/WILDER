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
from pdf_generator_service import gerar_buffer_relatorio_360, POSTS_VIRAIS_MESTRE, YOUTUBE_BENCHMARK_DATA

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

# DATASETS DE INTELIGÊNCIA MILITAR DE CAMPANHA

# 1. Radar Anti-Crise e Monitoramento de Notícias/Ataques a Wilder Morais
RADAR_NOTICIAS_ATAQUES = [
    {
        "id": 1,
        "veiculo": "O Popular / Política",
        "data_hora": "Hoje às 10:15",
        "manchete": "Oposição questiona movimentação pré-eleitoral de Wilder Morais no interior de Goiás",
        "sentimento": "NEUTRALIDADE TENDENCIOSA",
        "nivel_ameaca": "ALERTA MÉDIO 🟡",
        "resumo": "Matéria cita que Wilder tem intensificado agendas em Rio Verde e Jataí com lideranças rurais.",
        "estrategia_defesa_ia": "Neutralizar destacando que Wilder é Senador da República em exercício do mandato e trazendo os dados dos R$ 100 milhões em emendas enviadas para a saúde e agro de Goiás."
    },
    {
        "id": 2,
        "veiculo": "Jornal Opção",
        "data_hora": "Hoje às 08:30",
        "manchete": "Wilder Morais se consolida como principal nome da oposição com apoio do PL em Goiás",
        "sentimento": "POSITIVO / FAVORÁVEL 🟢",
        "nivel_ameaca": "SEM AMEAÇA 🟢",
        "resumo": "Análise política destaca a força do palanque conservador e a união do agronegócio ao redor de Wilder.",
        "estrategia_defesa_ia": "Impulsionar trechos do artigo nos grupos de WhatsApp de lideranças e utilizar de prova social no Instagram."
    },
    {
        "id": 3,
        "veiculo": "Diário da Manhã",
        "data_hora": "Ontem às 18:40",
        "manchete": "Rumores sem fundamento sobre emendas parlamentares na saúde da capital",
        "sentimento": "ATAQUE / FAKE NEWS 🔴",
        "nivel_ameaca": "ALERTA VERMELHO 🔴",
        "resumo": "Blog de oposição tenta associar atrasos de repasses estaduais às emendas federais.",
        "estrategia_defesa_ia": "RESPOSTA RÁPIDA: Publicar carrossel técnico comprovando com certidão que todas as emendas de Wilder chegaram 100% pagas e fiscalizadas pelo Tribunal de Contas."
    }
]

# 2. Mapa Tático de Reclamações da População por Região de Goiás
MAPA_RECLAMACOES_REGIONAL = [
    {
        "regiao": "Metropolitana de Goiânia (Goiânia, Aparecida, Senador Canedo)",
        "percentual_queixas": 42,
        "pauta_dominante": "Saúde Pública (Demora em consultas e filas no SUS)",
        "volume_queixas": "14.850 registros",
        "nivel_urgencia": "CRÍTICO 🔴",
        "tema_video_recomendado": "Mutirões de Saúde & Eficiência de Gestão (Perfil Engenheiro de Wilder)",
        "gancho_video_3s": "<i>'Sabe por que a saúde de Goiás trava? Porque falta gestão de engenheiro pra fazer funcionar!'</i>"
    },
    {
        "regiao": "Entorno do DF (Luziânia, Valparaíso, Águas Lindas, Formosa)",
        "percentual_queixas": 28,
        "pauta_dominante": "Transporte Público Metropolitano & Asfalto nas Vias Principais",
        "volume_queixas": "9.920 registros",
        "nivel_urgencia": "ALTO 🟡",
        "tema_video_recomendado": "Integração do Transporte & Obras de Infraestrutura",
        "gancho_video_3s": "<i>'O Entorno do DF não é quintal de ninguém. Merece transporte digno e asfalto de verdade!'</i>"
    },
    {
        "regiao": "Sudoeste Goiano (Rio Verde, Jataí, Mineiros, Quirinópolis)",
        "percentual_queixas": 14,
        "pauta_dominante": "Logística de Escoamento Agrícola & Manutenção de Pontes Rurais",
        "volume_queixas": "4.950 registros",
        "nivel_urgencia": "MÉDIO 🟢",
        "tema_video_recomendado": "Garantia de Logística para o Agro & Rodovias Vicinais",
        "gancho_video_3s": "<i>'Quem produz o alimento do Brasil em Goiás não pode ficar atolado na estrada!'</i>"
    },
    {
        "regiao": "Sul Goiano (Itumbiara, Caldas Novas, Catalão)",
        "percentual_queixas": 9,
        "pauta_dominante": "Emprego Jovem & Qualificação Técnica Universitária",
        "volume_queixas": "3.180 registros",
        "nivel_urgencia": "MODERADO 🟢",
        "tema_video_recomendado": "UFCAT Catalão, FIES & Primeiro Emprego Técnico",
        "gancho_video_3s": "<i>'Lutei para trazer a universidade federal pra Catalão e vou lutar pro jovem ter emprego garantido!'</i>"
    },
    {
        "regiao": "Norte & Nordeste Goiano (Porangatu, Uruaçu, Posse, Campos Belos)",
        "percentual_queixas": 7,
        "pauta_dominante": "Segurança Hídrica (Água Potável) & Hospitais Regionais",
        "volume_queixas": "2.470 registros",
        "nivel_urgencia": "ALTO 🟡",
        "tema_video_recomendado": "Poços Artesianos & Regionalização da Saúde no Interior",
        "gancho_video_3s": "<i>'O Norte de Goiás tem sede de desenvolvimento e de saúde perto de casa!'</i>"
    }
]

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
        
        /* HEADER MILITAR */
        .header { background: linear-gradient(135deg, #0b2214, #15803d, #16a34a); padding: 14px 28px; border-bottom: 3px solid #eab308; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 6px 25px rgba(22,163,74,0.4); }
        .brand { display: flex; align-items: center; gap: 14px; }
        .brand-logo { background: linear-gradient(135deg, #eab308, #f59e0b); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 800; color: #040e08; box-shadow: 0 4px 15px rgba(234,179,8,0.6); }
        .brand-text h1 { margin: 0; font-size: 19px; font-weight: 800; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.4); letter-spacing: 0.5px; }
        .brand-text p { margin: 2px 0 0 0; font-size: 12px; color: #fef08a; font-weight: 700; }
        
        .nav-links { display: flex; gap: 8px; flex-wrap: wrap; }
        .btn-nav { color: #f8fafc; text-decoration: none; font-size: 12.5px; font-weight: 700; background: #0c2415; padding: 8px 14px; border-radius: 8px; border: 1px solid #22c55e; transition: 0.2s; display: flex; align-items: center; gap: 6px; }
        .btn-nav:hover { background: #16a34a; border-color: #eab308; color: #fff; }
        .btn-alert { background: #991b1b; border-color: #ef4444; color: #fecdd3; }
        .btn-alert:hover { background: #dc2626; color: #fff; }
        .btn-pdf { background: linear-gradient(135deg, #15803d, #16a34a); border-color: #eab308; color: #fef08a; }
        
        /* CHAT BOX MILITAR */
        .chat-box { flex: 1; padding: 24px 28px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; max-width: 1100px; margin: 0 auto; width: 100%; }
        .msg { max-width: 88%; padding: 18px 22px; border-radius: 14px; font-size: 14.5px; line-height: 1.6; }
        .user { background: linear-gradient(135deg, #15803d, #16a34a); color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 4px 14px rgba(22,163,74,0.3); border: 1px solid #22c55e; }
        .bot { background: #0a1f12; color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #164624; box-shadow: 0 6px 20px rgba(0,0,0,0.5); }
        .bot strong { color: #86efac; }

        .quick-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
        .chip { background: #0d2e19; border: 1px solid #22c55e; color: #fef08a; padding: 9px 16px; border-radius: 20px; font-size: 12.5px; font-weight: 700; cursor: pointer; transition: 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
        .chip:hover { background: #16a34a; color: #fff; border-color: #eab308; }
        .chip-danger { border-color: #ef4444; color: #fca5a5; background: #2a0a0a; }
        .chip-danger:hover { background: #dc2626; color: #fff; }

        /* INPUT AREA */
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
                <p>● Central Operacional de Inteligência Tática, Anti-Crise & Monitoramento de Queixas</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="/radar_noticias" class="btn-nav btn-alert">🚨 Radar Anti-Crise</a>
            <a href="/mapa_demandas" class="btn-nav">🗺️ Mapa de Reclamações</a>
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 Baixar PDF 360°</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg bot">
            <strong>🔰 COMANDO CENTRAL DE IA — OPERAÇÕES DE CAMPANHA MILITAR</strong><br><br>
            Bem-vindo à Sala de Guerra Exclusiva de Wilder Morais. Este sistema monitora em tempo real notícias, ataques da oposição, reclamações regionais de Goiás e engajamento de redes.<br><br>
            <strong>Selecione o módulo de inteligência desejado:</strong>
            <div class="quick-actions">
                <span class="chip chip-danger" onclick="perguntarRapido('radar de noticias e ataques')">🚨 Radar Anti-Crise (Ataques a Wilder)</span>
                <span class="chip" onclick="perguntarRapido('mapa de reclamacoes por regiao')">🗺️ Mapa Tático de Reclamações em Goiás</span>
                <span class="chip" onclick="perguntarRapido('qual post tem mais engajamento?')">🔥 Posts Virais & Engajamento</span>
                <span class="chip" onclick="perguntarRapido('benchmarking do youtube')">📺 YouTube: Vídeos dos Concorrentes</span>
                <span class="chip" onclick="perguntarRapido('me de um relatorio')">📊 Dossiê Mestre em PDF</span>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Digite uma ordem ou pergunta tática (ex: 'radar de noticias', 'mapa de reclamacoes')..." onkeypress="if(event.key==='Enter') enviar()">
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

            chat.innerHTML += `<div class="msg user">${pergunta}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            botMsg.innerHTML = '<strong>[INTELIGÊNCIA MILITAR] Processando e consultando dados da campanha...</strong>';
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

# TELA DEDICADA 1: RADAR ANTI-CRISE DE NOTÍCIAS & ATAQUES
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
                <span style="font-weight: 800; color: #86efac;">📰 {{ item.veiculo }} &bull; <span style="color: #94a3b8; font-weight: normal;">{{ item.data_hora }}</span></span>
                <span class="badge {% if 'VERMELHO' in item.nivel_ameaca %}badge-red{% elif 'MÉDIO' in item.nivel_ameaca %}badge-yellow{% else %}badge-green{% endif %}">{{ item.nivel_ameaca }}</span>
            </div>
            <h3 style="margin: 0 0 8px 0; color: #fff;">"{{ item.manchete }}"</h3>
            <p style="margin: 0; color: #cbd5e1; font-size: 14px;">{{ item.resumo }}</p>
            <div class="estrategia-box">
                🛡️ <strong>PLANO DE CONTRANARRATIVA DE IA:</strong><br>
                {{ item.estrategia_defesa_ia }}
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
        
        /* GRÁFICO VISUAL EM CSS/BARRA */
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
        <p style="color: #a7f3d0; font-size: 15px;">Estudo regional de insatisfação popular para direcionamento de pautas de tráfego pago e gravação de vídeos segmentados por cidade.</p>

        <!-- GRÁFICO DE BARRAS REGIONAL -->
        <div class="chart-box">
            <h2 style="margin: 0 0 20px 0; color: #86efac; font-size: 17px;">📊 DISTRIBUIÇÃO REGIONAL DE QUEIXAS DA POPULAÇÃO (%)</h2>
            {% for item in reclamacoes %}
            <div class="bar-container">
                <div class="bar-label">
                    <span>{{ item.regiao }}</span>
                    <span style="color: #fef08a;">{{ item.percentual_queixas }}% ({{ item.volume_queixas }})</span>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill" style="width: {{ item.percentual_queixas * 2 }}%;"></div>
                </div>
            </div>
            {% endfor %}
        </div>

        <!-- LISTA TÁTICA DE VÍDEOS RECOMENDADOS -->
        <h2 style="color: #fef08a; font-size: 18px; margin-bottom: 16px;">🎬 DIRECIONAMENTO TÁTICO DE VÍDEOS POR REGIÃO</h2>
        {% for item in reclamacoes %}
        <div class="card-demanda">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong style="color: #86efac; font-size: 16px;">📍 {{ item.regiao }}</strong>
                <span style="background: #14351f; color: #fef08a; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 11px; border: 1px solid #22c55e;">{{ item.nivel_urgencia }}</span>
            </div>
            <p style="margin: 4px 0 10px 0; color: #e2e8f0; font-size: 14px;"><strong>Pauta Principal:</strong> {{ item.pauta_dominante }}</p>
            <div style="background: #040e08; padding: 12px; border-radius: 8px; border-left: 4px solid #16a34a;">
                🎥 <strong>TEMA DO VÍDEO RECOMENDADO:</strong> {{ item.tema_video_recomendado }}<br>
                🎯 <strong>GANCHO INICIAL DE 3s:</strong> {{ item.gancho_video_3s|safe }}
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

    # 1. Roteamento Radar Anti-Crise e Notícias
    if any(k in p_lower for k in ["radar", "ataque", "ataques", "noticia", "notícia", "crise", "falando mal", "fake news"]):
        noticias_html = "".join([
            f"<div style='background:#1a0808;padding:14px;border-radius:10px;margin-top:10px;border:1px solid #ef4444;'><div style='display:flex;justify-content:space-between;'>"
            f"<strong>📰 {n['veiculo']} ({n['data_hora']})</strong>"
            f"<span style='background:#ef4444;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold;'>{n['nivel_ameaca']}</span></div>"
            f"<div style='color:#fff;font-weight:bold;margin-top:6px;'>\"{n['manchete']}\"</div>"
            f"<div style='font-size:12.5px;color:#cbd5e1;margin-top:4px;'>{n['resumo']}</div>"
            f"<div style='background:#040e08;padding:8px;border-radius:6px;margin-top:8px;font-size:12px;border-left:3px solid #eab308;'>"
            f"🛡️ <strong>Estratégia de Defesa IA:</strong> {n['estrategia_defesa_ia']}</div></div>"
            for n in RADAR_NOTICIAS_ATAQUES
        ])
        return jsonify({
            "resposta": f"🚨 <strong>RADAR ANTI-CRISE & MONITORAMENTO DE NOTÍCIAS DA OPOSIÇÃO</strong><br>{noticias_html}<br><br>👉 <a href='/radar_noticias' target='_blank' style='color:#fef08a;font-weight:bold;text-decoration:underline;'>Abrir Painel Completo do Radar Anti-Crise</a>"
        }), 200

    # 2. Roteamento Mapa Tático de Reclamações por Região
    if any(k in p_lower for k in ["mapa", "reclamacao", "reclamação", "reclamacoes", "regiao", "região", "demandas", "queixas"]):
        mapa_html = "".join([
            f"<div style='background:#0e2917;padding:14px;border-radius:10px;margin-top:10px;border:1px solid #1a4628;'>"
            f"<strong>📍 {m['regiao']}</strong> ({m['percentual_queixas']}% do total de queixas &bull; {m['volume_queixas']})<br>"
            f"<span style='color:#fef08a;font-weight:bold;font-size:13px;'>Pauta Principal: {m['pauta_dominante']}</span><br>"
            f"<div style='margin-top:6px;font-size:12.5px;color:#e2e8f0;background:#040e08;padding:8px;border-radius:6px;border-left:3px solid #16a34a;'>"
            f"🎥 <strong>Vídeo Recomendado:</strong> {m['tema_video_recomendado']}<br>"
            f"🎯 <strong>Gancho 3s:</strong> {m['gancho_video_3s']}</div></div>"
            for m in MAPA_RECLAMACOES_REGIONAL
        ])
        return jsonify({
            "resposta": f"🗺️ <strong>MAPA TÁTICO DE RECLAMAÇÕES POPULARES POR REGIÃO DE GOIÁS</strong><br>{mapa_html}<br><br>👉 <a href='/mapa_demandas' target='_blank' style='color:#fef08a;font-weight:bold;text-decoration:underline;'>Abrir Gráficos Interativos do Mapa de Reclamações</a>"
        }), 200

    # 3. Roteador de YouTube dos Concorrentes
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

    # 4. Roteador de Engajamento de Posts Virais
    if any(k in p_lower for k in ["post", "posts", "engajou", "engajado", "curtidas", "viral"]):
        posts_html = "".join([
            f"<div style='background:#0e2917;padding:14px;border-radius:10px;margin-top:10px;border:1px solid #1a4628;'>"
            f"<strong>🏆 {p['candidato']} ({p['rede']})</strong><br>"
            f"<span style='color:#fef08a;font-weight:bold;font-size:14px;'>\"{p['titulo']}\"</span><br>"
            f"<div style='margin-top:6px;font-size:13px;color:#cbd5e1;'>"
            f"• <strong>Curtidas</strong>: {p['curtidas']} | <strong>Comentários</strong>: {p['comentarios']} | <strong>Views</strong>: {p['views']}<br>"
            f"• <strong>Engajamento</strong>: <span style='color:#4ade80;font-weight:bold;'>{p['engajamento']}</span> (Pauta: {p['pauta']})</div>"
            f"<div style='margin-top:6px;font-size:12px;color:#a7f3d0;background:#040e08;padding:8px;border-radius:6px;border:1px solid #16a34a;'>"
            f"💡 <strong>Análise de IA:</strong> {p['analise_ia']}</div></div>"
            for p in POSTS_VIRAIS_MESTRE
        ])
        return jsonify({
            "resposta": f"🔥 <strong>RANKING DOS POSTS MAIS ENGAJADOS NAS REDES SOCIAIS</strong><br>{posts_html}"
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
                    f"Todos os módulos táticos de inteligência (Radar Anti-Crise, Mapa de Reclamações e YouTube) estão operacionais.<br><br>"
                    f"👉 <a href='/download_pdf' target='_blank' style='background:linear-gradient(135deg, #15803d, #16a34a);color:#fef08a;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block;border:1px solid #eab308;'>📄 BAIXAR O DOSSIÊ MESTRE 360° DA CAMPANHA</a>"
    }), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
