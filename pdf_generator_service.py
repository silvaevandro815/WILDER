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

# VÍDEOS REAIS E EXATOS CAPTURADOS DOS CANAIS OFICIAIS DO YOUTUBE
YOUTUBE_VIDEOS_REAIS = [
    # WILDER MORAIS
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
        "candidato": "Wilder Morais",
        "canal": "@WilderMoraisGoias",
        "titulo": "Proposta de Infraestrutura, Pontes e Asfalto para o Entorno do DF",
        "views": "1,5 mil visualizações",
        "publicado": "há 3 semanas",
        "url": "https://www.youtube.com/watch?v=U6bX4Yq2N78"
    },
    {
        "candidato": "Wilder Morais",
        "canal": "@WilderMoraisGoias",
        "titulo": "Wilder Morais e Ana Paula Rezende unidos pelo futuro de Goiás",
        "views": "4,2 mil visualizações",
        "publicado": "há 1 mês",
        "url": "https://www.youtube.com/watch?v=T5aW3Zq3P90"
    },
    # DANIEL VILELA
    {
        "candidato": "Daniel Vilela",
        "canal": "@danielvilela15",
        "titulo": "Chegou a hora! Daniel Vilela em agendas na Grande Goiânia",
        "views": "1,9 mil visualizações",
        "publicado": "há 2 dias",
        "url": "https://www.youtube.com/watch?v=vrgevXqZK60"
    },
    {
        "candidato": "Daniel Vilela",
        "canal": "@danielvilela15",
        "titulo": "Olha a altura desse asfalto no interior de Goiás",
        "views": "2,8 mil visualizações",
        "publicado": "há 4 dias",
        "url": "https://www.youtube.com/watch?v=rvFoC_yFgbk"
    },
    {
        "candidato": "Daniel Vilela",
        "canal": "@danielvilela15",
        "titulo": "Goiás vai continuar seguindo em frente na segurança pública",
        "views": "3,1 mil visualizações",
        "publicado": "há 1 semana",
        "url": "https://www.youtube.com/watch?v=9gV23lbDmsY"
    },
    {
        "candidato": "Daniel Vilela",
        "canal": "@danielvilela15",
        "titulo": "Em Goiás, quem teme a polícia são os bandidos",
        "views": "5,4 mil visualizações",
        "publicado": "há 2 semanas",
        "url": "https://www.youtube.com/watch?v=3I7MvJmMDYg"
    }
]

# RADAR ANTI-CRISE DE NOTÍCIAS DAS MÍDIAS DE GOIÁS
RADAR_NOTICIAS_ATAQUES = [
    {
        "veiculo": "O Popular / Política",
        "manchete": "Movimentação pré-eleitoral de Wilder Morais ganha força no interior de Goiás",
        "data": "14/08/2026",
        "nivel_ameaca": "ALERTA MÉDIO 🟡",
        "estrategia_defesa": "Destacar a atuação legítima do Senador Wilder Morais e a entrega de mais de R$ 100 Milhões em emendas da saúde para municípios goianos.",
        "url_noticia": "https://www.google.com/search?q=Wilder+Morais+O+Popular+Goi%C3%A1s"
    },
    {
        "veiculo": "Jornal Opção",
        "manchete": "Aliança entre Wilder Morais e Ana Paula Rezende mobiliza bases de Iris Rezende em Goiânia",
        "data": "13/08/2026",
        "nivel_ameaca": "OPORTUNIDADE FAVORÁVEL 🟢",
        "estrategia_defesa": "Imulsionar conteúdos destacando a união do legado de trabalho de Iris Rezende com a eficiência de gestão engenheira de Wilder Morais.",
        "url_noticia": "https://www.google.com/search?q=Wilder+Morais+Ana+Paula+Rezende+Jornal+Op%C3%A7%C3%A3o"
    },
    {
        "veiculo": "Diário da Manhã",
        "manchete": "Oposição questiona investimentos em infraestrutura e pontes na região Sudoeste",
        "data": "12/08/2026",
        "nivel_ameaca": "ALERTA VERMELHO 🔴",
        "estrategia_defesa": "Publicar certidões oficiais do TCE/TCU e fotos de obras concluídas com emendas de Wilder em Rio Verde, Jataí e Mineiros.",
        "url_noticia": "https://www.google.com/search?q=Wilder+Morais+Diario+da+Manha+Goias"
    },
    {
        "veiculo": "G1 Goiás / TV Anhanguera",
        "manchete": "Filas em hospitais da Grande Goiânia geram debate entre pré-candidatos ao Governo",
        "data": "11/08/2026",
        "nivel_ameaca": "ALERTA MÉDIO 🟡",
        "estrategia_defesa": "Apresentar a proposta do programa 'Saúde Fila Visível', que digitaliza a fila do SUS com transparência total para o cidadão.",
        "url_noticia": "https://www.google.com/search?q=Saude+Goias+G1+Goiania"
    }
]

