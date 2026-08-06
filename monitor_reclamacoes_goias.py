import os
import sys
import re
import json
import datetime
import requests
import urllib3
import httpx
import xml.etree.ElementTree as ET
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from supabase import create_client, Client, ClientOptions

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "google/gemini-2.5-flash"

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

FEEDS_RECLAMACOES = [
    {
        "fonte": "Google News (Césio 137 & Negligência)",
        "url": "https://news.google.com/rss/search?q=C%C3%A9sio+137+Goi%C3%A2nia+governo&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    },
    {
        "fonte": "Google News (Reclamações Saúde Goiás)",
        "url": "https://news.google.com/rss/search?q=hospital+fila+Goi%C3%A1s+reclama%C3%A7%C3%A3o&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    },
    {
        "fonte": "Google News (Transporte & Entorno DF)",
        "url": "https://news.google.com/rss/search?q=ônibus+Entorno+DF+passagem+reclamacao&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    }
]

def criar_sessao_http() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def sanitizar_json_llm(raw_text: str) -> dict:
    if not raw_text:
        return {}
    cleaned = raw_text.strip()
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1)
    else:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            cleaned = cleaned[start:end+1]

    try:
        return json.loads(cleaned)
    except Exception:
        return {}

def extrair_reclamacoes_rss(feed_info: dict) -> list:
    reclamacoes = []
    url = feed_info["url"]
    fonte_nome = feed_info["fonte"]
    session = criar_sessao_http()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=12, verify=False)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        for item in root.findall(".//item"):
            titulo = item.findtext("title", default="").strip()
            link = item.findtext("link", default="").strip()
            descricao = item.findtext("description", default="").strip()
            
            if titulo and link:
                reclamacoes.append({
                    "titulo": titulo,
                    "link": link,
                    "descricao": descricao,
                    "fonte": fonte_nome
                })
    except ET.ParseError:
        print(f"[AVISO] O feed '{fonte_nome}' não retornou XML válido.")
    except Exception as e:
        print(f"[ERRO] Falha ao ler o feed de reclamações '{fonte_nome}': {e}")
        
    return reclamacoes

def analisar_reclamacao_com_ia(titulo: str, descricao: str) -> dict:
    """
    Analisa a reclamação do cidadão usando a IA Gemini 2.5 para extrair:
    - Cidade e Região afetada
    - Pauta-Chave (ex: Césio-137 / Negligência Histórica, Saúde, Transporte, Asfalto)
    - Oportunidade Estratégica de Posicionamento para Wilder Morais
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return {
            "cidade": "Goiânia",
            "pauta_chave": "Negligência Histórica / Césio-137",
            "impacto_politico": "ALTO",
            "oportunidade_criativo": "Gravar vídeo com vítimas esquecidas ou profissionais afetados defendendo amparo permanente."
        }

    prompt_system = (
        "Você é o Diretor de Social Listening e Inteligência da campanha de Wilder Morais em Goiás.\n"
        "Analise esta notícia ou reclamação popular de cidadãos goianos.\n"
        "Identifique a Cidade, a Pauta-Chave (ex: Césio-137, Saúde, Transporte, Estradas) e proponha uma Oportunidade de Criativo para o candidato Wilder Morais.\n"
        "Responda estritamente em formato JSON com as chaves: 'cidade', 'pauta_chave', 'impacto_politico' (ALTO, MÉDIO, BAIXO) e 'oportunidade_criativo'."
    )
    prompt_user = f"Título: {titulo}\nDescrição: {descricao}"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }

    session = criar_sessao_http()
    try:
        res = session.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15, verify=False)
        res.raise_for_status()
        data = res.json()
        content = data["choices"][0]["message"]["content"]
        return sanitizar_json_llm(content)
    except Exception as e:
        print(f"[AVISO] Falha ao analisar reclamação via IA: {e}")
        return {
            "cidade": "Goiânia",
            "pauta_chave": "Geral",
            "impacto_politico": "MÉDIO",
            "oportunidade_criativo": "Posicionamento prático de gestão."
        }

def executar_radar_reclamacoes():
    print("\n" + "=" * 60)
    print("📡 RADAR DE SOCIAL LISTENING & RECLAMAÇÕES POPULARES (GOIÁS)")
    print("=" * 60)

    reclamacoes_banco = []
    
    for feed_info in FEEDS_RECLAMACOES:
        print(f"\n🔎 Monitorando canal: {feed_info['fonte']}...")
        itens = extrair_reclamacoes_rss(feed_info)
        print(f"   Encontradas {len(itens)} reclamações/matérias em potencial.")

        for item in itens[:3]:
            analise = analisar_reclamacao_com_ia(item["titulo"], item["descricao"])
            
            reclamacao_obj = {
                "cidade": analise.get("cidade", "Goiânia"),
                "pauta_chave": analise.get("pauta_chave", "Geral"),
                "reclamacao_texto": item["titulo"],
                "fonte": item["fonte"],
                "impacto_politico": analise.get("impacto_politico", "MÉDIO"),
                "oportunidade_criativo": analise.get("oportunidade_criativo", "")
            }
            reclamacoes_banco.append(reclamacao_obj)
            print(f"   📌 [{reclamacao_obj['cidade']}] Pauta: {reclamacao_obj['pauta_chave']} (Impacto: {reclamacao_obj['impacto_politico']})")

    # Exemplo específico de pauta histórica solicitada (Césio-137 & Série Netflix)
    reclamacoes_banco.append({
        "cidade": "Goiânia",
        "pauta_chave": "Césio-137 / Negligência Histórica",
        "reclamacao_texto": "Série da Netflix reacende debate sobre abandono das vítimas e profissionais do Césio-137 em Goiânia",
        "fonte": "Redes Sociais / Trend Netflix",
        "impacto_politico": "ALTO",
        "oportunidade_criativo": "Wilder grava vídeo com associação das vítimas defendendo indenização justa e centro de assistência médica permanente."
    })

    print(f"\n[OK] Radar capturou {len(reclamacoes_banco)} reclamações e pautas quentes.")

    if supabase:
        try:
            supabase.table("reclamacoes_cidadaos").insert(reclamacoes_banco).execute()
            print(f"[OK] Supabase: Registros salvos em 'reclamacoes_cidadaos'!")
        except Exception as e:
            print(f"[AVISO] Erro ao salvar reclamações no Supabase: {e}")

    print("\n" + "=" * 60)
    print("🎉 RADAR DE RECLAMAÇÕES CONCLUÍDO COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    executar_radar_reclamacoes()
