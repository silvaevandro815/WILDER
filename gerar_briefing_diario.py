import os
import sys
import re
import json
import datetime
import requests
import urllib3
import smtplib
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
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[AVISO] Não foi possível inicializar cliente Supabase: {e}")

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

def obter_noticias_recentes() -> list:
    if not supabase:
        return [
            {"titulo": "Wilder Morais defende novos investimentos em infraestrutura para o Entorno do DF", "portal": "Jornal Opção", "sentimento": "[POSITIVA]"},
            {"titulo": "Governo de Goiás anuncia novas pautas de desenvolvimento regional", "portal": "Mais Goiás", "sentimento": "[NEUTRA]"}
        ]
    try:
        res = supabase.table("clipping_noticias").select("titulo, portal, sentimento, resumo").order("data", desc=True).limit(5).execute()
        return res.data if (res and res.data) else []
    except Exception as e:
        print(f"[AVISO] Erro ao buscar notícias no Supabase: {e}")
        return []

def obter_trends_recentes() -> list:
    if not supabase:
        return [
            {"termo": "Wilder Morais", "interesse_relativo": 45, "regiao_mais_buscada": "Sudoeste Goiano"},
            {"termo": "agronegócio goiás", "interesse_relativo": 85, "regiao_mais_buscada": "Rio Verde"}
        ]
    try:
        res = supabase.table("google_trends_goias").select("termo, interesse_relativo, regiao_mais_buscada").order("data", desc=True).limit(5).execute()
        return res.data if (res and res.data) else []
    except Exception as e:
        print(f"[AVISO] Erro ao buscar Google Trends no Supabase: {e}")
        return []

def gerar_briefing_ia(noticias: list, trends: list) -> dict:
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return {
            "resumo_cenario": "Cenário eleitoral em Goiás focado no agronegócio e desenvolvimento regional no Entorno do DF.",
            "pautas_google_trends": "Termos mais buscados: Agronegócio, Infraestrutura e Educação.",
            "alertas_concorrentes": "Daniel Vilela mantém presença institucional; Marconi Perillo busca recall no interior.",
            "ideias_roteiros": """
1. ROTEIRO 1: "Senador dos Livros"
- GANCHO (0-3s): "Você sabia que um livro no lugar certo pode mudar o futuro de um jovem de Goiás?"
- DESENVOLVIMENTO (3-24s): Wilder mostra projeto de incentivo à leitura e educação profissionalizante nas escolas do interior.
- CTA (24-30s): "Comenta 'EDUCAÇÃO' para receber o plano completo na sua DM."

2. ROTEIRO 2: "Engenheiro de Obras"
- GANCHO (0-3s): "Como engenheiro em 3 continentes, aprendi que obra boa é obra entregue no prazo!"
- DESENVOLVIMENTO (3-24s): Comparativo entre a burocracia estatal e a eficiência de gestão de projetos de infraestrutura.
- CTA (24-30s): "Siga o perfil para acompanhar as propostas de transporte e estradas em Goiás."
"""
        }

    prompt_system = (
        "Você é o Copiloto Estratégico de Inteligência e Growth do Social Media da campanha de Wilder Morais para Governador de Goiás.\n"
        "Gere o Briefing Diário do Social Media para maximizar a produtividade e retenção.\n"
        "Responda ESTRITAMENTE em formato JSON com as chaves: 'resumo_cenario', 'pautas_google_trends', 'alertas_concorrentes', 'ideias_roteiros'."
    )
    prompt_user = f"Notícias do Dia: {json.dumps(noticias, ensure_ascii=False)}\nGoogle Trends GO: {json.dumps(trends, ensure_ascii=False)}"

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "system", "content": prompt_system}, {"role": "user", "content": prompt_user}],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }

    session = criar_sessao_http()
    try:
        res = session.post(OPENROUTER_URL, headers=headers, json=payload, timeout=20, verify=False)
        res.raise_for_status()
        data = res.json()
        content = data["choices"][0]["message"]["content"]
        return sanitizar_json_llm(content)
    except Exception as e:
        print(f"[ERRO] Falha na API OpenRouter (briefing): {e}")
        return {
            "resumo_cenario": "Cenário estável.",
            "pautas_google_trends": "Goiás",
            "alertas_concorrentes": "Nenhum alerta.",
            "ideias_roteiros": "Consulte os modelos de roteiro no dossiê estratégico."
        }

