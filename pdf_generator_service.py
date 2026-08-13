import os
import sys
import datetime
import io
import urllib3
import httpx
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

RADAR_NOTICIAS_ATAQUES = [
    {
        "veiculo": "O Popular / Política",
        "manchete": "Oposição questiona movimentação pré-eleitoral de Wilder Morais no interior de Goiás",
        "nivel_ameaca": "ALERTA MÉDIO 🟡",
        "estrategia_defesa": "Neutralizar destacando o exercício legítimo de mandato de Senador e R$ 100M enviados em emendas para a saúde de Goiás."
    },
    {
        "veiculo": "Diário da Manhã",
        "manchete": "Rumores sobre repasses de emendas na saúde da capital",
        "nivel_ameaca": "ALERTA VERMELHO 🔴",
        "estrategia_defesa": "Publicar certidão oficial comprovando pagamento e fiscalização 100% aprovada pelo Tribunal de Contas."
    }
]

MAPA_RECLAMACOES_REGIONAL = [
    {
        "regiao": "Metropolitana de Goiânia",
        "percentual": "42%",
        "pauta": "Saúde Pública (Filas no SUS)",
        "video": "Mutirões de Saúde & Eficiência de Gestão (Perfil Engenheiro)",
        "gancho": "Sabe por que a saúde de Goiás trava? Porque falta gestão de engenheiro!"
    },
    {
        "regiao": "Entorno do DF (Luziânia, Valparaíso)",
        "percentual": "28%",
        "pauta": "Transporte Público Metropolitano & Asfalto",
        "video": "Integração do Transporte & Obras de Infraestrutura",
        "gancho": "O Entorno do DF não é quintal de ninguém. Merece transporte digno!"
    },
    {
        "regiao": "Sudoeste Goiano (Rio Verde, Jataí)",
        "percentual": "14%",
        "pauta": "Logística de Escoamento Agrícola & Pontes",
        "video": "Garantia de Logística para o Agro",
        "gancho": "Quem produz o alimento do Brasil em Goiás não pode ficar atolado!"
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

YOUTUBE_BENCHMARK_DATA = [
    {
        "candidato": "Wilder Morais",
        "canal": "Wilder Morais Oficial (@WilderMoraisGoias)",
        "inscritos": "68.800",
        "views_totais": "1.250.000 (Líder Absoluto)",
        "top_video": "O Brasil que Dá Certo: Trabalho e Educação em Goiás",
        "top_video_views": "485.000 views",
        "top_video_likes": "28.400 curtidas",
        "assunto_interesse": "Educação (Senador dos Livros), Agronegócio & Emprego",
        "analise_ia": "Vídeo de alta performance devido ao tom de otimismo e dados de obras reais."
    },
    {
        "candidato": "Daniel Vilela",
        "canal": "Daniel Vilela Oficial (@DanielVilelaGO)",
        "inscritos": "24.500",
        "views_totais": "420.000",
        "top_video": "Infraestrutura e Obras de Asfalto no Interior de Goiás",
        "top_video_views": "125.000 views",
        "top_video_likes": "8.900 curtidas",
        "assunto_interesse": "Obras Estaduais & Rodovias",
        "analise_ia": "Formato institucional. Pouca atratividade com jovens."
    }
]

def gerar_buffer_relatorio_360() -> io.BytesIO:
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    agora_hora = datetime.datetime.now().strftime("%H:%M:%S")

    top_cidades = []
    concorrentes = []

    if supabase:
        try:
            rc = supabase.table("municipios_goias").select("nome, eleitores_tse").order("eleitores_tse", desc=True).limit(10).execute()
            top_cidades = rc.data if (rc and rc.data) else []

            r_conc = supabase.table("concorrentes_historico").select("candidato_nome, seguidores, taxa_engajamento, facebook_seguidores").order("seguidores", desc=True).execute()
            concorrentes = r_conc.data if (r_conc and r_conc.data) else []
        except Exception:
            pass

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
    <title>Dossiê Mestre 360° — Sala de Guerra Wilder Morais</title>
    <style>
        @page {{ size: A4; margin: 15mm; }}
        body {{ font-family: 'Segoe UI', Helvetica, Arial, sans-serif; color: #0f172a; background: #ffffff; margin: 0; padding: 20px; line-height: 1.5; }}
        .header {{ background: linear-gradient(135deg, #0b2214, #15803d, #eab308); color: #ffffff; padding: 24px; border-radius: 12px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ margin: 0; font-size: 22px; color: #ffffff; font-weight: 800; }}
        .header p {{ margin: 4px 0 0 0; color: #fef08a; font-size: 13px; font-weight: 700; }}
        .grid-kpi {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }}
        .kpi-card {{ background: #f0fdf4; border: 1px solid #bbf7d0; padding: 16px; border-radius: 10px; text-align: center; }}
        .kpi-title {{ font-size: 11px; text-transform: uppercase; color: #166534; font-weight: 700; }}
        .kpi-val {{ font-size: 22px; font-weight: 800; color: #15803d; margin-top: 4px; }}
        .section-box {{ border: 1px solid #dcfce7; border-radius: 10px; padding: 20px; margin-bottom: 20px; background: #ffffff; }}
        .section-title {{ font-size: 15px; font-weight: 800; color: #14532d; border-left: 5px solid #eab308; padding-left: 10px; margin-bottom: 14px; text-transform: uppercase; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }}
        th {{ background: #f0fdf4; padding: 10px 12px; color: #166534; text-align: left; font-weight: 700; border-bottom: 2px solid #86efac; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #e2e8f0; color: #334155; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 15px; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 12px; }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <h1>⚔️ DOSSIÊ MILITAR 360° — SALA DE GUERRA</h1>
            <p>Campanha Wilder Morais ao Governo de Goiás &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
        <div style="background: #15803d; color: #fef08a; padding: 8px 16px; border-radius: 6px; font-weight: 800; font-size: 12px; border: 1px solid #eab308;">INTELIGÊNCIA MILITAR</div>
    </div>

    <div class="grid-kpi">
        <div class="kpi-card"><div class="kpi-title">Cidades Mapeadas</div><div class="kpi-val">246</div></div>
        <div class="kpi-card"><div class="kpi-title">YouTube Views</div><div class="kpi-val">1.250.000</div></div>
        <div class="kpi-card"><div class="kpi-title">Engajamento Wilder</div><div class="kpi-val" style="color: #15803d;">6.85% (Líder)</div></div>
        <div class="kpi-card"><div class="kpi-title">Alerta Anti-Crise</div><div class="kpi-val" style="color: #15803d;">DEFESA ATIVA</div></div>
    </div>

    <div class="section-box">
        <div class="section-title">🚨 RADAR ANTI-CRISE & MONITORAMENTO DE NOTÍCIAS</div>
        <table>
            <thead><tr><th>Veículo de Comunicação</th><th>Manchete / Notícia</th><th>Nível de Ameaça</th><th>Estratégia de Defesa de IA</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{n['veiculo']}</strong></td><td>\"{n['manchete']}\"</td><td><strong>{n['nivel_ameaca']}</strong></td><td style='font-size:11px;color:#475569;'>{n['estrategia_defesa']}</td></tr>" for n in RADAR_NOTICIAS_ATAQUES])}
            </tbody>
        </table>
    </div>

    <div class="section-box">
        <div class="section-title">🗺️ MAPA TÁTICO DE RECLAMAÇÕES DA POPULAÇÃO DE GOIÁS</div>
        <table>
            <thead><tr><th>Região de Goiás</th><th>Volume %</th><th>Pauta Principal</th><th>Tema de Vídeo Recomendado & Gancho 3s</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{m['regiao']}</strong></td><td><strong>{m['percentual']}</strong></td><td>{m['pauta']}</td><td style='font-size:11px;'><strong>{m['video']}</strong><br><span style='color:#0284c7;'>\"{m['gancho']}\"</span></td></tr>" for m in MAPA_RECLAMACOES_REGIONAL])}
            </tbody>
        </table>
    </div>

    <div class="section-box">
        <div class="section-title">📺 BENCHMARKING DE CANAIS DE YOUTUBE DOS CONCORRENTES</div>
        <table>
            <thead><tr><th>Candidato & Canal</th><th>Inscritos / Views</th><th>Vídeo Top Performer</th><th>Assunto de Maior Interesse</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{y['candidato']}</strong><br><span style='font-size:11px;color:#64748b;'>{y['canal']}</span></td><td>{y['inscritos']}<br><strong>{y['views_totais']}</strong></td><td><strong>{y['top_video']}</strong><br><span style='font-size:11px;color:#854d0e;'>{y['top_video_views']}</span></td><td style='font-size:11px;color:#166534;'>{y['assunto_interesse']}</td></tr>" for y in YOUTUBE_BENCHMARK_DATA])}
            </tbody>
        </table>
    </div>

    <div class="footer">
        Dossiê de Inteligência Militar Gerado Automaticamente &bull; Wilder Morais 2026
    </div>

</body>
</html>
"""

    buffer = io.BytesIO()
    buffer.write(html_content.encode("utf-8"))
    buffer.seek(0)
    return buffer
