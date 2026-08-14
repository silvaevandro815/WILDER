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

# VÍDEOS REAIS DO YOUTUBE
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

# MAPA TÁTICO DE RECLAMAÇÕES DETALHADO POR CIDADE COM CORES DIFERENCIADAS (RED, ORANGE, GREEN, BLUE, PURPLE)
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

# MONITORAMENTO COMPLETO DE NOTÍCIAS DOS CANDIDATOS (WILDER, DANIEL VILELA, MARCONI PERILLO) COM LINKS DIRETOS
RADAR_NOTICIAS_TODOS_CANDIDATOS = [
    # WILDER MORAIS
    {
        "candidato": "Wilder Morais",
        "veiculo": "O Popular / Política",
        "manchete": "Movimentação pré-eleitoral de Wilder Morais ganha força com chapa unificada no interior de Goiás",
        "data": "14/08/2026",
        "tipo_noticia": "🟢 POSITIVA",
        "nivel_ameaca": "OPORTUNIDADE FAVORÁVEL 🟢",
        "estrategia_defesa": "Potencializar nas redes a força da chapa Wilder Morais & Ana Paula Rezende e a entrega de mais de R$ 100M em emendas para a saúde.",
        "url_noticia": "https://opopular.com.br/politica"
    },
    {
        "candidato": "Wilder Morais",
        "veiculo": "Jornal Opção",
        "manchete": "Aliança entre Wilder Morais e Ana Paula Rezende mobiliza bases históricas de Iris Rezende em Goiânia",
        "data": "13/08/2026",
        "tipo_noticia": "🟢 POSITIVA",
        "nivel_ameaca": "OPORTUNIDADE FAVORÁVEL 🟢",
        "estrategia_defesa": "Conectar o legado de trabalho de Iris Rezende com o perfil técnico e engenheiro de Wilder Morais.",
        "url_noticia": "https://www.jornalopcao.com.br/politica"
    },
    # DANIEL VILELA
    {
        "candidato": "Daniel Vilela",
        "veiculo": "G1 Goiás / TV Anhanguera",
        "manchete": "Daniel Vilela intensifica agendas de vistoria de obras rodoviárias na região Sul de Goiás",
        "data": "14/08/2026",
        "tipo_noticia": "🟡 NEUTRA",
        "nivel_ameaca": "ALERTA MÉDIO 🟡",
        "estrategia_defesa": "Contrapor destacando trechos ainda esburacados no Sudoeste e a proposta do programa 'Ponte & Asfalto Agro' de Wilder.",
        "url_noticia": "https://g1.globo.com/go/goias/noticia"
    },
    {
        "candidato": "Daniel Vilela",
        "veiculo": "Diário da Manhã",
        "manchete": "Oposição aponta demora na entrega de leitos em hospitais do interior e questiona gestão da saúde",
        "data": "12/08/2026",
        "tipo_noticia": "🔴 CRÍTICA",
        "nivel_ameaca": "ALERTA DA OPOSIÇÃO 🔴",
        "estrategia_defesa": "Reforçar a crítica à saúde atual e divulgar o programa 'Saúde Fila Visível' de Wilder Morais.",
        "url_noticia": "https://dm.com.br/politica"
    },
    # MARCONI PERILLO
    {
        "candidato": "Marconi Perillo",
        "veiculo": "O Popular / Coluna Giro",
        "manchete": "Marconi Perillo busca recomposição de bases partidárias no Entorno do DF e região Leste",
        "data": "14/08/2026",
        "tipo_noticia": "🟡 NEUTRA",
        "nivel_ameaca": "ALERTA ESTRATÉGICO 🟡",
        "estrategia_defesa": "Destacar a renovação política representada por Wilder e o plano de integração do transporte do Entorno.",
        "url_noticia": "https://opopular.com.br/colunas/giro"
    },
    {
        "candidato": "Marconi Perillo",
        "veiculo": "Jornal Opção",
        "manchete": "Imprensa relembra desdobramentos de antigas gestões e debates sobre contratos de energia em Goiás",
        "data": "11/08/2026",
        "tipo_noticia": "🔴 CRÍTICA",
        "nivel_ameaca": "DESGASTE DE IMAGEM 🔴",
        "estrategia_defesa": "Manter neutralidade e focar na divulgação das propostas do futuro 'Goiás Para Quem Faz'.",
        "url_noticia": "https://www.jornalopcao.com.br"
    }
]

# DADOS DO GOOGLE TRENDS GOIÁS
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
    }
]

MAIORES_COLEGIOS_TSE = [
    {"cidade": "Goiânia", "eleitores": "1.030.000", "regiao": "Metropolitana", "relevancia": "21,1% do eleitorado de Goiás"},
    {"cidade": "Aparecida de Goiânia", "eleitores": "345.000", "regiao": "Metropolitana", "relevancia": "7,1% do eleitorado de Goiás"}
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
            <p>Notícias de Todos os Candidatos & Mapa Colorido por Região &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
    </div>

    <div class="section-box">
        <div class="section-title">📰 MONITORAMENTO DE NOTÍCIAS DOS CANDIDATOS (WILDER, DANIEL VILELA, MARCONI)</div>
        <table>
            <thead><tr><th>Candidato</th><th>Veículo & Data</th><th>Tipo</th><th>Manchete Mapeada</th><th>Link Direto da Matéria</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{n['candidato']}</strong></td><td>{n['veiculo']}<br><span style='font-size:11px;color:#64748b;'>{n['data']}</span></td><td><strong>{n['tipo_noticia']}</strong></td><td>\"{n['manchete']}\"</td><td><a href='{n['url_noticia']}' target='_blank'>📰 Ler Matéria no Portal</a></td></tr>" for n in RADAR_NOTICIAS_TODOS_CANDIDATOS])}
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
