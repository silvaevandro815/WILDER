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
  "resposta_dm": "Texto curto da DM (máx 3 frases), terminando com a promessa de resolver e cuidar de Goiás da forma que precisa ser."
}
"""

def processar_mensagem_wilder_ia(nome_eleitor: str, texto_eleitor: str, tipo_interacao: str = "DM") -> dict:
    """
    Processa a mensagem do eleitor com o System Prompt Mestre de Wilder Morais.
    Detecta gênero, cidade, dor/reclamação e gera a resposta direta e objetiva.
    """
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

def enviar_resposta_meta_graph_api(recipient_id: str, texto_resposta: str):
    """Envia a DM de resposta via Meta Graph API v20.0."""
    if not META_ACCESS_TOKEN or META_ACCESS_TOKEN == "your-meta-access-token":
        print("[INFO SIMULAÇÃO] Token da Meta ausente. DM gerada:", texto_resposta)
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
            print(f"[AVISO META] Status API: {res.status_code} - {res.text}")
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
        nome = data.get("nome", "Eleitor")
        sender_id = data.get("sender_id", "")

        # Executa o System Prompt Mestre de Wilder Morais
        ia_result = processar_mensagem_wilder_ia(nome, texto_recebido)
        
        genero = ia_result.get("genero_detectado", "HOMEM")
        cidade = ia_result.get("cidade_detectada", "Goiás")
        pauta = ia_result.get("pauta_ou_reclamacao", "Geral")
        sentimento = ia_result.get("sentimento", "POSITIVO")
        resposta_dm = ia_result.get("resposta_dm", "")

        print(f"🤖 [IA WILDER MESTRE] Gênero: {genero} | Cidade: {cidade} | Pauta: {pauta}")
        print(f"💬 Resposta DM: {resposta_dm}")

        # Envia a DM se o sender_id estiver presente
        if sender_id:
            enviar_resposta_meta_graph_api(sender_id, resposta_dm)

        # Grava os dados ricos extraídos no Supabase CRM (Conhecimento do META)
        if supabase:
            eleitor_dados = {
                "nome": nome,
                "whatsapp": data.get("whatsapp", ""),
                "cidade": cidade,
                "bairro": data.get("bairro", ""),
                "pauta_interesse": f"{pauta} [{genero}]",
                "fonte_origem": "Instagram IA Mestre Wilder"
            }
            supabase.table("eleitores_cadastrados").insert(eleitor_dados).execute()
            
            # Se houver reclamação específica, grava também na tabela de demandas populares
            if sentimento in ["CRITICA", "DUVIDA"] or len(texto_recebido) > 20:
                demanda_dados = {
                    "cidade": cidade,
                    "categoria": pauta,
                    "descricao": f"[{genero}] {texto_recebido}",
                    "nivel_urgencia": "MÉDIO"
                }
                supabase.table("demandas_populares").insert(demanda_dados).execute()
                print(f"[CONHECIMENTO REGISTRADO] Dor de {cidade} gravada em demandas_populares!")

        return jsonify({
            "status": "sucesso",
            "genero_detectado": genero,
            "cidade_detectada": cidade,
            "pauta_extraida": pauta,
            "resposta_dm_enviada": resposta_dm
        }), 200

    except Exception as e:
        print(f"[ERRO WEBHOOK] Falha ao processar interação: {e}")
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Servidor Webhook CRM Instagram com System Prompt Mestre de Wilder Morais na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
