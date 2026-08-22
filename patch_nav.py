#!/usr/bin/env python3
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FILE = r"c:\Users\User\Desktop\campanha wilder\server_web_unificado.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

ENGAJAMENTO_BTN_NAV = (
    '            <a href="/engajamento" class="btn-nav-link" '
    'style="background:linear-gradient(135deg,#7c3aed,#db2777);color:#fff;border-color:#7c3aed;">'
    '\U0001f680 Viral Lab</a>\n'
)

OLD_RADAR = (
    '            <a href="/eventos" class="btn-nav-link">\U0001f3aa Radar de 150 Eventos</a>\n'
    '        </div>\n'
    '    </div>\n'
    '\n'
    '    <div class="main-container">'
)
NEW_RADAR = (
    '            <a href="/eventos" class="btn-nav-link">\U0001f3aa Radar de 150 Eventos</a>\n'
    + ENGAJAMENTO_BTN_NAV +
    '        </div>\n'
    '    </div>\n'
    '\n'
    '    <div class="main-container">'
)
if ENGAJAMENTO_BTN_NAV in content:
    print("SKIP Patch 1 - ja aplicado")
elif OLD_RADAR in content:
    content = content.replace(OLD_RADAR, NEW_RADAR, 1)
    print("OK Patch 1 (radar_noticias nav): aplicado")
else:
    print("NAO ENCONTRADO Patch 1 - padrao nao encontrado")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch concluido.")
