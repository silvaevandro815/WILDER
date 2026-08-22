#!/usr/bin/env python3
"""
inject_engajamento.py - Injeta o HTML_ENGAJAMENTO_LAB e as rotas de API
no server_web_unificado.py sem tocar em nada existente.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILE = r"c:\Users\User\Desktop\campanha wilder\server_web_unificado.py"

# ===========================================================================
# HTML_ENGAJAMENTO_LAB — Laboratório de Engajamento Viral
# ===========================================================================
HTML_ENGAJAMENTO_LAB = r'''
# ══════════════════════════════════════════════════════════════════════════════
# LABORATORIO DE ENGAJAMENTO VIRAL — ALGORITMO DA META 2026
# ══════════════════════════════════════════════════════════════════════════════
HTML_ENGAJAMENTO_LAB = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Viral Lab — Engajamento & Algoritmo Meta | QG Wilder 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    """ + PREMIUM_THEME_CSS + """
    <style>
        .lab-hero {
            background: linear-gradient(135deg, #1a0533 0%, #0f1929 40%, #130a2b 100%);
            border: 1px solid rgba(124,58,237,0.4);
            border-radius: 18px;
            padding: 28px 24px;
            margin-bottom: 28px;
            position: relative;
            overflow: hidden;
        }
        .lab-hero::before {
            content: "";
            position: absolute;
            top: -60px; right: -60px;
            width: 220px; height: 220px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(124,58,237,0.25), transparent 70%);
        }
        .lab-hero::after {
            content: "";
            position: absolute;
            bottom: -40px; left: -40px;
            width: 160px; height: 160px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(219,39,119,0.2), transparent 70%);
        }
        .lab-hero-title {
            font-size: clamp(20px,4vw,30px);
            font-weight: 800;
            background: linear-gradient(135deg, #a78bfa, #f472b6, #fb923c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0 0 6px 0;
            position: relative;
            z-index: 1;
        }
        .lab-hero-sub {
            font-size: 13px;
            color: #94a3b8;
            position: relative;
            z-index: 1;
            max-width: 600px;
        }
        .signal-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 18px;
            position: relative;
            z-index: 1;
        }
        .signal-pill {
            background: rgba(124,58,237,0.15);
            border: 1px solid rgba(124,58,237,0.4);
            border-radius: 30px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 700;
            color: #c4b5fd;
        }
        .signal-pill.green { background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.4); color: #6ee7b7; }
        .signal-pill.pink  { background: rgba(219,39,119,0.12); border-color: rgba(219,39,119,0.4); color: #f9a8d4; }
        .signal-pill.gold  { background: rgba(245,158,11,0.12); border-color: rgba(245,158,11,0.4); color: #fcd34d; }

        .form-section {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
        }
        .form-section h3 {
            font-size: 15px;
            font-weight: 800;
            color: #a78bfa;
            margin: 0 0 16px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 14px;
            margin-bottom: 16px;
        }
        .form-label {
            font-size: 11.5px;
            font-weight: 700;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        .form-select, .form-input, .form-textarea {
            width: 100%;
            background: #0b0f19;
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: 10px 14px;
            color: #f8fafc;
            font-size: 13.5px;
            font-family: 'Plus Jakarta Sans', sans-serif;
            box-sizing: border-box;
            outline: none;
            transition: border-color 0.2s;
        }
        .form-select:focus, .form-input:focus, .form-textarea:focus {
            border-color: #7c3aed;
        }
        .form-textarea { resize: vertical; min-height: 90px; }

        .btn-gerar {
            background: linear-gradient(135deg, #7c3aed, #db2777);
            color: #fff;
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-size: 15px;
            font-weight: 800;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: opacity 0.2s, transform 0.15s;
            width: 100%;
            justify-content: center;
        }
        .btn-gerar:hover { opacity: 0.9; transform: scale(1.01); }
        .btn-gerar:active { transform: scale(0.98); }
        .btn-gerar:disabled { opacity: 0.5; cursor: wait; }

        .btn-auditar {
            background: linear-gradient(135deg, #0f766e, #0284c7);
            color: #fff;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 800;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: opacity 0.2s;
            width: 100%;
            justify-content: center;
            margin-top: 10px;
        }
        .btn-auditar:hover { opacity: 0.88; }
        .btn-auditar:disabled { opacity: 0.5; cursor: wait; }

        .resultado-panel {
            background: linear-gradient(135deg, #0a0f1e, #10162a);
            border: 1px solid rgba(124,58,237,0.35);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            display: none;
        }
        .resultado-panel.visible { display: block; }
        .resultado-panel h3 {
            font-size: 14px;
            font-weight: 800;
            color: #a78bfa;
            margin: 0 0 16px 0;
        }

        .score-meter-wrap {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 16px;
        }
        .score-circle {
            width: 72px;
            height: 72px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            font-weight: 900;
            flex-shrink: 0;
        }
        .score-bar-wrap {
            flex: 1;
        }
        .score-bar-bg {
            height: 12px;
            border-radius: 6px;
            background: #1e293b;
            overflow: hidden;
        }
        .score-bar-fill {
            height: 100%;
            border-radius: 6px;
            transition: width 1s ease;
        }
        .score-label-row {
            display: flex;
            justify-content: space-between;
            margin-top: 5px;
            font-size: 11px;
            color: #64748b;
        }

        .roteiro-section { margin-top: 16px; }
        .roteiro-bloco {
            background: #060a14;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            font-size: 13px;
        }
        .roteiro-bloco-label {
            font-size: 11px;
            font-weight: 800;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 6px;
        }
        .roteiro-gancho { border-left: 3px solid #7c3aed; }
        .roteiro-dev    { border-left: 3px solid #0ea5e9; }
        .roteiro-cta    { border-left: 3px solid #db2777; }
        .roteiro-dir    { border-left: 3px solid #f59e0b; }

        .palavra-mag  { background: rgba(16,185,129,0.18); color: #6ee7b7; border-radius: 4px; padding: 1px 6px; font-weight: 700; }
        .palavra-palk { background: rgba(239,68,68,0.18); color: #fca5a5; border-radius: 4px; padding: 1px 6px; font-weight: 700; text-decoration: line-through; }

        .asr-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        .asr-tag {
            background: rgba(16,185,129,0.1);
            border: 1px solid rgba(16,185,129,0.3);
            color: #6ee7b7;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
        }

        .spinner { display: none; width: 18px; height: 18px; border: 3px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        .magnetic-matrix {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 14px;
            margin-bottom: 24px;
        }
        .magnetic-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 18px;
        }
        .magnetic-card h4 {
            font-size: 13px;
            font-weight: 800;
            color: #a78bfa;
            margin: 0 0 10px 0;
        }
        .magnetic-word-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .magnetic-word {
            background: rgba(16,185,129,0.1);
            border: 1px solid rgba(16,185,129,0.25);
            color: #6ee7b7;
            padding: 3px 10px;
            border-radius: 16px;
            font-size: 11.5px;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.15s;
        }
        .magnetic-word:hover { background: rgba(16,185,129,0.25); }

        .reescrita-panel {
            background: linear-gradient(135deg, #0a1425, #111827);
            border: 1px solid rgba(14,165,233,0.3);
            border-radius: 14px;
            padding: 18px;
            margin-top: 14px;
        }
        .reescrita-panel h4 {
            font-size: 13px;
            font-weight: 800;
            color: #38bdf8;
            margin: 0 0 10px 0;
        }
        .reescrita-text {
            font-size: 13px;
            color: #e2e8f0;
            line-height: 1.7;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <!-- TOP BAR (mesma nav da home) -->
    <div class="app-header">
        <div class="brand-container">
            <img src="{{ wilder_avatar }}" alt="" class="brand-avatar">
            <div>
                <h1 class="brand-title">🚀 VIRAL LAB — ENGAJAMENTO & ALGORITMO</h1>
                <p class="brand-subtitle">● Motor de Roteiros Virais para a Meta · Furar a Bolha · Goiás 2026</p>
            </div>
        </div>
        <button class="menu-toggle-btn" onclick="toggleMobileMenu()">☰ Menu</button>
        <div class="nav-links-wrapper" id="navMenuWrapper">
            <a href="/"              class="btn-nav-link">🏠 Home QG</a>
            <a href="/dashboard"     class="btn-nav-link">📊 YouTube</a>
            <a href="/radar_noticias" class="btn-nav-link">🚨 Notícias</a>
            <a href="/mapa_demandas" class="btn-nav-link">🗺️ Mapa</a>
            <a href="/eventos"       class="btn-nav-link">🎪 Eventos</a>
            <a href="/engajamento"   class="btn-nav-link active" style="background:linear-gradient(135deg,#7c3aed,#db2777);color:#fff;border-color:#7c3aed;">🚀 Viral Lab</a>
        </div>
    </div>

    <div class="main-container">

        <!-- HERO BANNER -->
        <div class="lab-hero">
            <p class="lab-hero-title">🧬 Laboratório de Engajamento Viral</p>
            <p class="lab-hero-sub">
                Gere roteiros otimizados para o <strong style="color:#f472b6;">algoritmo da Meta 2026</strong>.
                Fure a bolha de seguidores e alcance <strong style="color:#a78bfa;">eleitores indecisos, jovens e novos públicos</strong>
                através dos sinais corretos de rankeamento do Instagram Reels.
            </p>
            <div class="signal-pills">
                <span class="signal-pill">📤 #1 Sinal: Sends por Reach (DM)</span>
                <span class="signal-pill green">⏱️ Retenção 0 a 3s (Gancho Visual)</span>
                <span class="signal-pill pink">🎙️ ASR — Áudio Indexado pelo Algoritmo</span>
                <span class="signal-pill gold">👁️ OCR — Texto na Tela (5 palavras)</span>
                <span class="signal-pill">🚫 Zero Vício de Palanque</span>
            </div>
        </div>

        <!-- SEÇÃO 1: GERADOR DE ROTEIRO VIRAL -->
        <div class="form-section">
            <h3>🎬 Gerador de Roteiro Viral com IA</h3>
            <div class="form-grid">
                <div>
                    <div class="form-label">Tema / Pauta</div>
                    <select class="form-select" id="selTema">
                        <option value="saúde e filas do SUS">💊 Saúde & Filas do SUS</option>
                        <option value="jovem e primeiro emprego">🎓 Jovem & Primeiro Emprego</option>
                        <option value="transporte e Entorno do DF">🚌 Transporte & Entorno do DF</option>
                        <option value="agro e estradas do interior">🌾 Agro & Estradas do Interior</option>
                        <option value="contraste político e resultado real">⚡ Contraste Político (ACM Style)</option>
                        <option value="segurança pública">🔒 Segurança Pública</option>
                        <option value="remédio em casa e idoso">👴 Idoso & Remédio em Casa</option>
                    </select>
                </div>
                <div>
                    <div class="form-label">Estímulo Algorítmico</div>
                    <select class="form-select" id="selEstimulo">
                        <option value="furar_bolha">💥 Furar a Bolha (Jovens & Indecisos)</option>
                        <option value="dor_profunda">🩸 Indignação com Dor Real</option>
                        <option value="contraste_adversario">⚡ Contraste Cirúrgico (ACM Style)</option>
                        <option value="prova_chao">🚜 Prova de Chão (João Campos Style)</option>
                        <option value="quebra_objecao">🎯 Quebra de Objeção & Visão de Futuro</option>
                    </select>
                </div>
                <div>
                    <div class="form-label">Formato</div>
                    <select class="form-select" id="selFormato">
                        <option value="reels_30s">🎬 Reels / Shorts (20-30s)</option>
                        <option value="carrossel_retencao">📑 Carrossel Magnético</option>
                        <option value="stories_conversao">📱 Sequência de Stories</option>
                        <option value="contraste_45s">⚡ Vídeo de Contraste (45s)</option>
                    </select>
                </div>
                <div>
                    <div class="form-label">Cidade / Público-Alvo</div>
                    <input class="form-input" id="inpCidade" type="text" value="Goiânia" placeholder="Ex: Luziânia, Entorno do DF...">
                </div>
            </div>
            <button class="btn-gerar" id="btnGerar" onclick="gerarRoteiro()">
                <span class="spinner" id="spnGerar"></span>
                🚀 Gerar Roteiro Viral Agora
            </button>
        </div>

        <!-- PAINEL DE RESULTADO DO ROTEIRO -->
        <div class="resultado-panel" id="painelRoteiro">
            <h3 id="roteiroTitulo">—</h3>

            <!-- Score Viral -->
            <div class="score-meter-wrap">
                <div class="score-circle" id="scoreCircle" style="background:linear-gradient(135deg,#7c3aed,#db2777);">
                    <span id="scoreNum">—</span>
                </div>
                <div class="score-bar-wrap">
                    <div style="font-size:13px;font-weight:800;color:#e2e8f0;margin-bottom:4px;">Score de Viralidade Previsto</div>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" id="scoreBar" style="width:0%;background:linear-gradient(90deg,#7c3aed,#db2777,#f59e0b);"></div>
                    </div>
                    <div class="score-label-row"><span>0 — Bolha fechada</span><span>100 — Viral nacional</span></div>
                </div>
            </div>

            <!-- Palavras ASR -->
            <div style="font-size:12px;font-weight:800;color:#64748b;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">Palavras-chave ASR (Indexação pelo Algoritmo)</div>
            <div class="asr-tags" id="asrTags"></div>

            <!-- Blocos do roteiro -->
            <div class="roteiro-section" id="roteiroSection"></div>
        </div>

        <!-- SEÇÃO 2: AUDITOR DE ROTEIRO -->
        <div class="form-section">
            <h3>🔬 Auditor de Roteiro — Nota do Algoritmo (0 a 100)</h3>
            <p style="font-size:13px;color:#64748b;margin:0 0 14px 0;">Cole qualquer texto, ideia de vídeo ou roteiro para receber a nota do algoritmo da Meta, detectar vícios de palanque e obter uma versão reescrita otimizada.</p>
            <textarea class="form-textarea" id="taAuditoria" placeholder="Cole aqui seu roteiro, copy ou ideia de conteúdo para ser auditado pelo algoritmo da Meta..."></textarea>
            <button class="btn-auditar" id="btnAuditar" onclick="auditarRoteiro()">
                <span class="spinner" id="spnAuditoria"></span>
                🔬 Auditar Agora (Score 0–100)
            </button>
        </div>

        <!-- PAINEL DE RESULTADO DA AUDITORIA -->
        <div class="resultado-panel" id="painelAuditoria">
            <h3>📋 Resultado da Auditoria Algorítmica</h3>

            <div class="score-meter-wrap">
                <div class="score-circle" id="auditScoreCircle" style="background:linear-gradient(135deg,#0f766e,#0284c7);">
                    <span id="auditScoreNum">—</span>
                </div>
                <div class="score-bar-wrap">
                    <div style="font-size:13px;font-weight:800;color:#e2e8f0;margin-bottom:4px;" id="auditClass">—</div>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" id="auditScoreBar" style="width:0%;background:linear-gradient(90deg,#0f766e,#0284c7);"></div>
                    </div>
                    <div class="score-label-row"><span>0 — Palanque Puro</span><span>100 — Viral Orgânico</span></div>
                </div>
            </div>

            <div style="font-size:13px;color:#94a3b8;margin-bottom:14px;" id="auditDiag"></div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px;">
                <div>
                    <div class="form-label" style="margin-bottom:6px;">🔴 Palavras de Palanque (Prejudicam)</div>
                    <div id="auditPalanque" style="font-size:13px;color:#fca5a5;"></div>
                </div>
                <div>
                    <div class="form-label" style="margin-bottom:6px;">🟢 Palavras Magnéticas (Amplificam)</div>
                    <div id="auditMagneticas" style="font-size:13px;color:#6ee7b7;"></div>
                </div>
            </div>

            <div style="font-size:12px;font-weight:800;color:#64748b;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">💡 Sugestão de Gancho (0–3s)</div>
            <div class="roteiro-bloco roteiro-gancho" style="margin-bottom:12px;">
                <div id="auditGancho" style="font-size:13.5px;color:#c4b5fd;font-style:italic;"></div>
            </div>

            <div class="reescrita-panel">
                <h4>✍️ Versão Reescrita para o Algoritmo da Meta</h4>
                <div class="reescrita-text" id="auditReescrita"></div>
            </div>
        </div>

        <!-- SEÇÃO 3: MATRIZ DE PALAVRAS MAGNÉTICAS -->
        <div class="form-section">
            <h3>🧲 Matriz de Palavras Magnéticas — Goiás 2026 (Clique para copiar)</h3>
            <p style="font-size:13px;color:#64748b;margin:0 0 16px 0;">Palavras indexadas pelo ASR (reconhecimento de áudio) e OCR (texto na tela) do algoritmo da Meta. Use no roteiro, na legenda e nos primeiros 3 segundos de fala.</p>
            <div class="magnetic-matrix" id="magneticMatrix">
                <!-- preenchido via JS -->
            </div>
        </div>

        <!-- SEÇÃO 4: DICAS RÁPIDAS DO ALGORITMO -->
        <div class="form-section">
            <h3>⚡ Sinais que o Algoritmo da Meta Realmente Ranqueia (2026)</h3>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;">
                <div style="background:#060a14;border:1px solid rgba(124,58,237,0.3);border-radius:12px;padding:16px;">
                    <div style="font-size:22px;margin-bottom:8px;">📤</div>
                    <div style="font-weight:800;color:#a78bfa;font-size:14px;margin-bottom:6px;">Sends per Reach (Sinal #1)</div>
                    <div style="font-size:12.5px;color:#64748b;line-height:1.6;">A quantidade de vezes que alguém encaminha seu Reel no DM é o sinal mais poderoso. Crie conteúdo que as pessoas queiram mandar para o grupo da família.</div>
                </div>
                <div style="background:#060a14;border:1px solid rgba(16,185,129,0.3);border-radius:12px;padding:16px;">
                    <div style="font-size:22px;margin-bottom:8px;">⏱️</div>
                    <div style="font-weight:800;color:#6ee7b7;font-size:14px;margin-bottom:6px;">Retenção 0–3 segundos</div>
                    <div style="font-size:12.5px;color:#64748b;line-height:1.6;">Se o usuário não travar o scroll nos primeiros 3 segundos, o algoritmo para de distribuir. O gancho visual e a primeira fala são decisivos.</div>
                </div>
                <div style="background:#060a14;border:1px solid rgba(245,158,11,0.3);border-radius:12px;padding:16px;">
                    <div style="font-size:22px;margin-bottom:8px;">🎙️</div>
                    <div style="font-weight:800;color:#fcd34d;font-size:14px;margin-bottom:6px;">ASR — Áudio Indexado</div>
                    <div style="font-size:12.5px;color:#64748b;line-height:1.6;">A Meta transcreve o áudio do seu vídeo. Palavras como "fila do SUS", "primeiro emprego" e "remédio em casa" fazem o algoritmo distribuir no Explore para públicos que pesquisam esses temas.</div>
                </div>
                <div style="background:#060a14;border:1px solid rgba(219,39,119,0.3);border-radius:12px;padding:16px;">
                    <div style="font-size:22px;margin-bottom:8px;">👁️</div>
                    <div style="font-weight:800;color:#f9a8d4;font-size:14px;margin-bottom:6px;">OCR — Texto na Tela</div>
                    <div style="font-size:12.5px;color:#64748b;line-height:1.6;">O algoritmo lê as palavras exibidas na tela. Use no máximo 5 palavras em caixa alta no gancho: "ISSO NÃO É SAÚDE" é mais poderoso que qualquer hashtag.</div>
                </div>
                <div style="background:#060a14;border:1px solid rgba(239,68,68,0.3);border-radius:12px;padding:16px;">
                    <div style="font-size:22px;margin-bottom:8px;">🚫</div>
                    <div style="font-weight:800;color:#fca5a5;font-size:14px;margin-bottom:6px;">Vício de Palanque = Morte</div>
                    <div style="font-size:12.5px;color:#64748b;line-height:1.6;">Palavras como "reestruturação", "plano plurianual" e "caros eleitores" são detectadas pelo ASR e fazem o algoritmo rotular o conteúdo como político — distribuição limitada aos seus próprios seguidores.</div>
                </div>
                <div style="background:#060a14;border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;">
                    <div style="font-size:22px;margin-bottom:8px;">🔑</div>
                    <div style="font-weight:800;color:#93c5fd;font-size:14px;margin-bottom:6px;">Palavra-chave no DM</div>
                    <div style="font-size:12.5px;color:#64748b;line-height:1.6;">Termine todo Reel com "Comenta PALAVRA que te envio o plano". Isso gera resposta automatizada, sinal de interação e aumenta o alcance orgânico em até 3x.</div>
                </div>
            </div>
        </div>

    </div><!-- /main-container -->

    <script>
    // ── Carrega a Matriz de Palavras Magnéticas via API
    async function carregarMatriz() {
        try {
            const r = await fetch('/api/palavras_magneticas');
            const d = await r.json();
            const container = document.getElementById('magneticMatrix');
            container.innerHTML = '';
            for (const [key, val] of Object.entries(d)) {
                const card = document.createElement('div');
                card.className = 'magnetic-card';
                let palavrasHTML = val.palavras_ouro.map(p =>
                    `<span class="magnetic-word" onclick="copiarPalavra('${p}')" title="Clique para copiar">${p}</span>`
                ).join('');
                card.innerHTML = `<h4>${val.titulo}</h4><div class="magnetic-word-list">${palavrasHTML}</div>`;
                container.appendChild(card);
            }
        } catch(e) {
            document.getElementById('magneticMatrix').innerHTML = '<p style="color:#64748b">Carregando matriz...</p>';
        }
    }

    function copiarPalavra(texto) {
        navigator.clipboard.writeText(texto).then(() => {
            showToast('Copiado: ' + texto);
        });
    }

    function showToast(msg) {
        const t = document.createElement('div');
        t.textContent = msg;
        t.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:#7c3aed;color:#fff;padding:10px 20px;border-radius:10px;font-weight:700;font-size:13px;z-index:9999;animation:fadeInOut 2.5s ease forwards;';
        document.body.appendChild(t);
        setTimeout(() => t.remove(), 2600);
    }

    // ── Gerar Roteiro Viral
    async function gerarRoteiro() {
        const btn = document.getElementById('btnGerar');
        const spn = document.getElementById('spnGerar');
        btn.disabled = true;
        spn.style.display = 'inline-block';

        const payload = {
            tema:     document.getElementById('selTema').value,
            estimulo: document.getElementById('selEstimulo').value,
            formato:  document.getElementById('selFormato').value,
            cidade:   document.getElementById('inpCidade').value || 'Goiás Geral'
        };

        try {
            const r = await fetch('/api/gerar_roteiro_viral', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await r.json();
            renderRoteiro(data);
        } catch(e) {
            alert('Erro ao gerar roteiro. Tente novamente.');
        } finally {
            btn.disabled = false;
            spn.style.display = 'none';
        }
    }

    function renderRoteiro(d) {
        const painel = document.getElementById('painelRoteiro');
        painel.classList.add('visible');
        document.getElementById('roteiroTitulo').textContent = d.titulo_estrategico || 'Roteiro Gerado';

        // Score
        const score = d.score_viral_previsto || 0;
        document.getElementById('scoreNum').textContent = score;
        setTimeout(() => { document.getElementById('scoreBar').style.width = score + '%'; }, 100);
        const sc = document.getElementById('scoreCircle');
        if (score >= 85) sc.style.background = 'linear-gradient(135deg,#059669,#10b981)';
        else if (score >= 65) sc.style.background = 'linear-gradient(135deg,#d97706,#f59e0b)';
        else sc.style.background = 'linear-gradient(135deg,#dc2626,#ef4444)';

        // ASR Tags
        const asrCont = document.getElementById('asrTags');
        asrCont.innerHTML = '';
        (d.palavras_chave_meta_asr || []).forEach(p => {
            const t = document.createElement('span');
            t.className = 'asr-tag';
            t.textContent = p;
            asrCont.appendChild(t);
        });

        // Blocos do roteiro
        const sec = document.getElementById('roteiroSection');
        sec.innerHTML = '';
        const g = d.gancho_0_a_3s || {};
        sec.innerHTML += `
            <div class="roteiro-bloco roteiro-gancho">
                <div class="roteiro-bloco-label">🎬 Gancho 0–3s (Trava o Scroll)</div>
                <div style="margin-bottom:6px;"><strong style="color:#a78bfa;">📷 Visual:</strong> <span style="color:#e2e8f0;">${g.visual_camera || '—'}</span></div>
                <div style="margin-bottom:6px;"><strong style="color:#f472b6;">📺 Texto na Tela (OCR):</strong> <span style="color:#fff;font-weight:800;font-size:15px;">${g.texto_na_tela_ocr || '—'}</span></div>
                <div><strong style="color:#a78bfa;">🎤 Fala de Abertura:</strong> <span style="color:#c4b5fd;font-style:italic;">"${g.fala_abertura || '—'}"</span></div>
            </div>`;

        (d.desenvolvimento_retencao || []).forEach((dev, i) => {
            sec.innerHTML += `
                <div class="roteiro-bloco roteiro-dev">
                    <div class="roteiro-bloco-label">⏱️ Desenvolvimento ${dev.tempo || ''}</div>
                    <div style="color:#bae6fd;">${dev.acao_e_fala || ''}</div>
                </div>`;
        });

        const cta = d.fechamento_cta_dm || {};
        sec.innerHTML += `
            <div class="roteiro-bloco roteiro-cta">
                <div class="roteiro-bloco-label">📤 CTA — DM & Compartilhamento (${cta.tempo || ''})</div>
                <div style="margin-bottom:6px;color:#fda4af;font-style:italic;">"${cta.fala_final || '—'}"</div>
                <div style="margin-bottom:4px;"><strong style="color:#f9a8d4;">🔑 Palavra-Chave DM:</strong> <span style="background:#db2777;color:#fff;padding:2px 10px;border-radius:8px;font-weight:800;">${cta.palavra_chave_dm || '—'}</span></div>
                <div style="font-size:12px;color:#64748b;">💡 ${cta.motivo_compartilhamento || ''}</div>
            </div>`;

        sec.innerHTML += `
            <div class="roteiro-bloco roteiro-dir">
                <div class="roteiro-bloco-label">🎥 Direção de Cena & Figurino</div>
                <div style="color:#fde68a;">${d.direcao_cena_e_figurino || '—'}</div>
            </div>
            <div class="roteiro-bloco" style="border-left:3px solid #10b981;">
                <div class="roteiro-bloco-label">🎵 Áudio & Trilha</div>
                <div style="color:#6ee7b7;">${d.dica_audio_e_trilha || '—'}</div>
            </div>`;

        painel.scrollIntoView({behavior:'smooth', block:'start'});
    }

    // ── Auditar Roteiro
    async function auditarRoteiro() {
        const texto = document.getElementById('taAuditoria').value.trim();
        if (!texto) { alert('Cole um roteiro para auditar.'); return; }
        const btn = document.getElementById('btnAuditar');
        const spn = document.getElementById('spnAuditoria');
        btn.disabled = true;
        spn.style.display = 'inline-block';

        try {
            const r = await fetch('/api/auditar_roteiro', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({roteiro: texto})
            });
            const data = await r.json();
            renderAuditoria(data);
        } catch(e) {
            alert('Erro ao auditar. Tente novamente.');
        } finally {
            btn.disabled = false;
            spn.style.display = 'none';
        }
    }

    function renderAuditoria(d) {
        const painel = document.getElementById('painelAuditoria');
        painel.classList.add('visible');
        const score = d.score_viral || 0;
        document.getElementById('auditScoreNum').textContent = score;
        document.getElementById('auditClass').textContent = d.classificacao || '—';
        document.getElementById('auditDiag').textContent = d.diagnostico_algoritmo || '';
        setTimeout(() => { document.getElementById('auditScoreBar').style.width = score + '%'; }, 100);
        const sc = document.getElementById('auditScoreCircle');
        if (score >= 85) sc.style.background = 'linear-gradient(135deg,#059669,#10b981)';
        else if (score >= 65) sc.style.background = 'linear-gradient(135deg,#d97706,#f59e0b)';
        else sc.style.background = 'linear-gradient(135deg,#dc2626,#ef4444)';

        const pal = d.palavras_palanque_detectadas || [];
        document.getElementById('auditPalanque').innerHTML = pal.length
            ? pal.map(p => `<span class="palavra-palk">${p}</span> `).join('')
            : '<span style="color:#64748b">Nenhuma detectada ✓</span>';

        const mag = d.palavras_magneticas_detectadas || [];
        document.getElementById('auditMagneticas').innerHTML = mag.length
            ? mag.map(m => `<span class="palavra-mag">${m}</span> `).join('')
            : '<span style="color:#64748b">Nenhuma encontrada</span>';

        document.getElementById('auditGancho').textContent = d.sugestao_gancho_3s || '—';
        document.getElementById('auditReescrita').textContent = d.versao_reescrita_meta || '';
        painel.scrollIntoView({behavior:'smooth', block:'start'});
    }

    // ── Toggle Menu Mobile
    function toggleMobileMenu() {
        const m = document.getElementById('navMenuWrapper');
        m.classList.toggle('open');
    }

    // ── Init
    carregarMatriz();

    // Animação fadeInOut para toast
    const style = document.createElement('style');
    style.textContent = '@keyframes fadeInOut { 0%{opacity:0;transform:translateX(-50%) translateY(10px)} 15%{opacity:1;transform:translateX(-50%) translateY(0)} 75%{opacity:1} 100%{opacity:0} }';
    document.head.appendChild(style);
    </script>
</body>
</html>
"""

