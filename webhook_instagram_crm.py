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
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
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

app = Flask(__name__)

# ===================================================================
# SYSTEM PROMPT MESTRE DE ALTA PERFORMANCE - WILDER MORAIS 2026
# ===================================================================
SYSTEM_PROMPT_WILDER_MESTRE = """
Você é o próprio WILDER MORAIS, engenheiro civil de 3 continentes, ex-Senador dos Livros, empresário de sucesso e pré-candidato ao Governo de Goiás em 2026 pelo PL.

SUA PERSONA E TOM DE VOZ:
- Autêntico, prático, acolhedor, tom de conversa do interior de Goiás, sem linguagem empolada de político de carreira.
- Fala como quem constrói e entrega resultados de verdade.

OBJETIVO DA INTERAÇÃO (MÁXIMA EFICIÊNCIA & OBJETIVIDADE):
- NÃO ESTENDA A CONVERSA. Seja direto, conciso (máximo 2 a 3 frases curtas) e focado.
- IDENTIFICAÇÃO DE GÊNERO: Identifique se o interlocutor é HOMEM ou MULHER pelo nome ou texto para ajustar os pronomes ("meu amigo" ou "minha amiga").
- CAPTURA DE DADOS: Identifique a Cidade, o Nome e a Dor/Ideia principal mencionada.
- ENCERRAMENTO OBRIGATÓRIO: Encerre a conversa com uma promessa firme e reconfortante: reafirmando que como governador você vai **resolver e cuidar de Goiás da forma que precisa ser**.

PLANO DE GOVERNO DE REFERÊNCIA DE WILDER MORAIS:
1. AGRONEGÓCIO & INFRAESTRUTURA: Estradas vicinais asfaltadas para o escoamento da safra, crédito desburocratizado e internet no campo.
2. EDUCAÇÃO (SENADOR DOS LIVROS): Escolas técnicas profissionalizantes, valorização de professores e acervos literários.
3. SAÚDE (SAÚDE PERTO DE VOCÊ): Programa Zera Fila de cirurgias e exames nas 246 cidades, policlínicas regionais e prontuário digital.
4. ENTORNO DO DF & SEGURANÇA: Autoridade Metropolitana de Transporte, combate ao crime com inteligência e apoio às famílias.

REGRAS DE RESPOSTA (FORMATO JSON ESTRITO):
Responda ESTRITAMENTE em formato JSON com as seguintes chaves:
{
  "genero_detectado": "HOMEM" ou "MULHER",
  "cidade_detectada": "Nome da Cidade ou Goiás",
  "pauta_ou_reclamacao": "Resumo da dor/ideia em 3 palavras",
  "sentimento": "POSITIVO", "CRITICA" ou "DUVIDA",
  "resposta_dm": "Texto curto da resposta (máx 3 frases), terminando com a promessa de resolver e cuidar de Goiás da forma que precisa ser."
}
"""

def processar_mensagem_wilder_ia(nome_eleitor: str, texto_eleitor: str, tipo_interacao: str = "DM") -> dict:
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return {
            "genero_detectado": "HOMEM",
            "cidade_detectada": "Goiânia",
            "pauta_ou_reclamacao": "Apoio Geral",
            "sentimento": "POSITIVO",
            "resposta_dm": f"Muito obrigado pelo carinho, meu amigo {nome_eleitor}! Como engenheiro e senador, estou pronto para resolver e cuidar de Goiás da forma que precisa ser."
        }

    prompt_user = f"Nome do Eleitor: {nome_eleitor}\nTipo de Interação: {tipo_interacao}\nMensagem/Comentário: '{texto_eleitor}'"

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_WILDER_MESTRE},
            {"role": "user", "content": prompt_user}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2
    }

    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=12, verify=False)
        r.raise_for_status()
        res_json = r.json()
        raw_content = res_json["choices"][0]["message"]["content"]
        
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_content.strip(), re.DOTALL)
        cleaned = match.group(1) if match else raw_content[raw_content.find("{"):raw_content.rfind("}")+1]
        return json.loads(cleaned)
    except Exception as e:
        print(f"[AVISO] Falha no System Prompt Mestre Wilder IA: {e}")
        return {
            "genero_detectado": "HOMEM",
            "cidade_detectada": "Goiás",
            "pauta_ou_reclamacao": "Contato Geral",
            "sentimento": "POSITIVO",
            "resposta_dm": f"Muito obrigado pela mensagem! Pode ter certeza de que estamos prontos para resolver e cuidar de Goiás da forma que precisa ser."
        }

def enviar_resposta_dm_meta(recipient_id: str, texto_resposta: str):
    """Envia mensagem direta (DM) no Instagram via Meta Graph API v20.0."""
    if not META_ACCESS_TOKEN or META_ACCESS_TOKEN == "your-meta-access-token":
        print("[INFO SIMULAÇÃO] Token Meta ausente. DM que seria enviada:", texto_resposta)
        return

    url = f"https://graph.facebook.com/v20.0/me/messages?access_token={META_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": texto_resposta}
    }
    
    try:
        res = requests.post(url, json=payload, timeout=10, verify=False)
        if res.status_code in [200, 201]:
            print(f"[META DM SUCESSO] DM enviada para o usuário ID {recipient_id}!")
        else:
            print(f"[AVISO META DM] Status: {res.status_code} - Detalhe: {res.text}")
    except Exception as err:
        print(f"[ERRO META DM] Falha na requisição Meta: {err}")

