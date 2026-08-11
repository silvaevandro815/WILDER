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
OPENROUTER_KEY_INFO_URL = "https://openrouter.ai/api/v1/auth/key"

def checar_saldo_openrouter() -> dict:
    """
    Verifica o uso exato de tokens da chave e o status de créditos no OpenRouter.
    Detecta automaticamente se a chave está ativa ou com créditos esgotados.
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return {
            "status": "ALERTA",
            "mensagem": "Chave do OpenRouter não configurada no .env",
            "uso_dolares": 0.0
        }

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}

    try:
        r = requests.get(OPENROUTER_KEY_INFO_URL, headers=headers, timeout=8, verify=False)
        
        # 1. Erro HTTP 402: Créditos Esgotados
        if r.status_code == 402:
            print("\n" + "🚨" * 30)
            print("⚠️ [ALERTA CRÍTICO DE SALDO] CRÉDITOS DO OPENROUTER ESGOTADOS (ERRO 402)!")
            print("👉 A IA PRECISA DE RECARGA PARA CONTINUAR GERANDO BRIEFINGS E RESPOSTAS.")
            print("🔗 Adicione créditos em: https://openrouter.ai/settings/keys")
            print("🚨" * 30 + "\n")
            return {
                "status": "ESGOTADO",
                "mensagem": "Créditos esgotados (HTTP 402). Adicione créditos no OpenRouter.",
                "uso_dolares": 0.0
            }

        r.raise_for_status()
        data_key = r.json().get("data", {})
        usage = data_key.get("usage", 0.0)
        limit = data_key.get("limit")

        print(f"✔ [OPENROUTER SALDO OK] Uso Atual da Chave 'wilder': ${usage:.4f} USD")
        return {
            "status": "OK",
            "mensagem": "Saldo do OpenRouter operando normalmente.",
            "uso_dolares": usage
        }

    except Exception as e:
        print(f"[AVISO MONITORAÇÃO SALDO] Não foi possível checar saldo OpenRouter: {e}")
        return {
            "status": "DESCONHECIDO",
            "mensagem": f"Falha de conexão com OpenRouter: {e}",
            "uso_dolares": 0.0
        }

if __name__ == "__main__":
    res = checar_saldo_openrouter()
    print(json.dumps(res, ensure_ascii=False, indent=2))
