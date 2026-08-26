#!/usr/bin/env python3
"""
inject_intel.py — Injeta a aba de Inteligência Territorial Militar no server_web_unificado.py
QG Digital Wilder Morais 2026
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILE = r"c:\Users\User\Desktop\campanha wilder\server_web_unificado.py"

# ============================================================================
# HTML DA PÁGINA DE INTELIGÊNCIA TERRITORIAL
# ============================================================================
HTML_INTEL = r'''
# ════════════════════════════════════════════════════════════════════════════
# INTELIGÊNCIA TERRITORIAL MILITAR — Monitoramento Real dos Goianos
# ════════════════════════════════════════════════════════════════════════════
HTML_INTELIGENCIA_TERRITORIAL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎖️ Intel Territorial — Centro de Comando | QG Wilder 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.heat/dist/leaflet-heat.js"></script>
    """ + PREMIUM_THEME_CSS + """
    <style>
        /* ── MILITAR OVERRIDE ────────────────────────────────────────────── */
        :root {
            --mil-green:   #00ff88;
            --mil-red:     #ff2244;
            --mil-amber:   #ffbb00;
            --mil-blue:    #00ccff;
            --mil-purple:  #aa44ff;
            --mil-bg:      #020811;
            --mil-panel:   #050e1a;
            --mil-border:  rgba(0,255,136,0.2);
        }
        body { background: var(--mil-bg) !important; }
        .mil-scan-line {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,136,0.015) 2px, rgba(0,255,136,0.015) 4px);
            pointer-events: none; z-index: 0;
        }
        .mil-content { position: relative; z-index: 1; }

        /* ── HEADER MILITAR ──────────────────────────────────────────────── */
        .mil-header {
            background: linear-gradient(135deg, #050e1a, #020811);
            border-bottom: 1px solid var(--mil-green);
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            box-shadow: 0 0 20px rgba(0,255,136,0.15);
        }
        .mil-brand {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .mil-brand img {
            width: 46px;
            height: 46px;
            border-radius: 50%;
            border: 2px solid var(--mil-green);
            box-shadow: 0 0 12px rgba(0,255,136,0.4);
        }
        .mil-title-block {}
        .mil-title-main {
            font-size: clamp(13px,2vw,18px);
            font-weight: 900;
            color: var(--mil-green);
            letter-spacing: 0.15em;
            text-transform: uppercase;
        }
        .mil-title-sub {
            font-size: 10.5px;
            color: #4a5568;
            letter-spacing: 0.08em;
        }
        .mil-status-pill {
            background: rgba(0,255,136,0.08);
            border: 1px solid var(--mil-green);
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 11.5px;
            font-weight: 800;
            color: var(--mil-green);
            letter-spacing: 0.06em;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .mil-live-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            background: var(--mil-green);
            box-shadow: 0 0 8px var(--mil-green);
            animation: blink 1s infinite;
        }
        .mil-nav {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .mil-nav-btn {
            background: rgba(0,255,136,0.05);
            border: 1px solid rgba(0,255,136,0.2);
            color: #94a3b8;
            padding: 6px 12px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 12px;
            font-weight: 700;
            transition: all 0.2s;
        }
        .mil-nav-btn:hover, .mil-nav-btn.active {
            background: rgba(0,255,136,0.15);
            border-color: var(--mil-green);
            color: var(--mil-green);
        }
        .mil-nav-btn.hot {
            background: linear-gradient(135deg,rgba(124,58,237,0.2),rgba(219,39,119,0.15));
            border-color: #7c3aed;
            color: #c4b5fd;
        }

        /* ── METRICS BAR ─────────────────────────────────────────────────── */
        .mil-metrics-bar {
            background: var(--mil-panel);
            border-bottom: 1px solid var(--mil-border);
            padding: 10px 20px;
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
            align-items: center;
        }
        .mil-metric {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .mil-metric-label {
            font-size: 9.5px;
            font-weight: 800;
            color: #4a5568;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .mil-metric-value {
            font-size: 18px;
            font-weight: 900;
            color: var(--mil-green);
            line-height: 1;
        }
        .mil-metric-value.red    { color: var(--mil-red); }
        .mil-metric-value.amber  { color: var(--mil-amber); }
        .mil-metric-value.blue   { color: var(--mil-blue); }
        .mil-sep { width: 1px; height: 40px; background: var(--mil-border); flex-shrink: 0; }

        /* ── LAYOUT ──────────────────────────────────────────────────────── */
        .mil-body {
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 0;
            height: calc(100vh - 130px);
            overflow: hidden;
        }
        @media (max-width: 900px) {
            .mil-body { grid-template-columns: 1fr; height: auto; overflow: auto; }
        }

        /* ── MAPA ────────────────────────────────────────────────────────── */
        .mil-map-area {
            position: relative;
            background: var(--mil-bg);
            border-right: 1px solid var(--mil-border);
        }
        #milMap {
            height: 100%;
            width: 100%;
            min-height: 400px;
        }
        .mil-map-controls {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .mil-ctrl-btn {
            background: rgba(5,14,26,0.92);
            border: 1px solid var(--mil-border);
            color: var(--mil-green);
            padding: 7px 13px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 800;
            cursor: pointer;
            letter-spacing: 0.05em;
            backdrop-filter: blur(4px);
            transition: all 0.2s;
        }
        .mil-ctrl-btn:hover { background: rgba(0,255,136,0.12); }
        .mil-ctrl-btn.active { background: rgba(0,255,136,0.2); border-color: var(--mil-green); }
        .mil-legend {
            position: absolute;
            bottom: 20px;
            left: 10px;
            z-index: 1000;
            background: rgba(5,14,26,0.92);
            border: 1px solid var(--mil-border);
            border-radius: 10px;
            padding: 12px 16px;
            backdrop-filter: blur(4px);
        }
        .mil-legend-title { font-size: 10px; font-weight: 800; color: var(--mil-green); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 8px; }
        .mil-legend-item { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; font-size: 11px; color: #94a3b8; }
        .mil-legend-dot { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }

        /* ── PAINEL LATERAL ──────────────────────────────────────────────── */
        .mil-side-panel {
            background: var(--mil-panel);
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }
        .mil-panel-tabs {
            display: flex;
            border-bottom: 1px solid var(--mil-border);
            background: var(--mil-bg);
            flex-shrink: 0;
        }
        .mil-tab {
            flex: 1;
            padding: 10px 6px;
            text-align: center;
            font-size: 10.5px;
            font-weight: 800;
            color: #4a5568;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .mil-tab.active {
            color: var(--mil-green);
            border-bottom-color: var(--mil-green);
            background: rgba(0,255,136,0.04);
        }
        .mil-tab-content { display: none; flex: 1; overflow-y: auto; }
        .mil-tab-content.active { display: block; }

        /* Alertas */
        .mil-alert-item {
            padding: 12px 16px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            display: flex;
            gap: 10px;
            align-items: flex-start;
        }
        .mil-alert-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            margin-top: 5px;
            flex-shrink: 0;
            box-shadow: 0 0 6px currentColor;
        }
        .mil-alert-mun { font-size: 12.5px; font-weight: 800; color: #f8fafc; }
        .mil-alert-msg { font-size: 11.5px; color: #64748b; margin-top: 3px; line-height: 1.4; }
        .mil-alert-ts  { font-size: 10px; color: #334155; margin-top: 4px; }

        /* Feed de queixas */
        .mil-queixa-item {
            padding: 11px 16px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
        }
        .mil-queixa-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
        }
        .mil-queixa-mun { font-size: 11px; font-weight: 800; color: #94a3b8; }
        .mil-queixa-badge {
            font-size: 9.5px;
            font-weight: 800;
            padding: 2px 8px;
            border-radius: 12px;
            letter-spacing: 0.05em;
        }
        .mil-queixa-text { font-size: 12px; color: #e2e8f0; line-height: 1.45; }
        .mil-queixa-meta { font-size: 10.5px; color: #334155; margin-top: 4px; }

        /* Ranking */
        .mil-rank-item {
            padding: 10px 16px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .mil-rank-num {
            font-size: 20px;
            font-weight: 900;
            color: #1e293b;
            min-width: 28px;
            text-align: right;
        }
        .mil-rank-bar-wrap { flex: 1; }
        .mil-rank-city { font-size: 12.5px; font-weight: 800; color: #f8fafc; }
        .mil-rank-reg  { font-size: 10.5px; color: #64748b; }
        .mil-rank-bar-bg { height: 5px; border-radius: 3px; background: #0f172a; margin-top: 5px; overflow: hidden; }
        .mil-rank-bar-fill { height: 100%; border-radius: 3px; transition: width 1.5s ease; }
        .mil-rank-count { font-size: 15px; font-weight: 900; min-width: 28px; text-align: right; }

        /* IBGE stats */
        .mil-ibge-card {
            margin: 10px 14px;
            background: rgba(0,255,136,0.04);
            border: 1px solid var(--mil-border);
            border-radius: 10px;
            padding: 14px;
        }
        .mil-ibge-city { font-size: 13px; font-weight: 800; color: var(--mil-green); margin-bottom: 8px; }
        .mil-ibge-row { display: flex; justify-content: space-between; font-size: 11.5px; margin-bottom: 4px; }
        .mil-ibge-key { color: #4a5568; }
        .mil-ibge-val { color: #e2e8f0; font-weight: 700; }

        /* Leaflet dark tiles */
        .leaflet-tile { filter: brightness(0.55) saturate(0.3) hue-rotate(180deg) !important; }
        .leaflet-container { background: #020811 !important; }
        .leaflet-popup-content-wrapper {
            background: #050e1a;
            border: 1px solid rgba(0,255,136,0.3);
            border-radius: 10px;
            color: #e2e8f0;
            box-shadow: 0 0 20px rgba(0,255,136,0.15);
        }
        .leaflet-popup-tip { background: #050e1a; }

        /* Animações */
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
        @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }
        .mil-pulse { animation: pulse 2s infinite; }

        /* Scrollbar estilizada */
        .mil-side-panel::-webkit-scrollbar,
        .mil-tab-content::-webkit-scrollbar { width: 4px; }
        .mil-side-panel::-webkit-scrollbar-track,
        .mil-tab-content::-webkit-scrollbar-track { background: transparent; }
        .mil-side-panel::-webkit-scrollbar-thumb,
        .mil-tab-content::-webkit-scrollbar-thumb { background: rgba(0,255,136,0.2); border-radius: 2px; }

        /* Nível de alarme */
        .nivel-0 { color: #1e293b; }
        .nivel-1 { color: #22c55e; }
        .nivel-2 { color: #eab308; }
        .nivel-3 { color: #f97316; }
        .nivel-4 { color: #ef4444; box-shadow: 0 0 8px #ef4444; }
    </style>
</head>
<body>
<div class="mil-scan-line"></div>
<div class="mil-content">

    <!-- HEADER MILITAR -->
    <div class="mil-header">
        <div class="mil-brand">
            <img src="{{ wilder_avatar }}" alt="Wilder">
            <div class="mil-title-block">
                <div class="mil-title-main">🎖️ Intel Territorial — Centro de Comando</div>
                <div class="mil-title-sub">MONITORAMENTO REAL • DADOS IBGE • RSS AO VIVO • NLP EM PORTUGUÊS • QG WILDER MORAIS 2026</div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
            <div class="mil-status-pill">
                <span class="mil-live-dot"></span>
                SISTEMA OPERACIONAL
            </div>
            <div class="mil-nav">
                <a href="/"              class="mil-nav-btn">🏠 Home</a>
                <a href="/mapa_demandas" class="mil-nav-btn">🗺️ Demandas</a>
                <a href="/radar_noticias" class="mil-nav-btn">🚨 Notícias</a>
                <a href="/dashboard"     class="mil-nav-btn">📊 YouTube</a>
                <a href="/engajamento"   class="mil-nav-btn hot">🚀 Viral Lab</a>
                <a href="/intel"         class="mil-nav-btn active">🎖️ Intel</a>
            </div>
        </div>
    </div>

    <!-- METRICS BAR -->
    <div class="mil-metrics-bar" id="metricsBar">
        <div class="mil-metric">
            <span class="mil-metric-label">Sinais Captados</span>
            <span class="mil-metric-value" id="metTotalSinais">—</span>
        </div>
        <div class="mil-sep"></div>
        <div class="mil-metric">
            <span class="mil-metric-label">Município mais Quente</span>
            <span class="mil-metric-value amber" id="metCidadeQuente">—</span>
        </div>
        <div class="mil-sep"></div>
        <div class="mil-metric">
            <span class="mil-metric-label">Pauta Dominante</span>
            <span class="mil-metric-value red" id="metPautaDom">—</span>
        </div>
        <div class="mil-sep"></div>
        <div class="mil-metric">
            <span class="mil-metric-label">Alertas Ativos</span>
            <span class="mil-metric-value" id="metAlertas">—</span>
        </div>
        <div class="mil-sep"></div>
        <div class="mil-metric">
            <span class="mil-metric-label">Municípios Mapeados</span>
            <span class="mil-metric-value blue" id="metMunicipios">—</span>
        </div>
        <div class="mil-sep"></div>
        <div class="mil-metric">
            <span class="mil-metric-label">Última Coleta</span>
            <span class="mil-metric-value" id="metUltimaColeta" style="font-size:12px;color:#64748b;">Aguardando...</span>
        </div>
        <div style="margin-left:auto;">
            <button onclick="forcarColeta(this)" style="background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);color:#00ff88;padding:8px 16px;border-radius:6px;font-size:12px;font-weight:800;cursor:pointer;letter-spacing:0.05em;">
                🔄 ATUALIZAR INTEL
            </button>
        </div>
    </div>

    <!-- CORPO PRINCIPAL: MAPA + PAINEL LATERAL -->
    <div class="mil-body">

        <!-- MAPA TÁTICO -->
        <div class="mil-map-area">
            <div id="milMap"></div>

            <!-- Controles do mapa -->
            <div class="mil-map-controls">
                <button class="mil-ctrl-btn active" id="btnModoCalor" onclick="toggleModoCalor(this)">🔥 CALOR</button>
                <button class="mil-ctrl-btn" id="btnModoMarcadores" onclick="toggleModoMarcadores(this)">📍 PINS</button>
                <button class="mil-ctrl-btn" id="btnModoRegioes" onclick="toggleModoRegioes(this)">🗺️ REGIÕES</button>
            </div>

            <!-- Legenda -->
            <div class="mil-legend">
                <div class="mil-legend-title">INTENSIDADE DE QUEIXAS</div>
                <div class="mil-legend-item"><div class="mil-legend-dot" style="background:#ef4444;"></div> CRÍTICO — Saúde / Segurança</div>
                <div class="mil-legend-item"><div class="mil-legend-dot" style="background:#f97316;"></div> ALTO — Transporte / Emprego</div>
                <div class="mil-legend-item"><div class="mil-legend-dot" style="background:#eab308;"></div> MÉDIO — Infraestrutura</div>
                <div class="mil-legend-item"><div class="mil-legend-dot" style="background:#22c55e;"></div> BAIXO — Monitorado</div>
                <div class="mil-legend-item"><div class="mil-legend-dot" style="background:#1e293b;border:1px solid #334155;"></div> SEM DADOS</div>
            </div>
        </div>

        <!-- PAINEL LATERAL -->
        <div class="mil-side-panel">
            <div class="mil-panel-tabs">
                <div class="mil-tab active" onclick="trocarTab('alertas',this)">⚡ ALERTAS</div>
                <div class="mil-tab" onclick="trocarTab('queixas',this)">📡 FEED</div>
                <div class="mil-tab" onclick="trocarTab('ranking',this)">🏆 RANKING</div>
                <div class="mil-tab" onclick="trocarTab('ibge',this)">📊 IBGE</div>
            </div>

            <!-- Tab: Alertas Táticos -->
            <div class="mil-tab-content active" id="tab-alertas">
                <div id="listaAlertas" style="color:#4a5568;padding:20px;font-size:12px;">Carregando alertas...</div>
            </div>

            <!-- Tab: Feed de Queixas -->
            <div class="mil-tab-content" id="tab-queixas">
                <div style="padding:10px 16px;">
                    <select id="filtroQueixa" onchange="renderQueixas()" style="width:100%;background:#060a14;border:1px solid #1e293b;color:#94a3b8;padding:7px 10px;border-radius:7px;font-size:12px;margin-bottom:2px;">
                        <option value="">Todas as pautas</option>
                        <option value="SAUDE">🏥 Saúde</option>
                        <option value="TRANSPORTE">🚌 Transporte</option>
                        <option value="EMPREGO">💼 Emprego</option>
                        <option value="SEGURANCA">🚨 Segurança</option>
                        <option value="INFRAESTRUTURA">🏗️ Infraestrutura</option>
                        <option value="EDUCACAO">📚 Educação</option>
                    </select>
                </div>
                <div id="listaQueixas" style="color:#4a5568;padding:20px;font-size:12px;">Carregando feed...</div>
            </div>

            <!-- Tab: Ranking de Cidades -->
            <div class="mil-tab-content" id="tab-ranking">
                <div id="listaRanking" style="color:#4a5568;padding:20px;font-size:12px;">Carregando ranking...</div>
            </div>

            <!-- Tab: Dados IBGE -->
            <div class="mil-tab-content" id="tab-ibge">
                <div style="padding:12px 16px;font-size:11px;color:#4a5568;border-bottom:1px solid rgba(0,255,136,0.08);">
                    Fonte: IBGE Serviço de Dados (API pública) + Censo 2022. Sem API key.
                </div>
                <div id="listaIbge" style="color:#4a5568;padding:20px;font-size:12px;">Carregando dados IBGE...</div>
            </div>
        </div>
    </div>

</div><!-- /mil-content -->

<script>
// ── DADOS GLOBAIS ──────────────────────────────────────────────────────────
let G_QUEIXAS   = [];
let G_MAPA_CALOR = [];
let G_ALERTAS   = [];
let G_RANKING   = [];
let G_IBGE      = {};
let G_STATUS    = {};

// ── MAPA LEAFLET ──────────────────────────────────────────────────────────
const map = L.map('milMap', {
    center: [-16.0, -49.5],
    zoom: 7,
    zoomControl: false,
    attributionControl: false
});
L.control.zoom({ position: 'bottomright' }).addTo(map);

// Tile layer escuro (Esri Dark Gray - Sem API Key)
const layerTaticoBase = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Esri, HERE &copy; OpenStreetMap',
    maxZoom: 16
});
const layerTaticoLabels = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16,
    opacity: 0.95
});
L.layerGroup([layerTaticoBase, layerTaticoLabels]).addTo(map);

let heatLayer = null;
let markerLayer = L.layerGroup().addTo(map);
let modoAtivo = 'calor';

function getNivelColor(nivel) {
    const cores = { 0:'#1e293b', 1:'#22c55e', 2:'#eab308', 3:'#f97316', 4:'#ef4444' };
    return cores[nivel] || '#1e293b';
}

function renderMapa(dados) {
    // Limpar camadas
    if (heatLayer) { map.removeLayer(heatLayer); heatLayer = null; }
    markerLayer.clearLayers();

    if (!dados || dados.length === 0) return;
    const maxQueixas = Math.max(...dados.map(d => d.total_queixas || 0)) || 1;

    if (modoAtivo === 'calor') {
        // Heatmap
        const pontos = dados
            .filter(d => d.total_queixas > 0)
            .map(d => [d.lat, d.lon, d.total_queixas / maxQueixas]);
        if (pontos.length > 0) {
            heatLayer = L.heatLayer(pontos, {
                radius: 35,
                blur: 22,
                maxZoom: 10,
                gradient: { 0.0: '#1e293b', 0.25: '#22c55e', 0.5: '#eab308', 0.75: '#f97316', 1.0: '#ef4444' }
            }).addTo(map);
        }
    }

    // Marcadores sempre visíveis (círculos)
    dados.forEach(d => {
        if (!d.lat || !d.lon) return;
        const cor = d.total_queixas > 0 ? getNivelColor(d.nivel) : '#1e293b';
        const radius = modoAtivo === 'pins' ? Math.max(4, d.total_queixas * 3 + 4) : Math.max(5, d.total_queixas * 2 + 5);

        const popupHtml = `
            <div style="font-family:'Plus Jakarta Sans',sans-serif;min-width:200px;padding:4px;">
                <div style="font-size:14px;font-weight:900;color:#00ff88;margin-bottom:6px;">
                    ${d.icone || '📍'} ${d.municipio}
                </div>
                <div style="font-size:11px;color:#64748b;margin-bottom:8px;">${d.regiao || ''}</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:11.5px;">
                    <div><span style="color:#4a5568;">Queixas:</span> <strong style="color:${cor};">${d.total_queixas}</strong></div>
                    <div><span style="color:#4a5568;">Pauta:</span> <strong style="color:${cor};">${d.pauta_dominante}</strong></div>
                    <div><span style="color:#4a5568;">Pop:</span> <strong style="color:#94a3b8;">${d.pop ? d.pop.toLocaleString('pt-BR') : '—'}</strong></div>
                    <div><span style="color:#4a5568;">Região:</span> <strong style="color:#94a3b8;">${d.regiao || '—'}</strong></div>
                </div>
                ${d.total_queixas > 0 ? '<div style="margin-top:8px;font-size:10.5px;color:#334155;">Clique para ver queixas desta cidade</div>' : ''}
            </div>`;

        const circle = L.circleMarker([d.lat, d.lon], {
            radius: radius,
            fillColor: cor,
            color: cor,
            weight: d.total_queixas > 2 ? 2 : 1,
            opacity: 0.9,
            fillOpacity: d.total_queixas > 0 ? 0.55 : 0.15
        }).bindPopup(popupHtml, { maxWidth: 260 })
          .on('click', () => filtrarCidade(d.municipio));

        markerLayer.addLayer(circle);

        // Label para cidades com queixas
        if (d.total_queixas > 0 && modoAtivo !== 'calor') {
            const label = L.divIcon({
                className: '',
                html: `<div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:10px;font-weight:800;color:${cor};text-shadow:0 0 8px #000,0 0 4px #000;white-space:nowrap;">${d.municipio}</div>`,
                iconAnchor: [-4, 6]
            });
            L.marker([d.lat, d.lon], { icon: label }).addTo(markerLayer);
        }
    });
}

function toggleModoCalor(btn) {
    modoAtivo = 'calor';
    document.querySelectorAll('.mil-ctrl-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderMapa(G_MAPA_CALOR);
}
function toggleModoMarcadores(btn) {
    modoAtivo = 'pins';
    document.querySelectorAll('.mil-ctrl-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderMapa(G_MAPA_CALOR);
}
function toggleModoRegioes(btn) {
    modoAtivo = 'regioes';
    document.querySelectorAll('.mil-ctrl-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderMapa(G_MAPA_CALOR);
}

// ── TABS ───────────────────────────────────────────────────────────────────
function trocarTab(id, el) {
    document.querySelectorAll('.mil-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.mil-tab-content').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('tab-' + id).classList.add('active');
}

// ── RENDER ALERTAS ─────────────────────────────────────────────────────────
function renderAlertas(alertas) {
    const el = document.getElementById('listaAlertas');
    if (!alertas || alertas.length === 0) {
        el.innerHTML = '<div style="padding:20px;font-size:12px;color:#1e293b;">Coletando dados... aguarde o primeiro ciclo.</div>';
        return;
    }
    el.innerHTML = alertas.map(a => `
        <div class="mil-alert-item">
            <div class="mil-alert-dot" style="background:${a.cor || '#ef4444'};color:${a.cor || '#ef4444'};"></div>
            <div>
                <div class="mil-alert-mun">${a.municipio}</div>
                <div class="mil-alert-msg">${a.mensagem}</div>
                <div class="mil-alert-ts">⏱️ ${a.timestamp}</div>
            </div>
        </div>`).join('');
}

// ── RENDER QUEIXAS ─────────────────────────────────────────────────────────
let _cidadeAtiva = '';
function filtrarCidade(cidade) {
    _cidadeAtiva = cidade;
    trocarTab('queixas', document.querySelector('.mil-tab:nth-child(2)'));
    renderQueixas();
}

function renderQueixas() {
    const el = document.getElementById('listaQueixas');
    const filtro = document.getElementById('filtroQueixa').value;
    let queixas = G_QUEIXAS.slice();
    if (_cidadeAtiva) queixas = queixas.filter(q => q.municipio === _cidadeAtiva);
    if (filtro) queixas = queixas.filter(q => q.pauta === filtro);
    if (queixas.length === 0) {
        el.innerHTML = `<div style="padding:20px;color:#1e293b;font-size:12px;">${_cidadeAtiva ? `Sem sinais em ${_cidadeAtiva}` : 'Coletando dados...'} <button onclick="_cidadeAtiva='';renderQueixas();" style="background:none;border:none;color:#00ff88;cursor:pointer;font-size:11px;">Limpar filtro</button></div>`;
        return;
    }
    el.innerHTML = (_cidadeAtiva ? `<div style="padding:8px 16px;font-size:11px;color:#00ff88;background:rgba(0,255,136,0.05);border-bottom:1px solid rgba(0,255,136,0.1);">📍 Filtrando: ${_cidadeAtiva} <button onclick="_cidadeAtiva='';renderQueixas();" style="background:none;border:none;color:#4a5568;cursor:pointer;font-size:11px;margin-left:8px;">✕ limpar</button></div>` : '') +
    queixas.slice(0, 60).map(q => `
        <div class="mil-queixa-item">
            <div class="mil-queixa-header">
                <span class="mil-queixa-mun">📍 ${q.municipio} · ${q.regiao}</span>
                <span class="mil-queixa-badge" style="background:${(q.cor||'#64748b')}22;color:${q.cor||'#64748b'};border:1px solid ${(q.cor||'#64748b')}44;">${q.icone||'📌'} ${q.pauta}</span>
            </div>
            <div class="mil-queixa-text">${q.manchete}</div>
            <div class="mil-queixa-meta">📰 ${q.fonte} · ${q.pub}</div>
        </div>`).join('');
}

// ── RENDER RANKING ──────────────────────────────────────────────────────────
function renderRanking(ranking) {
    const el = document.getElementById('listaRanking');
    if (!ranking || ranking.length === 0) {
        el.innerHTML = '<div style="padding:20px;color:#1e293b;font-size:12px;">Coletando dados...</div>';
        return;
    }
    const max = ranking[0].total || 1;
    el.innerHTML = ranking.slice(0, 20).map((r, i) => `
        <div class="mil-rank-item" onclick="filtrarCidade('${r.municipio}')" style="cursor:pointer;" onmouseenter="this.style.background='rgba(0,255,136,0.03)'" onmouseleave="this.style.background='transparent'">
            <div class="mil-rank-num" style="color:${i < 3 ? '#ef4444' : '#1e293b'};">${String(i+1).padStart(2,'0')}</div>
            <div class="mil-rank-bar-wrap">
                <div class="mil-rank-city">${r.icone||'📍'} ${r.municipio}</div>
                <div class="mil-rank-reg">${r.regiao} · Pop: ${r.pop ? r.pop.toLocaleString('pt-BR') : '—'}</div>
                <div class="mil-rank-bar-bg">
                    <div class="mil-rank-bar-fill" style="width:${(r.total/max*100).toFixed(1)}%;background:${r.cor||'#22c55e'};"></div>
                </div>
            </div>
            <div class="mil-rank-count" style="color:${r.cor||'#22c55e'};">${r.total}</div>
        </div>`).join('');
}

// ── RENDER IBGE ────────────────────────────────────────────────────────────
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
}

// ── ATUALIZAR MÉTRICAS BAR ──────────────────────────────────────────────────
function atualizarMetrics(ranking, alertas, mapaDados, status) {
    const total = ranking.reduce((acc, r) => acc + r.total, 0);
    document.getElementById('metTotalSinais').textContent = total || '—';
    document.getElementById('metCidadeQuente').textContent = ranking[0] ? ranking[0].municipio : '—';
    document.getElementById('metPautaDom').textContent = ranking[0] ? (ranking[0].icone + ' ' + ranking[0].pauta_dominante) : '—';
    document.getElementById('metAlertas').textContent = alertas.length;
    document.getElementById('metMunicipios').textContent = mapaDados.filter(m => m.total_queixas > 0).length;
    if (status && status.queixas) {
        document.getElementById('metUltimaColeta').textContent = status.queixas.atualizado;
    }
}

// ── CARREGAR TODOS OS DADOS ─────────────────────────────────────────────────
async function carregarTudo() {
    try {
        const [rQueixas, rMapa, rRanking, rIbge, rStatus] = await Promise.all([
            fetch('/api/intel_queixas').then(r => r.json()),
            fetch('/api/intel_mapa').then(r => r.json()),
            fetch('/api/intel_ranking').then(r => r.json()),
            fetch('/api/intel_ibge').then(r => r.json()),
            fetch('/api/intel_status').then(r => r.json()),
        ]);
        G_QUEIXAS    = rQueixas.queixas || [];
        G_MAPA_CALOR = rMapa.mapa_calor || [];
        G_ALERTAS    = rStatus.alertas_lista || [];
        G_RANKING    = rRanking.ranking || [];
        G_IBGE       = rIbge.ibge || {};
        G_STATUS     = rStatus;

        renderMapa(G_MAPA_CALOR);
        renderAlertas(G_ALERTAS);
        renderQueixas();
        renderRanking(G_RANKING);
        renderIbge(G_IBGE);
        atualizarMetrics(G_RANKING, G_ALERTAS, G_MAPA_CALOR, G_STATUS);
    } catch(e) {
        console.error('Erro ao carregar dados Intel:', e);
    }
}

async function forcarColeta(btn) {
    btn.textContent = '⏳ COLETANDO...';
    btn.disabled = true;
    try {
        await fetch('/api/intel_forcar', { method: 'POST' });
        await new Promise(r => setTimeout(r, 3000));
        await carregarTudo();
    } finally {
        btn.textContent = '🔄 ATUALIZAR INTEL';
        btn.disabled = false;
    }
}

// Auto-refresh a cada 5 minutos
setInterval(carregarTudo, 5 * 60 * 1000);

// Init
carregarTudo();
</script>
</body>
</html>
"""

