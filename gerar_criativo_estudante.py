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

SYSTEM_PROMPT_ESTUDANTE = """
Você é o Diretor Criativo de Redes Sociais da campanha de Wilder Morais para Governador de Goiás em 2026.
Sua missão é criar propostas virais para o Instagram no Dia do Estudante (11 de Agosto), combinando tendências, linguagem jovem/dinâmica e o legado real de Wilder Morais na Educação.

LEGADO DE WILDER MORAIS NA EDUCAÇÃO DE GOIÁS:
1. "Senador dos Livros": Distribuiu mais de 1 MILHÃO de livros no estado de Goiás.
2. Criou/Viabilizou 2 Novas Universidades Federais em Goiás: UFJ (Universidade Federal de Jataí) e UFCAT (Universidade Federal de Catalão).
3. Ampliou recursos para o FIES e defende o ensino técnico profissionalizante.
4. História de Vida: Menino de família simples no interior que mudou o rumo da família ao se formar em Engenharia.

SLOGAN: "O melhor pra Goiás é Wilder Morais!"
"""

def gerar_criativo_dia_estudante() -> dict:
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return {
            "titulo": "O conselho que mudou a minha vida (Dia do Estudante)",
            "formato": "Carrossel & Reels Viral",
            "gancho_3s": "Bens a gente pode perder. Mas o que você aprendeu, ninguém te tira!",
            "legado_chave": ["1 Milhão de Livros", "Universidades de Jataí (UFJ) e Catalão (UFCAT)", "Expansão do FIES"]
        }

    prompt_user = "Gere uma proposta de post viral de Dia do Estudante combinando a narrativa de conselho de pai/mãe com as entregas de 1 milhão de livros e universidades federais de Jataí e Catalão."
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_ESTUDANTE},
            {"role": "user", "content": prompt_user}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }

    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=12, verify=False)
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]
        return json.loads(raw)
    except Exception as e:
        print(f"[AVISO] Falha ao gerar criativo do Dia do Estudante: {e}")
        return {
            "titulo": "Dia do Estudante com Wilder Morais",
            "gancho_3s": "Estudo é o único bem que ninguém te tira."
        }

if __name__ == "__main__":
    res = gerar_criativo_dia_estudante()
    print(json.dumps(res, ensure_ascii=False, indent=2))