'''

# ===========================================================================
# ROTAS DE API E PÁGINA DO LABORATÓRIO
# ===========================================================================
ROTAS_ENGAJAMENTO = r'''
# ─── LABORATÓRIO DE ENGAJAMENTO VIRAL ────────────────────────────────────────
@app.route("/engajamento", methods=["GET"])
def engajamento_lab_page():
    return render_template_string(HTML_ENGAJAMENTO_LAB, wilder_avatar=WILDER_AVATAR_B64)

@app.route("/api/gerar_roteiro_viral", methods=["POST"])
def api_gerar_roteiro_viral():
    try:
        import engajamento_service as es
        data = request.json or {}
        tema     = data.get("tema", "saúde e filas do SUS")
        estimulo = data.get("estimulo", "furar_bolha")
        formato  = data.get("formato", "reels_30s")
        cidade   = data.get("cidade", "Goiás Geral")
        resultado = es.gerar_roteiro_viral_ia(tema, estimulo, formato, cidade)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/api/auditar_roteiro", methods=["POST"])
def api_auditar_roteiro():
    try:
        import engajamento_service as es
        data = request.json or {}
        texto = (data.get("roteiro") or data.get("texto") or "").strip()
        if not texto:
            return jsonify({"erro": "Envie o campo 'roteiro' com o texto para auditoria."}), 400
        resultado = es.auditar_roteiro_ia(texto)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/api/palavras_magneticas", methods=["GET"])