'''

# ============================================================================
# ROTAS DA INTELIGÊNCIA TERRITORIAL
# ============================================================================
ROTAS_INTEL = r'''
# ─── INTELIGÊNCIA TERRITORIAL MILITAR ─────────────────────────────────────────
@app.route("/intel", methods=["GET"])
@app.route("/inteligencia", methods=["GET"])
def intel_page():
    return render_template_string(HTML_INTELIGENCIA_TERRITORIAL, wilder_avatar=WILDER_AVATAR_B64)

@app.route("/api/intel_queixas", methods=["GET"])
def api_intel_queixas():
    try:
        import intel_engine
        return jsonify({"queixas": intel_engine.get_queixas(), "total": len(intel_engine.get_queixas())}), 200
    except Exception as e:
        return jsonify({"queixas": [], "total": 0, "erro": str(e)}), 200

@app.route("/api/intel_mapa", methods=["GET"])
def api_intel_mapa():
    try:
        import intel_engine
        return jsonify({"mapa_calor": intel_engine.get_mapa_calor()}), 200
    except Exception as e:
        return jsonify({"mapa_calor": [], "erro": str(e)}), 200

@app.route("/api/intel_ibge", methods=["GET"])
def api_intel_ibge():
    try:
        import intel_engine
        ibge_data = intel_engine.get_ibge()
        # Se ainda vazio, retorna tabela base offline
        if not ibge_data:
            muns = intel_engine.get_municipios_base()
            ibge_data = {m["codigo"]: m for m in muns}
        return jsonify({"ibge": ibge_data, "total": len(ibge_data)}), 200
    except Exception as e:
        return jsonify({"ibge": {}, "erro": str(e)}), 200

