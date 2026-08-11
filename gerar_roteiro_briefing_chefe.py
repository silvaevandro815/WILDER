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

SYSTEM_PROMPT_CHEFE = """
Você é o Especialista de Conteúdo e Storytelling Político da campanha de Wilder Morais 2026.
Sua missão é gerar ideias de posts, carrosséis e vídeos de altíssimo padrão emocional e estratégico para a pré-campanha de Wilder Morais.

DIRETRIZES DA NARRATIVA:
1. SEM ATAQUES DIRECTOS: Mostrar que Wilder é o melhor para cuidar de Goiás.
2. CONTRASTE SOCIAL: Goiás cresce na economia/PIB, mas o cidadão não cresce junto (falta de emprego, saúde precária, jovens indo embora).
3. HISTÓRIA DE WILDER: Homem simples do interior que venceu pelo estudo/trabalho, engenheiro de 3 continentes, Senador dos Livros.
4. SLOGAN E JINGLE: "O melhor pra Goiás é Wilder Morais!"
"""

def gerar_peca_semana(tipo_peca: str = "CARROSSEL_SOCIAL") -> dict:
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return {
            "titulo": "Goiás cresceu. Mas por que a vida da sua família continua difícil?",
            "slogan": "O melhor pra Goiás é Wilder Morais!",
            "formato": "Carrossel 10 Lâminas",
            "gancho_3s": "Goiás bate recordes de riqueza no Agro. Mas por que o nosso povo continua passando aperto?",
            "descricao": "Carrossel de alto impacto emocional mostrando o contraste entre o PIB de Goiás e a dor do cidadão."
        }

    prompt_user = f"Gere uma proposta de peça de alto impacto para a semana de pré-campanha do tipo: '{tipo_peca}'."
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_CHEFE},
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
        print(f"[AVISO] Falha ao gerar peça da semana: {e}")
        return {
            "titulo": "O melhor pra Goiás é Wilder Morais!",
            "gancho_3s": "Quem aí já aprendeu a melhor música de Goiás?",
            "descricao": "Vídeo retrospectiva com jingle oficial."
        }

if __name__ == "__main__":
    peca = sys.argv[1] if len(sys.argv) > 1 else "CARROSSEL_SOCIAL"
    res = gerar_peca_semana(peca)
    print(json.dumps(res, ensure_ascii=False, indent=2))
