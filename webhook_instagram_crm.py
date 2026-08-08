import os
import sys
import json
import re
import requests
import urllib3
import httpx
from flask import Flask, request, jsonify
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from supabase import create_client, Client, ClientOptions

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
VERIFY_TOKEN = os.getenv("INSTAGRAM_VERIFY_TOKEN", "wilder_eleitoral_2026")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
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

def gerar_resposta_persona_wilder(texto_eleitor: str, tipo_interacao: str = "DM") -> dict:
    """
    Gera uma resposta ultra-humana e autêntica personificando o próprio Wilder Morais.
    Distingue comentários e DMs POSITIVOS (agradecimento + convite) e NEGATIVOS/CRÍTICAS (respeito + escuta de engenheiro).
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return {
            "sentimento": "POSITIVO",
            "resposta_texto": "Muito obrigado pelo apoio e pelo carinho! Como engenheiro e senador, estou trabalhando por um Goiás mais forte. De qual cidade você é?"
        }

    prompt_system = (
        "Você é o próprio Wilder Morais, empresário, engenheiro e pré-candidato ao Governo de Goiás em 2026.\n"
        "Responda a esta mensagem no Instagram mantendo seu tom de voz autêntico: simples, acolhedor, goiano, prático (visão de engenheiro que constrói de verdade) e focado em resultados.\n\n"
        "REGRAS DE PERSONA:\n"
        "1. Se a mensagem for POSITIVA ou APOIO: Agradeça com carinho verdadeiro, trate como 'meu amigo/minha amiga' e pergunte de qual cidade de Goiás ele é.\n"
        "2. Se for uma CRÍTICA OU RECLAMAÇÃO: Nunca seja reativo. Valide a dor da pessoa, mostre que entende a indignação e explique que como engenheiro você defende gestão séria. Pergunte qual o principal problema da região dele.\n"
        "3. Responda em no máximo 2 ou 3 frases curtas, ideais para Direct do Instagram.\n"
        "Responda estritamente em JSON com as chaves: 'sentimento' (POSITIVO, NEGATIVO, DUVIDA), 'resposta_texto'."
    )

    prompt_user = f"Tipo de Interação: {tipo_interacao}\nMensagem do Eleitor: '{texto_eleitor}'"

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }

    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=12, verify=False)
        r.raise_for_status()
        res_json = r.json()
        raw_content = res_json["choices"][0]["message"]["content"]
        
        # Sanitiza JSON
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_content.strip(), re.DOTALL)
        cleaned = match.group(1) if match else raw_content[raw_content.find("{"):raw_content.rfind("}")+1]
        return json.loads(cleaned)
    except Exception as e:
        print(f"[AVISO] Falha na IA Persona Wilder: {e}")
        return {
            "sentimento": "POSITIVO",
            "resposta_texto": "Muito obrigado pelo seu carinho e mensagem! Goiás tem um futuro brilhante pela frente. De qual cidade você está falando?"
        }

def enviar_resposta_meta_graph_api(recipient_id: str, texto_resposta: str):
    """
    Envia a resposta gerada pela IA diretamente para a DM do Instagram via Meta Graph API oficial.
    """
    if not META_ACCESS_TOKEN or META_ACCESS_TOKEN == "your-meta-access-token":
        print("[INFO SIMULAÇÃO] Token da Meta ausente. Resposta gerada:", texto_resposta)
        return

    url = f"https://graph.facebook.com/v20.0/me/messages?access_token={META_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": texto_resposta}
    }
    
    try:
        res = requests.post(url, json=payload, timeout=10, verify=False)
        if res.status_code in [200, 201]:
            print(f"[META GRAPH API] DM enviada com sucesso para ID {recipient_id}!")
        else:
            print(f"[AVISO META] Resposta da API: {res.status_code} - {res.text}")
    except Exception as err:
        print(f"[ERRO META API] Falha ao enviar DM via Meta: {err}")

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("[WEBHOOK INSTAGRAM] Validação de Webhook aprovada com sucesso!")
        return challenge, 200
    return "Token de verificação inválido", 403

@app.route("/webhook", methods=["POST"])
def receber_interacao_instagram():
    data = request.json or {}
    print("[WEBHOOK RECEBIDO] Dados brutos:", json.dumps(data, ensure_ascii=False))
    
    is_echo = data.get("is_echo", False)
    sender_id = data.get("sender_id", "")
    page_id = os.getenv("FACEBOOK_PAGE_ID", "")
    
    if is_echo or (page_id and sender_id == page_id):
        print(f"[HANDOVER HUMANO DETECTADO] Resposta enviada por um assessor humano. Automação pausada.")
        return jsonify({"status": "ignorado", "motivo": "resposta_humana_prioritaria"}), 200

    try:
        texto_recebido = data.get("comentario") or data.get("mensagem") or ""
        nome = data.get("nome", "Eleitor Instagram")
        cidade = data.get("cidade", "Goiânia")
        sender_id = data.get("sender_id", "")

        # 1. Gera a resposta personalizada na voz do Wilder Morais via IA
        persona_result = gerar_resposta_persona_wilder(texto_recebido)
        resposta_texto = persona_result.get("resposta_texto", "")
        sentimento = persona_result.get("sentimento", "POSITIVO")

        print(f"🤖 Resposta Persona Wilder ({sentimento}): {resposta_texto}")

        # 2. Envia a resposta de volta ao Instagram se o sender_id estiver presente
        if sender_id:
            enviar_resposta_meta_graph_api(sender_id, resposta_texto)

        # 3. Grava no Supabase CRM
        if supabase:
            eleitor_dados = {
                "nome": nome,
                "cidade": cidade,
                "pauta_interesse": f"Interação Instagram [{sentimento}]",
                "fonte_origem": "Persona Wilder IA Auto-Response"
            }
            supabase.table("eleitores_cadastrados").insert(eleitor_dados).execute()
            print(f"[CRM SUPABASE] Eleitor '{nome}' registrado em {cidade}.")

        return jsonify({
            "status": "sucesso",
            "sentimento_detectado": sentimento,
            "resposta_enviada": resposta_texto
        }), 200

    except Exception as e:
        print(f"[ERRO WEBHOOK] Falha ao processar interação: {e}")
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Servidor Webhook CRM Instagram com Persona Wilder Morais IA na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