def responder_comentario_meta(comment_id: str, texto_resposta: str):
    """Responde publicamente a um COMENTÁRIO no post/Reel via Meta Graph API v20.0."""
    if not META_ACCESS_TOKEN or META_ACCESS_TOKEN == "your-meta-access-token":
        print("[INFO SIMULAÇÃO] Token Meta ausente. Resposta ao Comentário que seria enviada:", texto_resposta)
        return

    url = f"https://graph.facebook.com/v20.0/{comment_id}/replies?access_token={META_ACCESS_TOKEN}"
    payload = {"message": texto_resposta}
    
    try:
        res = requests.post(url, json=payload, timeout=10, verify=False)
        if res.status_code in [200, 201]:
            print(f"[META COMENTÁRIO SUCESSO] Resposta pública enviada para o comentário ID {comment_id}!")
        else:
            print(f"[AVISO META COMENTÁRIO] Status: {res.status_code} - Detalhe: {res.text}")
    except Exception as err:
        print(f"[ERRO META COMENTÁRIO] Falha na requisição Meta: {err}")

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    """Validação de segurança oficial da Meta."""
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
    Recebe eventos em tempo real da Meta para DMs e Comentários do Instagram.
    Suporta formato padronizado e o payload oficial Webhook da Meta (entry -> messaging / changes).
    """
    data = request.json or {}
    print("[WEBHOOK RECEBIDO] Payload bruto:", json.dumps(data, ensure_ascii=False))

    # 1. PARSER DO PAYLOAD OFICIAL DA META (DMs e Comentários)
    entries = data.get("entry", [])
    if entries and isinstance(entries, list):
        for entry in entries:
            # A) Eventos de Mensagens Diretas (DMs)
            messaging_list = entry.get("messaging", [])
            for messaging in messaging_list:
                sender_id = messaging.get("sender", {}).get("id")
                message_obj = messaging.get("message", {})
                is_echo = message_obj.get("is_echo", False)
                texto = message_obj.get("text", "")

                if is_echo or (FACEBOOK_PAGE_ID and sender_id == FACEBOOK_PAGE_ID):
                    print("[HANDOVER HUMANO] Mensagem enviada por assessor. Bot pausado.")
                    continue

                if sender_id and texto:
                    ia_result = processar_mensagem_wilder_ia("Eleitor Instagram", texto, "DM")
                    resposta_texto = ia_result.get("resposta_dm", "")
                    enviar_resposta_dm_meta(sender_id, resposta_texto)

            # B) Eventos de Comentários em Publicações/Reels
            changes_list = entry.get("changes", [])
            for change in changes_list:
                value = change.get("value", {})
                comment_id = value.get("comment_id")
                texto_comentario = value.get("text", "")
                from_obj = value.get("from", {})
                user_name = from_obj.get("username", "Eleitor Instagram")

                if comment_id and texto_comentario:
                    ia_result = processar_mensagem_wilder_ia(user_name, texto_comentario, "COMENTARIO")
                    resposta_texto = ia_result.get("resposta_dm", "")
                    responder_comentario_meta(comment_id, resposta_texto)

    # 2. PARSER DE TESTE / REQUISIÇÃO DIRETA PADRONIZADA
    texto_recebido = data.get("comentario") or data.get("mensagem") or ""
    sender_id_direto = data.get("sender_id", "")
    comment_id_direto = data.get("comment_id", "")
    nome_direto = data.get("nome", "Eleitor")

    if texto_recebido and (sender_id_direto or comment_id_direto):
        ia_result = processar_mensagem_wilder_ia(nome_direto, texto_recebido)
        resposta_texto = ia_result.get("resposta_dm", "")

        if sender_id_direto:
            enviar_resposta_dm_meta(sender_id_direto, resposta_texto)
        if comment_id_direto:
            responder_comentario_meta(comment_id_direto, resposta_texto)

        # Grava no Supabase CRM
        if supabase:
            try:
                supabase.table("eleitores_cadastrados").insert({
                    "nome": nome_direto,
                    "cidade": ia_result.get("cidade_detectada", "Goiás"),
                    "pauta_interesse": f"{ia_result.get('pauta_ou_reclamacao', 'Geral')} [{ia_result.get('genero_detectado', 'HOMEM')}]",
                    "fonte_origem": "Instagram IA Mestre Wilder"
                }).execute()
            except Exception as e:
                print(f"[AVISO] Erro ao gravar no Supabase: {e}")

    return jsonify({"status": "sucesso", "mensagem": "Webhook processado"}), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Servidor Webhook CRM Instagram com Resposta Automática a DMs e Comentários rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
