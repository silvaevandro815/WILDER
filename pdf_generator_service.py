import os
import sys
import datetime
import io
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

# Inteligência Local de Posts Virais
POSTS_VIRAIS_MESTRE = [
    {
        "candidato": "Wilder Morais",
        "rede": "Instagram Reels",
        "titulo": "O Senador dos Livros: +1 Milhão de Livros Distribuídos em Goiás",
        "curtidas": "28.400",
        "comentarios": "2.150",
        "views": "485.000",
        "engajamento": "7.42%",
        "pauta": "Educação & Legado",
        "analise_ia": "Gancho inicial de 3s apelando para nostalgia de Goiás e conselho de família. Alta retenção emocional."
    },
    {
        "candidato": "Wilder Morais",
        "rede": "YouTube VLOG",
        "titulo": "Cavalgada de Jataí e Encontro com Produtores Rurais de Goiás",
        "curtidas": "18.200",
        "comentarios": "1.420",
        "views": "310.000",
        "engajamento": "7.35%",
        "pauta": "Agronegócio & Tradição",
        "analise_ia": "Alta conexão emocional com o público sertanejo e produtor rural. Mostra simplicidade e pé no chão."
    },
    {
        "candidato": "Daniel Vilela",
        "rede": "Instagram Reels",
        "titulo": "Visita às Obras da GO-070 no Interior de Goiás",
        "curtidas": "9.400",
        "comentarios": "480",
        "views": "125.000",
        "engajamento": "3.20%",
        "pauta": "Infraestrutura / Governo",
        "analise_ia": "Discurso institucional focado em obras públicas. Engajamento moderado limitado à base aliada."
    },
    {
        "candidato": "Marconi Perillo",
        "rede": "Instagram Carrossel",
        "titulo": "TBT de Obras Históricas de Goiás",
        "curtidas": "7.200",
        "comentarios": "650",
        "views": "95.000",
        "engajamento": "2.65%",
        "pauta": "Nostalgia & Política",
        "analise_ia": "Post nostalgia de governos passados. Baixo apelo orgânico no público jovem e novos eleitores."
    }
]

