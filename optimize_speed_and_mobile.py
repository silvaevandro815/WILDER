#!/usr/bin/env python3
"""
optimize_speed_and_mobile.py — Otimiza performance (0ms latency, prefetching) e responsividade mobile/tablet
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILE = r"c:\Users\User\Desktop\campanha wilder\server_web_unificado.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. SUBSTITUIÇÃO DE UNPKG POR CDNJS (Elimina travamentos em conexões móveis)
# ─────────────────────────────────────────────────────────────────────────────
UNPKG_BLOCK = """    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.heat/dist/leaflet-heat.js"></script>"""

CDNJS_BLOCK = """    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css"/>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.heat/0.2.0/leaflet-heat.js"></script>"""

if UNPKG_BLOCK in content:
    content = content.replace(UNPKG_BLOCK, CDNJS_BLOCK, 1)
    print("✅ CDNs unpkg.com substituídos por cdnjs.cloudflare.com ultrarrápidos!")
else:
    # Substitui ocorrências individuais se houver
    content = content.replace("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css", "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css")
    content = content.replace("https://unpkg.com/leaflet@1.9.4/dist/leaflet.js", "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js")
    content = content.replace("https://unpkg.com/leaflet.heat/dist/leaflet-heat.js", "https://cdnjs.cloudflare.com/ajax/libs/leaflet.heat/0.2.0/leaflet-heat.js")
    print("✅ Ocorrências de unpkg.com normalizadas para cdnjs!")

# ─────────────────────────────────────────────────────────────────────────────
# 2. UPGRADE DO CSS GLOBAL E ADIÇÃO DA BARRA MOBILE BOTTOM & PREFETCH
# ─────────────────────────────────────────────────────────────────────────────
OLD_THEME_CSS = """# GLOBAL PREMIM RESPONSIVE CSS & HEADER COMPONENT
PREMIUM_THEME_CSS = \"\"\"
<style>
    :root {
        --bg-main: #0b0f19;
        --bg-card: #131b2e;
        --bg-card-hover: #1c2742;
        --border-color: rgba(255, 255, 255, 0.08);
        --accent-green: #10b981;
        --accent-gold: #f59e0b;
        --accent-cyan: #38bdf8;
        --accent-purple: #8b5cf6;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }

    * { box-sizing: border-box; }
    body { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg-main); color: var(--text-primary); margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }

    /* HEADER RESPONSIVO PREMIUM */
    .app-header { background: linear-gradient(135deg, #0d1527, #131b2e); border-bottom: 1px solid rgba(245, 158, 11, 0.3); padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 9999; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
    .brand-container { display: flex; align-items: center; gap: 12px; }
    .brand-avatar { width: 44px; height: 44px; min-width: 44px; min-height: 44px; border-radius: 50%; border: 2px solid var(--accent-gold); object-fit: cover; }
    .brand-title { font-size: 16px; font-weight: 800; color: #ffffff; letter-spacing: 0.3px; margin: 0; line-height: 1.2; }
    .brand-subtitle { font-size: 11.5px; color: var(--accent-gold); font-weight: 700; margin: 2px 0 0 0; }

    /* BOTÃO HAMBÚRGUER MOBILE */
    .menu-toggle-btn { display: none; background: #1e293b; color: #fff; border: 1px solid var(--border-color); padding: 8px 12px; border-radius: 8px; font-size: 18px; cursor: pointer; }

    /* LINKS DE NAVEGAÇÃO */
    .nav-links-wrapper { display: flex; gap: 8px; align-items: center; }
    .btn-nav-link { color: #cbd5e1; text-decoration: none; font-size: 12px; font-weight: 700; background: #1e293b; padding: 8px 14px; border-radius: 8px; border: 1px solid var(--border-color); transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }
    .btn-nav-link:hover, .btn-nav-link.active { background: var(--accent-green); color: #ffffff; border-color: var(--accent-green); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }

    /* ADAPTAÇÃO RESPONSIVA PARA MOBILE & TABLET (< 900px) */
    @media (max-width: 900px) {
        .app-header { padding: 12px 16px; flex-wrap: wrap; }
        .menu-toggle-btn { display: block; }
        .nav-links-wrapper { display: none; width: 100%; flex-direction: column; gap: 8px; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border-color); }
        .nav-links-wrapper.show-mobile-menu { display: flex; }
        .btn-nav-link { width: 100%; justify-content: center; padding: 10px; font-size: 13px; }
        .brand-title { font-size: 14.5px; }
    }

    /* CONTÊINERES E TABELAS RESPONSIVAS */
    .main-container { max-width: 1280px; margin: 24px auto; padding: 0 16px; }
    .table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: 12px; border: 1px solid var(--border-color); }
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
    th { background: #0f172a; color: var(--accent-green); padding: 12px 14px; font-weight: 800; border-bottom: 2px solid var(--accent-green); white-space: nowrap; }
    td { padding: 12px 14px; border-bottom: 1px solid var(--border-color); color: #e2e8f0; }

    /* CARDS EXECUTIVOS */
    .card-panel { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 20px; margin-bottom: 24px; box-shadow: 0 6px 20px rgba(0,0,0,0.4); }
    .card-panel-title { font-size: 16px; font-weight: 800; color: var(--accent-green); border-left: 4px solid var(--accent-gold); padding-left: 10px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
</style>

<script>
    function toggleMobileMenu() {
        const wrapper = document.getElementById('navMenuWrapper');
        if (wrapper) {
            wrapper.classList.toggle('show-mobile-menu');
        }
    }
</script>\"\"\""""

