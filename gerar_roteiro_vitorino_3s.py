import os
import sys
import json
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "google/gemini-2.5-flash"

SYSTEM_PROMPT_VITORINO = """
Você é o Diretor de Criação e Roteirista Chefe da campanha de Wilder Morais para Governador de Goiás em 2026, trabalhando sob a orientação metodológica do estrategista Marcelo Vitorino (Academia Vitorino & Mendonça).

METODOLOGIA VITORINO DE ALTA RETENÇÃO:
1. NADA DE CONTEÚDO ENGOMADO OU INSTITUCIONAL: Vídeos com terno, palanque e discurso político afastam o eleitor.
2. OS 3 PILARES VIRAIS (RETENÇÃO 100%):
   - GANCHO DE 3 SEGUNDOS (Interrupção de Padrão): Pergunta provocativa, fato chocante ou cena visual forte que faz o eleitor parar o dedo no Reels/TikTok/Shorts.
   - CURIOSIDADE + INFORMAÇÃO PRÁTICA (Conteúdo Utilitário): Entrega um dado real, mostrando visão de engenheiro prático e solução para a dor de Goiás.
   - EMOÇÃO + CTA NA DM (Conversão): Conexão humana direta (estilo Cleitinho/Zema) e chamada para ação na DM do Instagram.

NARRATIVA DE CONTRASTE ELEITORAL (GOIÁS 2026):
- WILDER MORAIS: O Engenheiro que Constrói, Senador dos Livros, empresário self-made de 3 continentes, prático, direto, sem frescura.
- DANIEL VILELA: O político engomado de gabinete que nunca construiu nada na vida real.
- MARCONI PERILLO: O passado ultrapassado e marcado por escândalos.

FORMATO DE SAÍDA (ESTRITO JSON):
{
  "titulo_video": "Nome chamativo do roteiro",
  "gancho_3s_visual_e_fala": "Descrição da cena de abertura (0-3s) + Primeira frase chocante",
  "desenvolvimento_informacao_15s": "Informação útil + contraste prático de engenharia (3-20s)",
  "emocao_e_cta_10s": "Fechamento emocionante + chamada para comentar a palavra-chave (20-30s)",
  "palavra_chave_cta": "PALAVRA-CHAVE EM MAIÚSCULAS",
  "orientacao_direcao_camera": "Dicas de figurino, microfone de lapela, enquadramento e locação"
}
"""

def gerar_roteiro_vitorino_3s(tema_ou_cidade: str) -> dict:
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key":
        return {
            "titulo_video": f"O Segredo da Saúde em {tema_ou_cidade}",
            "gancho_3s_visual_e_fala": "VISUAL: Wilder segura uma senha de hospital amassada. FALA: 'Você esperaria 5 horas por um atendimento se o seu filho estivesse com febre?'",
            "desenvolvimento_informacao_15s": "Como engenheiro, eu gerenciei obras em 3 continentes. O problema aqui não é falta de dinheiro, é falta de vergonha e gestão!",
            "emocao_e_cta_10s": "Vamos zerar essa fila nas 246 cidades. Comenta 'SAUDE' que te envio o plano completo no privado.",
            "palavra_chave_cta": "SAUDE",
            "orientacao_direcao_camera": "Sem terno. Camisa polo simples, microfone de lapela sem fio na mão, andando no pátio."
        }

    prompt_user = f"Tema/Cidade/Pauta Solicitada: '{tema_ou_cidade}'"

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_VITORINO},
            {"role": "user", "content": prompt_user}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }

    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15, verify=False)
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]
        return json.loads(raw)
    except Exception as e:
        print(f"[AVISO] Falha ao gerar roteiro Vitorino 3s: {e}")
        return {
            "titulo_video": "Goiás de Verdade",
            "gancho_3s_visual_e_fala": "Você sabia que um livro no lugar certo muda o futuro de um jovem?",
            "desenvolvimento_informacao_15s": "Enquanto políticos discursam, o Senador dos Livros entregou resultados práticos.",
            "emocao_e_cta_10s": "Comenta 'LIVROS' para receber a proposta completa na sua DM.",
            "palavra_chave_cta": "LIVROS",
            "orientacao_direcao_camera": "Estilo Cleitinho/Zema. Povo ao fundo, tom acolhedor e direto."
        }

if __name__ == "__main__":
    pauta = sys.argv[1] if len(sys.argv) > 1 else "Filas de Espera da Saúde no Entorno do DF"
    res = gerar_roteiro_vitorino_3s(pauta)
    print(json.dumps(res, ensure_ascii=False, indent=2))
