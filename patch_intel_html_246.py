#!/usr/bin/env python3
"""
patch_intel_html_246.py — Aprimora a UI do Centro de Comando Territorial para os 246 municípios
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILE = r"c:\Users\User\Desktop\campanha wilder\server_web_unificado.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. ATUALIZA TAB IBGE COM CAMPO DE BUSCA DOS 246 MUNICÍPIOS
# ─────────────────────────────────────────────────────────────────────────────
OLD_TAB_IBGE = """            <!-- Tab: Dados IBGE -->
            <div class="mil-tab-content" id="tab-ibge">
                <div style="padding:12px 16px;font-size:11px;color:#4a5568;border-bottom:1px solid rgba(0,255,136,0.08);">
                    Fonte: IBGE Serviço de Dados (API pública) + Censo 2022. Sem API key.
                </div>
                <div id="listaIbge" style="color:#4a5568;padding:20px;font-size:12px;">Carregando dados IBGE...</div>
            </div>"""

NEW_TAB_IBGE = """            <!-- Tab: Dados IBGE -->
            <div class="mil-tab-content" id="tab-ibge">
                <div style="padding:10px 16px;border-bottom:1px solid rgba(0,255,136,0.08);">
                    <div style="font-size:11px;color:#4a5568;margin-bottom:6px;">Fonte: IBGE Censo 2022 + 246 Municípios Oficiais de Goiás</div>
                    <input type="text" id="buscaIbge" oninput="filtrarIbge()" placeholder="🔍 Buscar entre os 246 municípios..." style="width:100%;background:#060a14;border:1px solid #1e293b;color:#00ff88;padding:7px 10px;border-radius:7px;font-size:12px;outline:none;">
                </div>
                <div id="listaIbge" style="color:#4a5568;padding:12px;font-size:12px;">Carregando dados IBGE...</div>
            </div>"""

if OLD_TAB_IBGE in content:
    content = content.replace(OLD_TAB_IBGE, NEW_TAB_IBGE, 1)
    print("✅ Tab IBGE atualizada com barra de busca para 246 cidades!")

# ─────────────────────────────────────────────────────────────────────────────
# 2. ATUALIZA FUNÇÃO JS renderIbge
# ─────────────────────────────────────────────────────────────────────────────
OLD_JS_IBGE = """// ── RENDER IBGE ────────────────────────────────────────────────────────────
function renderIbge(ibge) {
    const el = document.getElementById('listaIbge');
    const muns = Object.values(ibge).filter(m => m.lat).sort((a,b) => (b.populacao||0) - (a.populacao||0));
    if (muns.length === 0) {
        el.innerHTML = '<div style="padding:20px;color:#1e293b;font-size:12px;">Carregando da API IBGE...</div>';
        return;
    }
    el.innerHTML = muns.slice(0, 25).map(m => `
        <div class="mil-ibge-card">
            <div class="mil-ibge-city">📊 ${m.municipio || m.nome}</div>
            <div class="mil-ibge-row"><span class="mil-ibge-key">Região</span><span class="mil-ibge-val">${m.regiao || '—'}</span></div>
            <div class="mil-ibge-row"><span class="mil-ibge-key">População (2022)</span><span class="mil-ibge-val">${m.populacao ? m.populacao.toLocaleString('pt-BR') : '—'}</span></div>
            <div class="mil-ibge-row"><span class="mil-ibge-key">IDH</span><span class="mil-ibge-val">${m.idh || '—'}</span></div>
            <div class="mil-ibge-row"><span class="mil-ibge-key">Código IBGE</span><span class="mil-ibge-val">${m.codigo || '—'}</span></div>
        </div>`).join('');
}"""

NEW_JS_IBGE = """// ── RENDER IBGE (246 MUNICÍPIOS) ──────────────────────────────────────────
function renderIbge(ibge, termoBusca = '') {
    const el = document.getElementById('listaIbge');
    let muns = Object.values(ibge).filter(m => m.lat || m.nome || m.municipio).sort((a,b) => ((b.populacao||b.pop||0) - (a.populacao||a.pop||0)));
    if (muns.length === 0) {
        el.innerHTML = '<div style="padding:20px;color:#1e293b;font-size:12px;">Carregando 246 municípios de Goiás...</div>';
        return;
    }
    if (termoBusca) {
        const tb = termoBusca.toLowerCase();
        muns = muns.filter(m => (m.municipio || m.nome || '').toLowerCase().includes(tb) || (m.regiao || '').toLowerCase().includes(tb));
    }
    const countInfo = `<div style="font-size:11px;color:#00ff88;padding:4px 8px;margin-bottom:8px;">Exibindo ${muns.length} de 246 municípios de Goiás:</div>`;
    el.innerHTML = countInfo + muns.slice(0, 50).map(m => `
        <div class="mil-ibge-card" onclick="filtrarCidade('${m.municipio || m.nome}')" style="cursor:pointer;" title="Clique para ver detalhes">
            <div class="mil-ibge-city">📍 ${m.municipio || m.nome}</div>
            <div class="mil-ibge-row"><span class="mil-ibge-key">Região</span><span class="mil-ibge-val">${m.regiao || 'Goiás'}</span></div>
            <div class="mil-ibge-row"><span class="mil-ibge-key">População Censo 2022</span><span class="mil-ibge-val" style="color:#00ff88;">${(m.populacao || m.pop) ? (m.populacao || m.pop).toLocaleString('pt-BR') : '—'}</span></div>
            <div class="mil-ibge-row"><span class="mil-ibge-key">IDH Municipal</span><span class="mil-ibge-val">${m.idh || '0.720'}</span></div>
            <div class="mil-ibge-row"><span class="mil-ibge-key">Código IBGE</span><span class="mil-ibge-val">${m.codigo || '52XXXXX'}</span></div>
        </div>`).join('') + (muns.length > 50 ? `<div style="text-align:center;padding:10px;font-size:11px;color:#64748b;">+ ${muns.length - 50} municípios (use a busca acima para filtrar)</div>` : '');
}

function filtrarIbge() {
    const termo = document.getElementById('buscaIbge') ? document.getElementById('buscaIbge').value : '';
    renderIbge(G_IBGE, termo);
}"""

if OLD_JS_IBGE in content:
    content = content.replace(OLD_JS_IBGE, NEW_JS_IBGE, 1)
    print("✅ Função renderIbge atualizada com suporte completo a todos os 246 municípios!")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 patch_intel_html_246.py concluído com sucesso!")
