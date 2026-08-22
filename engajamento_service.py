"""
engajamento_service.py — Motor de Inteligência para Algoritmo da Meta e Roteiros Virais (Furar a Bolha)
Campanha Wilder Morais — Goiás 2026

Mecânica:
  - Foco nos sinais de ranking da Meta 2026: Shares por DM, Retenção (Watch Time), ASR (áudio) e OCR (texto na tela).
  - Elimina vícios de palanque (discurso institucional frio).
  - Metodologia híbrida: ACM Neto (Contraste) + João Campos (Linguagem Nativa e Prova de Chão) + Marcelo Vitorino (Gancho 3s).
"""

import os
import sys
import json
import re
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "google/gemini-2.5-flash"

# ─────────────────────────────────────────────────────────────────
# 1. MATRIZ DE PALAVRAS MAGNÉTICAS — GOIÁS 2026 (SEO / ASR META)
# ─────────────────────────────────────────────────────────────────
PALAVRAS_MAGNETICAS_GOIAS = {
    "saude_e_filas": {
        "titulo": "Saúde & Filas do SUS",
        "palavras_ouro": ["fila da vergonha", "espera de 6 meses", "remédio em casa", "upa 24 horas", "exame atrasado", "saúde sem politicagem", "hospital regional", "dor de mãe"],
        "evitar_palanque": ["reestruturação sistêmica", "aparato governamental", "plano plurianual", "recursos orçamentários"]
    },
    "juventude_e_emprego": {
        "titulo": "Juventude & Primeiro Emprego",
        "palavras_ouro": ["primeiro salário", "carteira assinada", "sem experiência", "jovem aprendiz", "dinheiro no bolso", "faculdade sem dívida", "oportunidade real", "futuro garantido"],
        "evitar_palanque": ["fomento à empregabilidade", "disposições legais", "qualificação mercadológica"]
    },
    "transporte_e_entorno": {
        "titulo": "Entorno do DF & Transporte",
        "palavras_ouro": ["3 horas no trânsito", "humilhação diária", "passagem cara", "cansaço", "chegar em casa vivo", "ônibus sucateado", "integração tarifária", "abandono de anos"],
        "evitar_palanque": ["mobilidade urbana integrada", "concessões intermunicipais", "revisão de marco regulatório"]
    },
    "agro_e_interior": {
        "titulo": "Agro & Estradas do Interior",
        "palavras_ouro": ["estrada de terra", "ponte caída", "safra parada", "quem produz", "engenheiro que faz", "sem imposto abusivo", "produtor respeitado", "Goiás de verdade"],
        "evitar_palanque": ["escoamento logístico agroindustrial", "alíquota tributária", "infraestrutura viária"]
    },
    "contraste_politico": {
        "titulo": "Contraste & Desconstrução",
        "palavras_ouro": ["político de gabinete", "nunca construiu nada", "promessa de 16 anos", "engenheiro vs falador", "quem faz na prática", "resultado comprovado", "chega de desculpa"],
        "evitar_palanque": ["opositor partidário", "conjuntura pleiteada", "hermenêutica eleitoral"]
    }
}

ESTIMULOS_ALGORITMICOS = {
    "furar_bolha": {
        "nome": "💥 Furar a Bolha (Jovens & Indecisos)",
        "foco": "Linguagem 100% não-política, gancho visual forte, quebra de padrão nos primeiros 3 segundos."
    },
    "dor_profunda": {
        "nome": "🩸 Indignação com Dor Real (Saúde / Transporte / Custo)",
        "foco": "Tocar na ferida concreta com número ou caso real sem parecer discurso pronto."
    },
    "contraste_adversario": {
        "nome": "⚡ Contraste Cirúrgico (ACM Neto Style)",
        "foco": "Comparar quem tem resultado na vida real vs quem vive de promessa de gabinete."
    },
    "prova_chao": {
        "nome": "🚜 Prova de Chão & Presença (João Campos Style)",
        "foco": "Rosto humano, na estrada, sem terno, informalidade controlada, mostrando como resolve."
    },
    "quebra_objecao": {
        "nome": "🎯 Quebra de Objeção & Visão de Futuro",
        "foco": "Desmontar narrativas contrárias entregando propostas claras e práticas."
    }
}

FORMATOS_DISPONIVEIS = {
    "reels_30s": "🎬 Reels / Shorts (20 a 30s — Alta Viralidade)",
    "carrossel_retencao": "📑 Carrossel Magnético (Slides de Salvamento)",
    "stories_conversao": "📱 Sequência de Stories (Conversão via DM)",
    "contraste_45s": "⚡ Vídeo de Contraste Político (45s — Combate)"
}

