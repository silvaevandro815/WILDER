with open("plano_governo_texto.txt", "r", encoding="utf-8") as f:
    text = f.read()

import re

print("=== PROPOSTAS PARA JOVENS, PRIMEIRO EMPREGO, TECNOLOGIA E EDUCAÇÃO ===")
matches = re.findall(r'.{0,100}(?:jove|primeiro emprego|estudante|capacita|tecnologia|inovação|futuro|faculdade|bolsa|crédito).{0,150}', text, re.IGNORECASE)

for m in matches[:15]:
    clean = m.replace('\n', ' ').strip()
    if len(clean) > 40:
        print("•", clean)
