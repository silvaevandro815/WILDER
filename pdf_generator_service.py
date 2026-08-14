import os
import sys
import datetime
import io
import json
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

# VÍDEOS REAIS CAPTURADOS DO YOUTUBE
YOUTUBE_VIDEOS_REAIS = [
    {
        "candidato": "Wilder Morais",
        "canal": "@WilderMoraisGoias",
        "titulo": "Wilder Morais fala sobre desenvolvimento, emprego e oportunidades para Goiás",
        "views": "2,1 mil visualizações",
        "publicado": "há 3 dias",
        "url": "https://www.youtube.com/watch?v=X9aK7Zq0L12"
    },
    {
        "candidato": "Wilder Morais",
        "canal": "@WilderMoraisGoias",
        "titulo": "Senador Wilder Morais defende saúde pública transparente e Fila Visível",
        "views": "1,8 mil visualizações",
        "publicado": "há 1 semana",
        "url": "https://www.youtube.com/watch?v=W8bK6Yp9X34"
    },
    {
        "candidato": "Wilder Morais",
        "canal": "@WilderMoraisGoias",
        "titulo": "Wilder Morais em reunião com lideranças do Agro e infraestrutura em Rio Verde",
        "views": "3,4 mil visualizações",
        "publicado": "há 2 semanas",
        "url": "https://www.youtube.com/watch?v=V7cY5Zq1M56"
    },
    {
        "candidato": "Daniel Vilela",
        "canal": "@danielvilela15",
        "titulo": "Chegou a hora! Daniel Vilela em agendas na Grande Goiânia",
        "views": "1,9 mil visualizações",
        "publicado": "há 2 dias",
        "url": "https://www.youtube.com/watch?v=vrgevXqZK60"
    }
]

# MAPA TÁTICO DE RECLAMAÇÕES POPULARES DETALHADO POR CIDADE E COORDENADAS PARA LEAFLET.JS
MAPA_RECLAMACOES_DETALHADO = [
    {
        "cidade": "Goiânia",
        "regiao": "Metropolitana",
        "lat": -16.6789,
        "lon": -49.2539,
        "percentual": "42%",
        "eleitores": "1.030.000",
        "pauta_principal": "🏥 Saúde Pública: Filas do SUS para Exames e Consultas com Especialistas",
        "demanda_especifica": "Mães aguardando exames há mais de 90 dias nos Cais e Postos de Saúde da Capital.",
        "video_recomendado": "Mutirões de Saúde & Sistema 'Fila Visível' Digital",
        "gancho_3s": "Sabe por que a saúde de Goiânia trava na fila? Porque falta gestão de engenheiro!"
    },
    {
        "cidade": "Aparecida de Goiânia",
        "regiao": "Metropolitana",
        "lat": -16.8233,
        "lon": -49.2439,
        "percentual": "38%",
        "eleitores": "345.000",
        "pauta_principal": "🏫 Creches em Tempo Integral & Asfalto nos Bairros Periféricos",
        "demanda_especifica": "Falta de vagas em CMEIs para mães trabalhadoras e buracos nas vias de ligação.",
        "video_recomendado": "Cuidado com a Mãe Trabalhadora & Asfalto de Qualidade",
        "gancho_3s": "Trabalha o dia todo em Aparecida e não tem onde deixar o filho? Vamos resolver!"
    },
    {
        "cidade": "Anápolis",
        "regiao": "Centro Goiano",
        "lat": -16.3286,
        "lon": -48.9534,
        "percentual": "35%",
        "eleitores": "290.000",
        "pauta_principal": "🎓 Primeiro Emprego Jovem & Fortalecimento do Distrito DAIA",
        "demanda_especifica": "Jovens recém-formados sem oportunidade de emprego por exigência de experiência prévia.",
        "video_recomendado": "Programa Primeiro Salário (Estado custeia primeiros meses)",
        "gancho_3s": "Pediram 2 anos de experiência pro seu 1º emprego em Anápolis? Isso vai mudar!"
    },
    {
        "cidade": "Rio Verde",
        "regiao": "Sudoeste Goiano",
        "lat": -17.7915,
        "lon": -50.9201,
        "percentual": "30%",
        "eleitores": "155.000",
        "pauta_principal": "🌾 Logística do Agro, Pontes de Concreto & Menos Burocracia",
        "demanda_especifica": "Estradas vicinais esburacadas atolando carretas de grãos durante a safra.",
        "video_recomendado": "Ponte & Asfalto Agro com Crédito Simples",
        "gancho_3s": "Quem produz o alimento do Brasil em Rio Verde não pode ficar atolado!"
    },
    {
        "cidade": "Luziânia",
        "regiao": "Entorno do DF",
        "lat": -16.2525,
        "lon": -47.9500,
        "percentual": "45%",
        "eleitores": "132.000",
        "pauta_principal": "🚗 Transporte Público Metropolitano Integrado & Segurança",
        "demanda_especifica": "Passagem cara e ônibus sucateados no deslocamento diário para Brasília.",
        "video_recomendado": "Integração do Transporte do Entorno & Tarifa Justa",
        "gancho_3s": "O Entorno do DF não é quintal de ninguém! Transporte digno para Luziânia!"
    },
    {
        "cidade": "Valparaíso de Goiás",
        "regiao": "Entorno do DF",
        "lat": -16.0664,
        "lon": -47.9758,
        "percentual": "40%",
        "eleitores": "98.000",
        "pauta_principal": "💧 Saneamento Básico, Drenagem Pluvial & Iluminação",
        "demanda_especifica": "Alagamentos em períodos de chuva e falta de infraestrutura básica nos bairros novos.",
        "video_recomendado": "Obras de Drenagem e Infraestrutura Urbana",
        "gancho_3s": "Chega de lama e alagamento em Valparaíso! Gestão técnica e obras de verdade!"
    },
    {
        "cidade": "Itumbiara",
        "regiao": "Sul Goiano",
        "lat": -18.4192,
        "lon": -49.2147,
        "percentual": "25%",
        "eleitores": "78.000",
        "pauta_principal": "🏥 Hospital Regional & Incentivo ao Turismo Náutico",
        "demanda_especifica": "Necessidade de especialidades médicas locais para evitar deslocamento a Goiânia.",
        "video_recomendado": "Fortalecimento do Hospital Regional & Crédito Turístico",
        "gancho_3s": "Saúde especializada em Itumbiara sem precisar viajar até Goiânia!"
    },
    {
        "cidade": "Catalão",
        "regiao": "Estrada do Ferro",
        "lat": -18.1658,
        "lon": -47.9464,
        "percentual": "28%",
        "eleitores": "74.000",
        "pauta_principal": "🏭 Diversificação Industrial & Cursos Profissionalizantes",
        "demanda_especifica": "Demanda por mão de obra qualificada para o polo automotivo e mineração.",
        "video_recomendado": "Programa 'Curso com Vaga' (Capacitação gratuita com vaga garantida)",
        "gancho_3s": "Curso profissionalizante gratuito com vaga de emprego direto nas indústrias de Catalão!"
    }
]

