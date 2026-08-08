import os
import sys
import datetime
import urllib3
import httpx
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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

def gerar_relatorio_pdf_executivo():
    """
    Gera um relatório impresso/PDF executivo dos dados coletados pelos robôs da campanha.
    """
    print("\n" + "=" * 60)
    print("📄 GERANDO RELATÓRIO EXECUTIVO EM PDF — CAMPANHA WILDER MORAIS")
    print("=" * 60)

    hoje = datetime.date.today().strftime("%d/%m/%Y")
    
    total_cidades = 246
    total_trends = 0
    total_briefings = 0
    total_youtube_views = 0

    if supabase:
        try:
            r_tr = supabase.table("google_trends_goias").select("id", count="exact").execute()
            total_trends = len(r_tr.data) if (r_tr and r_tr.data) else 0

            r_br = supabase.table("briefings_diarios").select("id", count="exact").execute()
            total_briefings = len(r_br.data) if (r_br and r_br.data) else 0

            r_yt = supabase.table("youtube_performance").select("visualizacoes_totais").order("data", desc=True).limit(1).execute()
            if r_yt and r_yt.data:
                total_youtube_views = r_yt.data[0].get("visualizacoes_totais", 0)
        except Exception as e:
            print(f"[AVISO] Erro ao obter estatísticas para PDF: {e}")

    filename_html = "relatorio_executivo_campanha.html"
    
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Executivo de Inteligência Eleitoral — Wilder Morais</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #1e293b; background: #fff; padding: 40px; line-height: 1.6; }}
        .header {{ border-bottom: 3px solid #0284c7; padding-bottom: 15px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
        h1 {{ color: #0f172a; margin: 0; font-size: 24px; }}
        .subtitle {{ color: #64748b; font-size: 14px; margin-top: 5px; }}
        .card-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; }}
        .card-title {{ font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: bold; }}
        .card-value {{ font-size: 28px; color: #0284c7; font-weight: bold; margin-top: 5px; }}
        .section {{ margin-bottom: 30px; }}
        .section-title {{ font-size: 18px; color: #0f172a; border-left: 4px solid #0284c7; padding-left: 10px; margin-bottom: 15px; }}
        footer {{ border-top: 1px solid #e2e8f0; padding-top: 15px; text-align: center; font-size: 12px; color: #94a3b8; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📊 RELATÓRIO EXECUTIVO DE INTELIGÊNCIA ELEITORAL</h1>
            <div class="subtitle">Campanha Wilder Morais — Governador de Goiás 2026 &bull; Data: {hoje}</div>
        </div>
    </div>

    <div class="card-grid">
        <div class="card">
            <div class="card-title">Cidades de Goiás Mapeadas</div>
            <div class="card-value">{total_cidades} Cidades</div>
        </div>
        <div class="card">
            <div class="card-title">Visualizações Canal YouTube</div>
            <div class="card-value">{total_youtube_views:,} Views</div>
        </div>
        <div class="card">
            <div class="card-title">Monitoramento Google Trends</div>
            <div class="card-value">{total_trends} Pautas Capturadas</div>
        </div>
        <div class="card">
            <div class="card-title">Briefings Matinais de IA</div>
            <div class="card-value">{total_briefings} Briefings Salvos</div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">📌 RESUMO DE OPERAÇÕES E METRICAS</div>
        <p>Este documento consolida os dados geoespaciais (PostGIS), engajamento de redes sociais, radar de notícias anticrise e análise de concorrência coletados automaticamente pelos robôs de inteligência eleitoral.</p>
    </div>

    <footer>
        Comitê de Inteligência Eleitoral &bull; Documento Gerado Automaticamente &bull; Wilder Morais 2026
    </footer>
</body>
</html>
"""

    with open(filename_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] Arquivo de Relatório Imprimível gerado: '{filename_html}'")
    print("[INFO] Abra o arquivo HTML no seu navegador e escolha 'Imprimir -> Salvar como PDF' para ter o relatório em mãos!")
    print("=" * 60)

if __name__ == "__main__":
    gerar_relatorio_pdf_executivo()
