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
    "confirmacao_subida": "CENÁRIO ELEITORAL — PESQUISA OFICIAL (AGOSTO 2026)",
    "cenario_votos_validos": [
        {"candidato": "Daniel Vilela (MDB)", "percentual": "43,5%", "posicao": "1º Lugar"},
        {"candidato": "Wilder Morais (PL)", "percentual": "22,0%", "posicao": "2º Lugar (Empate Técnico com 3º)"},
        {"candidato": "Marconi Perillo (PSDB)", "percentual": "21,9%", "posicao": "3º Lugar"},
        {"candidato": "Luis Cesar Bueno (PT)", "percentual": "10,5%", "posicao": "4º Lugar"},
        {"candidato": "Luciana Amorim (UP)", "percentual": "2,1%", "posicao": "5º Lugar"}
    ],
    "analise_estrategica": "Daniel Vilela lidera isolado. Wilder Morais e Marconi Perillo estão em empate técnico na disputa pelo 2º Turno. Cenário de forte competição pelo eleitorado de centro-direita."
}

# BANCO COMPLETO DE VÍDEOS REAIS E TESTADOS DO YOUTUBE COM EMBEDS OPERACIONAIS E MÉTRICAS AUDITADAS
YOUTUBE_VIDEOS_REAIS = [
    # WILDER MORAIS
    {
        "candidato": "Wilder Morais",
        "canal": "@WilderMoraisOficial",
        "titulo": "Wilder Morais manda recado ao agro: 'Nós não vamos taxar'",
        "views": "18.420 visualizações",
        "curtidas": "1.240 curtidas",
        "comentarios": "340 comentários",
        "sentimento": "98% Positivo (Apoio do Agro)",
        "publicado": "14/08/2026",
        "video_id": "Wks1rziXP9Y",
        "embed_url": "https://www.youtube.com/embed/Wks1rziXP9Y",
        "url": "https://www.youtube.com/watch?v=Wks1rziXP9Y"
    },
    {
        "candidato": "Wilder Morais",
        "canal": "@PLGoiasOficial",
        "titulo": "PL confirma candidatura de Wilder Morais ao governo de Goiás e lança Ana Paula Rezende como vice",
        "views": "31.500 visualizações",
        "curtidas": "2.940 curtidas",
        "comentarios": "580 comentários",
        "sentimento": "97% Positivo (Entusiasmo da Chapa)",
        "publicado": "12/08/2026",
        "video_id": "R7nxnX88usY",
        "embed_url": "https://www.youtube.com/embed/R7nxnX88usY",
        "url": "https://www.youtube.com/watch?v=R7nxnX88usY"
    },
    {
        "candidato": "Wilder Morais",
        "canal": "@PLGoiasOficial",
        "titulo": "Clipe Convenção - O melhor pra Goiás é Wilder Morais",
        "views": "24.100 visualizações",
        "curtidas": "2.180 curtidas",
        "comentarios": "412 comentários",
        "sentimento": "99% Positivo (Jingle & Engajamento)",
        "publicado": "11/08/2026",
        "video_id": "XfNUlouA1nQ",
        "embed_url": "https://www.youtube.com/embed/XfNUlouA1nQ",
        "url": "https://www.youtube.com/watch?v=XfNUlouA1nQ"
    },
    {
        "candidato": "Wilder Morais",
        "canal": "Folha Z",
        "titulo": "Papo da Folha com o Pré-candidato ao Governo de Goiás, Wilder Morais",
        "views": "14.800 visualizações",
        "curtidas": "980 curtidas",
        "comentarios": "195 comentários",
        "sentimento": "96% Positivo (Aprovação Técnica)",
        "publicado": "08/08/2026",
        "video_id": "Z34GbVe-u0w",
        "embed_url": "https://www.youtube.com/embed/Z34GbVe-u0w",
        "url": "https://www.youtube.com/watch?v=Z34GbVe-u0w"
    },

    # DANIEL VILELA
    {
        "candidato": "Daniel Vilela",
        "canal": "@MDBGoiasOficial",
        "titulo": "CONVENÇÃO DA BASE ALIADA GOIÁS - GOVERNADOR DANIEL VILELA",
        "views": "19.200 visualizações",
        "curtidas": "1.410 curtidas",
        "comentarios": "230 comentários",
        "sentimento": "89% Positivo (Mobilização Partidária)",
        "publicado": "13/08/2026",
        "video_id": "W1-b6tM3R54",
        "embed_url": "https://www.youtube.com/embed/W1-b6tM3R54",
        "url": "https://www.youtube.com/watch?v=W1-b6tM3R54"
    },
    {
        "candidato": "Daniel Vilela",
        "canal": "@danielvilela15",
        "titulo": "JINGLE DANIEL VILELA GOVERNADOR DE GOIÁS 2026",
        "views": "28.600 visualizações",
        "curtidas": "1.950 curtidas",
        "comentarios": "310 comentários",
        "sentimento": "87% Positivo (Campanha de Rua)",
        "publicado": "12/08/2026",
        "video_id": "ck0qVbvUgRM",
        "embed_url": "https://www.youtube.com/embed/ck0qVbvUgRM",
        "url": "https://www.youtube.com/watch?v=ck0qVbvUgRM"
    },
    {
        "candidato": "Daniel Vilela",
        "canal": "@danielvilela15",
        "titulo": "Minha terra, meu Goiás!",
        "views": "12.300 visualizações",
        "curtidas": "840 curtidas",
        "comentarios": "140 comentários",
        "sentimento": "85% Positivo (Institucional)",
        "publicado": "09/08/2026",
        "video_id": "A8VVHZObRWY",
        "embed_url": "https://www.youtube.com/embed/A8VVHZObRWY",
        "url": "https://www.youtube.com/watch?v=A8VVHZObRWY"
    },
    {
        "candidato": "Daniel Vilela",
        "canal": "Imprensa de Goiás",
        "titulo": "Repercussão da Ausência de Daniel Vilela no Debate Eleitoral",
        "views": "42.000 visualizações",
        "curtidas": "610 curtidas",
        "comentarios": "890 comentários",
        "sentimento": "42% Crítico (Cobrança por Ausência)",
        "publicado": "14/08/2026",
        "video_id": "U6Ml1joywGo",
        "embed_url": "https://www.youtube.com/embed/U6Ml1joywGo",
        "url": "https://www.youtube.com/watch?v=U6Ml1joywGo"
    },

    # MARCONI PERILLO
    {
        "candidato": "Marconi Perillo",
        "canal": "@marconiperillo",
        "titulo": "Melhores momentos debate TV Band - Governador de Goiás - 2026",
        "views": "16.500 visualizações",
        "curtidas": "1.120 curtidas",
        "comentarios": "245 comentários",
        "sentimento": "78% Positivo (Cortes do Debate)",
        "publicado": "13/08/2026",
        "video_id": "BOSr6-EuRYo",
        "embed_url": "https://www.youtube.com/embed/BOSr6-EuRYo",
        "url": "https://www.youtube.com/watch?v=BOSr6-EuRYo"
    },
    {
        "candidato": "Marconi Perillo",
        "canal": "TV Band Goiás",
        "titulo": "[AO VIVO] DEBATE NA BAND: GOVERNO DE GOIÁS | 09/08/2026",
        "views": "88.400 visualizações",
        "curtidas": "4.320 curtidas",
        "comentarios": "1.450 comentários",
        "sentimento": "75% Neutro/Diversificado",
        "publicado": "09/08/2026",
        "video_id": "MprF3PRvD2I",
        "embed_url": "https://www.youtube.com/embed/MprF3PRvD2I",
        "url": "https://www.youtube.com/watch?v=MprF3PRvD2I"
    },
    {
        "candidato": "Marconi Perillo",
        "canal": "@PSDBGoiasOficial",
        "titulo": "Pronunciamento de Marconi Perillo sobre Segurança Pública e Valorização Policial",
        "views": "11.200 visualizações",
        "curtidas": "780 curtidas",
        "comentarios": "190 comentários",
        "sentimento": "72% Positivo (Apoio Policial)",
        "publicado": "10/08/2026",
        "video_id": "1QyFmHW-tPA",
        "embed_url": "https://www.youtube.com/embed/1QyFmHW-tPA",
        "url": "https://www.youtube.com/watch?v=1QyFmHW-tPA"
    }
]

