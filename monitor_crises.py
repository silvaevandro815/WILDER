import os
import sys
import json
import smtplib
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERRO] SUPABASE_URL e SUPABASE_KEY devem estar configurados no arquivo .env")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurações do OpenRouter API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "google/gemini-2.5-flash"

# Lista de feeds RSS de portais de Goiás e buscas do Google News
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

def extrair_noticias_rss(feed_info: dict) -> list:
    """Fazem a varredura e extração de notícias de um feed RSS."""
    noticias = []
    url = feed_info["url"]
    portal_nome = feed_info["portal"]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        # Parse para formato RSS 2.0 (channel -> item)
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
                
    except Exception as e:
        print(f"[ERRO] Falha ao ler o feed '{portal_nome}' ({url}): {e}")
        
    return noticias

def analisar_noticia_com_openrouter(titulo: str, descricao: str) -> dict:
    """
    Envia a notícia para a API do OpenRouter (google/gemini-2.5-flash) para classificar o sentimento
    e gerar um resumo de 2 linhas caso seja classificado como ALERTA DE CRISE.
    """
    if not OPENROUTER_API_KEY:
        print("[AVISO] OPENROUTER_API_KEY não informada no .env. Classificação padrão definida como [NEUTRA].")
        return {"sentimento": "[NEUTRA]", "resumo": "Análise automática desativada (sem API key)."}

    prompt_system = (
        "Você é um especialista em inteligência eleitoral e gerenciamento de crises políticas em Goiás.\n"
        "Sua tarefa é analisar matérias jornalísticas referentes ao político/candidato Wilder Morais.\n"
        "Classifique o sentimento da matéria RIGIDAMENTE em uma das 3 opções exatas:\n"
        "- [POSITIVA]\n"
        "- [NEUTRA]\n"
        "- [ALERTA DE CRISE]\n\n"
        "Regras:\n"
        "1. [ALERTA DE CRISE] deve ser atribuído a acusações, denúncias, ataques, investigações, escândalos ou notícias com forte impacto negativo na imagem do candidato.\n"
        "2. Se for [ALERTA DE CRISE], crie obrigatoriamente um resumo de EXATAMENTE 2 LINHAS explicando o ataque ou o motivo da crise.\n"
        "3. Se for [POSITIVA] ou [NEUTRA], forneça um breve resumo de 1 linha.\n"
        "4. Responda ESTRITAMENTE em formato JSON com as chaves 'sentimento' e 'resumo'."
    )

    prompt_user = f"Título: {titulo}\nDescrição/Trecho: {descricao}"

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

    try:
        res = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15)
        res.raise_for_status()
        data = res.json()
        
        content = data["choices"][0]["message"]["content"]
        resultado = json.loads(content)
        
        sentimento = resultado.get("sentimento", "[NEUTRA]").strip()
        resumo = resultado.get("resumo", "").strip()
        
        return {"sentimento": sentimento, "resumo": resumo}

    except Exception as e:
        print(f"[ERRO] Falha ao chamar a API OpenRouter: {e}")
        return {"sentimento": "[NEUTRA]", "resumo": "Erro no processamento da IA."}

