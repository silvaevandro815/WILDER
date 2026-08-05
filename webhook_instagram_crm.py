import os
import sys
import json
import re
import requests
import urllib3
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
VERIFY_TOKEN = os.getenv("INSTAGRAM_VERIFY_TOKEN", "wilder_eleitoral_2026")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

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

# Carrega o catálogo de propostas e palavras-chave da campanha
PROPOSTAS_PATH = os.path.join(os.path.dirname(__file__), "propostas_wilder.json")
PROPOSTAS_CATALOGO = {}
if os.path.exists(PROPOSTAS_PATH):
    try:
        with open(PROPOSTAS_PATH, "r", encoding="utf-8") as f:
            PROPOSTAS_CATALOGO = json.load(f)
            print(f"[OK] Catálogo de Propostas carregado ({len(PROPOSTAS_CATALOGO)} temas configurados).")
    except Exception as e:
        print(f"[AVISO] Erro ao carregar propostas_wilder.json: {e}")

app = Flask(__name__)

def identificar_proposta_por_texto(texto_comentario_ou_dm: str) -> dict:
    """
    Compara o texto do comentário ou DM do eleitor com o catálogo de palavras-chave
    e retorna a resposta e a proposta correspondente.
    """
    if not texto_comentario_ou_dm:
        return PROPOSTAS_CATALOGO.get("EDUCACAO")

    texto_clean = texto_comentario_ou_dm.lower().strip()

    for tema, info in PROPOSTAS_CATALOGO.items():
        palavras = info.get("palavras_chave", [])
        for kw in palavras:
            if kw.lower() in texto_clean:
                print(f"[MATCH PALAVRA-CHAVE] Encontrado tema '{tema}' para palavra '{kw}'.")
                return info

    # Retorno padrão caso não haja match exato
    return PROPOSTAS_CATALOGO.get("EDUCACAO")

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    """Validação de segurança exigida pela Meta (Instagram Graph API)."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("[WEBHOOK INSTAGRAM] Validação de Webhook aprovada com sucesso!")
        return challenge, 200
    return "Token de verificação inválido", 403

@app.route("/webhook", methods=["POST"])
def receber_interacao_instagram():
    """
    Recebe comentários e DMs do Instagram, identifica a palavra-chave,
    seleciona a proposta correta e salva o cadastro do eleitor no Supabase.
    """
    data = request.json or {}
    print("[WEBHOOK RECEBIDO] Dados brutos:", json.dumps(data, ensure_ascii=False))

    try:
        texto_recebido = data.get("comentario") or data.get("mensagem") or ""
        nome = data.get("nome", "Eleitor Instagram")
        whatsapp = data.get("whatsapp", "")
        cidade = data.get("cidade", "Goiânia")

        # Identifica a proposta correspondente à palavra-chave comentada
        proposta_matched = identificar_proposta_por_texto(texto_recebido)
        mensagem_resposta_dm = proposta_matched.get("mensagem_dm") if proposta_matched else "Obrigado pelo seu contato com a campanha de Wilder Morais!"
        tema_identificado = proposta_matched.get("titulo", "Geral") if proposta_matched else "Geral"

        print(f"📩 Resposta de DM Selecionada: {mensagem_resposta_dm[:60]}...")

        # Grava os dados no Supabase CRM
        if supabase:
            eleitor_dados = {
                "nome": nome,
                "whatsapp": whatsapp,
                "cidade": cidade,
                "pauta_interesse": tema_identificado,
                "fonte_origem": "Instagram DM Auto-Response"
            }
            supabase.table("eleitores_cadastrados").insert(eleitor_dados).execute()
            print(f"[CRM SUPABASE] Eleitor '{nome}' registrado em {cidade} (Pauta: {tema_identificado}).")

        return jsonify({
            "status": "sucesso",
            "tema_identificado": tema_identificado,
            "resposta_dm_enviada": mensagem_resposta_dm
        }), 200

    except Exception as e:
        print(f"[ERRO WEBHOOK] Falha ao processar interação: {e}")
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Servidor Webhook CRM Instagram com Matcher de Propostas rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
