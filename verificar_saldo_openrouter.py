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
OPENROUTER_CREDITS_URL = "https://openrouter.ai/api/v1/credits"

def checar_saldo_openrouter() -> dict:
    """
    Verifica o uso de tokens e créditos remanescentes na conta do OpenRouter.
    Emite alerta visual e logs de aviso caso os créditos estejam acabando ou esgotados.
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return {
            "status": "ALERTA",
            "mensagem": "Chave do OpenRouter não configurada no .env",
            "uso_dolares": 0.0,
            "creditos_restantes": 0.0
        }

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}

    try:
        r = requests.get(OPENROUTER_KEY_INFO_URL, headers=headers, timeout=8, verify=False)
        
        if r.status_code == 402:
            print("\n" + "🚨" * 30)
            print("⚠️ [ALERTA CRÍTICO DE SALDO] CRÉDITOS DO OPENROUTER ESGOTADOS (ERRO 402)!")
            print("👉 A IA PRECISA DE CRÉDITOS PARA CONTINUAR GERANDO BRIEFINGS E RESPOSTAS.")
            print("🔗 Adicione créditos em: https://openrouter.ai/settings/keys")
            print("🚨" * 30 + "\n")
            return {
                "status": "ESGOTADO",
                "mensagem": "Créditos esgotados (HTTP 402). Adicione créditos no OpenRouter.",
                "uso_dolares": 0.0,
                "creditos_restantes": 0.0
            }

        r.raise_for_status()
        data_key = r.json().get("data", {})
        usage = data_key.get("usage", 0.0)
        limit = data_key.get("limit")

        # Tenta buscar os créditos totais se disponível
        r_cred = requests.get(OPENROUTER_CREDITS_URL, headers=headers, timeout=8, verify=False)
        credits_total = 0.0
        if r_cred.status_code == 200:
            c_data = r_cred.json().get("data", {})
            credits_total = c_data.get("total_credits", 0.0)

        print(f"✔ [OPENROUTER SALDO OK] Uso Total Acumulado: ${usage:.4f} USD | Créditos Adicionados: ${credits_total:.2f} USD")
        return {
            "status": "OK",
            "mensagem": "Saldo do OpenRouter operando normalmente.",
            "uso_dolares": usage,
            "creditos_restantes": credits_total
        }

    except Exception as e:
        print(f"[AVISO MONITORAÇÃO SALDO] Não foi possível checar saldo OpenRouter: {e}")
        return {
            "status": "DESCONHECIDO",
            "mensagem": f"Falha de conexão com OpenRouter: {e}",
            "uso_dolares": 0.0,
            "creditos_restantes": 0.0
        }

if __name__ == "__main__":
    res = checar_saldo_openrouter()
    print(json.dumps(res, ensure_ascii=False, indent=2))