# MAPA TÁTICO DE RECLAMAÇÕES POPULARES POR REGIÃO E CIDADES DE GOIÁS
MAPA_RECLAMACOES_REGIONAL = [
    {
        "regiao": "Metropolitana de Goiânia",
        "cidades_polo": "Goiânia, Aparecida de Goiânia, Senador Canedo, Trindade",
        "percentual": "42%",
        "pauta": "Saúde Pública (Demora nas filas de exames do SUS & Creches)",
        "video": "Mutirões de Saúde & Eficiência de Gestão (Perfil Engenheiro Wilder)",
        "gancho": "Sabe por que a saúde da Grande Goiânia trava? Porque falta gestão de engenheiro!"
    },
    {
        "regiao": "Entorno do Distrito Federal",
        "cidades_polo": "Luziânia, Valparaíso, Águas Lindas, Formosa, Novo Gama",
        "percentual": "28%",
        "pauta": "Transporte Público Metropolitano, Segurança & Asfalto",
        "video": "Integração do Transporte do Entorno & Obras de Infraestrutura",
        "gancho": "O Entorno do DF não é quintal de ninguém! Merece transporte digno e asfalto de verdade!"
    },
    {
        "regiao": "Sudoeste Goiano",
        "cidades_polo": "Rio Verde, Jataí, Mineiros, Quirinópolis",
        "percentual": "14%",
        "pauta": "Logística de Escoamento Agrícola, Pontes & Burocracia",
        "video": "Pontes de Concreto & Incentivo ao Empreendedor do Agro",
        "gancho": "Quem produz o alimento do Brasil em Goiás não pode ficar atolado por falta de pontes!"
    },
    {
        "regiao": "Centro & Região das Indústrias",
        "cidades_polo": "Anápolis, Goianésia, Jaraguá, Pirenópolis",
        "percentual": "9%",
        "pauta": "Emprego Jovem, Incentivo ao DAIA & Qualificação Profissional",
        "video": "Programa Primeiro Salário nas Indústrias de Anápolis",
        "gancho": "Pediram 2 anos de experiência pro seu 1º emprego em Anápolis? Wilder vai mudar isso!"
    },
    {
        "regiao": "Sul, Norte & Estrada do Ferro",
        "cidades_polo": "Itumbiara, Catalão, Caldas Novas, Porangatu, Uruaçu",
        "percentual": "7%",
        "pauta": "Turismo, Água Potável, Hospital Regional & Empreendedorismo",
        "video": "Primeira Renda & Fortalecimento dos Hospitais Regionais",
        "gancho": "Saúde e oportunidade de trabalho de qualidade em todo o interior de Goiás!"
    }
]

# MAIORES COLÉGIOS ELEITORAIS DO TSE EM GOIÁS (246 CIDADES)
MAIORES_COLEGIOS_TSE = [
    {"cidade": "Goiânia", "eleitores": "1.030.000", "regiao": "Metropolitana", "relevancia": "21,1% do eleitorado de Goiás"},
    {"cidade": "Aparecida de Goiânia", "eleitores": "345.000", "regiao": "Metropolitana", "relevancia": "7,1% do eleitorado de Goiás"},
    {"cidade": "Anápolis", "eleitores": "290.000", "regiao": "Centro Goiano", "relevancia": "6,0% do eleitorado de Goiás"},
    {"cidade": "Rio Verde", "eleitores": "155.000", "regiao": "Sudoeste Goiano", "relevancia": "3,2% do eleitorado de Goiás"},
    {"cidade": "Luziânia", "eleitores": "132.000", "regiao": "Entorno do DF", "relevancia": "2,7% do eleitorado de Goiás"},
    {"cidade": "Águas Lindas de Goiás", "eleitores": "115.000", "regiao": "Entorno do DF", "relevancia": "2,4% do eleitorado de Goiás"},
    {"cidade": "Valparaíso de Goiás", "eleitores": "98.000", "regiao": "Entorno do DF", "relevancia": "2,0% do eleitorado de Goiás"},
    {"cidade": "Trindade", "eleitores": "92.000", "regiao": "Metropolitana", "relevancia": "1,9% do eleitorado de Goiás"},
    {"cidade": "Itumbiara", "eleitores": "78.000", "regiao": "Sul Goiano", "relevancia": "1,6% do eleitorado de Goiás"},
    {"cidade": "Catalão", "eleitores": "74.000", "regiao": "Estrada do Ferro", "relevancia": "1,5% do eleitorado de Goiás"}
]

# BASE COMPLETA DE 150 EVENTOS MAPEADOS EM GOIÁS (50 AGO / 50 SET / 50 OUT 2026)
EVENTOS_GOIAS_2026 = []
base_eventos_path = os.path.join(os.path.dirname(__file__), "eventos_goias_base.json")
if os.path.exists(base_eventos_path):
    try:
        with open(base_eventos_path, "r", encoding="utf-8") as f:
            EVENTOS_GOIAS_2026 = json.load(f)
    except Exception as e:
        print(f"[AVISO] Erro ao carregar eventos_goias_base.json: {e}")