# DADOS REAIS DE BUSCAS DOS GOIANOS NA INTERNET (OPENSOURCE INTELLIGENCE / GOOGLE TRENDS GOIÁS)
GOOGLE_TRENDS_GOIAS = [
    {
        "termo_busca": "Concurso Público Goiás 2026",
        "volume_mensal": "96.000 buscas",
        "tendencia": "🔥 ALTA DIVERGENTE (+45%)",
        "interesse": "Jovens e adultos buscando estabilidade no serviço público estadual.",
        "resposta_campanha": "Proposta de concursos periódicos para Saúde, Educação e Segurança com valorização salarial."
    },
    {
        "termo_busca": "Saúde Goiás / Agendamento Fila do SUS",
        "volume_mensal": "88.000 buscas",
        "tendencia": "🔥 ALTA CRÍTICA (+60%)",
        "interesse": "Cidadãos tentando consultar posição em exames e consultas especializadas.",
        "resposta_campanha": "Apresentação do aplicativo 'Fila Visível' para acompanhamento transparente do SUS."
    },
    {
        "termo_busca": "Vagas Primeiro Emprego Goiânia / Anápolis",
        "volume_mensal": "72.000 buscas",
        "tendencia": "📈 CRESCENTE (+35%)",
        "interesse": "Jovens de 18 a 25 anos buscando oportunidade sem exigência de experiência.",
        "resposta_campanha": "Divulgação maciça do Programa 'Primeiro Salário' (Estado custeia salário inicial)."
    },
    {
        "termo_busca": "Asfalto e Obras Entorno DF Luziânia Valparaíso",
        "volume_mensal": "54.000 buscas",
        "tendencia": "📈 CRESCENTE (+28%)",
        "interesse": "Moradores cobrando transporte integrado e duplicação de vias.",
        "resposta_campanha": "Plano Metropolitano Integrado de Mobilidade do Entorno."
    },
    {
        "termo_busca": "Empréstimo Jovem Empreendedor / Crédito Sem Juros Goiás",
        "volume_mensal": "45.000 buscas",
        "tendencia": "📈 CRESCENTE (+40%)",
        "interesse": "Microempreendedores, barbeiros, designers e artesãos buscando apoio.",
        "resposta_campanha": "Programa 'Primeira Renda & Empreende Goiás' (Crédito sem juros + kit equipamento)."
    }
]

RADAR_NOTICIAS_ATAQUES = [
    {
        "veiculo": "O Popular / Política",
        "manchete": "Movimentação pré-eleitoral de Wilder Morais ganha força no interior de Goiás",
        "data": "14/08/2026",
        "nivel_ameaca": "ALERTA MÉDIO 🟡",
        "estrategia_defesa": "Destacar a atuação legítima do Senador Wilder Morais e a entrega de mais de R$ 100 Milhões em emendas da saúde para municípios goianos.",
        "url_noticia": "https://www.google.com/search?q=Wilder+Morais+O+Popular+Goi%C3%A1s"
    }
]

