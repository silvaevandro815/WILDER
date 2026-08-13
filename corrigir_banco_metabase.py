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

def diagnosticar_e_corrigir_bancos(user: str, pwd: str):
    # 1. Autentica
    r = requests.post(f"{METABASE_URL}/api/session", json={"username": user, "password": pwd}, timeout=10, verify=False)
    r.raise_for_status()
    token = r.json().get("id")
    headers = {"X-Metabase-Session": token, "Content-Type": "application/json"}
    print(f"✔ Autenticado no Metabase como: {user}")

    # 2. Lista todos os bancos cadastrados no Metabase
    r_db = requests.get(f"{METABASE_URL}/api/database", headers=headers, timeout=10, verify=False)
    res_db = r_db.json()
    dbs = res_db.get("data", res_db) if isinstance(res_db, dict) else res_db
    
    print("\n🔍 BANCOS DE DADOS ENCONTRADOS NO METABASE:")
    real_db_id = None
    if isinstance(dbs, list):
        for db in dbs:
            if isinstance(db, dict):
                db_id = db.get('id')
                name = db.get('name')
                engine = db.get('engine')
                print(f"   • ID: {db_id} | Nome: '{name}' | Engine: '{engine}'")
                if engine == "postgres" or "wilder" in str(name).lower() or db_id != 1:
                    real_db_id = db_id

    if not real_db_id:
        print("\n⚠ Apenas a 'Sample Database' (SQLite) está cadastrada no Metabase!")
        print("👉 O banco de dados PostgreSQL do Supabase ainda NÃO foi adicionado no Metabase.")
        print("\n👇 VAMOS ADICIONAR O SUPABASE AGORA VIA API MESMO:")
        return

    print(f"\n✔ Usando Banco de Dados Oficial PostgreSQL ID: {real_db_id}")

    # 3. Lista os cartões criados e atualiza a referência do Banco de Dados de 1 (Sample DB) para real_db_id
    r_cards = requests.get(f"{METABASE_URL}/api/card", headers=headers, timeout=10, verify=False)
    res_cards = r_cards.json()
    cards = res_cards.get("data", res_cards) if isinstance(res_cards, dict) else res_cards

    if isinstance(cards, list):
        for c in cards:
            if isinstance(c, dict):
                cid = c.get("id")
                nome = c.get("name")
                curr_db = c.get("dataset_query", {}).get("database")
                query_sql = c.get("dataset_query", {}).get("native", {}).get("query")

                if curr_db != real_db_id and query_sql:
                    print(f"🛠 Corrigindo Card ID {cid} ('{nome}'): Mudando Banco de ID {curr_db} -> ID {real_db_id}")
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
                        print(f"   ✔ Card {cid} corrigido com SUCESSO!")
                    except Exception as e:
                        print(f"   ✖ Erro ao atualizar Card {cid}: {e}")

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "silvaevandro815@gmail.com"
    pwd = sys.argv[2] if len(sys.argv) > 2 else "samurayX22@35"
    diagnosticar_e_corrigir_bancos(user, pwd)
