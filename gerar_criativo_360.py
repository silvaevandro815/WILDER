import os
import sys
import json
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "google/gemini-2.5-flash"

def gerar_estrategia_criativa_360(tipo_frente: str, local_ou_tema: str) -> str:
    """
    Gera scripts e orientações criativas para as 3 Frentes da Campanha Wilder Morais:
    1. 'OFICIAL' -> Instagram/YouTube/TikTok (Estilo Zema/Cleitinho/Repórter do Povo).
    2. 'GUERRILHA_WHATSAPP' -> Memes virais, stickers, kits de militância e ataques leves aos opositores.
    3. 'TRAFEGO_GEOLOCALIZADO' -> Anúncios americanos hiper-locais (ex: no pátio do Hospital X ou Ponto de Ônibus Y).
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return f"""
🎬 MODELO ESTRATÉGICO 360 ({tipo_frente.upper()}) - {local_ou_tema.upper()}

[FRENTE {tipo_frente.upper()}]
- CONCEITO: Conexão direta estilo Zema/Cleitinho sem linguagem formal de político.
- NARRATIVA: Wilder Morais fala da dor exata de {local_ou_tema} mostrando simplicidade e visão prática de engenheiro.
- AÇÃO DO SOCIAL MEDIA: Gravar com microfone de lapela sem terno, mostrando reação real do povo.
"""

    prompt_system = (
        "Você é o Diretor Geral de Estratégia de Criação, Growth e Operações de Guerra Eleitoral da campanha de Wilder Morais (Goiás 2026).\n"
        "Sua missão é romper a mesmice institucional dos políticos tradicionais inspirando-se no estilo Romeu Zema (empresário prático), Cleitinho (populista autêntico do povo) e nas estratégias de tráfego hiper-local americanas (Geofencing Ads).\n\n"
        "Estrutura da Resposta:\n"
        "1. VISÃO DA NARRATIVA & JORNADA DO HERÓI\n"
        "2. ROTEIRO DETALHADO DA CENA (Visual, Áudio, Fala do Wilder, Reação das Pessoas)\n"
        "3. ESTRATÉGIA DE GUERRILHA DE WHATSAPP (Memes, Música, Conteúdo para Militância)\n"
        "4. SEGMENTAÇÃO DE TRÁFEGO HIPER-LOCAL (Geofencing no Meta Ads / Google Ads)."
    )

    prompt_user = f"Frente Solicitada: {tipo_frente}\nLocal ou Tema Específico em Goiás: {local_ou_tema}"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user}
        ],
        "temperature": 0.5
    }

    try:
        res = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=20, verify=False)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[ERRO] Falha ao gerar estratégia 360: {e}"

if __name__ == "__main__":
    frente = sys.argv[1] if len(sys.argv) > 1 else "TRAFEGO_GEOLOCALIZADO"
    tema = sys.argv[2] if len(sys.argv) > 2 else "Fila do Hospital Materno-Infantil em Goiânia"
    print(gerar_estrategia_criativa_360(frente, tema))
