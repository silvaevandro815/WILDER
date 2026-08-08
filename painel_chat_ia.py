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

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
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
        options = ClientOptions(httpx_client=httpx.Client(verify=False))
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options=options)
    except Exception as e:
        print(f"[AVISO] Não foi possível inicializar cliente Supabase: {e}")

app = Flask(__name__)

# Template HTML do Chatbot Inteligente para Embutir no Metabase
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

def obter_contexto_dados_supabase() -> str:
    """Consulta os dados recentes das tabelas para alimentar o contexto da IA."""
    if not supabase:
        return "Banco Supabase desconectado."

    contexto = []
    try:
        # 1. Cidades de Goiás
        r_cid = supabase.table("municipios_goias").select("nome, eleitores_tse").order("eleitores_tse", desc=True).limit(5).execute()
        top_cidades = [f"{c['nome']} ({c['eleitores_tse']:,} eleitores)" for c in r_cid.data] if (r_cid and r_cid.data) else []
        contexto.append(f"Top 5 Cidades por Eleitorado: {', '.join(top_cidades)}")

        # 2. Concorrentes
        r_conc = supabase.table("concorrentes_historico").select("candidato_nome, seguidores, taxa_engajamento").order("data", desc=True).limit(2).execute()
        if r_conc and r_conc.data:
            conc_str = "; ".join([f"{c['candidato_nome']}: {c['seguidores']:,} seg ({c['taxa_engajamento']}%)" for c in r_conc.data])
            contexto.append(f"Última Medição de Concorrentes: {conc_str}")

        # 3. Google Trends
        r_tr = supabase.table("google_trends_goias").select("termo, interesse_relativo").order("data", desc=True).limit(3).execute()
        if r_tr and r_tr.data:
            tr_str = "; ".join([f"{t['termo']}: {t['interesse_relativo']}/100" for t in r_tr.data])
            contexto.append(f"Google Trends GO Recente: {tr_str}")

    except Exception as e:
        contexto.append(f"Erro ao ler banco: {e}")

    return "\n".join(contexto)

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_CHAT_WIDGET)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    pergunta = data.get("pergunta", "")

    if not pergunta:
        return jsonify({"resposta": "Por favor, digite uma pergunta sobre a campanha."}), 400

    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return jsonify({"resposta": "A chave do OpenRouter precisa estar configurada no .env para responder dúvidas."})

    contexto_dados = obter_contexto_dados_supabase()

    prompt_system = (
        "Você é o Copiloto Estratégico de Inteligência e Análise de Dados da campanha de Wilder Morais para Governador de Goiás em 2026.\n"
        "Você está embutido como um Chatbot dentro do painel do Metabase da equipe.\n"
        "Responda à pergunta da equipe de forma clara, profissional, didática e baseada em dados.\n\n"
        f"DADOS EM TEMPO REAL DO BANCO DE DADOS (SUPABASE):\n{contexto_dados}"
    )

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": pergunta}
        ],
        "temperature": 0.3
    }

    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15, verify=False)
        r.raise_for_status()
        res_json = r.json()
        resposta_texto = res_json["choices"][0]["message"]["content"]
        return jsonify({"resposta": resposta_texto}), 200
    except Exception as e:
        return jsonify({"resposta": f"Erro ao consultar a IA: {e}"}), 500

if __name__ == "__main__":
    porta = int(os.getenv("PORT_CHAT", 5001))
    print(f"🚀 Servidor do Chatbot de IA para o Metabase rodando na porta {porta}...")
    app.run(host="0.0.0.0", port=porta)