def api_palavras_magneticas():
    try:
        import engajamento_service as es
        return jsonify(es.PALAVRAS_MAGNETICAS_GOIAS), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

'''

# ===========================================================================
# INJEÇÃO NO ARQUIVO DO SERVER
# ===========================================================================
with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Marcador para inserir o HTML template (antes das rotas de flask)
ANCHOR_HTML = "# ROUTE HTML: RADAR NOTÍCIAS & PESQUISAS"
# Marcador para inserir as rotas (antes do if __name__)
ANCHOR_ROTAS = 'if __name__ == "__main__":'

if "HTML_ENGAJAMENTO_LAB" not in content:
    idx = content.find(ANCHOR_HTML)
    if idx != -1:
        content = content[:idx] + HTML_ENGAJAMENTO_LAB + content[idx:]
        print("OK - HTML_ENGAJAMENTO_LAB injetado")
    else:
        print("ERRO - ancora HTML nao encontrada")
else:
    print("SKIP - HTML_ENGAJAMENTO_LAB ja existe")

if "@app.route(\"/engajamento\"" not in content:
    idx2 = content.find(ANCHOR_ROTAS)
    if idx2 != -1:
        content = content[:idx2] + ROTAS_ENGAJAMENTO + content[idx2:]
        print("OK - Rotas de engajamento injetadas")
    else:
        print("ERRO - ancora rotas nao encontrada")
else:
    print("SKIP - Rotas de engajamento ja existem")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("DONE - server_web_unificado.py atualizado com sucesso!")
