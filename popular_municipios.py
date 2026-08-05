import os
import sys
import requests
import urllib3
from dotenv import load_dotenv
from supabase import create_client, Client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

IBGE_GOIAS_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/52/municipios"

PREFERENCIA_ELEITORADO = {
    "Goiânia": 1030000,
    "Aparecida de Goiânia": 345000,
    "Anápolis": 292000,
    "Rio Verde": 142000,
    "Luziânia": 135000,
    "Águas Lindas de Goiás": 115000,
    "Valparaíso de Goiás": 102000,
    "Trindade": 98000,
    "Formosa": 82000,
    "Itumbiara": 76000,
    "Jataí": 74000,
    "Senador Canedo": 71000,
    "Catalão": 69000,
    "Novo Gama": 65000,
    "Caldas Novas": 62000
}

def carregar_todos_municipios_goias():
    print("=" * 60)
    print("INICIANDO CARGA DAS 246 CIDADES DE GOIAS (API IBGE)")
    print("=" * 60)

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(IBGE_GOIAS_URL, headers=headers, timeout=15, verify=False)
        res.raise_for_status()
        cidades_ibge = res.json()
        
        print(f"[OK] API do IBGE consultada! Total de municipios em Goias: {len(cidades_ibge)}")
        exemplo = [c['nome'] for c in cidades_ibge[:5]]
        print(f"[INFO] Exemplo de municipios extraidos: {exemplo}...")

        is_supabase_configurado = (
            SUPABASE_URL and SUPABASE_KEY and
            "your-supabase" not in SUPABASE_URL and
            "your-supabase" not in SUPABASE_KEY
        )

        if not is_supabase_configurado:
            print("\n[INFO] As credenciais reais do Supabase ainda nao foram preenchidas no arquivo .env.")
            print("[OK] A extracao das 246 cidades do IBGE funcionou perfeitamente.")
            print("[DICA] Quando voce colocar sua SUPABASE_URL e SUPABASE_KEY no .env, este script salvara automaticamente no banco!")
            return

        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        cidades_existentes_res = supabase.table("municipios_goias").select("nome").execute()
        nomes_existentes = {c["nome"].lower() for c in cidades_existentes_res.data} if cidades_existentes_res.data else set()

        novos_municipios = []
        for cid in cidades_ibge:
            nome_cidade = cid["nome"].strip()
            if nome_cidade.lower() not in nomes_existentes:
                eleitores = PREFERENCIA_ELEITORADO.get(nome_cidade, 12500)
                novos_municipios.append({
                    "nome": nome_cidade,
                    "eleitores_tse": eleitores
                })

        if novos_municipios:
            print(f"[BD] Cadastrando {len(novos_municipios)} novas cidades no Supabase...")
            tamanho_lote = 50
            for i in range(0, len(novos_municipios), tamanho_lote):
                lote = novos_municipios[i:i + tamanho_lote]
                supabase.table("municipios_goias").insert(lote).execute()
            print(f"[OK] Todas as {len(novos_municipios)} cidades foram registradas com sucesso no Supabase!")
        else:
            print("[INFO] Todos os municipios de Goias ja se encontram cadastrados na tabela 'municipios_goias'.")

    except Exception as e:
        print(f"[ERRO] Erro ao carregar cidades do IBGE: {e}")

if __name__ == "__main__":
    carregar_todos_municipios_goias()
