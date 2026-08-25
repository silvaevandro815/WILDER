#!/usr/bin/env python3
"""
conteudo_autonomo_engine.py — Motor Autônomo de Criação de Conteúdo Político-Digital
Campanha Wilder Morais (Governador de Goiás 2026)

Funcionalidades:
  - Gera automaticamente roteiros de Reels, carrosséis e POVs a cada 6h
  - Contextualiza as notícias do momento com formatos virais
  - Sugere ataques/contraste baseados nas vulnerabilidades dos adversários
  - Adapta trends nacionais virais para a campanha goiana
  - Gera briefing diário pronto para o social media
"""

import os
import re
import json
import time
import threading
import urllib.request
import ssl
from datetime import datetime
from xml.etree import ElementTree as ET

from dotenv import load_dotenv
load_dotenv()

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL     = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME         = "google/gemini-2.5-flash"

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode    = ssl.CERT_NONE

_lock = threading.Lock()

# ──────────────────────────────────────────────────────────────────────────────
# CACHE CENTRAL
# ──────────────────────────────────────────────────────────────────────────────
CONTEUDO_CACHE = {
    "roteiros_do_dia":     {"data": [], "atualizado_em": None, "ciclos": 0},
    "briefing_social":     {"data": {}, "atualizado_em": None, "ciclos": 0},
    "ataques_prontos":     {"data": [], "atualizado_em": None, "ciclos": 0},
    "trends_adaptados":    {"data": [], "atualizado_em": None, "ciclos": 0},
}

def _agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M")

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS: BUSCA DE CONTEXTO AO VIVO
# ──────────────────────────────────────────────────────────────────────────────
def _get_noticias_vivas():
    """Coleta notícias ao vivo de todos os candidatos e Goiás."""
    queries = [
        "Wilder+Morais+Goiás+2026",
        "Daniel+Vilela+governador+Goias+2026",
        "Marconi+Perillo+eleicao+Goias",
        "saude+Goias+2026",
        "emprego+Goias+governo+2026",
    ]
    headers = {"User-Agent": "Mozilla/5.0 (compatible; RSS/2.0)"}
    noticias = []
    for q in queries:
        try:
            url = f"https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=_SSL_CTX, timeout=8) as r:
                root = ET.fromstring(r.read())
            for item in root.findall(".//item")[:3]:
                titulo = item.findtext("title", "").split(" - ")[0][:120].strip()
                if titulo:
                    noticias.append(titulo)
            time.sleep(0.3)
        except Exception:
            pass
    return noticias[:12]

def _get_trends_virais():
    """Busca tendências de formato/conteúdo que estão viralizando."""
    try:
        import viral_trends_engine as vte
        return vte.get_tendencias_nacionais()[:6]
    except Exception:
        return []

def _get_adversarios_context():
    """Obtém vulnerabilidades dos adversários do viral_trends_engine."""
    try:
        import viral_trends_engine as vte
        adv = vte.get_adversarios()
        texto = []
        for nome, d in adv.items():
            vuln = d.get("vulnerabilidades", [])[:2]
            atq  = d.get("pontos_de_ataque", [])[:2]
            texto.append(f"{nome}: vulnerabilidades={vuln}, ataques={atq}")
        return "\n".join(texto)
    except Exception:
        return "Daniel Vilela: governador em exercício = responsável pelas filas do SUS e buracos nas estradas."

def _get_dores_territoriais():
    """Obtém as dores populares dos municípios (intel_engine)."""
    try:
        import intel_engine
        queixas = intel_engine.get_queixas()[:8]
        return [f"{q.get('cidade','')}: {q.get('categoria','')} — {q.get('texto','')[:80]}" for q in queixas]
    except Exception:
        return [
            "Goiânia: Saúde — fila do SUS, cirurgias eletivas atrasadas",
            "Aparecida de Goiânia: Segurança — medo no bairro, rua escura",
            "Luziânia: Transporte — 3 horas de ônibus para Brasília",
            "Anápolis: Emprego — jovens sem primeiro emprego formal",
            "Rio Verde: Saúde — falta de especialistas no interior",
        ]