NEW_THEME_CSS = """# GLOBAL PREMIM RESPONSIVE CSS & HEADER COMPONENT
PREMIUM_THEME_CSS = \"\"\"
<style>
    :root {
        --bg-main: #0b0f19;
        --bg-card: #131b2e;
        --bg-card-hover: #1c2742;
        --border-color: rgba(255, 255, 255, 0.08);
        --accent-green: #10b981;
        --accent-gold: #f59e0b;
        --accent-cyan: #38bdf8;
        --accent-purple: #8b5cf6;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }

    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    html, body {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--bg-main);
        color: var(--text-primary);
        margin: 0; padding: 0;
        -webkit-font-smoothing: antialiased;
        min-height: 100vh;
        min-height: 100dvh;
    }

    /* HEADER RESPONSIVO PREMIUM */
    .app-header {
        background: linear-gradient(135deg, #0d1527, #131b2e);
        border-bottom: 1px solid rgba(245, 158, 11, 0.3);
        padding: 12px 20px;
        display: flex; justify-content: space-between; align-items: center;
        position: sticky; top: 0; z-index: 9999;
        box-shadow: 0 4px 20px rgba(0,0,0,0.6);
    }
    .brand-container { display: flex; align-items: center; gap: 12px; }
    .brand-avatar { width: 42px; height: 42px; min-width: 42px; min-height: 42px; border-radius: 50%; border: 2px solid var(--accent-gold); object-fit: cover; }
    .brand-title { font-size: 15.5px; font-weight: 800; color: #ffffff; letter-spacing: 0.3px; margin: 0; line-height: 1.2; }
    .brand-subtitle { font-size: 11px; color: var(--accent-gold); font-weight: 700; margin: 2px 0 0 0; }

    /* BOTÃO HAMBÚRGUER MOBILE */
    .menu-toggle-btn { display: none; background: #1e293b; color: #fff; border: 1px solid var(--border-color); padding: 8px 12px; border-radius: 8px; font-size: 18px; cursor: pointer; }

    /* LINKS DE NAVEGAÇÃO DESKTOP & TABLET */
    .nav-links-wrapper { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
    .btn-nav-link { color: #cbd5e1; text-decoration: none; font-size: 11.5px; font-weight: 700; background: #1e293b; padding: 7px 12px; border-radius: 8px; border: 1px solid var(--border-color); transition: all 0.15s ease; display: inline-flex; align-items: center; gap: 5px; white-space: nowrap; }
    .btn-nav-link:hover, .btn-nav-link.active { background: var(--accent-green); color: #ffffff; border-color: var(--accent-green); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }

    /* BARRA INFERIOR MOBILE NATIVA (ANDROID & IPHONE) */
    .mobile-bottom-nav {
        display: none; position: fixed; bottom: 0; left: 0; right: 0; height: 60px;
        background: rgba(6, 12, 24, 0.96); backdrop-filter: blur(16px);
        border-top: 1px solid rgba(0, 255, 136, 0.15); z-index: 10000;
        justify-content: space-around; align-items: center; padding: 0 4px;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.5);
    }
    .mobile-bottom-link {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        gap: 3px; color: #94a3b8; text-decoration: none; font-size: 10px; font-weight: 700;
        padding: 6px 8px; border-radius: 8px; transition: all 0.15s; flex: 1; text-align: center;
    }
    .mobile-bottom-link span.icon { font-size: 18px; line-height: 1; }
    .mobile-bottom-link.active, .mobile-bottom-link:hover { color: #00ff88; }

    /* ADAPTAÇÃO RESPONSIVA PARA TABLETS (< 1024px) E SMARTPHONES (< 768px) */
    @media (max-width: 1024px) {
        .main-container { max-width: 100%; margin: 16px auto; padding: 0 14px; }
        .btn-nav-link { font-size: 11px; padding: 6px 10px; }
    }

    @media (max-width: 768px) {
        body { padding-bottom: 68px !important; }
        .app-header { padding: 10px 14px; }
        .menu-toggle-btn { display: block; }
        .nav-links-wrapper { display: none; width: 100%; flex-direction: column; gap: 6px; margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-color); }
        .nav-links-wrapper.show-mobile-menu { display: flex; }
        .btn-nav-link { width: 100%; justify-content: center; padding: 10px; font-size: 12.5px; }
        .brand-title { font-size: 13.5px; }
        .brand-avatar { width: 36px; height: 36px; min-width: 36px; min-height: 36px; }
        .mobile-bottom-nav { display: flex; }
        .card-panel { padding: 14px; margin-bottom: 16px; border-radius: 12px; }
        .main-container { padding: 0 10px; margin: 12px auto; }
    }

    /* CONTÊINERES E TABELAS RESPONSIVAS */
    .main-container { max-width: 1280px; margin: 20px auto; padding: 0 16px; }
    .table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: 12px; border: 1px solid var(--border-color); }
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
    th { background: #0f172a; color: var(--accent-green); padding: 12px 14px; font-weight: 800; border-bottom: 2px solid var(--accent-green); white-space: nowrap; }
    td { padding: 12px 14px; border-bottom: 1px solid var(--border-color); color: #e2e8f0; }

    /* CARDS EXECUTIVOS */
    .card-panel { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 20px; margin-bottom: 20px; box-shadow: 0 6px 20px rgba(0,0,0,0.4); }
    .card-panel-title { font-size: 15.5px; font-weight: 800; color: var(--accent-green); border-left: 4px solid var(--accent-gold); padding-left: 10px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
</style>

<!-- ── PREFETCH INTELIGENTE & INSTANT NAVIGATION (0ms Latência) ── -->
<script>
    function toggleMobileMenu() {
        const wrapper = document.getElementById('navMenuWrapper');
        if (wrapper) {
            wrapper.classList.toggle('show-mobile-menu');
        }
    }

    // Pré-carrega páginas no toque ou hover para que abram instantaneamente
    (function() {
        const cacheLinks = new Set();
        function prefetch(url) {
            if (!url || cacheLinks.has(url) || url.startsWith('http') || url.startsWith('#')) return;
            cacheLinks.add(url);
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = url;
            document.head.appendChild(link);
        }

        document.addEventListener('pointerenter', function(e) {
            const a = e.target.closest('a');
            if (a && a.href && a.origin === location.origin) {
                prefetch(a.pathname);
            }
        }, true);

        document.addEventListener('touchstart', function(e) {
            const a = e.target.closest('a');
            if (a && a.href && a.origin === location.origin) {
                prefetch(a.pathname);
            }
        }, { passive: true, capture: true });
    })();
</script>

<!-- ── BARRA DE NAVEGAÇÃO INFERIOR PARA SMARTPHONES ANDROID / TABLETS ── -->
<div class="mobile-bottom-nav">
    <a href="/" class="mobile-bottom-link">
        <span class="icon">💬</span>
        <span>QG Chat</span>
    </a>
    <a href="/intel" class="mobile-bottom-link">
        <span class="icon">🎖️</span>
        <span>Intel 246</span>
    </a>
    <a href="/engajamento" class="mobile-bottom-link">
        <span class="icon">🚀</span>
        <span>Viral Lab</span>
    </a>
    <a href="/radar_noticias" class="mobile-bottom-link">
        <span class="icon">🚨</span>
        <span>Notícias</span>
    </a>
    <a href="/mapa_demandas" class="mobile-bottom-link">
        <span class="icon">🗺️</span>
        <span>Demandas</span>
    </a>
</div>\"\"\""""

if OLD_THEME_CSS in content:
    content = content.replace(OLD_THEME_CSS, NEW_THEME_CSS, 1)
    print("✅ PREMIUM_THEME_CSS atualizado com Prefetch 0ms e Barra Mobile Bottom!")
else:
    print("⚠️ PREMIUM_THEME_CSS já atualizado ou não encontrado.")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 optimize_speed_and_mobile.py concluído!")