@app.route("/api/intel_ranking", methods=["GET"])
def api_intel_ranking():
    try:
        import intel_engine
        return jsonify({"ranking": intel_engine.get_ranking_cidades()}), 200
    except Exception as e:
        return jsonify({"ranking": [], "erro": str(e)}), 200

@app.route("/api/intel_status", methods=["GET"])
def api_intel_status():
    try:
        import intel_engine
        status = intel_engine.get_status_intel()
        status["alertas_lista"] = intel_engine.get_alertas()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"motor": "INICIALIZANDO", "erro": str(e)}), 200

@app.route("/api/intel_forcar", methods=["POST", "GET"])
def api_intel_forcar():
    try:
        import intel_engine
        import threading
        threading.Thread(target=intel_engine.atualizar_intel_territorial, daemon=True).start()
        return jsonify({"status": "ok", "mensagem": "Coleta de inteligência territorial disparada!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

'''

# ============================================================================
# INJEÇÃO
# ============================================================================
with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Inject HTML template
ANCHOR_HTML = "# ══════════════════════════════════════════════════════════════════════════════\n# LABORATORIO DE ENGAJAMENTO VIRAL"
if "HTML_INTELIGENCIA_TERRITORIAL" not in content:
    idx = content.find(ANCHOR_HTML)
    if idx != -1:
        content = content[:idx] + HTML_INTEL + content[idx:]
        print("OK - HTML_INTELIGENCIA_TERRITORIAL injetado")
    else:
        # fallback: insere antes das rotas
        ANCHOR2 = "# ─── LABORATÓRIO DE ENGAJAMENTO VIRAL"
        idx2 = content.find(ANCHOR2)
        if idx2 != -1:
            content = content[:idx2] + HTML_INTEL + content[idx2:]
            print("OK - HTML_INTELIGENCIA_TERRITORIAL injetado (fallback anchor)")
        else:
            print("ERRO - nenhum anchor HTML encontrado")
else:
    print("SKIP - HTML_INTELIGENCIA_TERRITORIAL ja existe")

# Inject routes
ANCHOR_ROTAS = "@app.route(\"/engajamento\", methods=[\"GET\"])"
if "@app.route(\"/intel\"" not in content:
    idx3 = content.find(ANCHOR_ROTAS)
    if idx3 != -1:
        content = content[:idx3] + ROTAS_INTEL + content[idx3:]
        print("OK - Rotas Intel injetadas")
    else:
        print("ERRO - anchor de rotas nao encontrado")
else:
    print("SKIP - Rotas Intel ja existem")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("DONE - inject_intel.py concluido.")