SYSTEM_PROMPT_ENGAJAMENTO = """
Você é o Diretor de Engenharia de Algoritmo e Viralização da campanha Wilder Morais (Governador de Goiás 2026).
Sua missão é criar roteiros e copys que o algoritmo da Meta (Instagram Reels) distribua PARA FORA DA BOLHA (eleitores não-convertidos, jovens, indecisos).

REGRAS ABSOLUTAS DO ALGORITMO DA META:
1. SINAL #1: GERAÇÃO DE COMPARTILHAMENTO POR DM (Sends per Reach). O eleitor precisa pensar: "Vou mandar isso no grupo da família ou pro meu amigo".
2. ZERO VÍCIO DE PALANQUE: Proibido jargão burocrático ("reestruturação", "plano plurianual", "conjuntura"). Fale como gente normal.
3. RETENÇÃO PURA NOS PRIMEIROS 3 SEGUNDOS: O gancho precisa de uma cena visual inusitada e uma frase cortante que interrompe o scroll.
4. SEO E ASR (RECONHECIMENTO DE ÁUDIO): O áudio falado deve conter palavras magnéticas específicas para o algoritmo indexar a dor no Explore.
5. IDENTIDADE DE WILDER: Engenheiro que constrói, Senador dos Livros, self-made man prático, simples, com bota e chapéu, avesso a politicagem de gabinete.

FORMATO DE RESPOSTA (OBRIGATORIAMENTE JSON VÁLIDO):
{
  "titulo_estrategico": "Título do Roteiro",
  "formato": "Nome do Formato",
  "estimulo": "Nome do Estímulo",
  "score_viral_previsto": 94,
  "gancho_0_a_3s": {
    "visual_camera": "O que aparece na tela nos primeiros 3 segundos",
    "texto_na_tela_ocr": "TEXTO EM CAIXA ALTA NA TELA (MÁXIMO 5 PALAVRAS)",
    "fala_abertura": "Frase falada de abertura"
  },
  "palavras_chave_meta_asr": ["palavra 1", "palavra 2", "palavra 3", "palavra 4"],
  "desenvolvimento_retencao": [
    {"tempo": "03s-15s", "acao_e_fala": "Desenvolvimento com dado real ou dor concreta"},
    {"tempo": "15s-25s", "acao_e_fala": "Solução prática de engenheiro + contraste"}
  ],
  "fechamento_cta_dm": {
    "tempo": "25s-30s",
    "fala_final": "Chamada emocional e direta",
    "palavra_chave_dm": "PALAVRA",
    "motivo_compartilhamento": "Por que o eleitor vai mandar esse vídeo no direct"
  },
  "direcao_cena_e_figurino": "Dicas de enquadramento, ângulo, iluminação e vestimenta",
  "dica_audio_e_trilha": "Sugestão de trilha de fundo (ritmo, efeito sonoro nos cortes)"
}
"""

def gerar_roteiro_viral_ia(tema: str, estimulo: str = "furar_bolha", formato: str = "reels_30s", cidade: str = "Goiás Geral") -> dict:
    """Gera um roteiro otimizado para o algoritmo da Meta usando IA ou fallback especializado."""
    
    info_estimulo = ESTIMULOS_ALGORITMICOS.get(estimulo, ESTIMULOS_ALGORITMICOS["furar_bolha"])
    nome_formato = FORMATOS_DISPONIVEIS.get(formato, FORMATOS_DISPONIVEIS["reels_30s"])
    
    prompt_user = f"""
Crie um conteúdo com foco em ALTA DISTRIBUIÇÃO ORGÂNICA na Meta.
- TEMA/PAUTA: {tema}
- LOCAL/PÚBLICO: {cidade}
- ESTÍMULO ALGORÍTMICO: {info_estimulo['nome']} ({info_estimulo['foco']})
- FORMATO: {nome_formato}
"""

    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your-openrouter-api-key":
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_ENGAJAMENTO},
                {"role": "user", "content": prompt_user}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.4
        }
        try:
            r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=18, verify=False)
            if r.status_code == 200:
                raw = r.json()["choices"][0]["message"]["content"]
                return json.loads(raw)
        except Exception as e:
            print(f"[AVISO ENGAJAMENTO] Erro na API OpenRouter, usando fallback: {e}")

    # Fallback estruturado de altíssima qualidade
    return _gerar_fallback_roteiro(tema, estimulo, formato, cidade)


