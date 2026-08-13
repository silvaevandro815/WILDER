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

# Inteligência Local de Benchmarking de YouTube dos Concorrentes
YOUTUBE_BENCHMARK_DATA = [
    {
        "candidato": "Wilder Morais",
        "canal": "Wilder Morais Oficial (@WilderMoraisGoias)",
        "inscritos": "68.800",
        "views_totais": "1.250.000 (Líder Absoluto)",
        "top_video": "O Brasil que Dá Certo: Trabalho e Educação em Goiás",
        "top_video_views": "485.000 views",
        "top_video_likes": "28.400 curtidas",
        "assunto_interesse": "Educação (Senador dos Livros), Agronegócio & Geração de Empregos",
        "analise_ia": "Vídeo de alta performance devido ao tom de otimismo e dados de obras reais. Gancho emocional forte nos primeiros 3s apelando para orgulho goiano."
    },
    {
        "candidato": "Daniel Vilela",
        "canal": "Daniel Vilela Oficial (@DanielVilelaGO)",
        "inscritos": "24.500",
        "views_totais": "420.000",
        "top_video": "Infraestrutura e Obras de Asfalto no Interior de Goiás",
        "top_video_views": "125.000 views",
        "top_video_likes": "8.900 curtidas",
        "assunto_interesse": "Obras Estaduais, Rodovias & Parcerias com Prefeitos",
        "analise_ia": "Formato de minidocumentário institucional. Boa retenção no público político regional, mas pouca atratividade para eleitores jovens."
    },
    {
        "candidato": "Marconi Perillo",
        "canal": "Marconi Perillo Oficial (@MarconiPerillo)",
        "inscritos": "38.200",
        "views_totais": "610.000",
        "top_video": "Memórias de Goiás: Os Programas Sociais do Passado",
        "top_video_views": "95.000 views",
        "top_video_likes": "6.200 curtidas",
        "assunto_interesse": "Nostalgia Política, Histórico de Mandatos & Críticas ao Governo",
        "analise_ia": "Conteúdo focado no legado de gestões passadas. Retenção média baixa devido a tom defensivo e saudosista."
    }
]

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
    com o novo design verde e amarelo da campanha e inteligência de YouTube.
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
        .header {{ background: linear-gradient(135deg, #15803d, #16a34a, #eab308); color: #ffffff; padding: 24px; border-radius: 12px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 15px rgba(22,163,74,0.3); }}
        .header h1 {{ margin: 0; font-size: 22px; color: #ffffff; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .header p {{ margin: 4px 0 0 0; color: #fef08a; font-size: 13px; font-weight: 600; }}
        .grid-kpi {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }}
        .kpi-card {{ background: #f0fdf4; border: 1px solid #bbf7d0; padding: 16px; border-radius: 10px; text-align: center; }}
        .kpi-title {{ font-size: 11px; text-transform: uppercase; color: #166534; font-weight: 700; letter-spacing: 0.5px; }}
        .kpi-val {{ font-size: 22px; font-weight: 800; color: #15803d; margin-top: 4px; }}
        .section-box {{ border: 1px solid #dcfce7; border-radius: 10px; padding: 20px; margin-bottom: 20px; background: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
        .section-title {{ font-size: 15px; font-weight: 800; color: #14532d; border-left: 5px solid #eab308; padding-left: 10px; margin-bottom: 14px; text-transform: uppercase; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }}
        th {{ background: #f0fdf4; padding: 10px 12px; color: #166534; text-align: left; font-weight: 700; border-bottom: 2px solid #86efac; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #e2e8f0; color: #334155; }}
        tr:nth-child(even) td {{ background: #f8fafc; }}
        .badge-pos {{ background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
        .badge-wilder {{ background: #fef08a; color: #854d0e; padding: 2px 8px; border-radius: 4px; font-weight: 800; font-size: 11px; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 15px; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 12px; }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <h1>🔰 DOSSIÊ MESTRE 360° DE INTELIGÊNCIA ELEITORAL</h1>
            <p>Campanha Wilder Morais ao Governo de Goiás &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
        <div style="background: #15803d; color: #fef08a; padding: 8px 16px; border-radius: 6px; font-weight: 800; font-size: 12px; border: 1px solid #eab308;">VERDE & AMARELO GOIÁS</div>
    </div>

    <div class="grid-kpi">
        <div class="kpi-card"><div class="kpi-title">Cidades Mapeadas</div><div class="kpi-val">246</div></div>
        <div class="kpi-card"><div class="kpi-title">YouTube Views</div><div class="kpi-val">{youtube_stats.get('visualizacoes_totais', 1250000):,}</div></div>
        <div class="kpi-card"><div class="kpi-title">Engajamento Wilder</div><div class="kpi-val" style="color: #15803d;">6.85% (Líder)</div></div>
        <div class="kpi-card"><div class="kpi-title">Status da Operação</div><div class="kpi-val" style="color: #15803d;">100% ATIVO</div></div>
    </div>

    <div class="section-box">
        <div class="section-title">📺 BENCHMARKING DE CANAIS DE YOUTUBE DOS CONCORRENTES</div>
        <table>
            <thead><tr><th>Candidato & Canal</th><th>Inscritos / Views Totais</th><th>Vídeo Mais Visto (Top Performer)</th><th>Assunto de Maior Interesse</th><th>Análise de IA (Por que performou)</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{y['candidato']}</strong><br><span style='font-size:11px;color:#64748b;'>{y['canal']}</span></td><td>{y['inscritos']} inscritos<br><span style='font-size:11px;color:#15803d;font-weight:bold;'>{y['views_totais']}</span></td><td><strong>{y['top_video']}</strong><br><span style='font-size:11px;color:#854d0e;font-weight:bold;'>{y['top_video_views']} &bull; {y['top_video_likes']}</span></td><td style='font-size:11px;color:#166534;'><strong>{y['assunto_interesse']}</strong></td><td style='font-size:11px;color:#475569;'>{y['analise_ia']}</td></tr>" for y in YOUTUBE_BENCHMARK_DATA])}
            </tbody>
        </table>
    </div>

    <div class="section-box">
        <div class="section-title">⚔️ GUERRA DE CONCORRENTES & REDES SOCIAIS</div>
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
            <thead><tr><th>Candidato & Rede</th><th>Título do Post / Tema</th><th>Curtidas / Views</th><th>Engajamento</th><th>Análise de IA</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{p['candidato']}</strong><br><span style='font-size:11px;color:#64748b;'>{p['rede']}</span></td><td><strong>{p['titulo']}</strong><br><span style='font-size:11px;color:#15803d;font-weight:bold;'>{p['pauta']}</span></td><td>{p['curtidas']} curtidas<br><span style='font-size:11px;color:#64748b;'>{p['views']} views</span></td><td><span class='badge-pos'>{p['engajamento']}</span></td><td style='font-size:11px;color:#475569;'>{p['analise_ia']}</td></tr>" for p in POSTS_VIRAIS_MESTRE])}
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
