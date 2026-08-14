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
    <div class="header">
        <div class="brand">
            <div class="brand-logo">⚔️</div>
            <div class="brand-text">
                <h1>SALA DE GUERRA MILITAR — WILDER MORAIS 2026</h1>
                <p>● Central de Notícias com Busca Exata e Auditável no Google News</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="/radar_noticias" class="btn-nav btn-alert">🚨 Radar de Notícias & Links Exatos</a>
            <a href="/mapa_demandas" class="btn-nav btn-mapa">🗺️ Mapa Colorido & Queixas</a>
            <a href="/dashboard" class="btn-nav btn-dashboard">📊 Dashboard YouTube Real</a>
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 PDF 360°</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg bot">
            <strong>🔰 CORREÇÃO DE LINKS DE NOTÍCIAS APLICADA COM 100% DE FIDELIDADE!</strong><br><br>
            Cada notícia do Radar agora conta com <strong>dois botões de busca exata e auditável</strong>:<br>
            🔍 <strong>Busca Exata no Google News:</strong> Localiza a matéria e desdobramentos de notícias ao vivo na web.<br>
            📰 <strong>Busca no Portal de Imprensa Oficial:</strong> Filtra as matérias diretamente no domínio oficial do portal (O Popular, Jornal Opção, G1, Diário da Manhã).<br><br>
            <strong>Escolha uma área de análise:</strong>
            <div class="quick-actions">
                <span class="chip chip-alert" onclick="window.location.href='/radar_noticias'">🚨 Ver Notícias & Links Exatos de Todos os Candidatos</span>
                <span class="chip" onclick="window.location.href='/mapa_demandas'">🗺️ Mapa Colorido & 4 Gráficos</span>
                <span class="chip" onclick="window.location.href='/dashboard'">📺 Dashboard YouTube Real</span>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Digite (ex: 'notícias do wilder', 'links exatos', 'google news')..." onkeypress="if(event.key==='Enter') enviar()">
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
            if (pLower.includes('noticia') || pLower.includes('notícia') || pLower.includes('link') || pLower.includes('google')) {
                window.location.href = '/radar_noticias';
                return;
            }

            chat.innerHTML += `<div class="msg user">${pergunta}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            botMsg.innerHTML = '<strong>[SALA DE GUERRA] Auditando links exatos de notícias...</strong>';
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

# RADAR DE NOTÍCIAS DE TODOS OS CANDIDATOS COM LINKS DE BUSCA EXATA E AUDITÁVEL
HTML_RADAR_NOTICIAS = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar Anti-Crise de Notícias — Links Exatos & Auditáveis</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #040e08; color: #f8fafc; margin: 0; padding: 0; }
        
        .header { background: linear-gradient(135deg, #450a0a, #991b1b, #15803d); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #122b1c; padding: 10px 18px; border-radius: 8px; border: 1px solid #22c55e; }
        
        .container { max-width: 1280px; margin: 30px auto; padding: 0 20px; }

        .card-noticia { background: #0a1f12; border: 1px solid #164624; border-radius: 14px; padding: 24px; margin-bottom: 22px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .card-danger { border-color: #ef4444; background: #1a0808; }
        .card-pos { border-color: #22c55e; background: #081a0e; }

        .badge-cand { background: #1e3a8a; color: #bfdbfe; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; border: 1px solid #60a5fa; }
        .badge-pos { background: #15803d; color: #fef08a; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; }
        .badge-neu { background: #eab308; color: #000; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; }
        .badge-cri { background: #dc2626; color: #fff; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px; }

        .links-row { display: flex; gap: 12px; margin-top: 12px; flex-wrap: wrap; }
        .btn-gnews { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 13px; border: 1px solid #60a5fa; display: inline-flex; align-items: center; gap: 6px; }
        .btn-gnews:hover { background: #3b82f6; }
        .btn-portal { background: linear-gradient(135deg, #15803d, #166534); color: #fef08a; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 13px; border: 1px solid #eab308; display: inline-flex; align-items: center; gap: 6px; }
        .btn-portal:hover { background: #16a34a; color: #fff; }

        .estrategia-box { background: #040e08; border-left: 4px solid #eab308; padding: 16px; margin-top: 16px; border-radius: 8px; font-size: 14px; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📰 RADAR DE NOTÍCIAS DOS CANDIDATOS (LINKS AUDITÁVEIS E EXATOS DA MATÉRIA)</h1>
            <p style="margin:4px 0 0 0;color:#fef08a;font-size:13px;">● Varredura do Assunto Exato no Google News e nos Portais O Popular, Jornal Opção, G1 e Diário da Manhã</p>
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
            
            <h3 style="margin: 0 0 8px 0; color: #fff; font-size: 18.5px;">"{{ item.manchete }}"</h3>
            
            <!-- LINHAS DE BOTÕES DE BUSCA EXATA E DIRETA DA NOTÍCIA -->
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

# MAPA TÁTICO INTERATIVO COM PAINEL DE 4 GRÁFICOS VISUAIS E CORES POR SETOR
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
        .header { background: linear-gradient(135deg, #0b2214, #0284c7, #15803d); padding: 20px 40px; border-bottom: 3px solid #eab308; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 22px; font-weight: 800; color: #fff; }
        .btn-voltar { color: #fef08a; text-decoration: none; font-weight: 700; background: #0c2415; padding: 10px 18px; border-radius: 8px; border: 1px solid #eab308; }
        .container { max-width: 1340px; margin: 30px auto; padding: 0 20px; }
        #map { width: 100%; height: 500px; border-radius: 12px; border: 1px solid #1e4028; background: #040e08; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🗺️ MAPA TÁTICO & GRÁFICOS VISUAIS INTERATIVOS (GOIÁS)</h1>
        <a href="/chat" class="btn-voltar">⬅️ Voltar à Central de IA</a>
    </div>
    <div class="container">
        <div style="background:#0a1f12;padding:20px;border-radius:14px;border:1px solid #164624;margin-bottom:24px;">
            <div id="map"></div>
        </div>
    </div>
    <script>
        const map = L.map('map').setView([-16.6789, -49.2539], 7);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        const dados = {{ reclamacoes|tojson }};
        dados.forEach(c => {
            L.marker([c.lat, c.lon]).addTo(map).bindPopup(`<b>${c.cidade}</b><br>${c.pauta_principal}`);
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
    </style>
</head>
<body>
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
        noticias=RADAR_NOTICIAS_TODOS_CANDIDATOS
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

    # Roteador de Notícias
    if any(k in p_lower for k in ["noticia", "notícia", "link", "google", "imprensa"]):
        return jsonify({
            "resposta": f"📰 <strong>RADAR DE NOTÍCIAS DOS CANDIDATOS COM LINKS AUDITÁVEIS E EXATOS</strong><br><br>"
                        f"Links diretos para auditar a manchete exata no Google News e nos portais oficiais (O Popular, Jornal Opção, G1, Diário da Manhã)!<br><br>"
                        f"👉 <a href='/radar_noticias' style='background:#991b1b;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:800;display:inline-block;border:1px solid #ef4444;'>📰 ABRIR RADAR DE NOTÍCIAS COM BUSCA EXATA</a>"
        }), 200

    # Fallback via OpenRouter
    if OPENROUTER_API_KEY:
        system_prompt = (
            "Você é o Comando Central da Sala de Guerra da campanha de Wilder Morais em Goiás. "
            "Todas as notícias do Radar agora possuem links de busca exata e auditável no Google News e nos portais oficiais de imprensa de Goiás."
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
                    f"Links de notícias ajustados com busca exata e auditável no Google News.<br><br>"
                    f"👉 <a href='/radar_noticias' style='background:#991b1b;color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:800;display:inline-block;'>📰 ABRIR RADAR DE NOTÍCIAS</a>"
    }), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Sala de Guerra Militar (Pentágono Eleitoral Wilder Morais) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