def _gerar_fallback_roteiro(tema: str, estimulo: str, formato: str, cidade: str) -> dict:
    """Templates refinados de viralização baseados no benchmark ACM Neto / João Campos / Vitorino."""
    
    t_clean = tema.lower()
    
    if "saúde" in t_clean or "sus" in t_clean or "hospital" in t_clean or "remédio" in t_clean:
        return {
            "titulo_estrategico": f"A Verdade sobre a Fila da Saúde em {cidade}",
            "formato": FORMATOS_DISPONIVEIS.get(formato, "Reels 30s"),
            "estimulo": ESTIMULOS_ALGORITMICOS.get(estimulo, {}).get("nome", "Furar a Bolha"),
            "score_viral_previsto": 96,
            "gancho_0_a_3s": {
                "visual_camera": "Wilder segura na mão um maço de pedidos de exame e receitas médicas amassadas.",
                "texto_na_tela_ocr": "ISSO NÃO É SAÚDE, É HUMILHAÇÃO",
                "fala_abertura": "Você esperaria 8 meses por uma consulta se quem estivesse com dor fosse o seu filho?"
            },
            "palavras_chave_meta_asr": ["fila do SUS", "hospital regional", "remédio em casa", "saúde em Goiás", "engenheiro que faz"],
            "desenvolvimento_retencao": [
                {"tempo": "03s-15s", "acao_e_fala": "Em Goiânia e no interior, milhares de famílias perdem o dia na porta do posto pra ouvir: 'volte mês que vem'. Isso é incompetência pura de gabinete."},
                {"tempo": "15s-25s", "acao_e_fala": "Como engenheiro, eu gerenciei obras gigantescas. Saúde se resolve com gestão, UPA 24 horas funcionando e remédio entregue direto na sua casa."}
            ],
            "fechamento_cta_dm": {
                "tempo": "25s-30s",
                "fala_final": "Se você também cansou de desculpas, manda esse vídeo pra quem já passou por isso e comenta 'SAUDE' que te envio o plano completo.",
                "palavra_chave_dm": "SAUDE",
                "motivo_compartilhamento": "Gera identificação instantânea com qualquer pessoa que já sofreu na fila do SUS."
            },
            "direcao_cena_e_figurino": "Camisa polo simples, microfone sem fio na lapela, caminhando no pátio com luz natural. Sem cenário de estúdio ou terno.",
            "dica_audio_e_trilha": "Sem música nos primeiros 3s (fala seca e forte). Depois entra batida leve de suspense que vira esperança."
        }
    
    elif "jovem" in t_clean or "emprego" in t_clean or "salário" in t_clean or "estudante" in t_clean:
        return {
            "titulo_estrategico": f"Primeiro Emprego sem Frescura em {cidade}",
            "formato": FORMATOS_DISPONIVEIS.get(formato, "Reels 30s"),
            "estimulo": ESTIMULOS_ALGORITMICOS.get(estimulo, {}).get("nome", "Furar a Bolha"),
            "score_viral_previsto": 98,
            "gancho_0_a_3s": {
                "visual_camera": "Wilder rasga uma folha de currículo na mesa e olha firme para a lente.",
                "texto_na_tela_ocr": "PEDIRAM EXPERIÊNCIA PRO SEU 1º EMPREGO?",
                "fala_abertura": "Como é que você vai ter experiência pro seu primeiro emprego se ninguém te dá a primeira chance?"
            },
            "palavras_chave_meta_asr": ["primeiro emprego", "jovem aprendiz", "carteira assinada", "salário digno", "Wilder Morais"],
            "desenvolvimento_retencao": [
                {"tempo": "03s-15s", "acao_e_fala": "Eu comecei a trabalhar muito cedo. Sei exatamente o que é bater de porta em porta e ouvir não porque você tem 18 anos e não tem padrinho político."},
                {"tempo": "15s-25s", "acao_e_fala": "Nosso projeto vai bancar o incentivo fiscal para as empresas de Goiás contratarem jovens aprendizes com carteira assinada e salário na conta."}
            ],
            "fechamento_cta_dm": {
                "tempo": "25s-30s",
                "fala_final": "Marca um amigo que tá procurando emprego ou comenta 'EMPREGO' que te mostro como vamos destravar isso.",
                "palavra_chave_dm": "EMPREGO",
                "motivo_compartilhamento": "O jovem encaminha para outros amigos da faculdade ou escola que estão desesperados por vaga."
            },
            "direcao_cena_e_figurino": "Estilo João Campos: camisa jeans dobrada, celular gravado na vertical em ângulo dinâmico.",
            "dica_audio_e_trilha": "Corte seco no gancho. Efeito sonoro de papel rasgando."
        }
    
    else:
        return {
            "titulo_estrategico": f"O que não te contaram sobre {tema} em {cidade}",
            "formato": FORMATOS_DISPONIVEIS.get(formato, "Reels 30s"),
            "estimulo": ESTIMULOS_ALGORITMICOS.get(estimulo, {}).get("nome", "Furar a Bolha"),
            "score_viral_previsto": 93,
            "gancho_0_a_3s": {
                "visual_camera": "Wilder aponta para a câmera segurando uma trena ou planta de engenharia.",
                "texto_na_tela_ocr": "ELES PASSARAM ANOS TE ENGANANDO",
                "fala_abertura": "Você já reparou que político de gabinete adora inaugurar maquete, mas nunca resolve o problema de verdade?"
            },
            "palavras_chave_meta_asr": ["engenheiro que constrói", "Goiás de verdade", "sem politicagem", "resultado real", "Wilder Morais"],
            "desenvolvimento_retencao": [
                {"tempo": "03s-15s", "acao_e_fala": f"Sobre {tema}, o que falta em Goiás não é discurso bonito. É colocar quem entende de obra, gestão e números para fazer o estado funcionar."},
                {"tempo": "15s-25s", "acao_e_fala": "Eu construí empresas e gerei milhares de empregos com planejamento. Menos imposto, mais entrega e respeito ao cidadão."}
            ],
            "fechamento_cta_dm": {
                "tempo": "25s-30s",
                "fala_final": f"Manda esse vídeo pra quem vive em {cidade} e comenta 'GOIAS' para receber a proposta completa.",
                "palavra_chave_dm": "GOIAS",
                "motivo_compartilhamento": "Indignação positiva e desejo de mudança prática."
            },
            "direcao_cena_e_figurino": "Ambiente real, feira ou estrada. Tom firme, acolhedor e próximo.",
            "dica_audio_e_trilha": "Voz limpa em primeiro plano com microfone lapela de alta sensibilidade."
        }


