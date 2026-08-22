#!/usr/bin/env python3
"""
update_server_live_routes.py — Conecta todos os novos coletores e dados ao vivo no server_web_unificado.py
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILE = r"c:\Users\User\Desktop\campanha wilder\server_web_unificado.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. ATUALIZA ROTA /eventos
# ─────────────────────────────────────────────────────────────────────────────
OLD_EVENTOS_ROUTE = """@app.route("/eventos", methods=["GET"])
def eventos_radar_page():
    return render_template_string(
        HTML_RADAR_EVENTOS,
        eventos=EVENTOS_GOIAS_2026,
        wilder_avatar=WILDER_AVATAR_B64
    )"""

NEW_EVENTOS_ROUTE = """@app.route("/eventos", methods=["GET"])
def eventos_radar_page():
    eventos_vivos = live_engine.get_eventos()
    return render_template_string(
        HTML_RADAR_EVENTOS,
        eventos=eventos_vivos,
        wilder_avatar=WILDER_AVATAR_B64
    )"""

if OLD_EVENTOS_ROUTE in content:
    content = content.replace(OLD_EVENTOS_ROUTE, NEW_EVENTOS_ROUTE, 1)
    print("✅ Rota /eventos atualizada para usar live_engine.get_eventos()")
else:
    print("⚠️ Rota /eventos já atualizada ou padrão diferente")

# ─────────────────────────────────────────────────────────────────────────────
# 2. ATUALIZA ROTA /radar_noticias
# ─────────────────────────────────────────────────────────────────────────────
OLD_RADAR_ROUTE = """@app.route("/radar_noticias", methods=["GET"])
def radar_noticias_page():
    noticias_vivas = live_engine.get_noticias()
    status_motor = live_engine.get_status()
    return render_template_string(
        HTML_RADAR_NOTICIAS,
        noticias=noticias_vivas,
        pesquisa=PESQUISA_OFICIAL_GOIAS_2026,
        wilder_avatar=WILDER_AVATAR_B64,
        status_motor=status_motor
    )"""

NEW_RADAR_ROUTE = """@app.route("/radar_noticias", methods=["GET"])
def radar_noticias_page():
    noticias_vivas = live_engine.get_noticias()
    pesquisas_vivas = live_engine.get_pesquisas()
    status_motor = live_engine.get_status()
    return render_template_string(
        HTML_RADAR_NOTICIAS,
        noticias=noticias_vivas,
        pesquisa=pesquisas_vivas.get("consolidado", PESQUISA_OFICIAL_GOIAS_2026),
        noticias_pesquisas=pesquisas_vivas.get("noticias", []),
        wilder_avatar=WILDER_AVATAR_B64,
        status_motor=status_motor
    )"""

if OLD_RADAR_ROUTE in content:
    content = content.replace(OLD_RADAR_ROUTE, NEW_RADAR_ROUTE, 1)
    print("✅ Rota /radar_noticias atualizada com pesquisas ao vivo")
else:
    print("⚠️ Rota /radar_noticias já atualizada ou padrão diferente")

# ─────────────────────────────────────────────────────────────────────────────
# 3. ATUALIZA ROTAS DE API DO MOTOR AUTÔNOMO
# ─────────────────────────────────────────────────────────────────────────────
OLD_API_BLOCK = """@app.route("/api/status", methods=["GET"])
def api_status_motor():
    return jsonify(live_engine.get_status())

@app.route("/api/noticias", methods=["GET"])
def api_noticias_ao_vivo():
    return jsonify({"noticias": live_engine.get_noticias(), "total": len(live_engine.get_noticias())})

@app.route("/api/tendencias", methods=["GET"])
def api_tendencias_ao_vivo():
    return jsonify({"tendencias": live_engine.get_tendencias(), "total": len(live_engine.get_tendencias())})

@app.route("/api/forcar_atualizacao", methods=["POST", "GET"])
def api_forcar_atualizacao():
    import threading
    threading.Thread(target=live_engine.atualizar_noticias, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_tendencias, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_yt_videos, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_yt_canais, daemon=True).start()
    return jsonify({
        "status": "sucesso",
        "mensagem": "Ciclo completo de atualização autônoma disparado em background!",
        "timestamp": live_engine._agora_str()
    })"""

NEW_API_BLOCK = """@app.route("/api/status", methods=["GET"])
def api_status_motor():
    return jsonify(live_engine.get_status())

@app.route("/api/noticias", methods=["GET"])
def api_noticias_ao_vivo():
    noticias = live_engine.get_noticias()
    return jsonify({"noticias": noticias, "total": len(noticias)})

@app.route("/api/pesquisas", methods=["GET"])
def api_pesquisas_ao_vivo():
    return jsonify(live_engine.get_pesquisas())

@app.route("/api/eventos_grandes", methods=["GET"])
def api_eventos_grandes_ao_vivo():
    eventos = live_engine.get_eventos()
    return jsonify({"eventos": eventos, "total": len(eventos)})

@app.route("/api/tendencias", methods=["GET"])
def api_tendencias_ao_vivo():
    tendencias = live_engine.get_tendencias()
    detalhadas = live_engine.get_tendencias_detalhadas()
    return jsonify({
        "tendencias": tendencias,
        "categorizadas": detalhadas,
        "total": len(tendencias)
    })

