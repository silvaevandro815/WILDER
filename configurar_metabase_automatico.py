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

METABASE_URL = os.getenv("METABASE_URL", "https://dadoswilder.evandrosilvagallina.cloud")
METABASE_USER = os.getenv("METABASE_USER")
METABASE_PASSWORD = os.getenv("METABASE_PASSWORD")

def autenticar_metabase(url: str, user: str, password: str) -> str:
    """Autentica na API do Metabase e retorna o token de sessão."""
    endpoint = f"{url.rstrip('/')}/api/session"
    payload = {"username": user, "password": password}
    try:
        r = requests.post(endpoint, json=payload, timeout=10, verify=False)
        r.raise_for_status()
        return r.json().get("id")
    except Exception as e:
        print(f"[ERRO METABASE API] Falha ao autenticar: {e}")
        return None

def criar_dashboard_guerra(token: str, url: str) -> bool:
    """Cria o Dashboard 'Sala de Guerra — Wilder Morais 2026' via REST API."""
    headers = {"X-Metabase-Session": token, "Content-Type": "application/json"}
    endpoint = f"{url.rstrip('/')}/api/dashboard"
    
    payload = {
        "name": "🏛️ Sala de Guerra — Wilder Morais 2026",
        "description": "Central de Inteligência Eleitoral em Tempo Real para a Campanha ao Governo de Goiás.",
        "parameters": []
    }
    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=10, verify=False)
        r.raise_for_status()
        dash_id = r.json().get("id")
        print(f"✔ Dashboard criado com sucesso no Metabase! ID: {dash_id}")
        return True
    except Exception as e:
        print(f"[ERRO METABASE API] Falha ao criar Dashboard: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 2:
        METABASE_USER = sys.argv[1]
        METABASE_PASSWORD = sys.argv[2]

    if not METABASE_USER or not METABASE_PASSWORD:
        print("⚠ Insira as credenciais do Metabase (E-mail e Senha) para criação automática via API.")
        sys.exit(0)

    token = autenticar_metabase(METABASE_URL, METABASE_USER, METABASE_PASSWORD)
    if token:
        criar_dashboard_guerra(token, METABASE_URL)