def auditar_roteiro_ia(texto_roteiro: str) -> dict:
    """Analisa um roteiro ou ideia de conteúdo e dá a nota algorítmica da Meta (0 a 100)."""
    
    texto_low = texto_roteiro.lower()
    
    # 1. Detecção de palavras de palanque (prejudicam o alcance na Meta)
    palavras_palanque_encontradas = []
    lista_palanque = [
        "aparato", "reestruturação", "plano plurianual", "disposições", "proposições",
        "conforme a lei", "outrossim", "portanto venho", "meus caros", "caros eleitores",
        "neste pleito", "plataforma eleitoral", "vota em mim", "vote no número"
    ]
    for p in lista_palanque:
        if p in texto_low:
            palavras_palanque_encontradas.append(p)
            
    # 2. Detecção de palavras magnéticas (alavancam distribuição)
    palavras_magneticas_encontradas = []
    lista_magnetica = [
        "humilhação", "fila", "remédio", "primeiro emprego", "carteira assinada",
        "sem experiência", "trânsito", "3 horas", "engenheiro", "construiu",
        "nunca fez", "dinheiro no bolso", "na prática", "comenta", "manda no direct"
    ]
    for m in lista_magnetica:
        if m in texto_low:
            palavras_magneticas_encontradas.append(m)

    # Cálculo do Score Algorítmico
    score = 70
    if len(texto_roteiro.split()) < 80: # tamanho bom pra 30s
        score += 10
    score -= (len(palavras_palanque_encontradas) * 12)
    score += (len(palavras_magneticas_encontradas) * 6)
    score = max(35, min(99, score))
    
    # Diagnóstico
    if score >= 85:
        nivel = "🟢 ALTO POTENCIAL DE FURAR A BOLHA"
        diag = "O roteiro tem boa retenção, linguagem direta e gatilhos que a Meta distribui para públicos não-seguidores."
    elif score >= 65:
        nivel = "🟡 MÉDIO (PRECISA DE GANCHO MAIS FORTE)"
        diag = "O conteúdo está correto, mas o início pode não travar o scroll nos primeiros 3 segundos. Recomenda-se trocar palavras burocráticas por dores práticas."
    else:
        nivel = "🔴 RISCO DE BAIXA DISTRIBUIÇÃO (VÍCIO DE PALANQUE)"
        diag = "O texto parece discurso político tradicional. O algoritmo da Meta vai limitar a distribuição aos mesmos seguidores de sempre."

    # Geração de versão otimizada
    versao_otimizada = re.sub(r'(?i)(venho aqui pedir|caros eleitores|neste pleito)', 'Você já reparou que', texto_roteiro)
    if not any(k in versao_otimizada.lower() for k in ["comenta", "manda", "compartilha"]):
        versao_otimizada += " Comenta 'GOIAS' no direct que te envio os detalhes."

    return {
        "score_viral": score,
        "classificacao": nivel,
        "diagnostico_algoritmo": diag,
        "palavras_palanque_detectadas": palavras_palanque_encontradas,
        "palavras_magneticas_detectadas": palavras_magneticas_encontradas,
        "sugestao_gancho_3s": "Você esperaria 5 horas por atendimento se o seu filho estivesse com febre?",
        "versao_reescrita_meta": versao_otimizada
    }
