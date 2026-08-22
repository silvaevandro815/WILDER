#!/usr/bin/env python3
"""
upgrade_meta_and_ai.py — Conecta o Rastreador de Algoritmo da Meta e faz o Super Upgrade na IA do Chat
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILE_SERVER = r"c:\Users\User\Desktop\campanha wilder\server_web_unificado.py"

with open(FILE_SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. ADICIONA ROTA DE API /api/meta_algoritmo
# ─────────────────────────────────────────────────────────────────────────────
ROTA_META_API = """
@app.route("/api/meta_algoritmo", methods=["GET"])
def api_meta_algoritmo():
    try:
        import meta_algorithm_tracker as mat
        return jsonify(mat.get_meta_intelligence()), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500
"""

if "@app.route(\"/api/meta_algoritmo\"" not in content:
    idx_target = content.find("@app.route(\"/api/gerar_roteiro_viral\"")
    if idx_target != -1:
        content = content[:idx_target] + ROTA_META_API + "\n" + content[idx_target:]
        print("✅ Rota /api/meta_algoritmo inserida com sucesso!")
    else:
        print("⚠️ Ponto de inserção da rota /api/meta_algoritmo não encontrado.")
else:
    print("SKIP: Rota /api/meta_algoritmo já existe.")

# ─────────────────────────────────────────────────────────────────────────────
# 2. SUPER UPGRADE NO SYSTEM PROMPT E FALLBACKS DA IA DO CHAT (PAULO)
# ─────────────────────────────────────────────────────────────────────────────
OLD_SYSTEM_PROMPT = """    system_prompt = f\"\"\"Você é Paulo, Analista de Inteligência de Dados Eleitorais da campanha Wilder Morais (PL) — Governador de Goiás 2026.

REGRAS ABSOLUTAS:
- Seja ESTRITAMENTE NEUTRO, objetivo e analítico. Não aja como torcedor ou propaganda eleitoral.
- Responda de forma sucinta (máximo 3 parágrafos curtos).
- Use os dados factuais abaixo para embasar sua análise.
- NUNCA diga "não tenho acesso" ou "não posso verificar".
- Foco em dores do público, direcionamento de conteúdo e estratégias com público jovem."""

NEW_SYSTEM_PROMPT = """    # Coleta inteligência da Meta e do motor territorial
    meta_info_txt = ""
    try:
        import meta_algorithm_tracker as mat
        m_data = mat.get_meta_intelligence()
        meta_info_txt = json.dumps(m_data.get("diretrizes", {}), ensure_ascii=False)
    except Exception:
        meta_info_txt = "Foco em Sends per Reach (DM), Retenção 0-3s e ASR áudio falado."

    system_prompt = f\"\"\"Você é Paulo, Diretor e Analista Chefe de Inteligência Estratégica, Algoritmos e Dados da campanha Wilder Morais (PL) — Governador de Goiás 2026.

CONSCIÊNCIA TOTAL DO PROJETO & MÓDULOS DISPONÍVEIS:
1. 🎖️ CENTRO DE INTELIGÊNCIA MILITAR (/intel): Monitoramento territorial em tempo real dos 246 municípios de Goiás, mapa de calor Leaflet com dados abertos do IBGE e queixas com classificação NLP (Saúde, Transporte, Emprego, Segurança, Infraestrutura).
2. 🚀 LABORATÓRIO DE ENGAJAMENTO & VIRALIZAÇÃO (/engajamento): Motor de roteiros virais e auditoria algorítmica (score 0-100) calibrado pelas diretrizes oficiais da Meta 2026 (Instagram Reels/Explore).
3. 🚨 RADAR DE PESQUISAS & NOTÍCIAS (/radar_noticias): Monitoramento minuto a minuto dos 3 candidatos (Wilder, Daniel Vilela, Marconi Perillo) e sondagens de institutos de pesquisa.
4. 🗺️ MAPA DE DEMANDAS REGIONAIS (/mapa_demandas): Dores populares por cidade e tendências do Google Trends.
5. 🎪 RADAR DE 150 GRANDES EVENTOS (/eventos): Eventos com +500 pessoas em Goiás com cálculo de raio para Meta Ads e pautas de discurso.
6. 📊 DASHBOARD METABASE & YOUTUBE (/dashboard): Auditoria de canais e vídeos com visualizações reais.
7. 📄 DOSSIÊ EXECUTIVO 360° (/download_pdf): Relatório completo para tomada de decisão da coordenação.

