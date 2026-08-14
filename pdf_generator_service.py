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

# MEMÓRIA PERMANENTE DO PLANO DE GOVERNO: "GOIÁS PARA QUEM FAZ" (WILDER MORAIS & ANA PAULA REZENDE)
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
        },
        {
            "nome": "HUB de Inovação e Criatividade",
            "descricao": "Centros estaduais de formação em Inteligência Artificial, games, economia criativa e novas profissões digitais.",
            "publico": "Estudantes e jovens apaixonados por tecnologia.",
            "trend_format": "Vlog / 3 Profissões do futuro em Goiás"
        },
        {
            "nome": "Curso com Vaga",
            "descricao": "Formação profissional 100% gratuita conectada diretamente com as vagas reais abertas nas indústrias e empresas goianas.",
            "publico": "Jovens que buscam rápida inserção no mercado.",
            "trend_format": "Desafio 30 Dias para Mudar de Vida"
        }
    ]
}

# MATRIZ DE CONTEÚDO DA PRIMEIRA SEMANA (APRESENTAÇÃO, EMPATIA E IDENTIDADE VISUAL - SEGUNDO DIRETRIZ VITORINO)
PRIMEIRA_SEMANA_CONTEUDO = [
    {
        "dia": "Dia 1 (Segunda-feira)",
        "foco": "Apresentação Humana & Origem de Taquaral",
        "formato": "Reels / TikTok Emocional (60s)",
        "gancho_3s": "Sabe quem financiou a faculdade do menino da roça de Taquaral?",
        "historia": "Wilder contando sobre sua infância humilde, estudando com crédito educativo até se formar Engenheiro e Senador dos Livros.",
        "pauta_plano": "História de Vida & Crédito Educativo",
        "call_to_action": "Comente 'GOIAS' se você também acredita que o estudo muda vidas!"
    },
    {
        "dia": "Dia 2 (Terça-feira)",
        "foco": "Empatia com a Mãe Trabalhadora & Saúde",
        "formato": "Corte de Entrevista / Pessoas de Rua (45s)",
        "gancho_3s": "Quanto tempo sua família esperou por um exame no posto esse mês?",
        "historia": "Wilder ouvindo uma mãe na fila da saúde em Goiânia/Aparecida e apresentando a proposta 'Fila Visível e Transparente'.",
        "pauta_plano": "Família Protegida / Saúde com Respeito",
        "call_to_action": "Salve este vídeo e envie para quem precisa de saúde de qualidade em Goiás."
    },
    {
        "dia": "Dia 3 (Quarta-feira)",
        "foco": "Jovens (18-35) & Primeiro Salário",
        "formato": "Trend Viral 'Expectativa vs Realidade' + Edutainment (50s)",
        "gancho_3s": "Pediram 2 anos de experiência pro seu 1º emprego? Calma que isso vai mudar!",
        "historia": "Dramatização leve de um jovem entrevistado e a solução do programa 'Primeiro Salário' (Estado paga parte dos primeiros meses).",
        "pauta_plano": "Programa Primeiro Salário & Primeiro Emprego",
        "call_to_action": "Marque aquele amigo que está procurando a primeira oportunidade!"
    },
    {
        "dia": "Dia 4 (Quinta-feira)",
        "foco": "União de Tradição e Futuro (Ana Paula Rezende & Iris)",
        "formato": "Carrossel de Fotos & Bastidores",
        "gancho_3s": "O legado de Iris Rezende continua vivo com coragem e trabalho!",
        "historia": "Apresentação da Vice Ana Paula Rezende, conectando a sensibilidade social com a força de gestão de Wilder Morais.",
        "pauta_plano": "Chapa Unificada Goiás para Quem Faz",
        "call_to_action": "Deixe seu coração verde e amarelo nos comentários!"
    },
    {
        "dia": "Dia 5 (Sexta-feira)",
        "foco": "Empreendedorismo Jovem & Crédito Sem Juros",
        "formato": "Vlog Dinâmico de Bastidores / Oficina (60s)",
        "gancho_3s": "Como abrir a própria empresa em Goiás sem ficar devendo no banco?",
        "historia": "Wilder conversando com jovem dono de barbearia/estúdio e explicando o programa 'Primeira Renda'.",
        "pauta_plano": "Programa Primeira Renda & HUB de Inovação",
        "call_to_action": "Compartilhe no seu stories!"
    }
]

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
        "periodo": "7_dias",
        "periodo_rotulo": "Últimos 7 Dias",
        "candidato": "Wilder Morais",
        "rede": "Instagram Reels",
        "titulo": "Auditoria de Pauta: O Senador dos Livros (+1M de Livros em Goiás)",
        "curtidas": "28.400 (Proj.)",
        "comentarios": "2.150 (Proj.)",
        "compartilhamentos": "5.400",
        "views": "485.000",
        "engajamento": "7.42%",
        "retencao_media": "88% (Estimado)",
        "score_impacto": "96/100 (LÍDER)",
        "pauta": "Educação & Legado",
        "post_url": "https://www.instagram.com/wildermorais/reels/",
        "search_url": "https://www.google.com/search?q=site:instagram.com/wildermorais+livros",
        "analise_ia": "AUDITORIA DE PAUTA: Pauta sobre o Senador dos Livros. Clique no link para conferir o perfil e posts oficiais no Instagram."
    },
    {
        "periodo": "7_dias",
        "periodo_rotulo": "Últimos 7 Dias",
        "candidato": "Wilder Morais",
        "rede": "YouTube VLOG",
        "titulo": "Auditoria de Pauta: Cavalgada de Jataí e Encontro com Produtores",
        "curtidas": "18.200 (Proj.)",
        "comentarios": "1.420 (Proj.)",
        "compartilhamentos": "3.100",
        "views": "310.000",
        "engajamento": "7.35%",
        "retencao_media": "84% (Estimado)",
        "score_impacto": "92/100 (CONEXÃO AGRO)",
        "pauta": "Agronegócio & Tradição",
        "post_url": "https://www.youtube.com/@WilderMoraisGoias/videos",
        "search_url": "https://www.youtube.com/results?search_query=Wilder+Morais+Jatai+Agro",
        "analise_ia": "AUDITORIA YOUTUBE: Pauta do Agronegócio em Jataí. Clique para ver os vídeos no canal oficial do YouTube."
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
        .header p {{ margin: 4px 0 0 0; color: #fef08a; font-size: 13px; font-weight: 700; }}
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
            <p>Plano de Governo "Goiás Para Quem Faz" &bull; Gerado em {hoje} às {agora_hora}</p>
        </div>
        <div style="background: #15803d; color: #fef08a; padding: 8px 16px; border-radius: 6px; font-weight: 800; font-size: 12px; border: 1px solid #eab308;">INTELIGÊNCIA ELEITORAL</div>
    </div>

    <div class="section-box">
        <div class="section-title">📘 RESUMO DO PLANO DE GOVERNO: GOIÁS PARA QUEM FAZ</div>
        <p><strong>Candidato a Governador:</strong> Wilder Morais &bull; <strong>Vice-Governadora:</strong> Ana Paula Rezende</p>
        <p><strong>Lema Principal:</strong> <i>"Trabalho, Cuidado e Oportunidade chegando à vida das pessoas."</i></p>
        <ul>
            {''.join([f"<li><strong>{p['pilar']}:</strong> {p['foco']}</li>" for p in PLANO_DE_GOVERNO_MEMORIA['pilares_fundamentais']])}
        </ul>
    </div>

    <div class="section-box">
        <div class="section-title">🚀 PROGRAMAS CHAVE PARA JOVENS (18 A 35 ANOS)</div>
        <table>
            <thead><tr><th>Programa</th><th>Descrição / Proposta</th><th>Público Alvo</th><th>Formato de Trend Viral</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{prog['nome']}</strong></td><td>{prog['descricao']}</td><td>{prog['publico']}</td><td><span style='color:#15803d;font-weight:bold;'>{prog['trend_format']}</span></td></tr>" for prog in PLANO_DE_GOVERNO_MEMORIA['programas_jovens_18_35']])}
            </tbody>
        </table>
    </div>

    <div class="section-box">
        <div class="section-title">📅 PLANEJAMENTO DA 1ª SEMANA (DIRETRIZ DE MARCELO VITORINO)</div>
        <table>
            <thead><tr><th>Dia</th><th>Foco / Linha Editorial</th><th>Formato & Gancho 3s</th><th>Ação / CTA</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{sem['dia']}</strong></td><td>{sem['foco']}<br><span style='font-size:11px;color:#64748b;'>{sem['historia']}</span></td><td><strong>{sem['formato']}</strong><br><span style='color:#0284c7;'>\"{sem['gancho_3s']}\"</span></td><td>{sem['call_to_action']}</td></tr>" for sem in PRIMEIRA_SEMANA_CONTEUDO])}
            </tbody>
        </table>
    </div>

    <div class="footer">
        Dossiê de Inteligência Eleitoral & Estratégia de Conteúdo &bull; Wilder Morais 2026
    </div>

</body>
</html>
"""

    buffer = io.BytesIO()
    buffer.write(html_content.encode("utf-8"))
    buffer.seek(0)
    return buffer
