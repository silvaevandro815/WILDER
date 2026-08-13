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

print("=== COLUNAS DE municipios_goias ===")
res_mun = supabase.table("municipios_goias").select("*").limit(1).execute()
if res_mun.data:
    print("Colunas:", list(res_mun.data[0].keys()))
    print("Exemplo:", res_mun.data[0])

print("\n=== COLUNAS DE concorrentes_historico ===")
res_conc = supabase.table("concorrentes_historico").select("*").limit(1).execute()
if res_conc.data:
    print("Colunas:", list(res_conc.data[0].keys()))
    print("Exemplo:", res_conc.data[0])

print("\n=== COLUNAS DE youtube_performance ===")
res_yt = supabase.table("youtube_performance").select("*").limit(1).execute()
if res_yt.data:
    print("Colunas:", list(res_yt.data[0].keys()))

print("\n=== COLUNAS DE briefings_diarios ===")
res_bd = supabase.table("briefings_diarios").select("*").limit(1).execute()
if res_bd.data:
    print("Colunas:", list(res_bd.data[0].keys()))