def enviar_briefing_email(briefing: dict):
    emails_raw = os.getenv("EMAILS_DESTINATARIOS")
    if not emails_raw or not emails_raw.strip():
        return

    recipients = [e.strip() for e in emails_raw.split(",") if re.match(r"[^@]+@[^@]+\.[^@]+", e.strip())]
    if not recipients:
        return

    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    if not smtp_user or not smtp_password or smtp_user == "seu_email@gmail.com":
        return

    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    hoje_str = datetime.date.today().strftime("%d/%m/%Y")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"☀️ [BRIEFING DIÁRIO] Estratégia & Roteiros Social Media - {hoje_str}"
    msg["From"] = os.getenv("EMAIL_FROM", smtp_user)
    msg["To"] = ", ".join(recipients)

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #222; background-color: #f4f6f8; padding: 20px;">
      <div style="max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <div style="background-color: #1a73e8; padding: 20px; color: #ffffff; text-align: center;">
          <h1 style="margin: 0; font-size: 22px;">☀️ BRIEFING DIÁRIO DE SOCIAL MEDIA</h1>
          <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Campanha Wilder Morais &bull; {hoje_str}</p>
        </div>
        <div style="padding: 24px;">
          <div style="background-color: #e8f0fe; border-left: 4px solid #1a73e8; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
            <h3 style="margin: 0 0 5px 0; color: #1a73e8; font-size: 15px;">📰 Panorama do Dia em Goiás:</h3>
            <p style="margin: 0; font-size: 14px; color: #333;">{briefing.get('resumo_cenario', '')}</p>
          </div>
          <div style="background-color: #f8f9fa; border-left: 4px solid #34a853; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
            <h3 style="margin: 0 0 5px 0; color: #278038; font-size: 15px;">📈 O que o Eleitor Goiano está buscando no Google:</h3>
            <p style="margin: 0; font-size: 14px; color: #333;">{briefing.get('pautas_google_trends', '')}</p>
          </div>
          <div style="background-color: #fff8f6; border-left: 4px solid #ea4335; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
            <h3 style="margin: 0 0 10px 0; color: #ea4335; font-size: 16px;">🎬 3 Sugestões de Roteiros Virais para Hoje (30s):</h3>
            <div style="font-size: 14px; line-height: 1.6; color: #222; white-space: pre-line;">
              {briefing.get('ideias_roteiros', '')}
            </div>
          </div>
        </div>
        <div style="background-color: #f1f3f4; padding: 15px; text-align: center; font-size: 12px; color: #777;">
          Copiloto Estratégico de Inteligência Eleitoral &bull; Wilder Morais 2026
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
            server.sendmail(msg["From"], recipients, msg.as_string())
        print(f"[OK] Briefing enviado para {len(recipients)} destinatários.")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar e-mail de briefing: {e}")

def executar_briefing():
    print("\n" + "=" * 60)
    print("☀️ GERANDO BRIEFING DIÁRIO E ROTEIROS DO SOCIAL MEDIA")
    print("=" * 60)

    noticias = obter_noticias_recentes()
    trends = obter_trends_recentes()
    briefing = gerar_briefing_ia(noticias, trends)

    if supabase:
        try:
            dados = {
                "data": datetime.date.today().isoformat(),
                "resumo_cenario": briefing.get("resumo_cenario", ""),
                "ideias_roteiros": str(briefing.get("ideias_roteiros", "")),
                "pautas_google_trends": str(briefing.get("pautas_google_trends", "")),
                "alertas_concorrentes": str(briefing.get("alertas_concorrentes", ""))
            }
            supabase.table("briefings_diarios").insert(dados).execute()
            print("[OK] Briefing salvo em 'briefings_diarios'.")
        except Exception as e:
            print(f"[AVISO] Erro ao salvar briefing no Supabase: {e}")

    enviar_briefing_email(briefing)

    print("\n" + "=" * 60)
    print("🎉 BRIEFING DIÁRIO CONCLUÍDO COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    executar_briefing()
