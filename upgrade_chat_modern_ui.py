#!/usr/bin/env python3
"""
upgrade_chat_modern_ui.py — Transforma o chat da IA em uma interface moderna, estruturada e com visual de IA de última geração
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILE = r"c:\Users\User\Desktop\campanha wilder\server_web_unificado.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. ATUALIZA CSS DE MENSAGENS DO CHAT
# ─────────────────────────────────────────────────────────────────────────────
OLD_CHAT_CSS = """        .msg-bbl {
            max-width: 80%; padding: 12px 16px; border-radius: 18px;
            font-size: 14px; line-height: 1.6;
        }
        .msg-bbl.bot { background: #0d1525; color: #e2e8f0; border: 1px solid #1e293b; border-bottom-left-radius: 4px; }
        .msg-bbl.usr { background: linear-gradient(135deg, #059669, #10b981); color: #fff; border-bottom-right-radius: 4px; }"""

NEW_CHAT_CSS = """        .msg-bbl {
            max-width: 88%; padding: 16px 20px; border-radius: 18px;
            font-size: 15px; line-height: 1.75; letter-spacing: 0.01em;
            word-break: break-word;
        }
        .msg-bbl.bot {
            background: linear-gradient(135deg, #091322, #0d1a2d);
            color: #f1f5f9; border: 1px solid rgba(0, 255, 136, 0.2);
            border-bottom-left-radius: 4px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.35);
        }
        .msg-bbl.usr {
            background: linear-gradient(135deg, #059669, #10b981);
            color: #fff; font-weight: 600;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 15px rgba(16,185,129,0.3);
        }

        /* ── ELEMENTOS MODERNOS DA IA (FORMATO VISUAL PROFISSIONAL) ── */
        .ai-title {
            font-size: 16.5px; font-weight: 800; color: #00ff88;
            margin: 14px 0 8px 0; display: flex; align-items: center; gap: 8px;
            letter-spacing: 0.03em; border-bottom: 1px solid rgba(0,255,136,0.15);
            padding-bottom: 4px;
        }
        .ai-title:first-child { margin-top: 0; }
        .ai-p {
            margin: 0 0 12px 0; color: #e2e8f0; font-size: 14.5px; line-height: 1.7;
        }
        .ai-p:last-child { margin-bottom: 0; }
        .ai-list {
            margin: 10px 0 14px 0; padding-left: 0; list-style: none;
            display: flex; flex-direction: column; gap: 8px;
        }
        .ai-list-item {
            padding: 10px 14px; background: rgba(255, 255, 255, 0.035);
            border-radius: 10px; border-left: 3px solid #38bdf8;
            color: #f1f5f9; font-size: 14px; line-height: 1.6;
        }
        .ai-card {
            background: rgba(15, 23, 42, 0.8);
            border-left: 3px solid #00ff88; border-radius: 10px;
            padding: 12px 16px; margin: 12px 0;
            color: #e2e8f0; font-size: 14px; line-height: 1.65;
        }
        .ai-card.gold {
            border-left-color: #f59e0b;
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-left: 4px solid #f59e0b;
        }
        .ai-card.purple {
            border-left-color: #a855f7;
            background: rgba(168, 85, 247, 0.08);
            border: 1px solid rgba(168, 85, 247, 0.25);
            border-left: 4px solid #a855f7;
        }
        .ai-highlight { color: #38bdf8; font-weight: 700; }
        .ai-badge {
            display: inline-block; background: rgba(0, 255, 136, 0.12);
            color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.3);
            padding: 2px 8px; border-radius: 6px; font-size: 12px;
            font-weight: 800; margin-right: 6px;
        }"""

if OLD_CHAT_CSS in content:
    content = content.replace(OLD_CHAT_CSS, NEW_CHAT_CSS, 1)
    print("✅ CSS do Chat atualizado com tipografia moderna e cartões de destaque!")
else:
    print("⚠️ CSS do Chat já atualizado ou padrão diferente.")

# ─────────────────────────────────────────────────────────────────────────────
# 2. ATUALIZA JAVASCRIPT DO CHAT COM O FORMATADOR MARKDOWN/IA
# ─────────────────────────────────────────────────────────────────────────────
OLD_ENVIAR_JS = """            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pergunta })
                });
                const data = await res.json();
                botRow.querySelector('.msg-bbl.bot').innerHTML = data.resposta;
            } catch(e) {
                botRow.querySelector('.msg-bbl.bot').innerHTML = '<strong>Erro na consulta com o QG Digital.</strong>';
            }"""

NEW_ENVIAR_JS = """            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pergunta })
                });
                const data = await res.json();
                botRow.querySelector('.msg-bbl.bot').innerHTML = formatarRespostaModernaIA(data.resposta);
            } catch(e) {
                botRow.querySelector('.msg-bbl.bot').innerHTML = '<strong>Erro na consulta com o QG Digital.</strong>';
            }"""

if OLD_ENVIAR_JS in content:
    content = content.replace(OLD_ENVIAR_JS, NEW_ENVIAR_JS, 1)
    print("✅ Chamada de renderização JS atualizada para formatarRespostaModernaIA!")
else:
    print("⚠️ Chamada de renderização JS já atualizada.")

# Adiciona o parser formatarRespostaModernaIA()
PARSER_JS = """
        // ── FORMATADOR MODERNO DE RESPOSTAS DA IA (PADRÃO CHATGPT / CLAUDE) ──
        function formatarRespostaModernaIA(textoBruto) {
            if (!textoBruto) return '';
            
            // Se já vier com tags HTML completas, apenas aplica melhorias visuais
            let txt = textoBruto;

            // Remove asteriscos triplos ***texto***
            txt = txt.replace(/\\*\\*\\*(.*?)\\*\\*\\*/g, '<strong class="ai-highlight">$1</strong>');
            
            // Converte negritos **texto**
            txt = txt.replace(/\\*\\*(.*?)\\*\\*/g, '<strong class="ai-highlight">$1</strong>');

            // Separa por linhas para parsing estruturado
            const linhas = txt.split('\\n');
            let htmlFinal = '';
            let emLista = false;

            for (let i = 0; i < linhas.length; i++) {
                let linha = linhas[i].trim();
                if (!linha) {
                    if (emLista) { htmlFinal += '</ul>'; emLista = false; }
                    continue;
                }

                // Títulos (### ou ## ou #)
                if (linha.startsWith('### ') || linha.startsWith('## ') || linha.startsWith('# ')) {
                    if (emLista) { htmlFinal += '</ul>'; emLista = false; }
                    const tituloLimpo = linha.replace(/^#+\\s*/, '');
                    htmlFinal += `<div class="ai-title">📌 ${tituloLimpo}</div>`;
                    continue;
                }

                // Destaques / Recomendações Estratégicas
                if (linha.toLowerCase().includes('recomendação estratégica:') || linha.toLowerCase().includes('estratégia:') || linha.toLowerCase().includes('ação prática:')) {
                    if (emLista) { htmlFinal += '</ul>'; emLista = false; }
                    htmlFinal += `<div class="ai-card gold">💡 ${linha}</div>`;
                    continue;
                }

                // Itens de lista (1. , 2. , - , * , • )
                const matchLista = linha.match(/^(\\d+\\.|[-*•])\\s+(.*)/);
                if (matchLista) {
                    if (!emLista) { htmlFinal += '<ul class="ai-list">'; emLista = true; }
                    htmlFinal += `<li class="ai-list-item">${matchLista[2]}</li>`;
                    continue;
                }

                // Linha normal
                if (emLista) { htmlFinal += '</ul>'; emLista = false; }
                
                // Se for um bloco ou aviso
                if (linha.startsWith('👉') || linha.startsWith('📊') || linha.startsWith('🚀') || linha.startsWith('🎖️')) {
                    htmlFinal += `<div class="ai-card">${linha}</div>`;
                } else {
                    htmlFinal += `<p class="ai-p">${linha}</p>`;
                }
            }

            if (emLista) { htmlFinal += '</ul>'; }
            return htmlFinal || txt;
        }
"""

ANCHOR_JS_PARSER = "        // ── Envio da mensagem"
if "formatarRespostaModernaIA" not in content and ANCHOR_JS_PARSER in content:
    content = content.replace(ANCHOR_JS_PARSER, PARSER_JS + "\n" + ANCHOR_JS_PARSER, 1)
    print("✅ Parser formatarRespostaModernaIA inserido no script do chat!")
else:
    print("⚠️ Parser formatarRespostaModernaIA já inserido.")

# ─────────────────────────────────────────────────────────────────────────────
# 3. ATUALIZA O SYSTEM PROMPT PARA EXIGIR FORMATO VISUAL ELEGANTE
# ─────────────────────────────────────────────────────────────────────────────
OLD_PROMPT_INSTRUCT = """REGRAS ABSOLUTAS DE RESPOSTA:
- Seja ESTRITAMENTE ESTRATÉGICO, analítico, objetivo e consultivo.
- Oriente com clareza como aplicar os dados e como estruturar vídeos/roteiros de alto engajamento.
- NUNCA diga "não tenho acesso" ou "não posso verificar". Você tem domínio absoluto de todas as ferramentas e dados do sistema.
- Responda em no máximo 3 a 4 parágrafos objetivos, usando formatação limpa com tópicos quando pertinente."""

NEW_PROMPT_INSTRUCT = """FORMATO VISUAL OBRIGATÓRIO (MODERNO, SEPARADO E ELEGANTE):
- NUNCA responda em um único bloco de texto corrido ou amontoado.
- Use SEMPRE títulos de seção com marcadores (Ex: ### 📊 Análise do Cenário, ### 🔍 Perguntas Mais Frequentes, ### 💡 Recomendação Prática).
- Separe CADA pergunta ou ponto em itens de lista destacados (1., 2., 3. ou - ).
- Deixe linha em branco entre cada parágrafo e entre cada tópico.
- Destaque termos-chave e nomes em **negrito**.
- Seja direto, moderno e focado em tomada de decisão da campanha."""

if OLD_PROMPT_INSTRUCT in content:
    content = content.replace(OLD_PROMPT_INSTRUCT, NEW_PROMPT_INSTRUCT, 1)
    print("✅ Prompt do sistema atualizado para exigir respostas estruturadas com títulos e tópicos!")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 upgrade_chat_modern_ui.py executado com sucesso!")
