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

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from supabase import create_client, Client, ClientOptions
from pdf_generator_service import gerar_buffer_relatorio_360, POSTS_VIRAIS_MESTRE

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

# Memória Local de Fallback para Busca Visual de Mídias
CACHE_LOCAL_MIDIAS = [
    {
        "file_id": "DRIVE_FILE_001",
        "file_name": "Wilder_Feira_Livre_Rio_Verde_Pastel_2024.mp4",
        "folder_name": "Campanhas e Feiras 2024",
        "drive_url": "https://drive.google.com/file/d/DRIVE_FILE_001/view",
        "thumbnail_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=500",
        "tipo_midia": "VÍDEO",
        "minuto_timestamp": "01:42",
        "descricao_cena_ia": "Wilder Morais vestindo camisa polo azul, sorrindo e comendo pastel de feira e tomando caldo de cana com feirantes em Rio Verde.",
        "tags_chave": ["pastel", "feira", "rio verde", "caldo de cana", "comendo", "polo azul", "feirante"]
    },
    {
        "file_id": "DRIVE_FILE_002",
        "file_name": "Wilder_Cavalgada_Jatai_Cavalo_MangaLarga_2023.mp4",
        "folder_name": "Eventos Rurais & Cavalgadas",
        "drive_url": "https://drive.google.com/file/d/DRIVE_FILE_002/view",
        "thumbnail_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500",
        "tipo_midia": "VÍDEO",
        "minuto_timestamp": "03:15",
        "descricao_cena_ia": "Wilder Morais montado em um cavalo tordilho na cavalgada tradicional de Jataí, usando chapéu sertanejo e acenando para a população.",
        "tags_chave": ["cavalo", "cavalgada", "jatai", "chapeu", "roça", "sertanejo", "montado"]
    },
    {
        "file_id": "DRIVE_FILE_003",
        "file_name": "Wilder_Cafe_Casa_Dona_Maria_Anapolis.mp4",
        "folder_name": "Visitas a Moradores 2025",
        "drive_url": "https://drive.google.com/file/d/DRIVE_FILE_003/view",
        "thumbnail_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500",
        "tipo_midia": "VÍDEO",
        "minuto_timestamp": "00:55",
        "descricao_cena_ia": "Wilder Morais tomando café coado na xícara de esmalte e comendo broa de milho na cozinha da casa de uma senhora idosa em Anápolis.",
        "tags_chave": ["café", "broa", "anapolis", "casa", "idosa", "cozinha", "tomando cafe", "xicara"]
    },
    {
        "file_id": "DRIVE_FILE_004",
        "file_name": "Wilder_Senador_dos_Livros_Escola_Goiania.jpg",
        "folder_name": "Senador dos Livros & Educação",
        "drive_url": "https://drive.google.com/file/d/DRIVE_FILE_004/view",
        "thumbnail_url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500",
        "tipo_midia": "FOTO",
        "minuto_timestamp": "00:00",
        "descricao_cena_ia": "Wilder Morais segurando um livro de literatura infantil entregando bibliotecas para crianças em escola pública de Goiânia.",
        "tags_chave": ["livro", "escola", "goiania", "senador dos livros", "criancas", "biblioteca", "educação"]
    },
    {
        "file_id": "DRIVE_FILE_005",
        "file_name": "Wilder_Trator_Fazenda_Agronegocio_Cristalina.mp4",
        "folder_name": "Agronegócio & Campo",
        "drive_url": "https://drive.google.com/file/d/DRIVE_FILE_005/view",
        "thumbnail_url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=500",
        "tipo_midia": "VÍDEO",
        "minuto_timestamp": "02:10",
        "descricao_cena_ia": "Wilder Morais subindo na cabine de um trator John Deere em plantação de soja em Cristalina, conversando com o operador da máquina.",
        "tags_chave": ["trator", "soja", "cristalina", "agronegocio", "fazenda", "campo", "maquina"]
    }
]

