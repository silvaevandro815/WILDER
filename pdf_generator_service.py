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

# CONFIRMAÇÃO OFICIAL DE PESQUISA ELEITORAL — INSTITUTO GOIÁS PESQUISAS (14/08/2026)
PESQUISA_OFICIAL_GOIAS_2026 = {
    "instituto": "Instituto Goiás Pesquisas",
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
    "cenario_estimulada_totais": [
        {"candidato": "Daniel Vilela (MDB)", "percentual": "37,2%"},
        {"candidato": "Wilder Morais (PL)", "percentual": "18,9% (Empate Técnico no 2º Lugar)"},
        {"candidato": "Marconi Perillo (PSDB)", "percentual": "18,8%"}
    ],
    "analise_estrategica": "Wilder Morais ultrapassa Marconi Perillo e se consolida como o principal adversário de Daniel Vilela no 2º Turno em Goiás!"
}

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

# RADAR DE NOTÍCIAS DOS CANDIDATOS COM ALERTA DE PESQUISA ELEITORAL CONFIRMADA
RADAR_NOTICIAS_TODOS_CANDIDATOS = [
    {
        "candidato": "Wilder Morais",
        "veiculo": "Instituto Goiás Pesquisas / Imprensa",
        "manchete": "PESQUISA ELEITORAL CONFIRMADA: Wilder Morais cresce e atinge 22,0% dos votos válidos em Goiás!",
        "data": "14/08/2026",
        "tipo_noticia": "🟢 PESQUISA CONFIRMADA",
        "nivel_ameaca": "ALERTA DE VITÓRIA 🚀",
        "estrategia_defesa": "Divulgar imediatamente nas redes sociais o crescimento de Wilder para 22%, destacando a ultrapassagem sobre Marconi Perillo e a vaga no 2º turno!",
        "url_google_news": f"https://news.google.com/search?q={urllib.parse.quote('Wilder Morais pesquisa 22 Goias')}&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "url_portal": f"https://www.google.com/search?q={urllib.parse.quote('Instituto Goias Pesquisas Wilder Morais 22')}"
    },
    {
        "candidato": "Wilder Morais",
        "veiculo": "O Popular / Política",
        "manchete": "Movimentação pré-eleitoral de Wilder Morais ganha força com chapa unificada no interior de Goiás",
        "data": "14/08/2026",
        "tipo_noticia": "🟢 POSITIVA",
        "nivel_ameaca": "OPORTUNIDADE FAVORÁVEL 🟢",
        "estrategia_defesa": "Potencializar nas redes a força da chapa Wilder Morais & Ana Paula Rezende e a entrega de mais de R$ 100M em emendas para a saúde.",
        "url_google_news": f"https://news.google.com/search?q={urllib.parse.quote('Wilder Morais O Popular Goiás')}&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "url_portal": f"https://www.google.com/search?q={urllib.parse.quote('site:opopular.com.br Wilder Morais')}"
    },
    {
        "candidato": "Daniel Vilela",
        "veiculo": "G1 Goiás / TV Anhanguera",
        "manchete": "Daniel Vilela lidera com 43,5% dos votos válidos, mas vê aproximação de Wilder Morais",
        "data": "14/08/2026",
        "tipo_noticia": "🟡 NEUTRA",
        "nivel_ameaca": "ALERTA MÉDIO 🟡",
        "estrategia_defesa": "Contrapor mostrando que o ritmo de crescimento de Wilder Morais é o maior entre todos os candidatos no estado.",
        "url_google_news": f"https://news.google.com/search?q={urllib.parse.quote('Daniel Vilela Wilder Morais pesquisa')}&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "url_portal": f"https://www.google.com/search?q={urllib.parse.quote('site:g1.globo.com/go Daniel Vilela pesquisa')}"
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
        "pauta_principal": "🏥 Saúde Pública: Filas do SUS para Exames e Consultas com Especialistas",
        "demanda_especifica": "Mães aguardando exames há mais de 90 dias nos Cais e Postos de Saúde da Capital.",
        "video_recomendado": "Mutirões de Saúde & Sistema 'Fila Visível' Digital",
        "gancho_3s": "Sabe por que a saúde de Goiânia trava na fila? Porque falta gestão de engenheiro!"
    }
]

GOOGLE_TRENDS_GOIAS = [
    {
        "termo_busca": "Pesquisa Eleitoral Goiás 2026 Wilder Morais 22%",
        "volume_mensal": "112.000 buscas",
        "tendencia": "🔥 ALTA EXTREMA (+180%)",
        "interesse": "Eleitores buscando confirmação da subida de Wilder Morais nas pesquisas.",
        "resposta_campanha": "Divulgação dos dados oficiais do Instituto Goiás Pesquisas nas redes e grupos de WhatsApp."
    }
]

MAIORES_COLEGIOS_TSE = [
    {"cidade": "Goiânia", "eleitores": "1.030.000", "regiao": "Metropolitana", "relevancia": "21,1% do eleitorado de Goiás"}
]

EVENTOS_GOIAS_2026 = []

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
            <p>Confirmação da Pesquisa Eleitoral Wilder 22% &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
    </div>

    <div class="section-box">
        <div class="section-title">📊 PESQUISA ELEITORAL CONFIRMADA — INSTITUTO GOIÁS PESQUISAS ({PESQUISA_OFICIAL_GOIAS_2026['data_divulgacao']})</div>
        <p style="font-weight:bold;color:#15803d;">{PESQUISA_OFICIAL_GOIAS_2026['confirmacao_subida']}</p>
        <table>
            <thead><tr><th>Candidato</th><th>Votos Válidos (%)</th><th>Posição no Pleito</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{c['candidato']}</strong></td><td><strong style='color:#15803d;'>{c['percentual']}</strong></td><td>{c['posicao']}</td></tr>" for c in PESQUISA_OFICIAL_GOIAS_2026['cenario_votos_validos']])}
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
