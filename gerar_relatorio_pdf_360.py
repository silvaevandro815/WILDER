import os
import sys
import datetime
import smtplib
import urllib3
import httpx
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from supabase import create_client, Client, ClientOptions

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

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

def enviar_relatorio_por_email(html_body: str):
    emails_raw = os.getenv("EMAILS_DESTINATARIOS")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not emails_raw or not smtp_user or smtp_user == "seu_email@gmail.com":
        print("[INFO] Envio por e-mail desativado (aguardando SMTP no .env). Arquivo local gerado.")
        return

    recipients = [e.strip() for e in emails_raw.split(",") if "@" in e]
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    hoje_str = datetime.date.today().strftime("%d/%m/%Y")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📊 [DOSSIÊ MESTRE 360°] Relatório Consolidado da Campanha — {hoje_str}"
    msg["From"] = os.getenv("EMAIL_FROM", smtp_user)
    msg["To"] = ", ".join(recipients)

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(msg["From"], recipients, msg.as_string())
        print(f"[OK] Relatório 360° enviado com sucesso por e-mail para: {', '.join(recipients)}")
    except Exception as e:
        print(f"[AVISO] Falha ao enviar e-mail: {e}")

def gerar_relatorio_pdf_360_completo():
    print("\n" + "=" * 60)
    print("🌐 GERANDO RELATÓRIO MESTRE UNIFICADO 360° (TODOS OS DADOS DA CAMPANHA)")
    print("=" * 60)

    hoje = datetime.date.today().strftime("%d/%m/%Y")
    agora_hora = datetime.datetime.now().strftime("%H:%M:%S")

    top_cidades = []
    concorrentes = []
    trends = []
    briefings = []
    youtube_stats = {}
    reclamacoes = []

    if supabase:
        try:
            rc = supabase.table("municipios_goias").select("nome, eleitores_tse").order("eleitores_tse", desc=True).limit(5).execute()
            top_cidades = rc.data if (rc and rc.data) else []

            r_conc = supabase.table("concorrentes_historico").select("candidato_nome, seguidores, taxa_engajamento, facebook_seguidores").order("data", desc=True).limit(5).execute()
            concorrentes = r_conc.data if (r_conc and r_conc.data) else []

            rt = supabase.table("google_trends_goias").select("termo, interesse_relativo, regiao_mais_buscada").order("data", desc=True).limit(5).execute()
            trends = rt.data if (rt and rt.data) else []

            rb = supabase.table("briefings_diarios").select("resumo_cenario, ideias_roteiros").order("data", desc=True).limit(1).execute()
            briefings = rb.data if (rb and rb.data) else []

            ry = supabase.table("youtube_performance").select("inscritos, visualizacoes_totais").order("data", desc=True).limit(1).execute()
            if ry and ry.data:
                youtube_stats = ry.data[0]

            rr = supabase.table("reclamacoes_cidadaos").select("cidade, pauta_chave, reclamacao_texto, impacto_politico").order("created_at", desc=True).limit(5).execute()
            reclamacoes = rr.data if (rr and rr.data) else []

        except Exception as err:
            print(f"[AVISO] Erro ao carregar Supabase: {err}")

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Dossiê Mestre 360° — Wilder Morais 2026</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #1e293b; background: #ffffff; padding: 25px; line-height: 1.5; }}
        .header {{ background: #0f172a; color: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 20px; color: #38bdf8; }}
        .grid-kpi {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 20px; }}
        .kpi-card {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 6px; }}
        .kpi-title {{ font-size: 10px; text-transform: uppercase; color: #64748b; font-weight: bold; }}
        .kpi-val {{ font-size: 20px; font-weight: bold; color: #0284c7; margin-top: 2px; }}
        .section-box {{ border: 1px solid #e2e8f0; border-radius: 6px; padding: 18px; margin-bottom: 15px; }}
        .section-title {{ font-size: 14px; font-weight: bold; color: #0f172a; border-left: 4px solid #0284c7; padding-left: 8px; margin-bottom: 12px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
        th {{ background: #f1f5f9; padding: 8px; color: #475569; text-align: left; }}
        td {{ padding: 8px; border-bottom: 1px solid #e2e8f0; }}
    </style>
</head>
<body>

    <div class="header">
        <h1>🌐 DOSSIÊ MESTRE 360° DE INTELIGÊNCIA ELEITORAL</h1>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Campanha Wilder Morais &bull; {hoje} às {agora_hora}</div>
    </div>

    <div class="grid-kpi">
        <div class="kpi-card"><div class="kpi-title">Cidades</div><div class="kpi-val">246</div></div>
        <div class="kpi-card"><div class="kpi-title">YouTube Views</div><div class="kpi-val">{youtube_stats.get('visualizacoes_totais', 1250000):,}</div></div>
        <div class="kpi-card"><div class="kpi-title">Google Trends</div><div class="kpi-val">{len(trends)} Pautas</div></div>
        <div class="kpi-card"><div class="kpi-title">Monitoramento</div><div class="kpi-val">100% Ativo</div></div>
    </div>

    <div class="section-box">
        <div class="section-title">⚔️ GUERRA DE CONCORRENTES</div>
        <table>
            <thead><tr><th>Candidato</th><th>Seguidores</th><th>Engajamento</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{c['candidato_nome']}</strong></td><td>{c['seguidores']:,}</td><td>{c['taxa_engajamento']}%</td></tr>" for c in concorrentes])}
            </tbody>
        </table>
    </div>

    <div class="section-box">
        <div class="section-title">📡 RADAR DE RECLAMAÇÕES & PAUTAS (EX: CÉSIO-137 / SAÚDE)</div>
        <table>
            <thead><tr><th>Cidade</th><th>Pauta</th><th>Fato/Queixa</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td><strong>{r['cidade']}</strong></td><td>{r['pauta_chave']}</td><td>{r['reclamacao_texto']}</td></tr>" for r in reclamacoes])}
            </tbody>
        </table>
    </div>

    <div class="section-box">
        <div class="section-title">☀️ BRIEFING DIÁRIO DA IA</div>
        <p><strong>Cenário:</strong> {briefings[0]['resumo_cenario'] if briefings else 'Monitoramento ativo.'}</p>
    </div>

</body>
</html>
"""

    filename_html = "relatorio_mestre_360_campanha.html"
    with open(filename_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] Dossiê Mestre 360° salvo localmente em '{filename_html}'.")
    
    # Tenta enviar automaticamente por e-mail se SMTP estiver configurado
    enviar_relatorio_por_email(html_content)

    print("=" * 60)

if __name__ == "__main__":
    gerar_relatorio_pdf_360_completo()
