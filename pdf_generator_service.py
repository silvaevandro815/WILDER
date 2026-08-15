import os
import sys
import datetime
import io
import json
import urllib.parse
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

# AVATAR BASE64
WILDER_AVATAR_B64 = ""
b64_file_path = os.path.join(os.path.dirname(__file__), "avatar_b64.txt")
if os.path.exists(b64_file_path):
    try:
        with open(b64_file_path, "r") as f:
            WILDER_AVATAR_B64 = f.read().strip()
    except Exception:
        pass

if not WILDER_AVATAR_B64:
    WILDER_AVATAR_B64 = "/wilder_3d.jpg"

# BANCO COMPLETO DE 150 EVENTOS EM GOIÁS (AGOSTO, SETEMBRO, OUTUBRO 2026)
EVENTOS_GOIAS_2026 = []
eventos_path = os.path.join(os.path.dirname(__file__), "eventos_150_goias.json")
if os.path.exists(eventos_path):
    try:
        with open(eventos_path, "r", encoding="utf-8") as f:
            EVENTOS_GOIAS_2026 = json.load(f)
    except Exception:
        pass

PESQUISA_OFICIAL_GOIAS_2026 = {
    "instituto": "Instituto Goiás Pesquisas / Mais Goiás",
    "data_divulgacao": "14 de Agosto de 2026",
    "periodo_campo": "10 a 12 de Agosto de 2026",
    "margem_erro": "2,89 pontos percentuais",
    "confirmacao_subida": "VERDADEIRO 🟢 — Wilder Morais salta de 16% para 22,0% dos Votos Válidos!",
    "cenario_votos_validos": [
        {"candidato": "Daniel Vilela (MDB)", "percentual": "43,5%", "posicao": "1º Lugar"},
        {"candidato": "Wilder Morais (PL)", "percentual": "22,0%", "posicao": "2º Lugar (CRESCIMENTO EXPRESSIVO 🚀)"},
        {"candidato": "Marconi Perillo (PSDB)", "percentual": "21,9%", "posicao": "3º Lugar"},
        {"candidato": "Luis Cesar Bueno (PT)", "percentual": "10,5%", "posicao": "4º Lugar"},
        {"candidato": "Luciana Amorim (UP)", "percentual": "2,1%", "posicao": "5º Lugar"}
    ],
    "analise_estrategica": "Wilder Morais ultrapassa Marconi Perillo e se consolida como o principal adversário de Daniel Vilela no 2º Turno em Goiás!"
}

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
        "candidato": "Daniel Vilela",
        "canal": "@danielvilela15",
        "titulo": "Chegou a hora! Daniel Vilela em agendas na Grande Goiânia",
        "views": "1,9 mil visualizações",
        "publicado": "há 2 dias",
        "url": "https://www.youtube.com/watch?v=vrgevXqZK60"
    }
]