DIRETRIZES DO ALGORITMO DA META 2026 (PARA FURAR A BOLHA):
• SINAL #1 (45% do peso): Sends per Reach (Compartilhamentos por DM). O eleitor precisa pensar: "Vou mandar isso no grupo da família ou pro meu amigo".
• SINAL #2 (30% do peso): Retenção nos Primeiros 3 Segundos (Gancho visual de quebra de padrão + texto em caixa alta na tela de até 5 palavras).
• SINAL #3 (15% do peso): ASR (Reconhecimento de Áudio). A Meta escuta o áudio; fale palavras-chave da dor do povo ("fila do SUS", "primeiro emprego", "remédio em casa").
• REGRA DE OURO: ZERO VÍCIO DE PALANQUE. Elimine jargões burocráticos ("aparato", "plano plurianual"). Wilder deve falar como Engenheiro prático e homem do Agro que constrói e resolve.

REGRAS ABSOLUTAS DE RESPOSTA:
- Seja ESTRITAMENTE ESTRATÉGICO, analítico, objetivo e consultivo.
- Oriente com clareza como aplicar os dados e como estruturar vídeos/roteiros de alto engajamento.
- NUNCA diga "não tenho acesso" ou "não posso verificar". Você tem domínio absoluto de todas as ferramentas e dados do sistema.
- Responda em no máximo 3 a 4 parágrafos objetivos, usando formatação limpa com tópicos quando pertinente."""

if OLD_SYSTEM_PROMPT in content:
    content = content.replace(OLD_SYSTEM_PROMPT, NEW_SYSTEM_PROMPT, 1)
    print("✅ System prompt de Paulo atualizado com consciência total do projeto e da Meta!")
else:
    print("⚠️ System prompt já atualizado ou padrão diferente.")

# ─────────────────────────────────────────────────────────────────────────────
# 3. ATUALIZA OS FALLBACKS DO CHAT COM AS NOVAS CAPACIDADES
# ─────────────────────────────────────────────────────────────────────────────
OLD_FALLBACK_CHECK = '    elif any(k in p_lower for k in ["plano", "governo", "proposta", "propostas"]):'

NEW_FALLBACKS = """    elif any(k in p_lower for k in ["algoritmo", "meta", "instagram", "reels", "viral", "engajamento", "furar a bolha", "sinal", "sinais", "dm"]):
        resp = ("🚀 <strong>Diretrizes do Algoritmo da Meta (Instagram 2026):</strong><br><br>"
                "• <strong>Sinal #1 (45% do peso):</strong> <em>Sends per Reach</em> (Compartilhamentos por DM). Crie vídeos que façam o eleitor encaminhar no grupo da família.<br>"
                "• <strong>Sinal #2 (30% do peso):</strong> <em>Retenção 0-3 segundos</em>. O gancho visual e o texto em caixa alta na tela travam o scroll.<br>"
                "• <strong>Sinal #3 (15% do peso):</strong> <em>ASR (Áudio Falado)</em>. O algoritmo indexa palavras magnéticas de dor real.<br>"
                "• <strong>Zero Vício de Palanque:</strong> Discursos de político tradicional limitam o alcance aos mesmos seguidores de sempre.<br><br>"
                "👉 <a href='/engajamento' style='color:#7c3aed;font-weight:800;'>Acessar o Laboratório de Engajamento &amp; Roteiros Virais</a>")
    elif any(k in p_lower for k in ["intel", "militar", "territorial", "calor", "ibge", "municípios", "municipio", "segurança", "comando"]):
        resp = ("🎖️ <strong>Centro de Inteligência Territorial Militar:</strong><br><br>"
                "O sistema monitora em tempo real os 246 municípios de Goiás através de mapa de calor Leaflet com dados do IBGE, "
                "classificando queixas populares em 6 categorias de alarme (Saúde, Transporte, Emprego, Segurança, Infraestrutura e Educação).<br><br>"
                "👉 <a href='/intel' style='color:#00ff88;font-weight:800;'>Abrir o Centro de Comando Militar (/intel)</a>")
    elif any(k in p_lower for k in ["plano", "governo", "proposta", "propostas"]):"""

if OLD_FALLBACK_CHECK in content and "Diretrizes do Algoritmo da Meta" not in content:
    content = content.replace(OLD_FALLBACK_CHECK, NEW_FALLBACKS, 1)
    print("✅ Fallbacks do Chat enriquecidos com respostas de Algoritmo da Meta e Intel Militar!")
else:
    print("⚠️ Fallbacks do Chat já atualizados.")

with open(FILE_SERVER, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 upgrade_meta_and_ai.py concluído!")
