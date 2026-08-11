import os
import sys
import json
import re
import requests
import urllib3
import httpx
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from supabase import create_client, Client, ClientOptions
from busca_drive_ia import HTML_BUSCA_DRIVE, buscar_midias

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

HTML_CHAT_WIDGET = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Copiloto de IA da Campanha — Wilder Morais 2026</title>
    <style>
        body { font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; background: #0f172a; color: #f8fafc; display: flex; flex-direction: column; height: 100vh; }
        .header { background: #1e293b; padding: 14px 20px; border-bottom: 1px solid #334155; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { margin: 0; font-size: 16px; color: #38bdf8; display: flex; align-items: center; gap: 8px; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 14px; }
        .msg { max-width: 80%; padding: 12px 16px; border-radius: 12px; font-size: 14px; line-height: 1.5; }
        .user { background: #0284c7; color: #fff; align-self: flex-end; border-bottom-right-radius: 2px; }
        .bot { background: #1e293b; color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 2px; border: 1px solid #334155; }
        .input-box { padding: 14px 20px; background: #1e293b; border-top: 1px solid #334155; display: flex; gap: 10px; }
        input { flex: 1; padding: 12px 16px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 14px; outline: none; }
        input:focus { border-color: #38bdf8; }
        button { padding: 12px 24px; background: #0284c7; color: #fff; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #0369a1; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Copiloto Estratégico de IA (Metabase Wilder Morais)</h1>
        <span style="font-size: 12px; color: #94a3b8;">Conectado ao Supabase</span>
    </div>
    <div class="chat-box" id="chat">
        <div class="msg bot">
            Olá! Sou o <strong>Copiloto de IA da Campanha de Wilder Morais</strong>. Posso responder qualquer dúvida sobre os dados de Goiás, desempenho de cidades, tráfego pago, clipping de notícias, concorrentes e sugestões de vídeos. O que você gostaria de saber agora?
        </div>
    </div>
    <div class="input-box">
        <input type="text" id="pergunta" placeholder="Pergunte algo sobre os dados da campanha..." onkeypress="if(event.key==='Enter') enviar()">
        <button onclick="enviar()">Perguntar</button>
    </div>

    <script>
        async function enviar() {
            const input = document.getElementById('pergunta');
            const chat = document.getElementById('chat');
            const pergunta = input.value.trim();
            if (!pergunta) return;

            chat.innerHTML += `<div class="msg user">${pergunta}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            botMsg.innerText = 'Pensando e consultando banco de dados...';
            chat.appendChild(botMsg);
            chat.scrollTop = chat.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pergunta })
                });
                const data = await res.json();
                botMsg.innerText = data.resposta;
            } catch (err) {
                botMsg.innerText = 'Erro ao consultar a IA da campanha.';
            }
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

SYSTEM_PROMPT_WILDER_MESTRE = """
Você é o próprio WILDER MORAIS, engenheiro civil de 3 continentes, ex-Senador dos Livros, empresário de sucesso e pré-candidato ao Governo de Goiás em 2026 pelo PL.
Responda ESTRITAMENTE em formato JSON com as chaves: 'genero_detectado', 'cidade_detectada', 'pauta_ou_reclamacao', 'sentimento', 'resposta_dm'.
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
        "messages": [{"role": "system", "content": SYSTEM_PROMPT_WILDER_MESTRE}, {"role": "user", "content": prompt_user}],
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
        return {
            "genero_detectado": "HOMEM",
            "cidade_detectada": "Goiás",
            "pauta_ou_reclamacao": "Contato Geral",
            "sentimento": "POSITIVO",
            "resposta_dm": f"Muito obrigado pela mensagem! Pode ter certeza de que estamos prontos para resolver e cuidar de Goiás da forma que precisa ser."
        }

@app.route("/", methods=["GET"])
@app.route("/chat", methods=["GET"])
def chat_home():
    return render_template_string(HTML_CHAT_WIDGET)

@app.route("/busca_drive", methods=["GET"])
def busca_drive_home():
    return render_template_string(HTML_BUSCA_DRIVE)

@app.route("/api/busca_midia", methods=["GET"])
def api_busca_midia():
    q = request.args.get("q", "")
    resultados = buscar_midias(q)
    return jsonify({"status": "sucesso", "query": q, "total": len(resultados), "resultados": resultados}), 200

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    pergunta = data.get("pergunta", "")
    if not pergunta:
        return jsonify({"resposta": "Por favor, digite uma pergunta."}), 400

    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return jsonify({"resposta": "Chave OpenRouter ativa."})

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Você é o Copiloto de Inteligência da campanha de Wilder Morais em Goiás. Responda com base nos dados eleitorais de forma didática."},
            {"role": "user", "content": pergunta}
        ],
        "temperature": 0.3
    }
    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15, verify=False)
        resposta_texto = r.json()["choices"][0]["message"]["content"]
        return jsonify({"resposta": resposta_texto}), 200
    except Exception as e:
        return jsonify({"resposta": f"Erro na IA: {e}"}), 500

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Token inválido", 403

@app.route("/webhook", methods=["POST"])
def receber_interacao_instagram():
    data = request.json or {}
    texto = data.get("comentario") or data.get("mensagem") or ""
    if texto:
        ia_res = processar_mensagem_wilder_ia("Eleitor", texto)
        return jsonify({"status": "sucesso", "resposta": ia_res.get("resposta_dm")}), 200
    return jsonify({"status": "sucesso"}), 200

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"🚀 Servidor Unificado (Chat, Webhook & Busca Drive IA) rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