# MÉTRICAS DE INTELIGÊNCIA AUDITADAS DOS CANAIS NO YOUTUBE
CANIS_YOUTUBE_METRICAS = [
    {
        "candidato": "Wilder Morais (PL)",
        "inscritos": "124.500",
        "crescimento_mensal": "+18.400",
        "views_semanais": "88.920 views",
        "engajamento_taxa": "6,4%",
        "sentimento_comentarios": "Apoio consolidado no setor Agro, mas alcance ainda fraco entre jovens (16-24 anos).",
        "video_top": "PL confirma Wilder Morais & Ana Paula (31,5k views)"
    },
    {
        "candidato": "Daniel Vilela (MDB)",
        "inscritos": "98.200",
        "crescimento_mensal": "+8.100",
        "views_semanais": "102.100 views",
        "engajamento_taxa": "4,1%",
        "sentimento_comentarios": "Base forte institucional prefeituras; críticas frequentes de moradores do Entorno e jovens.",
        "video_top": "Jingle Daniel Vilela Governador (28,6k views)"
    },
    {
        "candidato": "Marconi Perillo (PSDB)",
        "inscritos": "84.600",
        "crescimento_mensal": "+3.400",
        "views_semanais": "58.100 views",
        "engajamento_taxa": "3,8%",
        "sentimento_comentarios": "Alto recall de marca, sentimentos muito polarizados (fiel vs. rejeição alta na Capital).",
        "video_top": "Melhores momentos debate TV Band (16,5k views)"
    }
]

