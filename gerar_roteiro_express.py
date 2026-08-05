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

def gerar_roteiro_express(cidade_ou_tema: str) -> str:
    """
    Gera sob demanda um Roteiro Viral de 30 segundos (Reels/TikTok) para o candidato Wilder Morais
    com base em uma cidade específica de Goiás ou tema solicitado pelo Social Media.
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return f"""
🎬 ROTEIRO EXPRESS (MODO BASE): {cidade_ou_tema.upper()}

- GANCHO (0-3s): "Você sabia que {cidade_ou_tema} tem potencial para produzir e crescer 2x mais?"
- NARRATIVA (3-24s): "Como senador e engenheiro, Wilder Morais já provou que investimento certo traz emprego de verdade para a região."
- CTA (24-30s): "Comenta '{cidade_ou_tema.upper()}' para receber as propostas completas na sua DM."
"""

    prompt_system = (
        "Você é o Diretor de Criação e Copywriter da campanha de Wilder Morais para Governador de Goiás.\n"
        "Crie um Roteiro Viral de 30 segundos para Reels/TikTok focado no público de Goiás.\n"
        "Estrutura Obrigatória:\n"
        "1. GANCHO (0-3s): Frase de altíssima retenção, curiosidade ou pergunta provocativa.\n"
        "2. NARRATIVA (3-24s): Dor local da região/tema + Ação/Visão de Wilder Morais (Engenheiro / Senador dos Livros / Vencedor pela Educação).\n"
        "3. CTA (24-30s): Chamada para ação na DM ou compartilhamento em família.\n"
        "4. SUGESTÃO DE LEGENDA E HASHTAGS REGIONAIS."
    )

    prompt_user = f"Tema ou Cidade Solicitada: {cidade_ou_tema}"

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
        "temperature": 0.4
    }

    try:
        res = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15, verify=False)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[ERRO] Falha ao gerar roteiro express: {e}"

if __name__ == "__main__":
    tema = sys.argv[1] if len(sys.argv) > 1 else "Entorno do DF e Saúde"
    print(gerar_roteiro_express(tema))
