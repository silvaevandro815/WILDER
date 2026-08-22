#!/usr/bin/env python3
"""
add_meta_radar_ui.py — Adiciona o card de monitoramento do algoritmo da Meta na UI do Viral Lab
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILE = r"c:\Users\User\Desktop\campanha wilder\server_web_unificado.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

CARD_META_RADAR = """        <!-- RADAR DE DIRETRIZES DA META AO VIVO -->
        <div style="background:linear-gradient(135deg, rgba(124,58,237,0.12), rgba(6,182,212,0.08));border:1px solid rgba(124,58,237,0.35);border-radius:16px;padding:20px;margin-bottom:24px;">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:14px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="width:10px;height:10px;border-radius:50%;background:#a78bfa;box-shadow:0 0 10px #a78bfa;display:inline-block;animation:blink 1.2s infinite;"></span>
                    <div>
                        <span style="font-weight:800;color:#c4b5fd;font-size:14px;letter-spacing:0.04em;">🛰️ RADAR DE DIRETRIZES DA META & INSTAGRAM 2026 (AO VIVO)</span>
                        <div style="font-size:11.5px;color:#94a3b8;">Monitoramento de anúncios de Adam Mosseri, Meta Newsroom e sinais de entrega orgânica</div>
                    </div>
                </div>
                <button onclick="carregarRadarMeta()" style="background:rgba(124,58,237,0.25);border:1px solid #7c3aed;color:#c4b5fd;padding:6px 14px;border-radius:8px;font-size:11.5px;font-weight:800;cursor:pointer;">
                    🔄 Sincronizar Algoritmo
                </button>
            </div>
            <div id="metaNewsGrid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px;">
                <div style="padding:10px;color:#64748b;font-size:12px;">Sincronizando diretrizes da Meta...</div>
            </div>
        </div>
"""

ANCHOR = "        <!-- SEÇÃO 1: GERADOR DE ROTEIRO VIRAL -->"

if "RADAR DE DIRETRIZES DA META AO VIVO" not in content and ANCHOR in content:
    content = content.replace(ANCHOR, CARD_META_RADAR + "\n" + ANCHOR, 1)
    print("✅ Card do Radar Meta inserido na UI do Viral Lab!")
else:
    print("⚠️ Card já inserido ou âncora não encontrada.")

# Adiciona a função JS carregarRadarMeta() no script do Viral Lab
JS_META_LOADER = """
    // ── Carrega atualizações do algoritmo da Meta
    async function carregarRadarMeta() {
        const grid = document.getElementById('metaNewsGrid');
        try {
            const r = await fetch('/api/meta_algoritmo');
            const d = await r.json();
            const news = d.noticias_algoritmo || [];
            if (news.length === 0) {
                grid.innerHTML = '<div style="font-size:12px;color:#94a3b8;grid-column:1/-1;">✅ Algoritmo Meta operando sob as diretrizes 2026: <strong>Sends per Reach (45%)</strong>, <strong>Retenção 0-3s (30%)</strong> e <strong>ASR de Áudio (15%)</strong>.</div>';
                return;
            }
            grid.innerHTML = news.slice(0, 4).map(n => `
                <a href="${n.url}" target="_blank" style="background:#060a14;border:1px solid rgba(124,58,237,0.25);border-radius:10px;padding:10px 14px;text-decoration:none;display:block;transition:all 0.2s;" onmouseenter="this.style.borderColor='#a78bfa'" onmouseleave="this.style.borderColor='rgba(124,58,237,0.25)'">
                    <div style="font-size:12px;font-weight:700;color:#f8fafc;line-height:1.35;">${n.titulo}</div>
                    <div style="font-size:10.5px;color:#7c3aed;margin-top:4px;">📡 ${n.fonte} · ${n.data}</div>
                </a>
            `).join('');
        } catch(e) {
            grid.innerHTML = '<div style="font-size:12px;color:#94a3b8;">Monitoramento da Meta 2026 ativo.</div>';
        }
    }
"""

ANCHOR_JS = "    // ── Carrega a Matriz de Palavras Magnéticas via API"

if "carregarRadarMeta()" not in content and ANCHOR_JS in content:
    content = content.replace(ANCHOR_JS, JS_META_LOADER + "\n" + ANCHOR_JS, 1)
    print("✅ Função JS carregarRadarMeta() inserida no script!")
else:
    print("⚠️ Função JS já inserida ou âncora não encontrada.")

# Chamada no init
ANCHOR_INIT = "carregarMatriz();"
if "carregarRadarMeta();" not in content and ANCHOR_INIT in content:
    content = content.replace(ANCHOR_INIT, "carregarMatriz();\n        carregarRadarMeta();", 1)
    print("✅ Chamada de inicialização carregarRadarMeta() inserida!")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 add_meta_radar_ui.py concluído!")