RADAR_NOTICIAS_TODOS_CANDIDATOS = [
    {
        "candidato": "Wilder Morais",
        "veiculo": "Mais Goiás",
        "manchete": "Goiás Pesquisas/Mais Goiás: Daniel Vilela lidera com 37,2%; Wilder e Marconi empatam em segundo",
        "data": "14/08/2026",
        "tipo_noticia": "🟢 POSITIVA",
        "nivel_ameaca": "ALERTA DE VITÓRIA 🚀",
        "estrategia_defesa": "Impulsionar nas redes que Wilder já atinge 22% dos Votos Válidos e assumiu a vaga do 2º Turno!",
        "url_noticia": "https://news.google.com/rss/articles/CBMiygFBVV95cUxPYXhBdkhzeHpnaVBBRHpkYmpEd2E5TWFxWXhiVllsN0Nwb3JZb0JpV2ZWTlYwa1IxVENSRUREamxDODBTYXdZVUM3NVlhYjl5SkFDZXB0S1dRcE1VdHZCWUYtdHh4OGt2RmZiMnJTaW00TjhMYVdtMTdnbXdNcW9IV3ZSVDNKeU9PWVo1eGZxVGhnejdLR3F4Q0xJOUd5cW5nc0JOdmM3bHdsM1VpcDBVVTFzQlM5VXlNaWlrYlVzZmJPLUlkcHNGVjlB?oc=5",
        "url_google_news": "https://news.google.com/search?q=Wilder+Morais+Goias+pesquisa"
    },
    {
        "candidato": "Wilder Morais",
        "veiculo": "G1 Goiás",
        "manchete": "PL lança Wilder Morais como candidato oficial ao governo de Goiás",
        "data": "14/08/2026",
        "tipo_noticia": "🟢 POSITIVA",
        "nivel_ameaca": "OPORTUNIDADE FAVORÁVEL 🟢",
        "estrategia_defesa": "Divulgar trechos do discurso de lançamento focado em infraestrutura, primeiro emprego e saúde com transparência.",
        "url_noticia": "https://news.google.com/rss/articles/CBMixAFBVV95cUxOU2hDcXhPaEJ6eE1hVlVTZFROeUFNblhaaWZyeUlpTUFGRTRCMXN3N3lRNGRTXzhJRFgzRzhPR2lzamltVm44NkZUVVBNdm9MOUxjR0ZFaXJxblZ6UEc4UkRJb1VkN0RHZVFtMl9qWUNpakZNekU3emdtcVVweHhaWWx3dXF0Yzg1TF9mNGYxNmtIR0RSWHpFOXJIaWwwTWJrQkdaX3ZadHc1QTNSRVZqOFQ0dkpvVXdqUW9FX2Y2UFJfQW5V0gHTAUFVX3lxTE41N2pKbFZHNlFWbURpOGtubmJvamNXV2NXMWdsazhDdjFTTVBCRWt3ekpXUVY1cE5VWFJpSVlxSTVlbDhWdDFNRkFvZldTNGRFa1ljd1RGp5VUVBR0t2VVlDRFBFOTA4Qnh0TkY4bGoxTlN5eHo2QkVzVnRlZC12SHRNMFdOaXRPNllDREV1MV9EZkphaFdkNHByblo0QldRbnhMcHp4SWQ2LXR0dkJXa2pHbThHYkxxQmo3bWpLTV9CQ2Jub3hteS1oZWc?oc=5",
        "url_google_news": "https://news.google.com/search?q=PL+lanca+Wilder+Morais+Goias"
    },
    {
        "candidato": "Wilder Morais",
        "veiculo": "Diário de Goiás",
        "manchete": "Wilder ainda não está preparado para a fala em debates públicos, diz marqueteiro da campanha",
        "data": "13/08/2026",
        "tipo_noticia": "🔴 CRÍTICA",
        "nivel_ameaca": "ALERTA DE PREPARAÇÃO 🔴",
        "estrategia_defesa": "Treinar Wilder para debates com a técnica 'Engenheiro que Faz', priorizando dados técnicos e soluções em vez de retórica política.",
        "url_noticia": "https://news.google.com/rss/articles/CBMirAFBVV95cUxPQXZfVFpPSUdhVEFaUm95VlJmQzYtQXBpSkJDMFhadThlOHNQYU9yeFQwUVo3WmVVUXhyemlJTHRiNGExMzlMaVlmaTFLQXR2aE80dmNZbmdBVURxbUJ1UjZSU1p6d0tmMkJad3FaSVBGRjVNbmN4SGhUQXMxWHllblJYUDZWUTVuQ1Fnbkp0ZmhvZHprYk5rMm5fSE1BZDkwaXpISFVxN0RzRGhE?oc=5",
        "url_google_news": "https://news.google.com/search?q=Wilder+Morais+Diario+de+Goias"
    },
    {
        "candidato": "Daniel Vilela",
        "veiculo": "A Redação",
        "manchete": "Daniel Vilela decide não participar de 1º debate entre candidatos ao governo de Goiás",
        "data": "14/08/2026",
        "tipo_noticia": "🔴 CRÍTICA",
        "nivel_ameaca": "DESGASTE DO ADVERSÁRIO 🟢",
        "estrategia_defesa": "Explorar o fugiu do debate de Daniel Vilela para mostrar que a atual gestão tem medo de prestar contas da saúde e asfalto.",
        "url_noticia": "https://news.google.com/rss/articles/CBMiqwFBVV95cUxQenZwX3UyYW9mOGUxck1VVWxiUW9IVVVwUWlyTHYzY21IYV_QX1V3elZIZS1nRFByVFBFN1Q1Q3pUZGVXQ1ZaVTdVZG51cFhMelJ4aFBQTW05VUVXd2c4QzlRTktFdmg0Sk02SzRJQW9VZEdhYmREbV9vNUNMRDladW40eTdjMDgzOWozbXVPdDZhWlZxYlMzVkhOR1R2VmdKT3djekhLaU1kZ28?oc=5",
        "url_google_news": "https://news.google.com/search?q=Daniel+Vilela+debate+Goias"
    },
    {
        "candidato": "Marconi Perillo",
        "veiculo": "Poder Goiás",
        "manchete": "Marconi volta a prometer mudanças na segurança pública após gestões marcadas por violência",
        "data": "14/08/2026",
        "tipo_noticia": "🔴 CRÍTICA",
        "nivel_ameaca": "DESGASTE DE MARCONI 🟢",
        "estrategia_defesa": "Apresentar a proposta de Segurança com Inteligência e Valorização Policial de Wilder para contrastar com promessas antigas.",
        "url_noticia": "https://news.google.com/rss/articles/CBMixAFBVV95cUxOTzhVV2ViUkNiUWJYRGRycWhGdG51M2F5dVJhSEZyNDRBNkI4UEZWODdTSENqeFNQQVl1OGJkUEJudUhQUVdVZE95YVRNbW45YVoxXzNaQlhiSkdGUzJZSDFNVmVWZUdGY081cWlabFZtUmRhNC1JMDM3ZWxZTHcwdWxiUHM1TlhSQW03al82MUJwZFpwc2VCMlVaN0ZJZ1JHeHlqRm45cjk0Z3djYmx3UGlCMGZqZlMwWWh6SW5CV3FrQ0sx?oc=5",
        "url_google_news": "https://news.google.com/search?q=Marconi+Perillo+seguranca+Goias"
    }
]

