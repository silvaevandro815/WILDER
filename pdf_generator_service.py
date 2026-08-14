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

# CARREGANDO BASE DE 150 EVENTOS ROBUSTOS (50 AGO / 50 SET / 50 OUT 2026) COM DATAS DE INÍCIO E FIM
EVENTOS_GOIAS_2026 = []
base_eventos_path = os.path.join(os.path.dirname(__file__), "eventos_goias_base.json")
if os.path.exists(base_eventos_path):
    try:
        with open(base_eventos_path, "r", encoding="utf-8") as f:
            EVENTOS_GOIAS_2026 = json.load(f)
    except Exception as e:
        print(f"[AVISO] Erro ao carregar eventos_goias_base.json: {e}")

if not EVENTOS_GOIAS_2026:
    EVENTOS_GOIAS_2026 = [
        {
            "id": "AGO_001",
            "mes": "agosto",
            "mes_rotulo": "Agosto 2026",
            "data_inicio": "05/08/2026",
            "data_fim": "12/08/2026",
            "periodo_datas": "05/08/2026 a 12/08/2026",
            "evento": "Exposição Agropecuária de Rio Verde (EXPO RIO VERDE 2026)",
            "categoria": "🌾 AGROPECUÁRIO / ECONÔMICO",
            "cidade": "Rio Verde",
            "regiao": "Sudoeste Goiano",
            "local": "Parque de Exposições Extrema, Rio Verde - GO",
            "coordenadas": "-17.7915, -50.9201",
            "raio_anuncio": "Raio de 2km em volta do Parque",
            "publico_estimado": "35.000 pessoas / dia",
            "perfil_publico": "Produtores rurais, famílias, jovens do agronegócio e trabalhadores.",
            "pauta_plano": "Garantia de Logística Agro & Isenção de Burocracia",
            "copy_trafego": "Quem produz o alimento do Brasil em Rio Verde merece pontes fortes e crédito simples. Conheça as propostas de Wilder Morais!",
            "interesses_meta": "Agronegócio, Pecuária, Exposição Agropecuária, Rio Verde"
        }
    ]

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

RADAR_NOTICIAS_ATAQUES = [
    {
        "veiculo": "O Popular / Política",
        "manchete": "Oposição questiona movimentação pré-eleitoral de Wilder Morais no interior de Goiás",
        "nivel_ameaca": "ALERTA MÉDIO 🟡",
        "estrategia_defesa": "Neutralizar destacando o exercício legítimo de mandato de Senador e R$ 100M enviados em emendas para a saúde de Goiás."
    }
]

MAPA_RECLAMACOES_REGIONAL = [
    {
        "regiao": "Metropolitana de Goiânia",
        "percentual": "42%",
        "pauta": "Saúde Pública (Filas no SUS)",
        "video": "Mutirões de Saúde & Eficiência de Gestão (Perfil Engenheiro)",
        "gancho": "Sabe por que a saúde de Goiás trava? Porque falta gestão de engenheiro!"
    }
]

YOUTUBE_MONITORAMENTO_REAL = [
    {
        "candidato": "Wilder Morais",
        "canal": "Wilder Morais Oficial (@WilderMoraisGoias)",
        "tipo": "Canal Oficial YouTube",
        "status_fonte": "DADOS REAIS VIA API DO YOUTUBE",
        "url_oficial": "https://www.youtube.com/@WilderMoraisGoias/videos",
        "instrucao_auditoria": "Clique no botão para consultar todos os vídeos e estatísticas em tempo real direto no YouTube."
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
            <p>Mapeamento de {len(EVENTOS_GOIAS_2026)} Eventos em Goiás &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
    </div>

    <div class="section-box">
        <div class="section-title">🎪 RADAR DE EVENTOS POPULOSOS DE GOIÁS (50/MÊS — AGOSTO, SETEMBRO E OUTUBRO 2026)</div>
        <table>
            <thead><tr><th>Período & Data</th><th>Categoria</th><th>Evento & Cidade</th><th>Local & Raio Geotargeting</th><th>Público</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{ev['periodo_datas']}</strong></td><td><span style='color:#15803d;font-weight:bold;'>{ev['categoria']}</span></td><td><strong>{ev['evento']}</strong><br><span style='color:#64748b;'>{ev['cidade']} ({ev['regiao']})</span></td><td>{ev['local']}<br><span style='color:#0284c7;'>Raio: {ev['raio_anuncio']}</span></td><td><strong>{ev['publico_estimado']}</strong></td></tr>" for ev in EVENTOS_GOIAS_2026[:25]])}
            </tbody>
        </table>
    </div>

    <div class="footer">
        Dossiê de Inteligência Eleitoral & Estratégia de Tráfego Pago &bull; Wilder Morais 2026
    </div>

</body>
</html>
"""

    buffer = io.BytesIO()
    buffer.write(html_content.encode("utf-8"))
    buffer.seek(0)
    return buffer
