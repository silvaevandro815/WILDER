import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

METABASE_URL = "https://dadoswilder.evandrosilvagallina.cloud"

r = requests.post(f"{METABASE_URL}/api/session", json={"username": "silvaevandro815@gmail.com", "password": "samurayX22@35"}, verify=False)
token = r.json().get("id")
headers = {"X-Metabase-Session": token}

print("=== DATABASES ===")
dbs = requests.get(f"{METABASE_URL}/api/database", headers=headers, verify=False).json()
print(json.dumps(dbs, indent=2))

print("=== CARDS ===")
cards = requests.get(f"{METABASE_URL}/api/card", headers=headers, verify=False).json()
for c in cards:
    print(f"Card ID: {c.get('id')} | Name: {c.get('name')} | Database ID: {c.get('database_id')} | dataset_query.database: {c.get('dataset_query', {}).get('database')}")
