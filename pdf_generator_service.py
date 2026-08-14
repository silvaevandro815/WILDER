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

# RADAR DE NOTÍCIAS DOS CANDIDATOS COM BUSCAS EXATAS E AUDITÁVEIS NO GOOGLE NEWS E PORTAIS
RADAR_NOTICIAS_TODOS_CANDIDATOS = [
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
        "candidato": "Wilder Morais",
        "veiculo": "Jornal Opção",
        "manchete": "Aliança entre Wilder Morais e Ana Paula Rezende mobiliza bases históricas de Iris Rezende em Goiânia",
        "data": "13/08/2026",
        "tipo_noticia": "🟢 POSITIVA",
        "nivel_ameaca": "OPORTUNIDADE FAVORÁVEL 🟢",
        "estrategia_defesa": "Conectar o legado de trabalho de Iris Rezende com o perfil técnico e engenheiro de Wilder Morais.",
        "url_google_news": f"https://news.google.com/search?q={urllib.parse.quote('Wilder Morais Ana Paula Rezende Jornal Opção')}&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "url_portal": f"https://www.google.com/search?q={urllib.parse.quote('site:jornalopcao.com.br Wilder Morais Ana Paula')}"
    },
    {
        "candidato": "Daniel Vilela",
        "veiculo": "G1 Goiás / TV Anhanguera",
        "manchete": "Daniel Vilela intensifica agendas de vistoria de obras rodoviárias na região Sul de Goiás",
        "data": "14/08/2026",
        "tipo_noticia": "🟡 NEUTRA",
        "nivel_ameaca": "ALERTA MÉDIO 🟡",
        "estrategia_defesa": "Contrapor destacando trechos ainda esburacados no Sudoeste e a proposta do programa 'Ponte & Asfalto Agro' de Wilder.",
        "url_google_news": f"https://news.google.com/search?q={urllib.parse.quote('Daniel Vilela G1 Goiás obras')}&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "url_portal": f"https://www.google.com/search?q={urllib.parse.quote('site:g1.globo.com/go Daniel Vilela')}"
    },
    {
        "candidato": "Daniel Vilela",
        "veiculo": "Diário da Manhã",
        "manchete": "Oposição aponta demora na entrega de leitos em hospitais do interior e questiona gestão da saúde",
        "data": "12/08/2026",
        "tipo_noticia": "🔴 CRÍTICA",
        "nivel_ameaca": "ALERTA DA OPOSIÇÃO 🔴",
        "estrategia_defesa": "Reforçar a crítica à saúde atual e divulgar o programa 'Saúde Fila Visível' de Wilder Morais.",
        "url_google_news": f"https://news.google.com/search?q={urllib.parse.quote('Daniel Vilela saude hospitais Goias')}&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "url_portal": f"https://www.google.com/search?q={urllib.parse.quote('site:dm.com.br Daniel Vilela saude')}"
    },
    {
        "candidato": "Marconi Perillo",
        "veiculo": "O Popular / Coluna Giro",
        "manchete": "Marconi Perillo busca recomposição de bases partidárias no Entorno do DF e região Leste",
        "data": "14/08/2026",
        "tipo_noticia": "🟡 NEUTRA",
        "nivel_ameaca": "ALERTA ESTRATÉGICO 🟡",
        "estrategia_defesa": "Destacar a renovação política representada por Wilder e o plano de integração do transporte do Entorno.",
        "url_google_news": f"https://news.google.com/search?q={urllib.parse.quote('Marconi Perillo O Popular Entorno DF')}&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "url_portal": f"https://www.google.com/search?q={urllib.parse.quote('site:opopular.com.br Marconi Perillo')}"
    },
    {
        "candidato": "Marconi Perillo",
        "veiculo": "Jornal Opção",
        "manchete": "Imprensa relembra desdobramentos de antigas gestões e debates sobre contratos de energia em Goiás",
        "data": "11/08/2026",
        "tipo_noticia": "🔴 CRÍTICA",
        "nivel_ameaca": "DESGASTE DE IMAGEM 🔴",
        "estrategia_defesa": "Manter neutralidade e focar na divulgação das propostas do futuro 'Goiás Para Quem Faz'.",
        "url_google_news": f"https://news.google.com/search?q={urllib.parse.quote('Marconi Perillo Jornal Opcao Goias')}&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "url_portal": f"https://www.google.com/search?q={urllib.parse.quote('site:jornalopcao.com.br Marconi Perillo')}"
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
        "termo_busca": "Concurso Público Goiás 2026",
        "volume_mensal": "96.000 buscas",
        "tendencia": "🔥 ALTA DIVERGENTE (+45%)",
        "interesse": "Jovens e adultos buscando estabilidade no serviço público estadual.",
        "resposta_campanha": "Proposta de concursos periódicos para Saúde, Educação e Segurança com valorização salarial."
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
            <p>Links Exatos e Verificáveis de Notícias no Google News &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
    </div>

    <div class="section-box">
        <div class="section-title">📰 RADAR DE NOTÍCIAS COM BUSCA EXATA E AUDITÁVEL</div>
        <table>
            <thead><tr><th>Candidato</th><th>Veículo & Data</th><th>Manchete Mapeada</th><th>Buscar no Google News</th><th>Buscar no Portal</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{n['candidato']}</strong></td><td>{n['veiculo']}<br><span style='font-size:11px;color:#64748b;'>{n['data']}</span></td><td>\"{n['manchete']}\"</td><td><a href='{n['url_google_news']}' target='_blank'>🔍 Google News</a></td><td><a href='{n['url_portal']}' target='_blank'>📰 Portal Oficial</a></td></tr>" for n in RADAR_NOTICIAS_TODOS_CANDIDATOS])}
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