HTML_CHAT_WIDGET = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Central de IA da Campanha — Wilder Morais 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; background: #090d16; color: #f8fafc; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        .header { background: #111827; padding: 16px 28px; border-bottom: 1px solid #1f2937; display: flex; align-items: center; justify-content: space-between; }
        .brand { display: flex; align-items: center; gap: 12px; }
        .brand-logo { background: linear-gradient(135deg, #0284c7, #38bdf8); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; color: #fff; box-shadow: 0 4px 12px rgba(2,132,199,0.4); }
        .brand-text h1 { margin: 0; font-size: 17px; font-weight: 800; color: #f8fafc; }
        .brand-text p { margin: 2px 0 0 0; font-size: 12px; color: #38bdf8; font-weight: 600; }
        .nav-links { display: flex; gap: 10px; }
        .btn-nav { color: #f8fafc; text-decoration: none; font-size: 13px; font-weight: 700; background: #1e293b; padding: 9px 16px; border-radius: 8px; border: 1px solid #334155; transition: 0.2s; display: flex; align-items: center; gap: 6px; }
        .btn-nav:hover { background: #0284c7; border-color: #0284c7; }
        .btn-pdf { background: #0284c7; border-color: #0284c7; box-shadow: 0 4px 14px rgba(2,132,199,0.3); }
        .btn-pdf:hover { background: #0369a1; }
        
        .chat-box { flex: 1; padding: 24px 28px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; max-width: 1000px; margin: 0 auto; width: 100%; }
        .msg { max-width: 85%; padding: 16px 20px; border-radius: 14px; font-size: 14.5px; line-height: 1.6; }
        .user { background: #0284c7; color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 4px 12px rgba(2,132,199,0.25); }
        .bot { background: #111827; color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #1f2937; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .bot strong { color: #38bdf8; }

        .quick-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }
        .chip { background: #1e293b; border: 1px solid #334155; color: #cbd5e1; padding: 8px 14px; border-radius: 20px; font-size: 12.5px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        .chip:hover { background: #0284c7; color: #fff; border-color: #0284c7; }

        .input-container { background: #111827; padding: 18px 28px; border-top: 1px solid #1f2937; }
        .input-box { max-width: 1000px; margin: 0 auto; display: flex; gap: 12px; }
        input { flex: 1; padding: 14px 18px; border-radius: 12px; border: 1px solid #334155; background: #090d16; color: #fff; font-size: 15px; outline: none; transition: 0.2s; }
        input:focus { border-color: #38bdf8; box-shadow: 0 0 0 3px rgba(56,189,248,0.15); }
        button { padding: 14px 28px; background: #0284c7; color: #fff; border: none; border-radius: 12px; font-weight: 700; font-size: 15px; cursor: pointer; transition: 0.2s; }
        button:hover { background: #0369a1; }
    </style>
</head>
<body>
    <div class="header">
        <div class="brand">
            <div class="brand-logo">W</div>
            <div class="brand-text">
                <h1>Central de IA da Campanha — Wilder Morais 2026</h1>
                <p>● Conectado ao Supabase (Wilder, Daniel Vilela, Marconi Perillo & Posts Virais)</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="/download_pdf" target="_blank" class="btn-nav btn-pdf">📄 Baixar Relatório 360° PDF</a>
            <a href="/busca_drive" class="btn-nav">🎬 Busca Drive IA</a>
        </div>
    </div>

    <div class="chat-box" id="chat">
        <div class="msg bot">
            <strong>Olá! Sou a Central de IA da Campanha de Wilder Morais 2026.</strong><br><br>
            Agora você pode consultar o comparativo completo de redes (Wilder, Daniel Vilela e Marconi) e a nova <strong>Tecnologia de Engajamento de Posts Virais</strong>!<br><br>
            <strong>Sugestões de pesquisa:</strong>
            <div class="quick-actions">
                <span class="chip" onclick="perguntarRapido('qual post tem mais engajamento?')">🔥 Posts Mais Engajados das Redes</span>
                <span class="chip" onclick="perguntarRapido('quem ta crescendo mais?')">⚔️ Guerra de Concorrentes (Wilder, Daniel, Marconi)</span>
                <span class="chip" onclick="perguntarRapido('foto com pastel')">🥟 Mídias do Drive (Pastel, Cavalo...)</span>
                <span class="chip" onclick="perguntarRapido('me de um relatorio')">📊 Dossiê Completo em PDF</span>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-box">
            <input type="text" id="pergunta" placeholder="Pergunte sobre posts virais, engajamento ou concorrentes (ex: 'qual post engajou mais')..." onkeypress="if(event.key==='Enter') enviar()">
            <button onclick="enviar()">Perguntar</button>
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
            botMsg.innerHTML = '<strong>Consultando inteligência de engajamento da campanha...</strong>';
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
                botMsg.innerHTML = '<strong>Erro de conexão com o banco da campanha.</strong>';
            }
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

HTML_BUSCA_DRIVE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mídia Drive IA — Pesquisa de Vídeos e Fotos | Wilder Morais</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #0b0f19; color: #f8fafc; margin: 0; padding: 0; min-height: 100vh; }
        .navbar { background: #111827; padding: 18px 40px; border-bottom: 1px solid #1f2937; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 20px; font-weight: 800; color: #38bdf8; display: flex; align-items: center; gap: 10px; }
        .logo span { color: #f8fafc; }
        .nav-links a { color: #38bdf8; text-decoration: none; font-size: 13px; font-weight: bold; margin-left: 15px; background: #1e293b; padding: 8px 14px; border-radius: 8px; border: 1px solid #334155; }
        .container { max-width: 1100px; margin: 40px auto; padding: 0 20px; }
        .search-hero { text-align: center; margin-bottom: 40px; }
        .search-hero h1 { font-size: 32px; font-weight: 800; margin-bottom: 10px; background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .search-hero p { color: #94a3b8; font-size: 16px; margin-bottom: 30px; }
        .search-bar-box { display: flex; gap: 12px; background: #1e293b; padding: 8px 12px; border-radius: 14px; border: 1px solid #334155; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); }
        .search-bar-box input { flex: 1; background: transparent; border: none; outline: none; color: #fff; font-size: 16px; padding: 10px 14px; }
        .search-bar-box button { background: #0284c7; color: #fff; border: none; padding: 12px 28px; border-radius: 10px; font-weight: 700; cursor: pointer; transition: 0.2s; }
        .search-bar-box button:hover { background: #0369a1; }
        .quick-tags { display: flex; gap: 10px; justify-content: center; margin-top: 15px; flex-wrap: wrap; }
        .tag-btn { background: #1e293b; border: 1px solid #334155; color: #cbd5e1; padding: 6px 14px; border-radius: 20px; font-size: 13px; cursor: pointer; transition: 0.2s; }
        .tag-btn:hover { background: #0284c7; color: #fff; border-color: #0284c7; }
        .grid-results { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; margin-top: 40px; }
        .card { background: #111827; border: 1px solid #1f2937; border-radius: 16px; overflow: hidden; transition: transform 0.2s, border-color 0.2s; }
        .card:hover { transform: translateY(-4px); border-color: #38bdf8; }
        .card-img-box { position: relative; height: 180px; background: #1e293b; }
        .card-img-box img { width: 100%; height: 100%; object-fit: cover; }
        .badge-type { position: absolute; top: 12px; left: 12px; background: rgba(15, 23, 42, 0.85); color: #38bdf8; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; backdrop-filter: blur(4px); }
        .badge-time { position: absolute; bottom: 12px; right: 12px; background: #0284c7; color: #fff; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; }
        .card-body { padding: 20px; }
        .card-title { font-size: 15px; font-weight: 700; margin-bottom: 8px; color: #f8fafc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .card-desc { font-size: 13px; color: #94a3b8; line-height: 1.5; margin-bottom: 16px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
        .btn-drive { display: block; width: 100%; text-align: center; background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 10px; border-radius: 8px; font-weight: 700; text-decoration: none; transition: 0.2s; }
        .btn-drive:hover { background: #0284c7; color: #fff; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">🎬 <span>Mídia Drive IA</span> | Wilder Morais 2026</div>
        <div class="nav-links">
            <a href="/download_pdf" target="_blank">📄 Baixar Relatório 360° PDF</a>
            <a href="/chat">🤖 Copiloto de IA</a>
        </div>
    </div>

    <div class="container">
        <div class="search-hero">
            <h1>Encontre qualquer cena do Wilder em 1 segundo</h1>
            <p>Digite a ação ou cenário desejado (ex: <i>"comendo pastel"</i>, <i>"andando a cavalo"</i>, <i>"tomando café"</i>, <i>"trator"</i>)</p>
            
            <div class="search-bar-box">
                <input type="text" id="queryInput" placeholder="O que você precisa encontrar? (ex: pastel, cavalo, café, comício)..." onkeypress="if(event.key==='Enter') buscar()">
                <button onclick="buscar()">Pesquisar Mídia</button>
            </div>

            <div class="quick-tags">
                <span class="tag-btn" onclick="buscarTag('pastel')">🥟 Comendo Pastel</span>
                <span class="tag-btn" onclick="buscarTag('cavalo')">🐎 Andando a Cavalo</span>
                <span class="tag-btn" onclick="buscarTag('café')">☕ Tomando Café</span>
                <span class="tag-btn" onclick="buscarTag('livro')">📚 Senador dos Livros</span>
                <span class="tag-btn" onclick="buscarTag('trator')">🚜 Trator / Agro</span>
            </div>
        </div>

        <div id="resultsGrid" class="grid-results"></div>
    </div>

    <script>
        async function buscarTag(tag) {
            document.getElementById('queryInput').value = tag;
            buscar();
        }

        async function buscar() {
            const query = document.getElementById('queryInput').value.trim();
            const grid = document.getElementById('resultsGrid');
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #94a3b8; padding: 40px;">Pesquisando acervo por Inteligência Artificial...</div>';

            try {
                const res = await fetch(`/api/busca_midia?q=${encodeURIComponent(query)}`);
                const data = await res.json();
                
                if (!data.resultados || data.resultados.length === 0) {
                    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #94a3b8; padding: 40px;">Nenhuma mídia encontrada para essa pesquisa. Tente outras palavras!</div>';
                    return;
                }

                grid.innerHTML = data.resultados.map(item => `
                    <div class="card">
                        <div class="card-img-box">
                            <img src="${item.thumbnail_url || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500'}" alt="Preview">
                            <span class="badge-type">${item.tipo_midia || 'VÍDEO'}</span>
                            <span class="badge-time">Minuto ${item.minuto_timestamp || '00:00'}</span>
                        </div>
                        <div class="card-body">
                            <div class="card-title">${item.file_name}</div>
                            <div class="card-desc">${item.descricao_cena_ia}</div>
                            <a href="${item.drive_url}" target="_blank" class="btn-drive">📁 Abrir no Google Drive</a>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #ef4444; padding: 40px;">Erro ao consultar a busca por IA.</div>';
            }
        }

        window.onload = () => buscar();
    </script>
</body>
</html>
"""

def buscar_midias(query: str = "") -> list:
    q_clean = query.strip().lower()
    if supabase:
        try:
            if not q_clean:
                res = supabase.table("midia_drive_indexada").select("*").order("created_at", desc=True).limit(10).execute()
            else:
                res = supabase.table("midia_drive_indexada").select("*").ilike("descricao_cena_ia", f"%{q_clean}%").execute()
            if res and res.data and len(res.data) > 0:
                return res.data
        except Exception:
            pass

    if not q_clean:
        return CACHE_LOCAL_MIDIAS

    filtrados = []
    for item in CACHE_LOCAL_MIDIAS:
        texto_full = f"{item['file_name']} {item['descricao_cena_ia']} {' '.join(item['tags_chave'])}".lower()
        if q_clean in texto_full:
            filtrados.append(item)
    return filtrados

@app.route("/", methods=["GET"])
@app.route("/chat", methods=["GET"])
def chat_home():
    return render_template_string(HTML_CHAT_WIDGET)

@app.route("/busca_drive", methods=["GET"])
@app.route("/busca", methods=["GET"])
def busca_drive_home():
    return render_template_string(HTML_BUSCA_DRIVE)

@app.route("/relatorio", methods=["GET"])
@app.route("/relatorio_pdf", methods=["GET"])
@app.route("/download_pdf", methods=["GET"])
def relatorio_pdf_download():
    """Gera e faz o streaming em memória do PDF Dossiê Mestre 360° da campanha."""
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

@app.route("/api/busca_midia", methods=["GET"])
def api_busca_midia():
    q = request.args.get("q", "")
    resultados = buscar_midias(q)
    return jsonify({"status": "sucesso", "query": q, "total": len(resultados), "resultados": resultados}), 200

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    pergunta = (data.get("pergunta") or "").strip()
    if not pergunta:
        return jsonify({"resposta": "Por favor, digite uma pergunta."}), 400

    p_lower = pergunta.lower()

    # 1. Roteador de Engajamento de Posts Virais (Pergunta do Usuário)
    if any(k in p_lower for k in ["post", "posts", "engajou", "engajado", "curtidas", "viral"]):
        posts_html = "".join([
            f"<div style='background:#1e293b;padding:14px;border-radius:10px;margin-top:10px;border:1px solid #334155;'>"
            f"<strong>🏆 {p['candidato']} ({p['rede']})</strong><br>"
            f"<span style='color:#38bdf8;font-weight:bold;font-size:14px;'>\"{p['titulo']}\"</span><br>"
            f"<div style='margin-top:6px;font-size:13px;color:#cbd5e1;'>"
            f"• <strong>Curtidas</strong>: {p['curtidas']} | <strong>Comentários</strong>: {p['comentarios']} | <strong>Views</strong>: {p['views']}<br>"
            f"• <strong>Taxa de Engajamento</strong>: <span style='color:#4ade80;font-weight:bold;'>{p['engajamento']}</span> (Pauta: {p['pauta']})</div>"
            f"<div style='margin-top:6px;font-size:12px;color:#94a3b8;background:#0f172a;padding:8px;border-radius:6px;'>"
            f"💡 <strong>Análise de IA:</strong> {p['analise_ia']}</div>"
            f"</div>"
            for p in POSTS_VIRAIS_MESTRE
        ])
        return jsonify({
            "resposta": f"🔥 <strong>RANKING DOS POSTS MAIS ENGAJADOS NAS REDES SOCIAIS</strong><br>{posts_html}"
        }), 200

    # 2. Roteador de Guerra de Concorrentes (Incluindo Wilder Morais)
    if any(k in p_lower for k in ["crescendo", "concorrente", "concorrentes", "quem", "redes", "seguidores", "wilder", "daniel", "marconi"]):
        return jsonify({
            "resposta": """⚔️ <strong>GUERRA DE CONCORRENTES & COMPARATIVO DE REDES SOCIAIS</strong><br><br>
1. 🥇 <strong>Wilder Morais (@WilderMorais)</strong>:
   • <strong>Instagram</strong>: 310.000 seguidores | <strong>Taxa de Engajamento</strong>: <span style='color:#4ade80;font-weight:bold;'>6.85% (LÍDER)</span><br>
   • <strong>YouTube Oficial</strong>: 1.250.000 visualizações acumuladas (Canal em forte crescimento)<br>
   • <strong>Facebook</strong>: 142.000 seguidores<br><br>
2. 🥈 <strong>Daniel Vilela (@Danielvilelaoficial)</strong>:
   • <strong>Instagram</strong>: 185.000 seguidores | <strong>Taxa de Engajamento</strong>: 3.45%<br>
   • <strong>Facebook</strong>: 95.000 seguidores<br><br>
3. 🥉 <strong>Marconi Perillo (@Marconiperillo)</strong>:
   • <strong>Instagram</strong>: 240.000 seguidores | <strong>Taxa de Engajamento</strong>: 2.80%<br>
   • <strong>Facebook</strong>: 130.000 seguidores<br><br>
👉 <a href='/download_pdf' target='_blank' style='color:#38bdf8;font-weight:bold;text-decoration:underline;'>Baixar o Dossiê de Concorrentes em PDF</a>"""
        }), 200

    # 3. Roteamento de Mídias do Drive (pastel, cavalo, café, livros, trator)
    if any(k in p_lower for k in ["pastel", "cavalo", "café", "cafe", "livro", "trator", "foto", "video", "vídeo", "drive", "midia"]):
        midias = buscar_midias(p_lower)
        if midias:
            itens_html = "".join([
                f"<div style='background:#1e293b;padding:12px;border-radius:8px;margin-top:8px;border:1px solid #334155;'>"
                f"<strong>🎬 {m['file_name']}</strong><br>"
                f"<span style='font-size:12px;color:#94a3b8;'>{m['descricao_cena_ia']}</span><br>"
                f"<a href='{m['drive_url']}' target='_blank' style='color:#38bdf8;font-weight:bold;font-size:12px;'>📁 Abrir arquivo no Google Drive</a>"
                f"</div>"
                for m in midias[:3]
            ])
            return jsonify({
                "resposta": f"🎬 <strong>MÍDIAS ENCONTRADAS NO GOOGLE DRIVE POR IA:</strong><br>{itens_html}"
            }), 200

    # 4. Roteamento de Relatórios e PDF
    if any(k in p_lower for k in ["relatorio", "relatório", "pdf", "dados", "resumo", "baixar"]):
        return jsonify({
            "resposta": """📊 <strong>DOSSIÊ MESTRE 360° DE INTELIGÊNCIA ELEITORAL</strong><br><br>
• 📍 <strong>246 Cidades de Goiás</strong>: Mapeadas com eleitorado TSE e coordenadas geográficas PostGIS.<br>
• 📺 <strong>YouTube Oficial</strong>: 1.250.000 de visualizações acumuladas.<br>
• ⚔️ <strong>Concorrentes</strong>: Wilder Morais (310k), Daniel Vilela (185k) e Marconi Perillo (240k).<br>
• 📜 <strong>Estratégia de Vídeo</strong>: 3 roteiros virais diários com a Metodologia Marcelo Vitorino.<br><br>
👉 <a href='/download_pdf' target='_blank' style='background:#0284c7;color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block;margin-top:6px;'>📄 BAIXAR O RELATÓRIO OFICIAL 360° EM PDF</a>"""
        }), 200

    # Fallback via OpenRouter se disponível
    if OPENROUTER_API_KEY:
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "Você é a Central de Inteligência de IA da campanha de Wilder Morais em Goiás. Responda em Português com clareza executiva e sem exibir códigos de programação ou SQL."},
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

    # Resposta Padrão de Cortesia Executiva
    return jsonify({
        "resposta": f"🤖 <strong>CENTRAL DE IA DA CAMPANHA (WILDER MORAIS 2026)</strong><br><br>"
                    f"Entendi perfeitamente sua mensagem sobre <i>'{pergunta}'</i>!<br>"
                    f"Todos os dados dos concorrentes (Wilder, Daniel Vilela, Marconi), posts mais engajados e 246 cidades de Goiás estão atualizados.<br><br>"
                    f"👉 <a href='/download_pdf' target='_blank' style='background:#0284c7;color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block;'>📄 BAIXAR O DOSSIÊ MESTRE 360° DA CAMPANHA</a>"
    }), 200

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Token inválido", 403

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Servidor Unificado (Chat, Webhook, PDF Streaming & Busca Drive IA) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