@app.route("/api/forcar_atualizacao", methods=["POST", "GET"])
def api_forcar_atualizacao():
    import threading
    threading.Thread(target=live_engine.atualizar_noticias, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_pesquisas_eleitorais, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_tendencias, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_eventos_grandes, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_yt_videos, daemon=True).start()
    threading.Thread(target=live_engine.atualizar_yt_canais, daemon=True).start()
    try:
        import intel_engine
        threading.Thread(target=intel_engine.atualizar_intel_territorial, daemon=True).start()
    except Exception:
        pass
    return jsonify({
        "status": "sucesso",
        "mensagem": "Ciclo militar completo de atualização disparado (Notícias, Pesquisas, Tendências, Eventos +500, YouTube, Intel)!",
        "timestamp": live_engine._agora_str()
    })"""

if OLD_API_BLOCK in content:
    content = content.replace(OLD_API_BLOCK, NEW_API_BLOCK, 1)
    print("✅ Bloco de rotas da API atualizado com /api/pesquisas e /api/eventos_grandes")
else:
    print("⚠️ Bloco de rotas da API já atualizado ou padrão diferente")

# ─────────────────────────────────────────────────────────────────────────────
# 4. ATUALIZA HTML_RADAR_NOTICIAS COM BOX DE SONDAGENS AO VIVO
# ─────────────────────────────────────────────────────────────────────────────
OLD_PESQUISA_TABLE_END = """                    </tbody>
                </table>
            </div>
        </div>"""

NEW_PESQUISA_TABLE_END = """                    </tbody>
                </table>
            </div>

            {% if noticias_pesquisas %}
            <div style="margin-top:16px;padding-top:14px;border-top:1px dashed rgba(245,158,11,0.35);">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <span style="width:8px;height:8px;border-radius:50%;background:var(--accent-gold);box-shadow:0 0 8px var(--accent-gold);display:inline-block;animation:blink 1.2s infinite;"></span>
                    <span style="font-size:12px;font-weight:800;color:var(--accent-gold);letter-spacing:0.06em;text-transform:uppercase;">SONDAGENS & NOTÍCIAS DE PESQUISAS DETECTADAS AO VIVO:</span>
                </div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px;">
                    {% for np in noticias_pesquisas %}
                    <a href="{{ np.url }}" target="_blank" style="background:#0b0f19;border:1px solid #1e293b;border-radius:10px;padding:10px 14px;text-decoration:none;display:block;transition:all 0.2s;" onmouseenter="this.style.borderColor='var(--accent-gold)'" onmouseleave="this.style.borderColor='#1e293b'">
                        <div style="font-size:12.5px;font-weight:700;color:#f8fafc;line-height:1.4;">{{ np.manchete }}</div>
                        <div style="font-size:11px;color:#64748b;margin-top:6px;">📰 {{ np.veiculo }} · {{ np.data }}</div>
                    </a>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </div>"""

if OLD_PESQUISA_TABLE_END in content:
    content = content.replace(OLD_PESQUISA_TABLE_END, NEW_PESQUISA_TABLE_END, 1)
    print("✅ Template HTML_RADAR_NOTICIAS atualizado com bloco de sondagens detectadas")
else:
    print("⚠️ Template HTML_RADAR_NOTICIAS já atualizado ou padrão diferente")

# ─────────────────────────────────────────────────────────────────────────────
# 5. ATUALIZA NAV DO HTML_RADAR_EVENTOS
# ─────────────────────────────────────────────────────────────────────────────
OLD_EVENTOS_NAV = """        <div class="nav-links-wrapper" id="navMenuWrapper">
            <a href="/chat" class="btn-nav-link">💬 QG Digital Chat</a>
            <a href="/dashboard" class="btn-nav-link">📊 Gestão YouTube Real</a>
            <a href="/mapa_demandas" class="btn-nav-link">🗺️ Mapa Colorido & 4 Gráficos</a>
            <a href="/radar_noticias" class="btn-nav-link">🚨 Pesquisas & Notícias</a>
        </div>"""

NEW_EVENTOS_NAV = """        <div class="nav-links-wrapper" id="navMenuWrapper">
            <a href="/" class="btn-nav-link">🏠 Home QG</a>
            <a href="/dashboard" class="btn-nav-link">📊 YouTube</a>
            <a href="/mapa_demandas" class="btn-nav-link">🗺️ Demandas</a>
            <a href="/radar_noticias" class="btn-nav-link">🚨 Notícias</a>
            <a href="/engajamento" class="btn-nav-link" style="background:linear-gradient(135deg,#7c3aed,#db2777);color:#fff;border-color:#7c3aed;">🚀 Viral Lab</a>
            <a href="/intel" class="btn-nav-link" style="background:linear-gradient(135deg,#0f172a,#1e3a4a);border-color:#00ff88;color:#00ff88;">🎖️ Intel</a>
        </div>"""

if OLD_EVENTOS_NAV in content:
    content = content.replace(OLD_EVENTOS_NAV, NEW_EVENTOS_NAV, 1)
    print("✅ Navigation bar de HTML_RADAR_EVENTOS atualizada")
else:
    print("⚠️ Navigation bar de HTML_RADAR_EVENTOS já atualizada ou padrão diferente")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 update_server_live_routes.py executado com sucesso!")
