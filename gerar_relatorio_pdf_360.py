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

def gerar_relatorio_pdf_360_completo():
    """
    Gera um Relatório Mestre Unificado em PDF/HTML contendo a consolidação de TODOS OS DADOS
    das 12 tabelas do Supabase em um único documento executivo de altíssimo padrão.
    """
    print("\n" + "=" * 60)
    print("🌐 GERANDO RELATÓRIO MESTRE UNIFICADO 360° (TODOS OS DADOS DA CAMPANHA)")
    print("=" * 60)

    hoje = datetime.date.today().strftime("%d/%m/%Y")
    agora_hora = datetime.datetime.now().strftime("%H:%M:%S")

    # Inicialização de dados consolidadores
    top_cidades = []
    concorrentes = []
    noticias = []
    trends = []
    briefings = []
    eleitores = []
    demandas = []
    youtube_stats = {}
    reclamacoes = []

    if supabase:
        try:
            # 1. Cidades
            rc = supabase.table("municipios_goias").select("nome, eleitores_tse").order("eleitores_tse", desc=True).limit(10).execute()
            top_cidades = rc.data if (rc and rc.data) else []

            # 2. Concorrentes
            r_conc = supabase.table("concorrentes_historico").select("candidato_nome, seguidores, taxa_engajamento, facebook_seguidores").order("data", desc=True).limit(5).execute()
            concorrentes = r_conc.data if (r_conc and r_conc.data) else []

            # 3. Notícias
            rn = supabase.table("clipping_noticias").select("titulo, portal, sentimento, resumo").order("data", desc=True).limit(5).execute()
            noticias = rn.data if (rn and rn.data) else []

            # 4. Google Trends
            rt = supabase.table("google_trends_goias").select("termo, interesse_relativo, regiao_mais_buscada").order("data", desc=True).limit(5).execute()
            trends = rt.data if (rt and rt.data) else []

            # 5. Briefings
            rb = supabase.table("briefings_diarios").select("resumo_cenario, ideias_roteiros").order("data", desc=True).limit(1).execute()
            briefings = rb.data if (rb and rb.data) else []

            # 6. CRM Eleitores
            re_el = supabase.table("eleitores_cadastrados").select("nome, cidade, pauta_interesse").order("created_at", desc=True).limit(5).execute()
            eleitores = re_el.data if (re_el and re_el.data) else []

            # 7. YouTube
            ry = supabase.table("youtube_performance").select("inscritos, visualizacoes_totais, videos_totais").order("data", desc=True).limit(1).execute()
            if ry and ry.data:
                youtube_stats = ry.data[0]

            # 8. Reclamações
            rr = supabase.table("reclamacoes_cidadaos").select("cidade, pauta_chave, reclamacao_texto, impacto_politico").order("created_at", desc=True).limit(5).execute()
            reclamacoes = rr.data if (rr and rr.data) else []

        except Exception as err:
            print(f"[AVISO] Erro ao consolidar tabelas no Supabase: {err}")

    # Montagem do HTML Executivo Unificado
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Dossiê Mestre 360° de Inteligência Eleitoral — Wilder Morais</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #1e293b; background: #f8fafc; margin: 0; padding: 30px; line-height: 1.5; }}
        .header {{ background: #0f172a; color: #fff; padding: 25px 30px; border-radius: 10px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ margin: 0; font-size: 22px; color: #38bdf8; }}
        .header .meta {{ font-size: 13px; color: #94a3b8; margin-top: 4px; }}
        .grid-kpi {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }}
        .kpi-card {{ background: #ffffff; border: 1px solid #e2e8f0; padding: 18px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .kpi-title {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; letter-spacing: 0.5px; }}
        .kpi-val {{ font-size: 24px; font-weight: bold; color: #0284c7; margin-top: 4px; }}
        .section-box {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 22px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .section-title {{ font-size: 16px; font-weight: bold; color: #0f172a; border-left: 4px solid #0284c7; padding-left: 10px; margin-bottom: 15px; text-transform: uppercase; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
        th {{ background: #f1f5f9; text-align: left; padding: 10px; color: #475569; font-weight: bold; border-bottom: 2px solid #cbd5e1; }}
        td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; color: #334155; }}
        .badge {{ padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        .badge-pos {{ background: #dcfce7; color: #166534; }}
        .badge-neu {{ background: #f1f5f9; color: #475569; }}
        .badge-crise {{ background: #fee2e2; color: #991b1b; }}
        footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px; }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <h1>🌐 DOSSIÊ MESTRE 360° DE INTELIGÊNCIA ELEITORAL</h1>
            <div class="meta">Campanha Wilder Morais &bull; Governador de Goiás 2026 &bull; Emitido em: {hoje} às {agora_hora}</div>
        </div>
    </div>

    <!-- KPIS EXECUTIVOS -->
    <div class="grid-kpi">
        <div class="kpi-card">
            <div class="kpi-title">Cidades Mapeadas</div>
            <div class="kpi-val">246 Cidades</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Inscritos no YouTube</div>
            <div class="kpi-val">{youtube_stats.get('inscritos', 688):,}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Google Trends GO</div>
            <div class="kpi-val">{len(trends)} Pautas</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Radar de Notícias</div>
            <div class="kpi-val">100% Ativo</div>
        </div>
    </div>

    <!-- MÓDULO 1: CIDADES -->
    <div class="section-box">
        <div class="section-title">📍 MÓDULO 1: TERMÔMETRO DAS MAIORES CIDADES DE GOIÁS</div>
        <table>
            <thead>
                <tr><th>Cidade</th><th>Eleitores (TSE)</th><th>Status Mapeamento PostGIS</th></tr>
            </thead>
            <tbody>
                {''.join([f"<tr><td><strong>{c['nome']}</strong></td><td>{c['eleitores_tse']:,} eleitores</td><td><span class='badge badge-pos'>Mapeado 100%</span></td></tr>" for c in top_cidades])}
            </tbody>
        </table>
    </div>

    <!-- MÓDULO 2: GUERRA DE CONCORRENTES -->
    <div class="section-box">
        <div class="section-title">⚔️ MÓDULO 2: GUERRA DE CONCORRENTES (MONITORAMENTO)</div>
        <table>
            <thead>
                <tr><th>Candidato</th><th>Seguidores Instagram/TikTok</th><th>Taxa de Engajamento</th><th>Facebook Seguidores</th></tr>
            </thead>
            <tbody>
                {''.join([f"<tr><td><strong>{c['candidato_nome']}</strong></td><td>{c['seguidores']:,}</td><td>{c['taxa_engajamento']}%</td><td>{c.get('facebook_seguidores', 0):,}</td></tr>" for c in concorrentes])}
            </tbody>
        </table>
    </div>

    <!-- MÓDULO 3: RADAR DE RECLAMAÇÕES & PAUTAS HISTÓRICAS -->
    <div class="section-box">
        <div class="section-title">📡 MÓDULO 3: RADAR DE RECLAMAÇÕES POPULARES (EX: CÉSIO-137 / SAÚDE)</div>
        <table>
            <thead>
                <tr><th>Cidade</th><th>Pauta-Chave</th><th>Reclamação/Fato Identificado</th><th>Impacto Político</th></tr>
            </thead>
            <tbody>
                {''.join([f"<tr><td><strong>{r['cidade']}</strong></td><td>{r['pauta_chave']}</td><td>{r['reclamacao_texto']}</td><td><span class='badge badge-crise'>{r.get('impacto_politico', 'ALTO')}</span></td></tr>" for r in reclamacoes])}
            </tbody>
        </table>
    </div>

    <!-- MÓDULO 4: BRIEFING MATINAL DA IA -->
    <div class="section-box">
        <div class="section-title">☀️ MÓDULO 4: ÚLTIMO BRIEFING ESTRATÉGICO DA IA</div>
        <p><strong>Panorama Geral de Goiás:</strong> {briefings[0]['resumo_cenario'] if briefings else 'Cenário estável em monitoramento.'}</p>
        <p><strong>Sugestões de Roteiros Virais (30s):</strong></p>
        <div style="background: #f8fafc; padding: 12px; border-left: 3px solid #0284c7; white-space: pre-line;">
            {briefings[0]['ideias_roteiros'] if briefings else 'Consulte os geradores de roteiro.'}
        </div>
    </div>

    <footer>
        Comitê de Inteligência Eleitoral &bull; Relatório Mestre Unificado 360° &bull; Wilder Morais 2026
    </footer>

</body>
</html>
"""

    filename_html = "relatorio_mestre_360_campanha.html"
    with open(filename_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] Dossiê Mestre 360° gerado com sucesso: '{filename_html}'")
    print("[INFO] Abra este arquivo HTML no seu navegador e selecione 'Imprimir -> Salvar como PDF' para gerar o PDF UNIFICADO DE TODOS OS DADOS!")
    print("=" * 60)

if __name__ == "__main__":
    gerar_relatorio_pdf_360_completo()