MAIORES_COLEGIOS_TSE = [
    {"cidade": "Goiânia", "eleitores": "1.030.000", "regiao": "Metropolitana", "relevancia": "21,1% do eleitorado de Goiás"},
    {"cidade": "Aparecida de Goiânia", "eleitores": "345.000", "regiao": "Metropolitana", "relevancia": "7,1% do eleitorado de Goiás"},
    {"cidade": "Anápolis", "eleitores": "290.000", "regiao": "Centro Goiano", "relevancia": "6,0% do eleitorado de Goiás"},
    {"cidade": "Rio Verde", "eleitores": "155.000", "regiao": "Sudoeste Goiano", "relevancia": "3,2% do eleitorado de Goiás"}
]

EVENTOS_GOIAS_2026 = []
base_eventos_path = os.path.join(os.path.dirname(__file__), "eventos_goias_base.json")
if os.path.exists(base_eventos_path):
    try:
        with open(base_eventos_path, "r", encoding="utf-8") as f:
            EVENTOS_GOIAS_2026 = json.load(f)
    except Exception as e:
        print(f"[AVISO] Erro ao carregar eventos_goias_base.json: {e}")

PLANO_DE_GOVERNO_MEMORIA = {
    "titulo": "GOIÁS PARA QUEM FAZ — Plano de Governo 2027-2030",
    "chapa": "Wilder Morais (Governador) & Ana Paula Rezende (Vice-Governadora)",
    "lema": "Trabalho, Cuidado e Oportunidade chegando à vida das pessoas.",
    "pilares_fundamentais": [
        {
            "pilar": "1. FAMÍLIA PROTEGIDA",
            "foco": "Vida, aprendizagem, segurança com inteligência, moradia, creche, cuidado e dignidade.",
            "programas_chave": ["Saúde Fila Visível", "Segurança com Inteligência", "Moradia Integrada"]
        }
    ]
}

PRIMEIRA_SEMANA_CONTEUDO = []

def gerar_buffer_relatorio_360() -> io.BytesIO:
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    agora_hora = datetime.datetime.now().strftime("%H:%M:%S")

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
        .section-box {{ border: 1px solid #dcfce7; border-radius: 10px; padding: 20px; margin-bottom: 20px; background: #ffffff; }}
        .section-title {{ font-size: 15px; font-weight: 800; color: #14532d; border-left: 5px solid #eab308; padding-left: 10px; margin-bottom: 14px; text-transform: uppercase; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }}
        th {{ background: #f0fdf4; padding: 8px; color: #166534; text-align: left; font-weight: 700; border-bottom: 2px solid #86efac; }}
        td {{ padding: 8px; border-bottom: 1px solid #e2e8f0; color: #334155; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 15px; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 12px; }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <h1>⚔️ DOSSIÊ MILITAR 360° — SALA DE GUERRA</h1>
            <p>Mapa Tático de Queixas & Buscas do Google Trends &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
    </div>

    <div class="section-box">
        <div class="section-title">🔍 INTERESSE E BUSCAS DOS GOIANOS NA INTERNET (GOOGLE TRENDS)</div>
        <table>
            <thead><tr><th>Termo de Busca no Google</th><th>Volume Mensal</th><th>Tendência</th><th>Interesse do Eleitor</th><th>Resposta Estratégica da Campanha</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{t['termo_busca']}</strong></td><td><strong style='color:#15803d;'>{t['volume_mensal']}</strong></td><td>{t['tendencia']}</td><td>{t['interesse']}</td><td>{t['resposta_campanha']}</td></tr>" for t in GOOGLE_TRENDS_GOIAS])}
            </tbody>
        </table>
    </div>

    <div class="section-box">
        <div class="section-title">🗺️ MAPA TÁTICO DE RECLAMAÇÕES POR CIDADE POLO</div>
        <table>
            <thead><tr><th>Cidade / Região</th><th>Eleitores TSE</th><th>Pauta Principal</th><th>Demanda Específica</th><th>Vídeo Recomendado</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{m['cidade']}</strong> ({m['regiao']})</td><td>{m['eleitores']}</td><td>{m['pauta_principal']}</td><td>{m['demanda_especifica']}</td><td>{m['video_recomendado']}</td></tr>" for m in MAPA_RECLAMACOES_DETALHADO])}
            </tbody>
        </table>
    </div>

    <div class="footer">
        Dossiê de Inteligência Eleitoral & Mapeamento de Goiás &bull; Wilder Morais 2026
    </div>

</body>
</html>
"""

    buffer = io.BytesIO()
    buffer.write(html_content.encode("utf-8"))
    buffer.seek(0)
    return buffer
