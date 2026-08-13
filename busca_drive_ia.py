import os
import sys
import json
import re
import urllib3
import httpx
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

load_dotenv()

from supabase import create_client, Client, ClientOptions

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

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

# Memória Local de Fallback (para busca instantânea)
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

app = Flask(__name__)

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
        <div style="font-size: 13px; color: #94a3b8;">Indexador Multimodal de Acervo</div>
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
    """Busca mídias indexadas via Supabase ou no cache de fallback."""
    q_clean = query.strip().lower()
    
    if supabase:
        try:
            if not q_clean:
                res = supabase.table("midia_drive_indexada").select("*").order("created_at", desc=True).limit(10).execute()
            else:
                res = supabase.table("midia_drive_indexada").select("*").ilike("descricao_cena_ia", f"%{q_clean}%").execute()
            if res and res.data:
                return res.data
        except Exception:
            pass

    # Fallback no Cache Local
    if not q_clean:
        return CACHE_LOCAL_MIDIAS

    filtrados = []
    for item in CACHE_LOCAL_MIDIAS:
        texto_full = f"{item['file_name']} {item['descricao_cena_ia']} {' '.join(item['tags_chave'])}".lower()
        if q_clean in texto_full:
            filtrados.append(item)
    return filtrados

@app.route("/", methods=["GET"])
@app.route("/busca", methods=["GET"])
def index():
    return render_template_string(HTML_BUSCA_DRIVE)

@app.route("/api/busca_midia", methods=["GET"])
def api_busca_midia():
    q = request.args.get("q", "")
    resultados = buscar_midias(q)
    return jsonify({"status": "sucesso", "query": q, "total": len(resultados), "resultados": resultados}), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT_BUSCA_DRIVE", 5002))
    print(f"🚀 Servidor de Busca Visual por IA no Google Drive rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