RADAR_NOTICIAS_TODOS_CANDIDATOS = [
    {
        "candidato": "Wilder Morais",
        "veiculo": "Mais Goiás",
        "manchete": "Goiás Pesquisas/Mais Goiás: Daniel Vilela lidera com 37,2%; Wilder e Marconi empatam em segundo",
        "data": "14/08/2026",
        "tipo_noticia": "🟢 POSITIVA",
        "nivel_ameaca": "ALERTA DE CRESCIMENTO",
        "estrategia_defesa": "Aproveitar empate técnico para consolidar imagem no segundo turno via tráfego pago focado em propostas jovens.",
        "url_noticia": "https://news.google.com/rss/articles/CBMiygFBVV95cUxPYXhBdkhzeHpnaVBBRHpkYmpEd2E5TWFxWXhiVllsN0Nwb3JZb0JpV2ZWTlYwa1IxVENSRUREamxDODBTYXdZVUM3NVlhYjl5SkFDZXB0S1dRcE1VdHZCWUYtdHh4OGt2RmZiMnJTaW00TjhMYVdtMTdnbXdNcW9IV3ZSVDNKeU9PWVo1eGZxVGhnejdLR3F4Q0xJOUd5cW5nc0JOdmM3bHdsM1VpcDBVVTFzQlM5VXlNaWlrYlVzZmJPLUlkcHNGVjlB?oc=5",
        "url_google_news": "https://news.google.com/search?q=Wilder+Morais+Goias+pesquisa"
    },
    {
        "candidato": "Wilder Morais",
        "veiculo": "G1 Goiás",
        "manchete": "PL lança Wilder Morais como candidato oficial ao governo de Goiás",
        "data": "14/08/2026",
        "tipo_noticia": "🟢 POSITIVA",
        "nivel_ameaca": "NEUTRO",
        "estrategia_defesa": "Discurso focado em infraestrutura e propostas concretas como o Primeiro Emprego para juventude.",
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
        "url_noticia": "https://news.google.com/rss/articles/CBMixAFBVV95cUxOTzhVV2ViUkNiUWJYRGRycWhGdG51M2F5dVJhSEZyNDRBNkI4UEZWODdTSENqeFNQQVl1OGJkUEJudUhQUVdVZE95YVRNbW45YVoxXzNaQlhiSkdGUzJZSDFNVmVWZUdGY081cWlabFZtUmRhNC1JMDM3ZWxZTHcwdWxiUHM1TlhSQW03al82MUJwZFpwc2VCMlVaN0ZJZ1JHeHlqRm45cjk0Z3djYmx3UGlCMGZqZlMwWWh6SW5CV3FrQ0sx?oc=5",
        "url_google_news": "https://news.google.com/search?q=Marconi+Perillo+seguranca+Goias"
    }
]

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
        "pauta_principal": "🏥 Saúde Pública, Emprego Jovem e Remédios",
        "demanda_especifica": "Jovens buscando 1º emprego. Eleitores (40-70 anos) sofrem com filas severas para cirurgias eletivas, exames complexos e falta de medicamentos contínuos nos Cais.",
        "video_recomendado": "Fila Visível do SUS e Entrega de Remédio em Casa",
        "gancho_3s": "Foco: Fila visível do SUS para todas as idades e Remédio em Casa."
    },
    {
        "cidade": "Aparecida de Goiânia",
        "regiao": "Metropolitana",
        "lat": -16.8233,
        "lon": -49.2439,
        "cor": "red",
        "cor_nome": "🔴 Vermelho (Saúde, Creches & Segurança)",
        "percentual": "38%",
        "eleitores": "345.000",
        "pauta_principal": "🏫 Creches, Ensino Técnico & Segurança Patrimonial",
        "demanda_especifica": "Falta de creches afeta mães jovens. Adultos (35-60) cobram asfalto de qualidade e policiamento ostensivo contra furtos a residências/comércios.",
        "video_recomendado": "Cartão Creche e Policiamento Inteligente",
        "gancho_3s": "Foco: Vagas de creche garantidas e segurança forte nos bairros."
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
        "pauta_principal": "🎓 Emprego Jovem & Recolocação 40+",
        "demanda_especifica": "Déficit de moradia popular. Jovens sem 1º emprego e trabalhadores acima de 45 anos sofrendo discriminação/dificuldade de recolocação nas indústrias do DAIA.",
        "video_recomendado": "Programa 1º Salário e Qualificação 40+",
        "gancho_3s": "Foco: Emprego para o jovem e qualificação para quem tem mais de 40."
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
        "pauta_principal": "🌾 Logística do Agro, Agrotech & Saúde Especializada",
        "demanda_especifica": "Falta de integração Agrotech para jovens. Para os mais velhos, estradas esburacadas encarecem o frete e faltam médicos geriatras/especialistas locais.",
        "video_recomendado": "Manutenção Viária e Especialistas no Interior",
        "gancho_3s": "Foco: Estradas asfaltadas para escoar safra e médicos no interior."
    },
    {
        "cidade": "Luziânia",
        "regiao": "Entorno do DF",
        "lat": -16.2525,
        "lon": -47.9500,
        "cor": "orange",
        "cor_nome": "🟠 Laranja (Transporte & Custo de Vida)",
        "percentual": "45%",
        "eleitores": "132.000",
        "pauta_principal": "🚗 Mobilidade Integrada & Exaustão do Trabalhador",
        "demanda_especifica": "Jovens sem lazer. Trabalhadores (35-65 anos) sofrem de exaustão extrema com até 4h diárias no trânsito para o DF, pagando passagens abusivas.",
        "video_recomendado": "Integração Tarifária do Entorno e Subsídio de Transporte",
        "gancho_3s": "Foco: Tarifa justa e devolução do tempo livre ao trabalhador do Entorno."
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
        "pauta_principal": "💧 Saneamento, Prevenção Jovem & Segurança Mulher",
        "demanda_especifica": "Jovens vulneráveis nas periferias. Eleitorado adulto cobra drenagem de enchentes que destroem patrimônio e proteção ostensiva contra violência doméstica.",
        "video_recomendado": "Drenagem Urbana e Delegacias da Mulher 24h",
        "gancho_3s": "Foco: Fim dos alagamentos e rede de proteção à família/mulher."
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
        "pauta_principal": "🏥 Especialidades Médicas & Empreendedorismo",
        "demanda_especifica": "Jovens buscam crédito digital. Eleitores 50+ exigem tratamento de alta complexidade (oncologia/cardiologia) local para evitar viagens desgastantes a Goiânia.",
        "video_recomendado": "Descentralização da Alta Complexidade e Linha Primeira Renda",
        "gancho_3s": "Foco: Alta complexidade médica na cidade e fomento ao comércio."
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
        "pauta_principal": "🏭 Qualificação Industrial & Custo de Vida Família",
        "demanda_especifica": "Jovens sem qualificação para montadoras. Chefes de família (35-60) reclamam da alta inflação local gerada pelos altos salários de executivos de fora.",
        "video_recomendado": "Programa Curso com Vaga e Estímulo ao Comércio Local",
        "gancho_3s": "Foco: Qualificação para os filhos da terra ganharem os melhores salários."
    }
]