def enviar_email_alerta_crise(titulo: str, link: str, portal: str, resumo: str):
    """Envia um e-mail formatado em HTML via SMTP quando uma notícia é identificada como ALERTA DE CRISE."""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM", smtp_user)
    
    # Destinatários do comitê (separados por vírgula no .env)
    recipients_raw = os.getenv("ALERT_EMAIL_RECIPIENTS", "")
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]

    if not smtp_user or not smtp_password or not recipients:
        print("[AVISO] Configurações de SMTP ou destinatários não preenchidos no .env. E-mail de alerta não enviado.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚨 [ALERTA DE CRISE] Notícia relevante: {titulo[:60]}"
    msg["From"] = email_from
    msg["To"] = ", ".join(recipients)

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
    </head>
    <body style="font-family: 'Segoe UI', Helvetica, Arial, sans-serif; color: #222; background-color: #f4f6f8; padding: 20px;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        
        <!-- Header de Alerta -->
        <div style="background-color: #d93025; padding: 20px; color: #ffffff; text-align: center;">
          <h1 style="margin: 0; font-size: 22px; font-weight: bold;">🚨 ALERTA DE CRISE ELEITORAL</h1>
          <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Monitoramento de Mídia - Wilder Morais</p>
        </div>
        
        <!-- Corpo da Mensagem -->
        <div style="padding: 24px;">
          <p style="font-size: 15px; line-height: 1.5; color: #444;">
            Uma nova matéria foi classificada como <strong>[ALERTA DE CRISE]</strong> pelo sistema de inteligência.
          </p>

          <table style="width: 100%; margin-top: 15px; border-collapse: collapse;">
            <tr>
              <td style="padding: 8px 0; font-weight: bold; width: 80px; color: #555;">Título:</td>
              <td style="padding: 8px 0; color: #111;">{titulo}</td>
            </tr>
            <tr>
              <td style="padding: 8px 0; font-weight: bold; color: #555;">Portal:</td>
              <td style="padding: 8px 0; color: #111;">{portal}</td>
            </tr>
            <tr>
              <td style="padding: 8px 0; font-weight: bold; color: #555;">Link:</td>
              <td style="padding: 8px 0;">
                <a href="{link}" target="_blank" style="color: #1a73e8; text-decoration: none; word-break: break-all;">
                  Acessar Matéria Completa &rarr;
                </a>
              </td>
            </tr>
          </table>

          <!-- Caixas de Resumo do Ataque -->
          <div style="margin-top: 20px; background-color: #fff8f6; border-left: 4px solid #d93025; padding: 15px; border-radius: 4px;">
            <h3 style="margin: 0 0 8px 0; font-size: 14px; color: #d93025; text-transform: uppercase;">
              Resumo do Ataque / Crise (IA):
            </h3>
            <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #333; font-weight: 500;">
              {resumo}
            </p>
          </div>
        </div>

        <!-- Rodapé -->
        <div style="background-color: #f8f9fa; padding: 15px; text-align: center; border-top: 1px solid #eee; font-size: 12px; color: #777;">
          Comitê de Inteligência Eleitoral &bull; Sistema de Monitoramento Automático
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
        print(f"[E-MAIL SENT] Alerta disparado com sucesso para os destinatários: {recipients}")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar e-mail via SMTP: {e}")

def noticia_ja_processada(link: str) -> bool:
    """Verifica no Supabase se a notícia com este link já foi registrada anteriormente."""
    try:
        response = supabase.table("clipping_noticias").select("id").eq("link", link).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"[ERRO] Falha ao consultar Supabase (link check): {e}")
        return False

def salvar_noticia_supabase(noticia: dict, analise: dict):
    """Salva a notícia processada e sua análise na tabela 'clipping_noticias' do Supabase."""
    try:
        dados = {
            "titulo": noticia["titulo"],
            "link": noticia["link"],
            "portal": noticia["portal"],
            "sentimento": analise["sentimento"],
            "resumo": analise["resumo"]
        }
        response = supabase.table("clipping_noticias").insert(dados).execute()
        print(f"[SUPABASE] Notícia registrada no banco com ID: {response.data[0]['id']}")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar no Supabase: {e}")

def executar_monitoramento():
    """Fluxo principal de execução do monitoramento de notícias e alertas."""
    print("=" * 60)
    print("🚀 INICIANDO MONITORAMENTO DE NOTÍCIAS E ALERTAS DE CRISE")
    print("=" * 60)

    total_novas = 0
    total_crises = 0

    for feed_info in FEEDS_RSS:
        print(f"\n🔎 Verificando feed: {feed_info['portal']}...")
        noticias = extrair_noticias_rss(feed_info)
        print(f"   Encontradas {len(noticias)} notícias no feed.")

        for noticia in noticias:
            link = noticia["link"]
            
            # Evita reprocessar notícias já salvas no banco de dados
            if noticia_ja_processada(link):
                continue
            
            total_novas += 1
            print(f"\n📰 Processando nova matéria: {noticia['titulo'][:70]}...")
            
            # Análise de inteligência via OpenRouter
            analise = analisar_noticia_com_openrouter(noticia["titulo"], noticia["descricao"])
            print(f"   Classificação: {analise['sentimento']}")
            
            # Se for ALERTA DE CRISE, envia o e-mail via SMTP
            if analise["sentimento"] == "[ALERTA DE CRISE]":
                total_crises += 1
                print(f"   🚨 ALERTA DE CRISE DETECTADO! Disparando e-mail ao comitê...")
                enviar_email_alerta_crise(
                    titulo=noticia["titulo"],
                    link=noticia["link"],
                    portal=noticia["portal"],
                    resumo=analise["resumo"]
                )

            # Salva histórico no Supabase
            salvar_noticia_supabase(noticia, analise)

    print("\n" + "=" * 60)
    print(f"✅ VARREDURA CONCLUÍDA: {total_novas} notícias processadas, {total_crises} alertas de crise disparados.")
    print("=" * 60)

if __name__ == "__main__":
    executar_monitoramento()
