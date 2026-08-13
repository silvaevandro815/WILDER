import sys
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

METABASE_URL = "https://dadoswilder.evandrosilvagallina.cloud"

def atualizar_queries_exatas(user: str, pwd: str):
    r = requests.post(f"{METABASE_URL}/api/session", json={"username": user, "password": pwd}, verify=False)
    token = r.json().get("id")
    headers = {"X-Metabase-Session": token, "Content-Type": "application/json"}
    print(f"✔ Autenticado no Metabase como: {user}")

    # Consultas SQL com o nome EXATO das colunas do PostgreSQL Supabase
    queries_corretas = {
        "Concorrentes": 'SELECT candidato_nome AS "Candidato", seguidores AS "Seguidores Instagram" FROM concorrentes_historico;',
        "Top 10": 'SELECT nome AS "Cidade", eleitores_tse AS "Eleitores TSE" FROM municipios_goias ORDER BY eleitores_tse DESC LIMIT 10;',
        "Inscritos": 'SELECT inscritos AS "Inscritos no YouTube" FROM youtube_performance ORDER BY id DESC LIMIT 1;',
        "Views": 'SELECT visualizacoes_totais AS "Views Totais" FROM youtube_performance ORDER BY id DESC LIMIT 1;',
        "Total Eleitoral": 'SELECT SUM(eleitores_tse) AS "Total Eleitores Goiás" FROM municipios_goias;',
        "Copiloto": 'SELECT data AS "Data", resumo_cenario AS "Panorama", ideias_roteiros AS "Roteiros Virais" FROM briefings_diarios ORDER BY id DESC LIMIT 1;'
    }

    # 1. Busca todos os cartões cadastrados
    cards = requests.get(f"{METABASE_URL}/api/card", headers=headers, verify=False).json()

    for c in cards:
        cid = c.get("id")
        nome = c.get("name", "")
        
        for chave, query_sql in queries_corretas.items():
            if chave.lower() in nome.lower():
                print(f"🛠️ Atualizando SQL do Card ID {cid} ('{nome}')...")
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
                    print(f"   [OK] Card ID {cid} atualizado com as colunas EXATAS!")
                else:
                    print(f"   [ERRO] Falha ao atualizar Card ID {cid}: {r_up.status_code} - {r_up.text}")

    print("\n🎉 CORREÇÃO DE COLUNAS DO METABASE CONCLUÍDA COM SUCESSO!")

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "silvaevandro815@gmail.com"
    pwd = sys.argv[2] if len(sys.argv) > 2 else "samurayX22@35"
    atualizar_queries_exatas(user, pwd)