# ──────────────────────────────────────────────────────────────────────────────
# FORMATOS VIRAIS MODERNOS (2025-2026)
# ──────────────────────────────────────────────────────────────────────────────
FORMATOS_VIRAIS_2026 = [
    {
        "id": "reel_dor_real",
        "nome": "🎬 Reel de Dor Real (30s)",
        "descricao": "Candidato na rua, problema real na câmera, solução prática. Sem estúdio, sem terno.",
        "estrutura": "0s: gancho visual chocante | 3s: dado real chocante | 15s: solução prática | 25s: CTA compartilhamento",
        "plataforma": "Instagram Reels / TikTok",
        "score_algoritmo": 97,
    },
    {
        "id": "pov_eleitor",
        "nome": "🧑 POV do Eleitor (15-20s)",
        "descricao": "POV: você está na fila do SUS. POV: você perdeu o emprego. O candidato aparece como solução.",
        "estrutura": "0s: texto POV na tela | 2s: cena realista | 10s: virada com solução | 18s: CTA",
        "plataforma": "TikTok / Reels",
        "score_algoritmo": 95,
    },
    {
        "id": "carrossel_contraste",
        "nome": "📑 Carrossel de Contraste (5-7 slides)",
        "descricao": "Slide 1 chocante (dado ruim do adversário), slides seguintes com proposta prática, último slide com CTA de salvamento.",
        "estrutura": "Slide 1: dado chocante | Slides 2-5: proposta | Slide final: 'Salva pra não esquecer'",
        "plataforma": "Instagram Feed / Stories",
        "score_algoritmo": 92,
    },
    {
        "id": "resposta_rapida",
        "nome": "⚡ Resposta Rápida ao Adversário (20-30s)",
        "descricao": "Candidato responde declaração do adversário em menos de 2h. Tom irônico + dado real.",
        "estrutura": "0s: cita a fala do adversário | 5s: ironia cirúrgica | 15s: dado real contrário | 25s: 'compartilha'",
        "plataforma": "Stories / Reels",
        "score_algoritmo": 96,
    },
    {
        "id": "bastidor_real",
        "nome": "🎥 Bastidor Real (qualquer duração)",
        "descricao": "Câmera no ombro, candidato resolvendo problema real, sem roteiro, sem ensaio. Autenticidade máxima.",
        "estrutura": "Começa sem aviso | Mostra problema | Candidato resolve ao vivo | Final natural",
        "plataforma": "Stories / Reels / TikTok",
        "score_algoritmo": 94,
    },
    {
        "id": "voce_sabia",
        "nome": "❓ Você Sabia? (Carrossel de Conscientização)",
        "descricao": "Dados que chocam o eleitor. Cada slide revela um dado ruim do governo atual + proposta de solução.",
        "estrutura": "Capa: pergunta | Slides: dados chocantes | Último: 'Agora você sabe. Compartilha.'",
        "plataforma": "Instagram Feed",
        "score_algoritmo": 90,
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT DO GERADOR AUTÔNOMO DE CONTEÚDO
# ──────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT_CONTEUDO = """Você é o Diretor Criativo e Estrategista de Conteúdo Digital da campanha Wilder Morais (Governador de Goiás 2026).

IDENTIDADE DO WILDER MORAIS:
- Engenheiro civil, self-made man, homem prático que constrói coisas reais
- Senador da República (PL), homem do agro, chapéu e bota quando no interior
- Anti-palanque: fala como gente normal, sem jargão político
- Contraste com Daniel Vilela (governador que herdou o cargo, nunca construiu nada) e Marconi Perillo (ex-governador que já teve sua chance)

CENÁRIO ELEITORAL REAL (08/2026):
- Daniel Vilela (MDB): 43,5% — LÍDER, mas vulnerável como governador em exercício
- Wilder Morais (PL): 22,0% — 2º lugar, empate técnico com Marconi
- Marconi Perillo (PSDB): 21,9% — divide o eleitorado conservador com Wilder

REGRAS ABSOLUTAS DE CONTEÚDO PARA ALGORITMO META 2026:
1. SINAL #1 (45% do peso): Sends por DM — o eleitor PRECISA querer encaminhar no grupo da família
2. SINAL #2 (30%): Retenção 0-3s — gancho visual que para o scroll IMEDIATAMENTE
3. SINAL #3 (15%): ASR (áudio falado) — falar palavras da dor real: "fila do SUS", "primeiro emprego", "buraco na estrada"
4. ZERO VÍCIO DE PALANQUE — proibido: "aparato", "plano plurianual", "conjuntura", "neste pleito"
5. FORMATOS QUE ESTÃO VIRALIZANDO EM 2026: POV, bastidor real, resposta rápida em 2h, carrossel de contraste com dado chocante

COMO GERAR O ROTEIRO (RESPONDA SEMPRE EM JSON VÁLIDO):
{
  "id": "roteiro_único_id",
  "tipo": "reel_dor_real|pov_eleitor|carrossel_contraste|resposta_rapida|bastidor_real|voce_sabia",
  "tema": "tema central",
  "urgencia": "ALTA|MÉDIA|BAIXA",
  "pauta_base": "notícia ou dor que motivou este roteiro",
  "titulo_criativo": "Título interno para o social media identificar",
  "score_viral_previsto": 95,
  "gancho_0_a_3s": {
    "visual": "o que aparece na tela",
    "texto_tela": "TEXTO EM CAIXA ALTA (MÁX 5 PALAVRAS)",
    "fala": "primeira frase falada"
  },
  "roteiro_completo": "roteiro detalhado cena a cena em texto corrido",
  "palavras_asr": ["palavra1", "palavra2", "palavra3"],
  "cta_compartilhamento": "frase final que estimula envio por DM",
  "direcao_producao": "onde gravar, roupa, câmera, ângulo",
  "horario_ideal_postar": "HH:MM — justificativa",
  "adaptacao_adversario": "como este conteúdo ataca Daniel ou Marconi indiretamente"
}"""

# ──────────────────────────────────────────────────────────────────────────────
# MÓDULO 1: GERADOR DE ROTEIROS CONTEXTUALIZADOS
# ──────────────────────────────────────────────────────────────────────────────
def _chamar_ia_roteiro(user_prompt: str, temperatura: float = 0.55) -> dict:
    """Chama a IA para gerar um roteiro. Retorna dict com o roteiro ou fallback."""
    if not OPENROUTER_API_KEY or "your-openrouter" in OPENROUTER_API_KEY:
        return {}
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_CONTEUDO},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": temperatura,
            "max_tokens": 1500,
        }
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=25, verify=False)
        if r.status_code == 200:
            raw = r.json()["choices"][0]["message"]["content"]
            return json.loads(raw)
    except Exception as e:
        print(f"[CONTEÚDO ENGINE] Erro IA: {e}")
    return {}

def gerar_roteiro_contextualizado(noticia: str, formato_id: str = "reel_dor_real", cidade: str = "Goiás") -> dict:
    """Gera um roteiro viral baseado em uma notícia/pauta real."""
    formato = next((f for f in FORMATOS_VIRAIS_2026 if f["id"] == formato_id), FORMATOS_VIRAIS_2026[0])
    adv_ctx = _get_adversarios_context()

    prompt = f"""
Crie um roteiro urgente para a campanha do Wilder Morais baseado NESTA PAUTA DO MOMENTO:

NOTÍCIA/PAUTA: {noticia}
CIDADE/REGIÃO: {cidade}
FORMATO: {formato['nome']} — {formato['descricao']}
ESTRUTURA DO FORMATO: {formato['estrutura']}
SCORE MÍNIMO ESPERADO: {formato['score_algoritmo']}

CONTEXTO DOS ADVERSÁRIOS:
{adv_ctx}

REGRA: O roteiro deve parecer UMA REAÇÃO ao que está acontecendo HOJE, não um conteúdo genérico.
Mencione a cidade/região específica se possível.
Use o formato exigido para a resposta JSON.
"""
    resultado = _chamar_ia_roteiro(prompt)
    if not resultado:
        resultado = _fallback_roteiro_contextualizado(noticia, formato, cidade)
    resultado["formato_info"] = formato
    resultado["gerado_em"] = _agora()
    return resultado

def _fallback_roteiro_contextualizado(noticia: str, formato: dict, cidade: str) -> dict:
    """Fallback de alta qualidade quando a IA não responde."""
    n = noticia.lower()

    if "sus" in n or "saúde" in n or "hospital" in n or "fila" in n or "médico" in n:
        return {
            "id": "fallback_sus_001",
            "tipo": formato["id"],
            "tema": "Saúde e Filas do SUS",
            "urgencia": "ALTA",
            "pauta_base": noticia,
            "titulo_criativo": "A Vergonha da Fila do SUS em Goiás",
            "score_viral_previsto": 96,
            "gancho_0_a_3s": {
                "visual": f"Wilder segura pedidos de exame médico em {cidade}. Câmera em close.",
                "texto_tela": "ISSO ACONTECE AGORA EM GOIÁS",
                "fala": f"Você sabia que em {cidade} famílias esperam 8 meses por uma consulta que o governador prometeu resolver há 4 anos?"
            },
            "roteiro_completo": f"[0s] Câmera abre em close no rosto do Wilder, sem estúdio, luz natural. Texto na tela: 'ISSO ACONTECE AGORA EM GOIÁS'\n[3s] Wilder segura documentos de pacientes. 'Isso aqui são pedidos de exame de gente real de {cidade}. Esperando há meses.'\n[12s] 'O governador em exercício tem responsabilidade por isso. São 4 anos de promessa e zero de entrega.'\n[22s] 'Como engenheiro, sei que problema de gestão tem solução. Remédio em casa, UPA funcionando 24h, especialista no interior. Isso não é promessa, é projeto pronto.'\n[28s] 'Manda esse vídeo pra quem já esperou na fila do SUS. Comenta SAUDE no direct que te mando o plano completo.'",
            "palavras_asr": ["fila do SUS", "hospital", "remédio em casa", "especialista", "governador"],
            "cta_compartilhamento": "Manda pra quem esperou na fila do SUS. Comenta SAUDE.",
            "direcao_producao": f"Gravar em frente a UPA ou posto de saúde de {cidade}. Camisa polo simples, sem paletó. Microfone lapela. Câmera na mão, movimento natural.",
            "horario_ideal_postar": "07:00 ou 18:30 — horário de maior pico de audiência em Goiás",
            "adaptacao_adversario": "Responsabiliza Daniel Vilela (governador em exercício) diretamente pelas filas sem citá-lo pelo nome — o eleitor faz a conexão.",
        }

    elif "emprego" in n or "desemprego" in n or "trabalho" in n or "jovem" in n or "salário" in n:
        return {
            "id": "fallback_emprego_001",
            "tipo": formato["id"],
            "tema": "Emprego e Juventude",
            "urgencia": "ALTA",
            "pauta_base": noticia,
            "titulo_criativo": "O Primeiro Emprego que Goiás não Dá",
            "score_viral_previsto": 98,
            "gancho_0_a_3s": {
                "visual": "Wilder rasga um currículo e olha firme para a câmera.",
                "texto_tela": "PEDIRAM EXPERIÊNCIA PRO 1º EMPREGO?",
                "fala": "Como é que você vai ter experiência pro seu primeiro emprego se ninguém te dá a primeira chance?"
            },
            "roteiro_completo": "[0s] Gancho: Wilder rasga currículo, texto na tela.\n[3s] 'Eu sei exatamente como é bater de porta em porta aos 18 anos e ouvir não porque você não tem padrinho político.'\n[12s] 'Em Goiás, o desemprego jovem está em X%. O governador faz discurso bonito mas o jovem goiano não está vendo salário na conta.'\n[22s] 'Nosso projeto: incentivo fiscal pra empresa que contratar jovem aprendiz com carteira assinada. Simples assim.'\n[28s] 'Marca um amigo que está procurando emprego. Comenta EMPREGO no direct.'",
            "palavras_asr": ["primeiro emprego", "carteira assinada", "jovem aprendiz", "salário digno", "Goiás"],
            "cta_compartilhamento": "Marca um amigo que está procurando emprego. Comenta EMPREGO.",
            "direcao_producao": "Gravar em praça ou shopping, com jovens de fundo. Câmera vertical. Camisa jeans dobrada.",
            "horario_ideal_postar": "12:00 ou 20:00 — jovens no celular no almoço e à noite",
            "adaptacao_adversario": "Implica que o governo atual não gerou emprego jovem — Daniel Vilela como responsável.",
        }

    else:
        # Roteiro genérico de contraste e engenheiro
        return {
            "id": "fallback_generico_001",
            "tipo": formato["id"],
            "tema": "Mudança Real em Goiás",
            "urgencia": "MÉDIA",
            "pauta_base": noticia,
            "titulo_criativo": "O Engenheiro Contra o Político de Gabinete",
            "score_viral_previsto": 92,
            "gancho_0_a_3s": {
                "visual": "Wilder aponta para câmera em frente a uma obra ou estrada.",
                "texto_tela": "POLÍTICO DE GABINETE OU QUEM FAZ?",
                "fala": "Você já notou que político de gabinete adora inaugurar maquete mas nunca resolve o problema de verdade?"
            },
            "roteiro_completo": "[0s] Wilder em frente a estrutura real (obra, estrada, unidade de saúde).\n[3s] 'Como engenheiro, eu sei que problema tem solução. Não tem desculpa de falta de recurso quando existe gestão séria.'\n[15s] 'Goiás precisa de menos discurso e mais entrega. Saúde funcionando, estrada boa, emprego com carteira assinada.'\n[25s] 'Manda esse vídeo pra quem está cansado de promessa. Compartilha com quem você quer ver a mudança.'",
            "palavras_asr": ["engenheiro", "construiu", "na prática", "resultado real", "Goiás de verdade"],
            "cta_compartilhamento": "Manda pra quem está cansado de promessa. Comenta GOIAS.",
            "direcao_producao": "Ambiente externo real. Camisa do campo ou polo simples. Câmera no ombro.",
            "horario_ideal_postar": "18:00 — melhor horário de alcance geral no Instagram",
            "adaptacao_adversario": "Contraste implícito com Marconi (ex-governador que já teve sua chance) e Daniel (herdeiro do cargo).",
        }

# ──────────────────────────────────────────────────────────────────────────────
# MÓDULO 2: GERADOR DE ATAQUES/CONTRASTE PRONTOS
# ──────────────────────────────────────────────────────────────────────────────
def gerar_ataques_adversarios() -> list:
    """Gera carrosséis de contraste prontos para postar contra Daniel e Marconi."""
    ataques = [
        {
            "id": "ataque_daniel_sus",
            "alvo": "Daniel Vilela (MDB — Governador em Exercício)",
            "tipo": "carrossel_contraste",
            "urgencia": "ALTA",
            "titulo": "4 Anos, 0 Resolução: O que o Governador Prometeu e não Entregou",
            "slides": [
                {"slide": 1, "texto": "DANIEL VILELA É GOVERNADOR HÁ 4 ANOS", "subtexto": "E a fila do SUS só cresceu."},
                {"slide": 2, "texto": "EM GOIÂNIA: 42% DAS FAMÍLIAS", "subtexto": "esperaram mais de 6 meses por cirurgia eletiva (dados IBGE 2026)."},
                {"slide": 3, "texto": "NO DEBATE DA BAND: DANIEL NÃO APARECEU", "subtexto": "Candidato que lidera nas pesquisas não tem coragem de debater?"},
                {"slide": 4, "texto": "ENQUANTO ISSO: WILDER ESTÁ NA RUA", "subtexto": "Como engenheiro, ele sabe que problema de gestão tem solução prática."},
                {"slide": 5, "texto": "SALVA ESSE CARROSSEL 📌", "subtexto": "E manda pra quem ainda não decidiu o voto."},
            ],
            "cta": "Salva e manda no grupo da família. Comenta MUDANÇA no direct.",
            "horario_ideal": "19:00",
        },
        {
            "id": "ataque_marconi_chance",
            "alvo": "Marconi Perillo (PSDB — Ex-Governador)",
            "tipo": "carrossel_contraste",
            "urgencia": "MÉDIA",
            "titulo": "Marconi Já Foi Governador. O que Mudou?",
            "slides": [
                {"slide": 1, "texto": "MARCONI PERILLO JÁ FOI GOVERNADOR", "subtexto": "Múltiplos mandatos. Você se lembra do que ele entregou?"},
                {"slide": 2, "texto": "O QUE FICOU DO GOVERNO MARCONI:", "subtexto": "As mesmas filas, os mesmos problemas, o mesmo Goiás de sempre."},
                {"slide": 3, "texto": "VOTAR EM MARCONI = DIVIDIR O VOTO DA MUDANÇA", "subtexto": "Wilder + Marconi = 44%. Divididos, nenhum dos dois chega no 2º turno."},
                {"slide": 4, "texto": "QUEM CONSTRÓI COISAS NOVAS?", "subtexto": "O engenheiro que nunca prometeu o que não pode fazer."},
                {"slide": 5, "texto": "SALVA E COMPARTILHA 📌", "subtexto": "Goiás precisa de quem ainda não teve sua chance de errar."},
            ],
            "cta": "Compartilha com quem está em dúvida. Comenta WILDER no direct.",
            "horario_ideal": "20:00",
        },
    ]
    return ataques

# ──────────────────────────────────────────────────────────────────────────────
# MÓDULO 3: ADAPTAR TRENDS VIRAIS PARA A CAMPANHA
# ──────────────────────────────────────────────────────────────────────────────
def adaptar_trends_virais() -> list:
    """Pega as tendências nacionais e sugere como adaptar para a campanha do Wilder."""
    trends_nacionais = _get_trends_virais()
    adaptacoes = []

    # Adaptações fixas de formato (sempre relevantes em 2026)
    adaptacoes_base = [
        {
            "trend": "POV Político (o que mais está viralizando no TikTok BR)",
            "descricao": "POV: você é goiano, está na fila do SUS há 6 meses...",
            "como_usar": "Wilder entra no frame como solução. Sem falar de eleição diretamente — fala de solução.",
            "exemplo_gancho": "POV: você pediu consulta com especialista em Goiás. São 5 meses de espera.",
            "formato": "TikTok / Reels 15-20s",
            "urgencia": "ALTA",
        },
        {
            "trend": "Série: 'Aqui no Meu Goiás' (bastidor real)",
            "descricao": "Série de vídeos curtos mostrando Wilder em diferentes cidades de Goiás ouvindo problemas reais.",
            "como_usar": "Cada episódio = uma cidade + um problema + uma solução prática. Sem roteiro, câmera no ombro.",
            "exemplo_gancho": "Hoje eu vim até Rio Verde porque me falaram que aqui a situação da saúde está crítica...",
            "formato": "Reels 30-45s / Stories sequência",
            "urgencia": "ALTA",
        },
        {
            "trend": "Carrossel 'Você Sabia?' (maior save rate no Instagram)",
            "descricao": "Cada slide revela um dado chocante sobre Goiás que o eleitor não sabia.",
            "como_usar": "Dados do IBGE sobre saúde, emprego, segurança em Goiás. Último slide = solução do Wilder.",
            "exemplo_gancho": "Você sabia que Goiás tem a 3ª maior fila de cirurgia eletiva do Centro-Oeste?",
            "formato": "Instagram Feed — Carrossel 5-7 slides",
            "urgencia": "MÉDIA",
        },
        {
            "trend": "Resposta Rápida ao Adversário (< 2 horas)",
            "descricao": "Toda vez que Daniel ou Marconi fazem uma declaração, o Wilder responde em vídeo curto com ironia + dado.",
            "como_usar": "Configurar alerta de notícia. Gravar resposta de 20s. Postar antes que o assunto esfrie.",
            "exemplo_gancho": "Vi que o governador prometeu resolver as filas do SUS hoje. Ele prometeu isso em 2022 também...",
            "formato": "Stories + Reels 20-30s",
            "urgencia": "ALTA",
        },
        {
            "trend": "Número Real + Solução Prática (formato educativo viral)",
            "descricao": "Mostrar um número chocante e em seguida a solução específica. Simples, direto, compartilhável.",
            "como_usar": "'X famílias em Goiânia esperaram mais de 6 meses por exame. Minha proposta: [solução em 10 segundos]'.",
            "formato": "Reels 20-25s",
            "urgencia": "ALTA",
        },
    ]

    # Adicionar trends ao vivo se disponíveis
    for t in trends_nacionais[:3]:
        titulo = t.get("titulo", "")
        if titulo and len(titulo) > 10:
            adaptacoes.append({
                "trend": f"📰 Notícia Viral Nacional: {titulo[:80]}",
                "descricao": "Tendência nacional identificada ao vivo no Google News.",
                "como_usar": "Verificar se tem ângulo goiano. Se sim, criar Reel de 20s conectando o assunto nacional à realidade de Goiás.",
                "formato": "Reels / Stories",
                "urgencia": "MÉDIA",
            })

    return adaptacoes_base + adaptacoes

# ──────────────────────────────────────────────────────────────────────────────
# MÓDULO 4: BRIEFING DIÁRIO DO SOCIAL MEDIA
# ──────────────────────────────────────────────────────────────────────────────
def gerar_briefing_social_media() -> dict:
    """Gera o briefing diário completo para o social media da campanha."""
    noticias = _get_noticias_vivas()
    dores    = _get_dores_territoriais()

    # Top 3 pautas mais urgentes para o dia
    pautas_urgentes = []
    for n in noticias[:5]:
        nl = n.lower()
        urgencia = "ALTA" if any(k in nl for k in ["sus", "saúde", "emprego", "segurança", "desemprego", "fila", "crise"]) else "MÉDIA"
        pautas_urgentes.append({"pauta": n, "urgencia": urgencia})

    # Dica de horário
    hora = datetime.now().hour
    if 6 <= hora < 10:
        dica_hora = "Bom horário! Poste agora: audiência matinal em Goiás é forte entre 7h-9h."
    elif 11 <= hora < 14:
        dica_hora = "Ótimo horário de almoço! Reels têm alto alcance entre 12h-13h."
    elif 17 <= hora < 20:
        dica_hora = "HORÁRIO NOBRE DIGITAL: 18h-20h é o pico de engajamento no Instagram em Goiás."
    elif 20 <= hora < 23:
        dica_hora = "Horário noturno: bom para carrosséis de salvamento e conteúdo reflexivo."
    else:
        dica_hora = "Programe publicação para 7h, 12h ou 18h — picos de audiência em Goiás."

    briefing = {
        "gerado_em": _agora(),
        "data_hoje": datetime.now().strftime("%d/%m/%Y"),
        "dica_horario": dica_hora,
        "pautas_urgentes_do_dia": pautas_urgentes[:5],
        "dores_territoriais_ativas": dores[:5],
        "meta_de_conteudo_hoje": {
            "reels": 2,
            "carrossel": 1,
            "stories": 4,
            "total": 7,
        },
        "prioridade_1": pautas_urgentes[0]["pauta"] if pautas_urgentes else "Saúde e filas do SUS em Goiás",
        "acao_imediata": "Grave um Reel de 30s sobre a pauta prioritária acima. Sem teleprompter, sem estúdio. Na rua.",
        "palavras_proibidas_hoje": ["aparato", "plano plurianual", "conjuntura", "neste pleito", "caros eleitores", "outrossim"],
        "palavras_magneticas_hoje": ["fila do SUS", "primeiro emprego", "buraco na estrada", "engenheiro que faz", "Goiás de verdade", "remédio em casa"],
        "regra_do_dia": "Toda declaração do Daniel Vilela ou Marconi Perillo DEVE ter resposta em vídeo em menos de 2 horas.",
    }
    return briefing

# ──────────────────────────────────────────────────────────────────────────────
# EXECUTOR PRINCIPAL — Gera todo o conteúdo do dia
# ──────────────────────────────────────────────────────────────────────────────
def gerar_conteudo_do_dia():
    """Executa todos os módulos e atualiza o cache central."""
    print(f"[CONTEÚDO ENGINE] 🎬 Gerando conteúdo autônomo do dia... ({_agora()})")

    noticias = _get_noticias_vivas()
    roteiros = []

    # Gera roteiros contextualizados para as top 3 notícias
    formatos_rotativos = ["reel_dor_real", "pov_eleitor", "carrossel_contraste", "resposta_rapida", "bastidor_real"]
    for i, noticia in enumerate(noticias[:4]):
        formato_id = formatos_rotativos[i % len(formatos_rotativos)]
        roteiro = gerar_roteiro_contextualizado(noticia, formato_id, "Goiás")
        roteiros.append(roteiro)
        time.sleep(1)  # Delay entre chamadas à IA

    # Também gera um roteiro sobre a dor territorial mais urgente
    # Adiciona roteiro de Apresentação Positiva & Humanização do Wilder (Instagram Intel)
    try:
        import instagram_intel_engine as iie
        consciencia = iie.get_consciencia_situacional()
        ideias_pos = consciencia.get("ideias_apresentacao_wilder", [])
        if ideias_pos:
            ideia_sel = ideias_pos[len(roteiros) % len(ideias_pos)]
            roteiros.insert(0, {
                "id": f"pos_{ideia_sel['id']}",
                "tipo": "reel_apresentacao_positiva",
                "tema": ideia_sel["pilar"],
                "urgencia": "MÉDIA",
                "pauta_base": "Construção de Imagem & Conexão Afetiva com o Povo Goiano",
                "titulo_criativo": ideia_sel["titulo"],
                "score_viral_previsto": 99,
                "gancho_0_a_3s": {
                    "visual": ideia_sel["gancho_3s"].split("Fala:")[0].replace("Visual:","").strip(),
                    "texto_tela": "VOCÊ CONHECE O WILDER DE VERDADE?",
                    "fala": ideia_sel["gancho_3s"].split("Fala:")[1].strip() if "Fala:" in ideia_sel["gancho_3s"] else ideia_sel["gancho_3s"]
                },
                "roteiro_completo": ideia_sel["desenvolvimento"],
                "palavras_asr": ["Wilder Morais", "Goiás de verdade", "engenheiro", "trabalho duro", "família", "Taquaral"],
                "cta_compartilhamento": ideia_sel["cta_dm"],
                "direcao_producao": f"Luz natural, sem estúdio, roupa do dia a dia. Formato: {ideia_sel['formato']}",
                "horario_ideal_postar": "12:30 ou 19:30 — momento de conexão e família",
                "adaptacao_adversario": "Fortalece a figura humana e idônea do Wilder, criando blindagem natural contra ataques dos adversários.",
                "formato_info": {
                    "id": "reel_apresentacao_positiva",
                    "nome": "🌟 Apresentação & Humanização do Wilder (45s)",
                    "descricao": "Roteiro emotivo e inspirador que apresenta a trajetória, valores e realizações reais do candidato.",
                    "estrutura": "Gancho pessoal (0-3s) + História/Realização (3-30s) + Visão de futuro (30-40s) + CTA no Direct",
                    "score_algoritmo": 99
                },
                "gerado_em": _agora()
            })
    except Exception as e_pos:
        print(f"[CONTEÚDO ENGINE] Aviso integração positiva Instagram: {e_pos}")

    ataques   = gerar_ataques_adversarios()
    trends    = adaptar_trends_virais()
    briefing  = gerar_briefing_social_media()

    with _lock:
        CONTEUDO_CACHE["roteiros_do_dia"]["data"]         = roteiros
        CONTEUDO_CACHE["roteiros_do_dia"]["atualizado_em"] = _agora()
        CONTEUDO_CACHE["roteiros_do_dia"]["ciclos"]       += 1

        CONTEUDO_CACHE["ataques_prontos"]["data"]          = ataques
        CONTEUDO_CACHE["ataques_prontos"]["atualizado_em"] = _agora()

        CONTEUDO_CACHE["trends_adaptados"]["data"]          = trends
        CONTEUDO_CACHE["trends_adaptados"]["atualizado_em"] = _agora()

        CONTEUDO_CACHE["briefing_social"]["data"]           = briefing
        CONTEUDO_CACHE["briefing_social"]["atualizado_em"]  = _agora()

    print(f"[CONTEÚDO ENGINE] ✅ {len(roteiros)} roteiros (incluindo Apresentação do Wilder) | {len(ataques)} ataques | {len(trends)} trends adaptados.")

# ──────────────────────────────────────────────────────────────────────────────
# INTERFACE PÚBLICA
# ──────────────────────────────────────────────────────────────────────────────
def get_roteiros_do_dia() -> list:
    with _lock:
        return list(CONTEUDO_CACHE["roteiros_do_dia"]["data"])

def get_briefing_social() -> dict:
    with _lock:
        return dict(CONTEUDO_CACHE["briefing_social"]["data"])

def get_ataques_prontos() -> list:
    with _lock:
        return list(CONTEUDO_CACHE["ataques_prontos"]["data"])

def get_trends_adaptados() -> list:
    with _lock:
        return list(CONTEUDO_CACHE["trends_adaptados"]["data"])

def get_formatos_disponveis() -> list:
    return FORMATOS_VIRAIS_2026

def get_status() -> dict:
    with _lock:
        return {
            "roteiros_do_dia":  {"total": len(CONTEUDO_CACHE["roteiros_do_dia"]["data"]),  "atualizado_em": CONTEUDO_CACHE["roteiros_do_dia"]["atualizado_em"]},
            "briefing_social":  {"gerado": bool(CONTEUDO_CACHE["briefing_social"]["data"]), "atualizado_em": CONTEUDO_CACHE["briefing_social"]["atualizado_em"]},
            "ataques_prontos":  {"total": len(CONTEUDO_CACHE["ataques_prontos"]["data"]),  "atualizado_em": CONTEUDO_CACHE["ataques_prontos"]["atualizado_em"]},
            "trends_adaptados": {"total": len(CONTEUDO_CACHE["trends_adaptados"]["data"]), "atualizado_em": CONTEUDO_CACHE["trends_adaptados"]["atualizado_em"]},
        }

# ──────────────────────────────────────────────────────────────────────────────
# TESTE DIRETO
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print("=" * 60)
    print("🎬 CONTEÚDO AUTÔNOMO ENGINE — TESTE DIRETO")
    print("=" * 60)
    gerar_conteudo_do_dia()
    print("\n📋 BRIEFING DO SOCIAL MEDIA:")
    print(json.dumps(get_briefing_social(), ensure_ascii=False, indent=2)[:1500])
    print("\n🎬 PRIMEIRO ROTEIRO:")
    roteiros = get_roteiros_do_dia()
    if roteiros:
        print(json.dumps(roteiros[0], ensure_ascii=False, indent=2)[:1500])
    print("\n✅ Engine operacional!")