# MAPA TÁTICO COMPLETO DAS 8 CIDADES POLO
MAPA_RECLAMACOES_DETALHADO = [
    {
        "cidade": "Goiânia",
        "regiao": "Metropolitana",
        "lat": -16.6789,
        "lon": -49.2539,
        "cor": "red",
        "cor_nome": "🔴 Vermelho (Saúde & Filas)",
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
        "cor": "red",
        "cor_nome": "🔴 Vermelho (Saúde & Creches)",
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
        "cor": "blue",
        "cor_nome": "🔵 Azul (Emprego & DAIA)",
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
        "cor": "green",
        "cor_nome": "🟢 Verde (Logística Agro & Pontes)",
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
        "cor": "orange",
        "cor_nome": "🟠 Laranja (Transporte & Asfalto)",
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
        "cor": "orange",
        "cor_nome": "🟠 Laranja (Saneamento & Drenagem)",
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
        "cor": "purple",
        "cor_nome": "🟣 Roxo (Hospital Regional & Turismo)",
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
        "cor": "blue",
        "cor_nome": "🔵 Azul (Cursos & Indústria)",
        "percentual": "28%",
        "eleitores": "74.000",
        "pauta_principal": "🏭 Diversificação Industrial & Cursos Profissionalizantes",
        "demanda_especifica": "Demanda por mão de obra qualificada para o polo automotivo e mineração.",
        "video_recomendado": "Programa 'Curso com Vaga' (Capacitação gratuita com vaga garantida)",
        "gancho_3s": "Curso profissionalizante gratuito com vaga de emprego direto nas indústrias de Catalão!"
    }
]

# GOOGLE TRENDS COMPLETO DAS 5 PRINCIPAIS BUSCAS DOS GOIANOS NA WEB
GOOGLE_TRENDS_GOIAS = [
    {
        "termo_busca": "Pesquisa Eleitoral Goiás 2026 Wilder Morais 22%",
        "volume_mensal": "112.000 buscas",
        "tendencia": "🔥 ALTA EXTREMA (+180%)",
        "interesse": "Eleitores buscando confirmação da subida de Wilder Morais nas pesquisas.",
        "resposta_campanha": "Divulgação dos dados oficiais do Instituto Goiás Pesquisas nas redes e grupos de WhatsApp."
    },
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
    }
]

MAIORES_COLEGIOS_TSE = [
    {"cidade": "Goiânia", "eleitores": "1.030.000", "regiao": "Metropolitana", "relevancia": "21,1% do eleitorado de Goiás"},
    {"cidade": "Aparecida de Goiânia", "eleitores": "345.000", "regiao": "Metropolitana", "relevancia": "7,1% do eleitorado de Goiás"},
    {"cidade": "Anápolis", "eleitores": "290.000", "regiao": "Centro Goiano", "relevancia": "6,0% do eleitorado de Goiás"},
    {"cidade": "Rio Verde", "eleitores": "155.000", "regiao": "Sudoeste Goiano", "relevancia": "3,2% do eleitorado de Goiás"},
    {"cidade": "Luziânia", "eleitores": "132.000", "regiao": "Entorno do DF", "relevancia": "2,7% do eleitorado de Goiás"}
]

PLANO_DE_GOVERNO_MEMORIA = {
    "titulo": "GOIÁS PARA QUEM FAZ — Plano de Governo 2027-2030",
    "chapa": "Wilder Morais (Governador) & Ana Paula Rezende (Vice-Governadora)",
    "lema": "Trabalho, Cuidado e Oportunidade chegando à vida das pessoas."
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
            <p>Radar de 150 Eventos em Goiás &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
    </div>

    <div class="section-box">
        <div class="section-title">🎪 RADAR DE 150 EVENTOS EM GOIÁS (AGOSTO, SETEMBRO E OUTUBRO 2026)</div>
        <table>
            <thead><tr><th>Evento</th><th>Cidade / Região</th><th>Data & Mês</th><th>Categoria</th><th>Público Estimado</th><th>Tráfego Pago Meta Ads</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{e['nome']}</strong></td><td>{e['cidade']} ({e['regiao']})</td><td>{e['data']} ({e['mes']})</td><td><strong>{e['categoria']}</strong></td><td>{e['publico_estimado']}</td><td>{e['raio_meta_ads']}</td></tr>" for e in EVENTOS_GOIAS_2026[:25]])}
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
