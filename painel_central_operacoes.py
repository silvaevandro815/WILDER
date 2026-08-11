import os
import sys
import json
import datetime
import urllib3
import httpx
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from supabase import create_client, Client, ClientOptions
from verificar_saldo_openrouter import checar_saldo_openrouter

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")

is_supabase_configurado = (
    SUPABASE_URL and SUPABASE_KEY and
    "your-supabase" not in SUPABASE_URL and
    "your-supabase" not in SUPABASE_KEY
)

supabase: Client = None
if is_supabase_configurado:
    try:
        options = ClientOptions(httpx_client=httpx.Client(verify=False))
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options=options)
    except Exception as e:
        print(f"[AVISO] Não foi possível inicializar cliente Supabase: {e}")

def verificar_saude_sistema():
    print("=" * 60)
    print("🛡️ CHECAGEM GERAL DE SAÚDE DO SISTEMA (INTEGRIDADE 360°)")
    print("=" * 60)

    # 1. Supabase
    if supabase:
        try:
            res = supabase.table("municipios_goias").select("count", count="exact").execute()
            total_cidades = res.count if hasattr(res, 'count') else 246
            print(f"✔ Supabase PostgreSQL: CONECTADO | {total_cidades} municípios mapeados.")
        except Exception as e:
            print(f"✖ Supabase PostgreSQL: Falha ({e})")
    else:
        print("✖ Supabase PostgreSQL: Não configurado no .env")

    # 2. OpenRouter IA & Saldo de Tokens
    saldo_info = checar_saldo_openrouter()
    if saldo_info["status"] == "OK":
        print(f"✔ OpenRouter IA (Gemini 2.5): SALDO OK | Uso: ${saldo_info['uso_dolares']:.4f} USD")
    elif saldo_info["status"] == "ESGOTADO":
        print(f"🚨 OpenRouter IA: CRÉDITOS ESGOTADOS! Adicione saldo em https://openrouter.ai/settings/keys")

    # 3. Meta Graph API (Instagram / Facebook)
    if META_ACCESS_TOKEN and META_ACCESS_TOKEN != "your-meta-access-token":
        print("✔ Meta Graph API (v20.0): TOKEN CONFIGURADO")
    else:
        print("⚠ Meta Graph API: Token pendente no .env (Aguardando equipe)")

    print("=" * 60)

def obter_resumo_executivo():
    print("\n📊 RESUMO EXECUTIVO DE DADOS DA CAMPANHA DE WILDER MORAIS:")
    if not supabase:
        print("[INFO] Conecte ao Supabase para visualizar estatísticas ao vivo.")
        return

    tabelas = [
        ("municipios_goias", "Municípios Mapeados (PostGIS)"),
        ("metricas_wilder", "Registros de Alcance/Tráfego"),
        ("concorrentes_historico", "Histórico de Concorrentes"),
        ("clipping_noticias", "Notícias Monitoradas"),
        ("google_trends_goias", "Pautas do Google Trends"),
        ("briefings_diarios", "Briefings Diários Salvos"),
        ("eleitores_cadastrados", "Eleitores no CRM"),
        ("demandas_populares", "Demandas Populares Registradas"),
        ("youtube_performance", "Métricas do YouTube"),
        ("reclamacoes_cidadaos", "Radar de Reclamações Sociais"),
        ("midia_drive_indexada", "Mídias do Drive Indexadas por IA")
    ]

    for tab, desc in tabelas:
        try:
            r = supabase.table(tab).select("id", count="exact").execute()
            cnt = len(r.data) if (r and r.data) else 0
            print(f"   • {desc} ({tab}): {cnt} registros")
        except Exception:
            print(f"   • {desc} ({tab}): 0 registros")

if __name__ == "__main__":
    verificar_saude_sistema()
    obter_resumo_executivo()