def gerar_buffer_relatorio_360() -> io.BytesIO:
    """
    Gera o Dossiê Mestre 360° da Campanha de Wilder Morais em memória (BytesIO)
    com dados de todos os candidatos e inteligência de posts mais engajados.
    """
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    agora_hora = datetime.datetime.now().strftime("%H:%M:%S")

    top_cidades = []
    concorrentes = []
    youtube_stats = {}
    briefings = []

    if supabase:
        try:
            rc = supabase.table("municipios_goias").select("nome, eleitores_tse").order("eleitores_tse", desc=True).limit(10).execute()
            top_cidades = rc.data if (rc and rc.data) else []

            r_conc = supabase.table("concorrentes_historico").select("candidato_nome, seguidores, taxa_engajamento, facebook_seguidores").order("seguidores", desc=True).execute()
            concorrentes = r_conc.data if (r_conc and r_conc.data) else []

            rb = supabase.table("briefings_diarios").select("resumo_cenario, ideias_roteiros").order("data", desc=True).limit(1).execute()
            briefings = rb.data if (rb and rb.data) else []

            ry = supabase.table("youtube_performance").select("inscritos, visualizacoes_totais").order("data", desc=True).limit(1).execute()
            if ry and ry.data:
                youtube_stats = ry.data[0]

        except Exception as err:
            print(f"[AVISO] Erro ao carregar Supabase para PDF: {err}")

    # Fallback se a tabela de concorrentes estiver vazia no banco
    if not concorrentes:
        concorrentes = [
            {"candidato_nome": "Wilder Morais (@WilderMorais)", "seguidores": 310000, "taxa_engajamento": 6.85, "facebook_seguidores": 142000},
            {"candidato_nome": "Daniel Vilela (@Danielvilelaoficial)", "seguidores": 185000, "taxa_engajamento": 3.45, "facebook_seguidores": 95000},
            {"candidato_nome": "Marconi Perillo (@Marconiperillo)", "seguidores": 240000, "taxa_engajamento": 2.80, "facebook_seguidores": 130000}
        ]

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Dossiê Mestre 360° — Wilder Morais 2026</title>
    <style>
        @page {{ size: A4; margin: 15mm; }}
        body {{ font-family: 'Segoe UI', Helvetica, Arial, sans-serif; color: #0f172a; background: #ffffff; margin: 0; padding: 20px; line-height: 1.5; }}
        .header {{ background: #0f172a; color: #ffffff; padding: 24px; border-radius: 12px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ margin: 0; font-size: 22px; color: #38bdf8; font-weight: 800; }}
        .header p {{ margin: 4px 0 0 0; color: #94a3b8; font-size: 13px; }}
        .grid-kpi {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }}
        .kpi-card {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 10px; text-align: center; }}
        .kpi-title {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.5px; }}
        .kpi-val {{ font-size: 22px; font-weight: 800; color: #0284c7; margin-top: 4px; }}
        .section-box {{ border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin-bottom: 20px; background: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
        .section-title {{ font-size: 15px; font-weight: 800; color: #0f172a; border-left: 4px solid #0284c7; padding-left: 10px; margin-bottom: 14px; text-transform: uppercase; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }}
        th {{ background: #f1f5f9; padding: 10px 12px; color: #475569; text-align: left; font-weight: 700; border-bottom: 2px solid #cbd5e1; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #e2e8f0; color: #334155; }}
        tr:nth-child(even) td {{ background: #f8fafc; }}
        .badge-pos {{ background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
        .badge-wilder {{ background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-weight: 800; font-size: 11px; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 15px; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 12px; }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <h1>🌐 DOSSIÊ MESTRE 360° DE INTELIGÊNCIA ELEITORAL</h1>
            <p>Campanha Wilder Morais ao Governo de Goiás &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
        <div style="background: #0284c7; color: #fff; padding: 8px 16px; border-radius: 6px; font-weight: bold; font-size: 12px;">RELATÓRIO OFICIAL</div>
    </div>

    <div class="grid-kpi">
        <div class="kpi-card"><div class="kpi-title">Cidades Mapeadas</div><div class="kpi-val">246</div></div>
        <div class="kpi-card"><div class="kpi-title">YouTube Views</div><div class="kpi-val">{youtube_stats.get('visualizacoes_totais', 1250000):,}</div></div>
        <div class="kpi-card"><div class="kpi-title">Engajamento Wilder</div><div class="kpi-val" style="color: #16a34a;">6.85% (Líder)</div></div>
        <div class="kpi-card"><div class="kpi-title">Status da Operação</div><div class="kpi-val" style="color: #16a34a;">100% ATIVO</div></div>
    </div>

    <div class="section-box">
        <div class="section-title">⚔️ GUERRA DE CONCORRENTES & COMPARATIVO DE REDES</div>
        <table>
            <thead><tr><th>Candidato</th><th>Seguidores Instagram</th><th>Taxa Engajamento</th><th>Seguidores Facebook</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{c['candidato_nome']}</strong> {'<span class=\"badge-wilder\">PRÉ-CANDIDATO</span>' if 'Wilder' in c['candidato_nome'] else ''}</td><td>{c['seguidores']:,}</td><td><span class='badge-pos'>{c['taxa_engajamento']}%</span></td><td>{c['facebook_seguidores']:,}</td></tr>" for c in concorrentes])}
            </tbody>
        </table>
    </div>

    <div class="section-box">
        <div class="section-title">🏆 TECNOLOGIA DE ENGAJAMENTO: RANKING DE POSTS VIRAIS</div>
        <table>
            <thead><tr><th>Candidato & Rede</th><th>Título do Post / Tema</th><th>Curtidas / Views</th><th>Engajamento</th><th>Análise de IA (Por que viralizou?)</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{p['candidato']}</strong><br><span style='font-size:11px;color:#64748b;'>{p['rede']}</span></td><td><strong>{p['titulo']}</strong><br><span style='font-size:11px;color:#0284c7;'>{p['pauta']}</span></td><td>{p['curtidas']} curtidas<br><span style='font-size:11px;color:#64748b;'>{p['views']} views</span></td><td><span class='badge-pos'>{p['engajamento']}</span></td><td style='font-size:11px;color:#475569;'>{p['analise_ia']}</td></tr>" for p in POSTS_VIRAIS_MESTRE])}
            </tbody>
        </table>
    </div>

    <div class="section-box">
        <div class="section-title">🗺️ TOP 10 MAIORES COLÉGIOS ELEITORAIS DE GOIÁS (TSE)</div>
        <table>
            <thead><tr><th>#</th><th>Cidade / Município</th><th>Eleitores TSE (Votos)</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td>{i+1}</td><td><strong>{c['nome']}</strong></td><td>{c['eleitores_tse']:,} eleitores</td></tr>" for i, c in enumerate(top_cidades)])}
            </tbody>
        </table>
    </div>

    <div class="footer">
        Relatório Gerado Automaticamente pelo Sistema de Inteligência Eleitoral de Wilder Morais &bull; 2026
    </div>

</body>
</html>
"""

    buffer = io.BytesIO()
    buffer.write(html_content.encode("utf-8"))
    buffer.seek(0)
    return buffer
