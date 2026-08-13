import os
import sys
import json
import httpx
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

from supabase import create_client, Client, ClientOptions

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

options = ClientOptions(httpx_client=httpx.Client(verify=False))
supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options=options)

print("=== CANDIDATOS EM concorrentes_historico ===")
res = supabase.table("concorrentes_historico").select("*").execute()
if res.data:
    for row in res.data:
        print(row)
else:
    print("Nenhum dado retornado.")