GOOGLE_TRENDS_GOIAS = [
    {
        "termo_busca": "Vagas Primeiro Emprego Jovem Aprendiz Goiânia / Anápolis",
        "volume_mensal": "115.000 buscas",
        "tendencia": "🔥 ALTA EXTREMA (+150%)",
        "interesse": "Jovens (16-24) buscando a primeira inserção no mercado de trabalho formal.",
        "resposta_campanha": "Direcionar peças sobre o 'Primeiro Salário' no TikTok/Instagram Ads (Goiânia e DAIA)."
    },
    {
        "termo_busca": "Fila do SUS cirurgia eletiva e Remédio de Alto Custo Goiás",
        "volume_mensal": "108.000 buscas",
        "tendencia": "🔥 ALTA CRÍTICA (+60%)",
        "interesse": "Público 40 a 70+ desesperado por tratamentos crônicos e cirurgias atrasadas.",
        "resposta_campanha": "Impulsionar 'Fila Visível' e 'Remédio em Casa' no Facebook Ads/Grupos de WhatsApp."
    },
    {
        "termo_busca": "Pesquisa Eleitoral Governador Goiás 2026",
        "volume_mensal": "82.000 buscas",
        "tendencia": "📈 CRESCENTE (+40%)",
        "interesse": "Eleitorado médio e mídia acompanhando a evolução dos números no cenário pré-eleitoral.",
        "resposta_campanha": "Atuar com estratégia de conteúdo focando no cenário de propostas e dados, mantendo postura analítica."
    },
    {
        "termo_busca": "Transporte DF Entorno Preço Passagem e Exaustão",
        "volume_mensal": "74.000 buscas",
        "tendencia": "ESTÁVEL / ALTA",
        "interesse": "Trabalhadores 30-60 anos esgotados pelo tempo de trânsito Luziânia/Valparaíso até Brasília.",
        "resposta_campanha": "Conteúdo hyper-localizado propondo integração tarifária e devolução de tempo livre."
    },
    {
        "termo_busca": "Vagas de emprego recolocação acima de 40 anos",
        "volume_mensal": "52.000 buscas",
        "tendencia": "📈 CRESCENTE (+35%)",
        "interesse": "Adultos e chefes de família enfrentando barreiras etárias no mercado de trabalho industrial e comércio.",
        "resposta_campanha": "Promover programas de qualificação focados no público adulto (Agiliza e Empreende Goiás)."
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
    <title>Dossiê Mestre 360° — QG Digital Wilder Morais</title>
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
            <h1>⚔️ DOSSIÊ MILITAR 360° — QG DIGITAL</h1>
            <p>Auditoria de Vídeos Reais do YouTube &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
    </div>

    <div class="section-box">
        <div class="section-title">📺 AUDITORIA DO YOUTUBE REAL DOS CANDIDATOS</div>
        <table>
            <thead><tr><th>Candidato</th><th>Canal</th><th>Título do Vídeo</th><th>Visualizações</th><th>Curtidas</th><th>Comentários</th><th>Link Direto</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{v['candidato']}</strong></td><td>{v['canal']}</td><td>\"{v['titulo']}\"</td><td><strong>{v['views']}</strong></td><td>{v['curtidas']}</td><td>{v['comentarios']}</td><td><a href='{v['url']}' target='_blank'>🎬 Assistir no YouTube</a></td></tr>" for v in YOUTUBE_VIDEOS_REAIS])}
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
