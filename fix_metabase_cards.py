import sys
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

METABASE_URL = "https://dadoswilder.evandrosilvagallina.cloud"

r = requests.post(f"{METABASE_URL}/api/session", json={"username": "silvaevandro815@gmail.com", "password": "samurayX22@35"}, verify=False)
token = r.json().get("id")
headers = {"X-Metabase-Session": token, "Content-Type": "application/json"}

# 1. Busca todos os cartões criados
cards = requests.get(f"{METABASE_URL}/api/card", headers=headers, verify=False).json()

print(f"Total de cartoes no Metabase: {len(cards)}")

# 2. Atualiza CADA CARTÃO com database_id = 2 (Base PostgreSQL 'wilder')
for c in cards:
    cid = c.get("id")
    nome = c.get("name", "")
    db_id = c.get("database_id") or c.get("dataset_query", {}).get("database")
    
    # Se for um cartão da nossa campanha
    if any(k in nome for k in ["Concorrentes", "YouTube", "Total Eleitoral", "Top 10", "Copiloto", "Views", "Inscritos"]):
        print(f"-> Atualizando Card ID {cid} ('{nome}')... (DB Atual: {db_id})")
        
        query_sql = c.get("dataset_query", {}).get("native", {}).get("query")
        if not query_sql:
            if "Concorrentes" in nome:
                query_sql = 'SELECT nome_concorrente AS "Candidato", seguidores_instagram AS "Seguidores" FROM concorrentes_historico;'
            elif "Inscritos" in nome:
                query_sql = 'SELECT inscritos AS "Inscritos no YouTube" FROM youtube_performance ORDER BY id DESC LIMIT 1;'
            elif "Views" in nome:
                query_sql = 'SELECT visualizacoes_totais AS "Views Totais" FROM youtube_performance ORDER BY id DESC LIMIT 1;'
            elif "Total Eleitoral" in nome:
                query_sql = 'SELECT SUM(eleitores_tse) AS "Total Eleitores Goiás" FROM municipios_goias;'
            elif "Top 10" in nome:
                query_sql = 'SELECT nome_municipio AS "Cidade", eleitores_tse AS "Eleitores TSE", regiao AS "Região" FROM municipios_goias ORDER BY eleitores_tse DESC LIMIT 10;'
            elif "Copiloto" in nome:
                query_sql = 'SELECT data_briefing AS "Data", resumo_executivo AS "Panorama", roteiros_sugeridos AS "Roteiros Virais" FROM briefings_diarios ORDER BY id DESC LIMIT 1;'

        payload = {
            "name": nome,
            "database_id": 2,
            "dataset_query": {
                "type": "native",
                "native": {"query": query_sql},
                "database": 2
            }
        }
        
        r_up = requests.put(f"{METABASE_URL}/api/card/{cid}", headers=headers, json=payload, verify=False)
        if r_up.status_code == 200:
            print(f"   [OK] Card ID {cid} fixado no PostgreSQL com SUCESSO!")
        else:
            print(f"   [ERRO] Falha ao atualizar Card ID {cid}: {r_up.status_code} - {r_up.text}")

print("\n🎉 CORREÇÃO DOS CARTÕES DO METABASE FINALIZADA!")
