import os
import sys
import re
import json
import smtplib
import requests
import urllib3
import xml.etree.ElementTree as ET
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from supabase import create_client, Client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

is_supabase_configurado = (
    SUPABASE_URL and SUPABASE_KEY and
    "your-supabase" not in SUPABASE_URL and
    "your-supabase" not in SUPABASE_KEY
)

supabase: Client = None
if is_supabase_configurado:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[AVISO] Não foi possível inicializar cliente Supabase: {e}")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "google/gemini-2.5-flash"

FEEDS_RSS = [
    {
        "portal": "Google News (Wilder Morais)",
        "url": "https://news.google.com/rss/search?q=Wilder+Morais&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    },
    {
        "portal": "Jornal Opção",
        "url": "https://www.jornalopcao.com.br/feed/"
    },
    {
        "portal": "Mais Goiás",
        "url": "https://www.maisgoias.com.br/feed/"
    }
]

def criar_sessao_http() -> requests.Session:
    """Cria uma sessão HTTP com suporte a retentativas automáticas."""
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def sanitizar_json_llm(raw_text: str) -> dict:
    """Extrai e sanitiza JSON retornado pelo modelo de linguagem (LLM), mesmo que envolvido por markdown."""
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

def extrair_noticias_rss(feed_info: dict) -> list:
    """Extrai com segurança as notícias de um feed RSS, tratando erros de XML ou HTTP."""
    noticias = []
    url = feed_info["url"]
    portal_nome = feed_info["portal"]
    session = criar_sessao_http()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
                noticias.append({
                    "titulo": titulo,
                    "link": link,
                    "descricao": descricao,
                    "portal": portal_nome
                })
    except ET.ParseError:
        print(f"[AVISO] O feed '{portal_nome}' não retornou XML válido (possível bloqueio/HTML).")
    except Exception as e:
        print(f"[ERRO] Falha ao ler o feed '{portal_nome}': {e}")
        
    return noticias

def analisar_noticia_com_openrouter(titulo: str, descricao: str) -> dict:
    """Envia a notícia para a API do OpenRouter para classificação de sentimento e geração de resumo de crise."""
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return {"sentimento": "[NEUTRA]", "resumo": "Análise automática desativada (sem API Key)."}

    prompt_system = (
        "Você é um especialista em inteligência eleitoral e gerenciamento de crises políticas em Goiás.\n"
        "Analise a matéria sobre o candidato Wilder Morais.\n"
        "Classifique o sentimento RIGIDAMENTE em: [POSITIVA], [NEUTRA] ou [ALERTA DE CRISE].\n"
        "Se for [ALERTA DE CRISE], gere um resumo de 2 linhas explicando o ataque.\n"
        "Responda estritamente em formato JSON com as chaves 'sentimento' e 'resumo'."
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
        "temperature": 0.2
    }

    session = criar_sessao_http()
    try:
        res = session.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15, verify=False)
        res.raise_for_status()
        data = res.json()
        content = data["choices"][0]["message"]["content"]
        resultado = sanitizar_json_llm(content)
        
        sentimento = resultado.get("sentimento", "[NEUTRA]").strip()
        resumo = resultado.get("resumo", "").strip()
        return {"sentimento": sentimento, "resumo": resumo}

    except Exception as e:
        print(f"[AVISO] Falha ao processar notícia via OpenRouter: {e}")
        return {"sentimento": "[NEUTRA]", "resumo": "Erro no processamento de IA."}

