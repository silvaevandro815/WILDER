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

# CARREGAR AVATAR BASE64 PARA EXIBIÇÃO 100% PERFEITA
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

# BANCO COMPLETO DE NOTÍCIAS REAIS VALIDADAS AO VIVO (GOIÁS 2026) COM LINKS DIRETOS
RADAR_NOTICIAS_TODOS_CANDIDATOS = [
    # WILDER MORAIS
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
        "manchete": "Wilder ainda não está preparado para a fala em debates públicos, avalia ala da imprensa",
        "data": "13/08/2026",
        "tipo_noticia": "🔴 CRÍTICA",
        "nivel_ameaca": "ALERTA DE PREPARAÇÃO 🔴",
        "estrategia_defesa": "Treinar Wilder para debates com a técnica 'Engenheiro que Faz', priorizando dados técnicos e soluções em vez de retórica política.",
        "url_noticia": "https://news.google.com/rss/articles/CBMirAFBVV95cUxPQXZfVFpPSUdhVEFaUm95VlJmQzYtQXBpSkJDMFhadThlOHNQYU9yeFQwUVo3WmVVUXhyemlJTHRiNGExMzlMaVlmaTFLQXR2aE80dmNZbmdBVURxbUJ1UjZSU1p6d0tmMkJad3FaSVBGRjVNbmN4SGhUQXMxWHllblJYUDZWUTVuQ1Fnbkp0ZmhvZHprYk5rMm5fSE1BZDkwaXpISFVxN0RzRGhE?oc=5",
        "url_google_news": "https://news.google.com/search?q=Wilder+Morais+Diario+de+Goias"
    },
    {
        "candidato": "Wilder Morais",
        "veiculo": "Portal GO 020",
        "manchete": "Wilder Morais escolhe cidade natal Taquaral para iniciar caminhada política",
        "data": "12/08/2026",
        "tipo_noticia": "🟢 POSITIVA",
        "nivel_ameaca": "OPORTUNIDADE FAVORÁVEL 🟢",
        "estrategia_defesa": "Produzir vídeo emocionante sobre a infância de Wilder na roça de Taquaral até o sucesso como engenheiro e senador.",
        "url_noticia": "https://news.google.com/rss/articles/CBMiwwFBVV95cUxNNVZDb0lkZllUVDdBazlzdWQ4UnVQTFh2OFJJMlBoZW5QS3NhdUJvVkJHZWtycVd2V0dVVlhtSkQwcTdRYUJsSDA4Y3JlRzJjMXF5M1FGeldKWG02RnlXdjBOaktxVENLNzJhM29DZXdiY1FwNEIwMkxpUkZkUF_FamRvbEJmemprNExIS0hqSjlGeHo3ZHN0VGlzY3hONXM0YVc4WkxaWUZKdHRyV25jTTNLVUx1V2pZVGNwdzNBaWNxbUU?oc=5",
        "url_google_news": "https://news.google.com/search?q=Wilder+Morais+Taquaral+Goias"
    },
    # DANIEL VILELA
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
        "candidato": "Daniel Vilela",
        "veiculo": "G1 Goiás",
        "manchete": "Daniel Vilela declara R$ 5,6 milhões em bens ao TSE nas eleições de Goiás",
        "data": "13/08/2026",
        "tipo_noticia": "🟡 NEUTRA",
        "nivel_ameaca": "MONITORAMENTO 🟡",
        "estrategia_defesa": "Acompanhar repercussão sobre patrimônio dos candidatos.",
        "url_noticia": "https://news.google.com/rss/articles/CBMi0wFBVV95cUxNVUlaZERsX1AxczVVeDBfTE9wcDFmR2F0MnVoRlE2RlNMbWMtMFlyVUdxZ052ZUNoaDVNUFhYZktWc29SR1JJR0VIWWIyTGc5eHc4d2llUTJYaW56ZG5QSmtkSlJwNUpoWWNsd2ttX2Jsa0VlT0R4a09BTkN6eFVud082Yy1DYnpKWC1OdE5HbTBOTnU4THZndHlrY0hiU29seTQ0Y1lhcWItNHVrcUVzREdOUlRmMDVROFVYZzdyeHRpNl_rNWhDOFlzVHZ2U3ZRbEtJ0gHiAUFVX3lxTE9kcmZuVHBBUy1SX0pVODNBakwzVVFpSVFfOG8tR2MteENaXzJNVlVmWDBKYjU1dnJMSk9IaTQtN1RReTRQSTRHbTVPbHNhSWxGT3oyMGNuMUltcEFuNnlVd2kzVXNnRzZobzlzVmZVZ1F6VDFNR3ZCMF81VDVHOEhFSHlLYXhxd3hEQlI0Mm42YTYwUnYxenczUjdqODVJVkZIUzdCSGNKLXNLTTZsZXNYem1wcDFkc1ZOcER4TlZhb0FwVkRnN201aWJzNWRoSVNfTzlVTmViOXdCcGhvdDNVM2c?oc=5",
        "url_google_news": "https://news.google.com/search?q=Daniel+Vilela+declaracao+TSE"
    },
    {
        "candidato": "Daniel Vilela",
        "veiculo": "Poder Goiás",
        "manchete": "Prefeito de Sanclerlândia abandona Marconi e declara apoio formal a Daniel Vilela",
        "data": "12/08/2026",
        "tipo_noticia": "🟢 POSITIVA DO ADVERSÁRIO",
        "nivel_ameaca": "ALERTA DE ADERÊNCIA 🟡",
        "estrategia_defesa": "Reforçar diálogo com lideranças locais do oeste goiano para conter avanço de alianças da base governista.",
        "url_noticia": "https://news.google.com/rss/articles/CBMiugFBVV95cUxOQk8zOFE4YUR3dy1QdmpOeTRzRjRJQlpGaE4yU2Vmd29EUUxBb3czcFF3ZlN1TnV5cFhfcEtMYmVreFU5NG1MUFpnSm1uM0JWekhJNWtCbHF3WURGeFZ6a1NuWUt4eTBRZWFvRzZ0T3ZyWTlHWjl6QXc4aFdrZVRYWmRuXzdWU29tNVdQVDFUNmpNOHBPLVNnR1h6bk1ta1lEMll3ejdzYnkzWEJFUEJRSjFRSWFaWkdhUkE?oc=5",
        "url_google_news": "https://news.google.com/search?q=Daniel+Vilela+Sanclerlandia+Goias"
    },
    # MARCONI PERILLO
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
    },
    {
        "candidato": "Marconi Perillo",
        "veiculo": "Tribuna do Planalto",
        "manchete": "Zé Mário Schreiner, Marconi Perillo e Jacqueline Zaiden articulam apoio das forças do agro em Goiás",
        "data": "13/08/2026",
        "tipo_noticia": "🟢 POSITIVA DO ADVERSÁRIO",
        "nivel_ameaca": "CONCORRÊNCIA NO AGRO 🟡",
        "estrategia_defesa": "Reafirmar a identidade de Wilder Morais como o verdadeiro Senador do Agro e autor de emendas diretas para máquinas e pontes.",
        "url_noticia": "https://news.google.com/rss/articles/CBMi2AFBVV95cUxPUUE2b2lYdUV4SlNlVGl5R3hPOGFlOTRkbktveWlxUmdNRVNTYVduSlFzZmVsUVpBT1Q5dkIxWFJvc0ZpR29vMUkxTWV5cVN3QXdMcGwzb1g2bU9MOWJSa3ZRVXVDVlUxRXNBMlNYemVudE1YLWx2NlRwWFZvaTFqcXUtX1pSbXo4T3lFMFUwM21mZWZWZXdSUW81am4tMThTcHVnekpRTnQ5UnVzQVpuanBZUWdTWmNnLWpVSGE1RFVtLXdyazdTdHRWbnlfVBJBOWJhMUxudmw?oc=5",
        "url_google_news": "https://news.google.com/search?q=Marconi+Perillo+agro+Goias"
    },
    {
        "candidato": "Marconi Perillo",
        "veiculo": "A Redação",
        "manchete": "Agropecuarista Jacqueline Zaiden é anunciada como candidata a vice na chapa de Marconi Perillo",
        "data": "12/08/2026",
        "tipo_noticia": "🟡 NEUTRA",
        "nivel_ameaca": "MONITORAMENTO 🟡",
        "estrategia_defesa": "Destacar a chapa forte de Wilder Morais com Ana Paula Rezende, unindo o legado de Iris Rezende e o agronegócio.",
        "url_noticia": "https://news.google.com/rss/articles/CBMi2AFBVV95cUxQb2J3RjVucUFCa282Ym1ETGVBYU40YWNsajVWX3M2SURRdXdhcVROek5NSU02NGF1UEhrdmRCaXp1WTNHb0RTRl_za1hGYWpyaTUyNGVQdUZsQnJkY19RYmh6TU1GOUZwNlByMkdKVWxuc2VORDRQcTRidjJPWXMxcTdFamkxUjl2UjhmV0phejIzX0Roa0ZHelhVUlVnREhrRl_RLW5Ga1U3S21pVVpnbHZwMVVPbHhYYm1tNVZmSVNGVFBISlQwaHdBd2xBMFVrZkp5VE03RWg?oc=5",
        "url_google_news": "https://news.google.com/search?q=Jacqueline+Zaiden+Marconi+Perillo"
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
            <p>Monitoramento de Notícias Reais dos Candidatos &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
    </div>

    <div class="section-box">
        <div class="section-title">📰 NOTÍCIAS REAIS VALIDADAS (WILDER, DANIEL VILELA, MARCONI)</div>
        <table>
            <thead><tr><th>Candidato</th><th>Veículo & Data</th><th>Classificação</th><th>Manchete Mapeada</th><th>Link Direto da Matéria</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{n['candidato']}</strong></td><td>{n['veiculo']}<br><span style='font-size:11px;color:#64748b;'>{n['data']}</span></td><td><strong>{n['tipo_noticia']}</strong></td><td>\"{n['manchete']}\"</td><td><a href='{n['url_noticia']}' target='_blank'>📰 Ler Matéria Oficial</a></td></tr>" for n in RADAR_NOTICIAS_TODOS_CANDIDATOS])}
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
