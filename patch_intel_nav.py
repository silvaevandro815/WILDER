#!/usr/bin/env python3
"""
patch_intel_nav.py — Adiciona link 🎖️ Intel em todas as navs do sistema
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILE = r"c:\Users\User\Desktop\campanha wilder\server_web_unificado.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

INTEL_BTN_TOP = '            <a href="/intel"      class="nav-icon-btn" style="background:linear-gradient(135deg,#0f172a,#1e3a4a);border:1px solid #00ff88;color:#00ff88;">\U0001f3d6\ufe0f Intel</a>\n'
INTEL_BTN_STORY = '        <a href="/intel" class="story-item">\n            <div class="story-ring" style="background:linear-gradient(135deg,#001a0a,#00ff8844);border:2px solid #00ff88;"><div class="story-ring-inner">\U0001f3d6\ufe0f</div></div>\n            <span class="story-label">Intel</span>\n        </a>\n'
INTEL_BTN_DRAWER = '            <a href="/intel"        class="drawer-link" style="background:linear-gradient(135deg,rgba(0,255,136,0.08),rgba(0,200,100,0.05));border-color:#00ff8840;color:#00ff88;">\U0001f3d6\ufe0f Centro de Inteligência</a>\n'

patches = [
    # 1. Top nav bar
    (
        '            <a href="/engajamento"  class="nav-icon-btn" style="background:linear-gradient(135deg,#7c3aed,#db2777);color:#fff;">\U0001f680 Engajamento</a>\n'
        '            <a href="/download_pdf" target="_blank" class="nav-icon-btn">\U0001f4c4 PDF 360\u00b0</a>',
        '            <a href="/engajamento"  class="nav-icon-btn" style="background:linear-gradient(135deg,#7c3aed,#db2777);color:#fff;">\U0001f680 Engajamento</a>\n'
        + INTEL_BTN_TOP +
        '            <a href="/download_pdf" target="_blank" class="nav-icon-btn">\U0001f4c4 PDF 360\u00b0</a>',
        "top nav bar"
    ),
    # 2. Stories bar
    (
        '        <a href="/engajamento" class="story-item">\n'
        '            <div class="story-ring" style="background:linear-gradient(135deg,#7c3aed,#db2877)"><div class="story-ring-inner">\U0001f680</div></div>\n'
        '            <span class="story-label">Viral Lab</span>\n'
        '        </a>\n'
        '    </div>',
        '        <a href="/engajamento" class="story-item">\n'
        '            <div class="story-ring" style="background:linear-gradient(135deg,#7c3aed,#db2877)"><div class="story-ring-inner">\U0001f680</div></div>\n'
        '            <span class="story-label">Viral Lab</span>\n'
        '        </a>\n'
        + INTEL_BTN_STORY +
        '    </div>',
        "stories bar"
    ),
    # 3. Mobile drawer
    (
        '            <a href="/engajamento"    class="drawer-link" style="background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(219,39,119,0.1));border-color:#7c3aed;">\U0001f680 Engajamento Viral Lab</a>\n'
        '            <a href="/download_pdf" target="_blank" class="drawer-link">\U0001f4c4 PDF 360\u00b0 Completo</a>',
        '            <a href="/engajamento"    class="drawer-link" style="background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(219,39,119,0.1));border-color:#7c3aed;">\U0001f680 Engajamento Viral Lab</a>\n'
        + INTEL_BTN_DRAWER +
        '            <a href="/download_pdf" target="_blank" class="drawer-link">\U0001f4c4 PDF 360\u00b0 Completo</a>',
        "mobile drawer"
    ),
]

for old, new, nome in patches:
    if old in content and INTEL_BTN_TOP.strip() not in content:
        content = content.replace(old, new, 1)
        print(f"OK - {nome} atualizado")
    elif INTEL_BTN_TOP.strip() in content:
        print(f"SKIP - {nome} ja atualizado")
    else:
        print(f"NAO ENCONTRADO - {nome}")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_intel_nav.py concluido.")