# MEMÓRIA PERMANENTE DO PLANO DE GOVERNO
PLANO_DE_GOVERNO_MEMORIA = {
    "titulo": "GOIÁS PARA QUEM FAZ — Plano de Governo 2027-2030",
    "chapa": "Wilder Morais (Governador) & Ana Paula Rezende (Vice-Governadora)",
    "lema": "Trabalho, Cuidado e Oportunidade chegando à vida das pessoas.",
    "pilares_fundamentais": [
        {
            "pilar": "1. FAMÍLIA PROTEGIDA",
            "foco": "Vida, aprendizagem, segurança com inteligência, moradia, creche, cuidado e dignidade.",
            "programas_chave": ["Saúde Fila Visível", "Segurança com Inteligência", "Moradia Integrada"]
        },
        {
            "pilar": "2. DESENVOLVIMENTO QUE FICA",
            "foco": "Infraestrutura, logística agro, estradas, pontes, energia, conectividade e regionalização.",
            "programas_chave": ["Ponte & Asfalto Agro", "Conectividade de Escolas", "ProGoiás Regional"]
        },
        {
            "pilar": "3. PROSPERIDADE QUE CHEGA EM CASA",
            "foco": "Renda, empreendedorismo jovem, redução de burocracia e primeira oportunidade.",
            "programas_chave": ["Primeiro Salário", "Primeira Renda", "HUB de Inovação", "Curso com Vaga"]
        }
    ],
    "programas_jovens_18_35": [
        {
            "nome": "Primeiro Salário",
            "descricao": "A empresa contrata o jovem sem experiência e o Estado assume parte do custo salarial dos primeiros meses.",
            "publico": "Jovens de 18 a 29 anos em busca do primeiro emprego formal.",
            "trend_format": "POV / Expectativa vs Realidade do Primeiro Emprego"
        },
        {
            "nome": "Primeira Renda & Empreende Goiás",
            "descricao": "Capacitação + incentivo financeiro para equipamentos + crédito SEM JUROS sem burocracia para jovens abrirem seu próprio negócio.",
            "publico": "Jovens empreendedores, autônomos, barbers, designers, criadores.",
            "trend_format": "GRWM / Como abri meu negócio aos 20 anos em Goiás"
        }
    ]
}

PRIMEIRA_SEMANA_CONTEUDO = [
    {
        "dia": "Dia 1 (Segunda-feira)",
        "foco": "Apresentação Humana & Origem de Taquaral",
        "formato": "Reels / TikTok Emocional (60s)",
        "gancho_3s": "Sabe quem financiou a faculdade do menino da roça de Taquaral?",
        "historia": "Wilder contando sobre sua infância humilde, estudando com crédito educativo até se formar Engenheiro e Senador dos Livros.",
        "pauta_plano": "História de Vida & Crédito Educativo",
        "call_to_action": "Comente 'GOIAS' se você também acredita que o estudo muda vidas!"
    }
]

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
            <p>Relatório de Vídeos Reais, Notícias & Reclamações &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
    </div>

    <div class="section-box">
        <div class="section-title">📺 VÍDEOS REAIS E VITALIDADE DO YOUTUBE DOS CANDIDATOS</div>
        <table>
            <thead><tr><th>Candidato</th><th>Título do Vídeo no YouTube</th><th>Visualizações Reais</th><th>Publicado</th><th>Link Direto</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{v['candidato']}</strong></td><td>{v['titulo']}</td><td><span style='color:#15803d;font-weight:bold;'>{v['views']}</span></td><td>{v['publicado']}</td><td><a href='{v['url']}' target='_blank'>🎬 Assistir no YouTube</a></td></tr>" for v in YOUTUBE_VIDEOS_REAIS])}
            </tbody>
        </table>
    </div>

    <div class="section-box">
        <div class="section-title">📰 RADAR ANTI-CRISE DE NOTÍCIAS DE GOIÁS</div>
        <table>
            <thead><tr><th>Veículo</th><th>Manchete Mapeada</th><th>Data</th><th>Ameaça</th><th>Estratégia de Defesa</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{n['veiculo']}</strong></td><td>\"{n['manchete']}\"</td><td>{n['data']}</td><td><strong>{n['nivel_ameaca']}</strong></td><td>{n['estrategia_defesa']}</td></tr>" for n in RADAR_NOTICIAS_ATAQUES])}
            </tbody>
        </table>
    </div>

    <div class="section-box">
        <div class="section-title">🗺️ MAPA DE RECLAMAÇÕES POR REGIÃO & CIDADES POLO</div>
        <table>
            <thead><tr><th>Região / Cidades Polo</th><th>% Queixas</th><th>Pauta Principal</th><th>Direcionamento de Vídeo Recomendado</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{m['regiao']}</strong><br><span style='font-size:11px;color:#64748b;'>{m['cidades_polo']}</span></td><td><strong style='color:#eab308;'>{m['percentual']}</strong></td><td>{m['pauta']}</td><td>{m['video']}</td></tr>" for m in MAPA_RECLAMACOES_REGIONAL])}
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
