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

def vincular_cards_ao_banco_postgres(user: str, pwd: str):
    r = requests.post(f"{METABASE_URL}/api/session", json={"username": user, "password": pwd}, timeout=10, verify=False)
    r.raise_for_status()
    token = r.json().get("id")
    headers = {"X-Metabase-Session": token, "Content-Type": "application/json"}
    print(f"✔ Autenticado no Metabase como: {user}")

    # Database ID 2 é a base PostgreSQL 'wilder'
    real_db_id = 2

    # Lista todos os cartões cadastrados
    r_cards = requests.get(f"{METABASE_URL}/api/card", headers=headers, timeout=10, verify=False)
    cards = r_cards.json()

    print(f"\n🔄 Vinculando todos os cartões do Metabase à base de dados PostgreSQL 'wilder' (ID: {real_db_id})...")

    for c in cards:
        cid = c.get("id")
        nome = c.get("name")
        dataset_query = c.get("dataset_query", {})
        query_sql = dataset_query.get("native", {}).get("query")

        if query_sql:
            payload_update = {
                "dataset_query": {
                    "type": "native",
                    "native": {"query": query_sql},
                    "database": real_db_id
                }
            }
            try:
                r_up = requests.put(f"{METABASE_URL}/api/card/{cid}", headers=headers, json=payload_update, timeout=10, verify=False)
                r_up.raise_for_status()
                print(f"   ✔ Card ID {cid} ('{nome}') conectado ao PostgreSQL com SUCESSO!")
            except Exception as e:
                print(f"   ✖ Erro ao conectar Card ID {cid}: {e}")

    print("\n🎉 TODOS OS CARTÕES FORAM VINCULADOS AO BANCO POSTGRESQL DA CAMPANHA!")

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "silvaevandro815@gmail.com"
    pwd = sys.argv[2] if len(sys.argv) > 2 else "samurayX22@35"
    vincular_cards_ao_banco_postgres(user, pwd)
