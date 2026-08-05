import os
import sys
import json
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

app = Flask(__name__)

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
    Recebe as DMs, comentários e dados dos eleitores vindos do Instagram/Typebot
    e grava automaticamente nas tabelas 'eleitores_cadastrados' e 'demandas_populares' no Supabase.
    """
    data = request.json
    print("[WEBHOOK RECEBIDO] Dados brutos:", json.dumps(data, ensure_ascii=False))

    try:
        # Extração de campos estruturados enviados pelo webhook ou Typebot
        nome = data.get("nome", "Eleitor Não Identificado")
        whatsapp = data.get("whatsapp", "")
        cidade = data.get("cidade", "Goiânia")
        bairro = data.get("bairro", "")
        pauta_interesse = data.get("pauta_interesse", "Geral")
        fonte = data.get("fonte_origem", "Instagram DM")
        descricao_demanda = data.get("descricao_demanda", "")

        # 1. Registra no CRM de Eleitores do Supabase
        if supabase:
            eleitor_dados = {
                "nome": nome,
                "whatsapp": whatsapp,
                "cidade": cidade,
                "bairro": bairro,
                "pauta_interesse": pauta_interesse,
                "fonte_origem": fonte
            }
            res_eleitor = supabase.table("eleitores_cadastrados").insert(eleitor_dados).execute()
            print(f"[CRM SUPABASE] Eleitor '{nome}' de {cidade} cadastrado com sucesso!")

            # 2. Se houver descrição de uma dor/demanda da cidade, registra na tabela 'demandas_populares'
            if descricao_demanda:
                demanda_dados = {
                    "cidade": cidade,
                    "categoria": pauta_interesse,
                    "descricao": descricao_demanda,
                    "nivel_urgencia": "MÉDIO"
                }
                supabase.table("demandas_populares").insert(demanda_dados).execute()
                print(f"[DEMANDA REGISTRADA] Dor de {cidade} em {pauta_interesse} registrada!")

        return jsonify({"status": "sucesso", "mensagem": "Dados gravados no Supabase"}), 200

    except Exception as e:
        print(f"[ERRO WEBHOOK] Falha ao processar dados do eleitor: {e}")
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Servidor Webhook CRM Instagram rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
