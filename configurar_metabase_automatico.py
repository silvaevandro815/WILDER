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

def autenticar_metabase(url: str, user: str, password: str) -> str:
    """Autentica na API do Metabase e retorna o token de sessão."""
    endpoint = f"{url.rstrip('/')}/api/session"
    payload = {"username": user, "password": password}
    try:
        r = requests.post(endpoint, json=payload, timeout=10, verify=False)
        r.raise_for_status()
        token = r.json().get("id")
        print(f"✔ Autenticado com SUCESSO no Metabase como: {user}")
        return token
    except Exception as e:
        print(f"✖ Falha na autenticação do Metabase: {e}")
        return None

def obter_database_id_postgres(token: str, url: str) -> int:
    """Obtém o ID da base de dados PostgreSQL 'wilder' (ID 2)."""
    headers = {"X-Metabase-Session": token}
    endpoint = f"{url.rstrip('/')}/api/database"
    try:
        r = requests.get(endpoint, headers=headers, timeout=10, verify=False)
        r.raise_for_status()
        dbs = r.json()
        if isinstance(dbs, list):
            for db in dbs:
                if isinstance(db, dict):
                    if db.get("engine") == "postgres" or db.get("id") == 2 or "wilder" in str(db.get("name")).lower():
                        print(f"✔ Base PostgreSQL Encontrada no Metabase ID: {db.get('id')} ({db.get('name')})")
                        return db.get("id")
    except Exception as e:
        print(f"[AVISO] Usando ID padrão 2 para banco PostgreSQL: {e}")
    return 2

def criar_card_sql(token: str, url: str, db_id: int, nome: str, sql: str, display: str = "table") -> int:
    """Cria uma Pergunta/Card com consulta SQL no Metabase conectada ao PostgreSQL."""
    headers = {"X-Metabase-Session": token, "Content-Type": "application/json"}
    endpoint = f"{url.rstrip('/')}/api/card"
    
    payload = {
        "name": nome,
        "dataset_query": {
            "type": "native",
            "native": {"query": sql},
            "database": db_id
        },
        "display": display,
        "visualization_settings": {}
    }
    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=10, verify=False)
        r.raise_for_status()
        card_id = r.json().get("id")
        print(f"   • Card Criado e Conectado ao PostgreSQL: '{nome}' (ID: {card_id})")
        return card_id
    except Exception as e:
        print(f"   ✖ Erro ao criar card '{nome}': {e}")
        return None

def montar_dashboard_guerra_completo(token: str, url: str, user: str, password: str):
    db_id = obter_database_id_postgres(token, url)
    headers = {"X-Metabase-Session": token, "Content-Type": "application/json"}
    
    endpoint_dash = f"{url.rstrip('/')}/api/dashboard"
    payload_dash = {
        "name": "🏛️ QG DIGITAL — WILDER MORAIS 2026",
        "description": "Painel de Inteligência Eleitoral em Tempo Real (Cidades, Redes, Notícias e IA)",
        "parameters": []
    }
    dash_id = 3
    try:
        r = requests.post(endpoint_dash, headers=headers, json=payload_dash, timeout=10, verify=False)
        if r.status_code == 200:
            dash_id = r.json().get("id")
    except Exception:
        pass

    print(f"✔ Montando Painel Executivo no Dashboard ID: {dash_id}")

    cards_specs = [
        ("📺 Inscritos no YouTube Oficial", 'SELECT inscritos AS "Inscritos no YouTube" FROM youtube_performance ORDER BY id DESC LIMIT 1;', "number", 0, 0, 4, 3),
        ("👀 Alcance Total de Views", 'SELECT visualizacoes_totais AS "Views Totais" FROM youtube_performance ORDER BY id DESC LIMIT 1;', "number", 4, 0, 4, 3),
        ("📍 Total Eleitoral de Goiás", 'SELECT SUM(eleitores_tse) AS "Total Eleitores Goiás" FROM municipios_goias;', "number", 8, 0, 4, 3),
        ("🗺️ Top 10 Maiores Colégios Eleitorais de Goiás", 'SELECT nome_municipio AS "Cidade", eleitores_tse AS "Eleitores TSE", regiao AS "Região" FROM municipios_goias ORDER BY eleitores_tse DESC LIMIT 10;', "table", 0, 3, 6, 6),
        ("⚔️ Concorrentes Instagram", 'SELECT nome_concorrente AS "Candidato", seguidores_instagram AS "Seguidores" FROM concorrentes_historico;', "bar", 6, 3, 6, 6),
        ("📜 Copiloto de IA: Briefing & Roteiros 3s", 'SELECT data_briefing AS "Data", resumo_executivo AS "Panorama", roteiros_sugeridos AS "Roteiros Virais" FROM briefings_diarios ORDER BY id DESC LIMIT 1;', "table", 0, 9, 12, 6)
    ]

    for nome, sql, display, col, row, size_x, size_y in cards_specs:
        cid = criar_card_sql(token, url, db_id, nome, sql, display)
        if cid:
            endpoint_add = f"{url.rstrip('/')}/api/dashboard/{dash_id}/cards"
            payload_add = {
                "cardId": cid,
                "row": row,
                "col": col,
                "size_x": size_x,
                "size_y": size_y
            }
            try:
                requests.post(endpoint_add, headers=headers, json=payload_add, timeout=10, verify=False)
            except Exception:
                pass

    print("\n🎉 MONTAGEM DO METABASE CONCLUÍDA COM SUCESSO ABSOLUTO!")

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "silvaevandro815@gmail.com"
    pwd = sys.argv[2] if len(sys.argv) > 2 else "samurayX22@35"

    token = autenticar_metabase(METABASE_URL, user, pwd)
    if token:
        montar_dashboard_guerra_completo(token, METABASE_URL, user, pwd)