def enviar_email_alerta_crise(titulo: str, link: str, portal: str, resumo: str):
    """Envia um e-mail formatado em HTML via SMTP caso uma notícia seja classificada como [ALERTA DE CRISE]."""
    emails_raw = os.getenv("EMAILS_DESTINATARIOS")
    if not emails_raw or not emails_raw.strip():
        print("[ERRO] A variável 'EMAILS_DESTINATARIOS' não está configurada no .env. E-mail de crise abortado.")
        return

    recipients = [e.strip() for e in emails_raw.split(",") if re.match(r"[^@]+@[^@]+\.[^@]+", e.strip())]
    if not recipients:
        print("[ERRO] Nenhum e-mail válido encontrado em EMAILS_DESTINATARIOS.")
        return

    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    if not smtp_user or not smtp_password or smtp_user == "seu_email@gmail.com":
        print("[AVISO] Credenciais SMTP ausentes ou inválidas no .env. E-mail não enviado.")
        return

    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    email_from = os.getenv("EMAIL_FROM", smtp_user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚨 [ALERTA DE CRISE] Notícia relevante: {titulo[:60]}"
    msg["From"] = email_from
    msg["To"] = ", ".join(recipients)

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #222; background-color: #f4f6f8; padding: 20px;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <div style="background-color: #d93025; padding: 20px; color: #ffffff; text-align: center;">
          <h1 style="margin: 0; font-size: 22px;">🚨 ALERTA DE CRISE ELEITORAL</h1>
          <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Monitoramento de Mídia - Wilder Morais</p>
        </div>
        <div style="padding: 24px;">
          <p style="font-size: 15px; color: #444;">Uma nova matéria foi classificada como <strong>[ALERTA DE CRISE]</strong>.</p>
          <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <tr><td style="font-weight: bold; width: 80px;">Título:</td><td>{titulo}</td></tr>
            <tr><td style="font-weight: bold;">Portal:</td><td>{portal}</td></tr>
            <tr><td style="font-weight: bold;">Link:</td><td><a href="{link}" target="_blank">{link}</a></td></tr>
          </table>
          <div style="margin-top: 20px; background-color: #fff8f6; border-left: 4px solid #d93025; padding: 15px; border-radius: 4px;">
            <h3 style="margin: 0 0 8px 0; color: #d93025; font-size: 14px;">RESUMO DO ATAQUE (IA):</h3>
            <p style="margin: 0; font-size: 14px; color: #333;">{resumo}</p>
          </div>
        </div>
        <div style="background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #777;">
          Comitê de Inteligência Eleitoral &bull; Monitoramento Automático
        </div>
      </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(email_from, recipients, msg.as_string())
        print(f"[OK] E-mail de alerta enviado para {len(recipients)} destinatários.")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar e-mail via SMTP: {e}")

def noticia_ja_processada(link: str) -> bool:
    if not supabase:
        return False
    try:
        res = supabase.table("clipping_noticias").select("id").eq("link", link).execute()
        return bool(res and res.data and len(res.data) > 0)
    except Exception:
        return False

def salvar_noticia_supabase(noticia: dict, analise: dict):
    if not supabase:
        return
    try:
        dados = {
            "titulo": noticia["titulo"],
            "link": noticia["link"],
            "portal": noticia["portal"],
            "sentimento": analise["sentimento"],
            "resumo": analise["resumo"]
        }
        supabase.table("clipping_noticias").insert(dados).execute()
        print(f"[OK] Notícia registrada no Supabase.")
    except Exception as e:
        print(f"[AVISO] Erro ao salvar notícia no Supabase (possível duplicata): {e}")

def executar_monitoramento():
    print("=" * 60)
    print("🚀 INICIANDO MONITORAMENTO DE NOTÍCIAS E ALERTA DE CRISE")
    print("=" * 60)

    total_novas = 0
    total_crises = 0

    for feed_info in FEEDS_RSS:
        print(f"\n🔎 Verificando feed: {feed_info['portal']}...")
        noticias = extrair_noticias_rss(feed_info)
        print(f"   Encontradas {len(noticias)} notícias no feed.")

        for noticia in noticias:
            if noticia_ja_processada(noticia["link"]):
                continue
            
            total_novas += 1
            print(f"\n📰 Processando nova matéria: {noticia['titulo'][:70]}...")
            analise = analisar_noticia_com_openrouter(noticia["titulo"], noticia["descricao"])
            print(f"   Classificação: {analise['sentimento']}")
            
            if analise["sentimento"] == "[ALERTA DE CRISE]":
                total_crises += 1
                enviar_email_alerta_crise(noticia["titulo"], noticia["link"], noticia["portal"], analise["resumo"])

            salvar_noticia_supabase(noticia, analise)

    print("\n" + "=" * 60)
    print(f"✅ VARREDURA CONCLUÍDA: {total_novas} novas notícias, {total_crises} crises registradas.")
    print("=" * 60)

if __name__ == "__main__":
    executar_monitoramento()
