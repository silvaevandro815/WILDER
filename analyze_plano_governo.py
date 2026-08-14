with open("plano_governo_texto.txt", "r", encoding="utf-8") as f:
    text = f.read()

import re

print("=== ESTRUTURA DO PLANO DE GOVERNO (TÍTULOS E SEÇÕES) ===")
titles = re.findall(r'\n([0-9]\.?\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]{4,60})\n', text)
for t in set(titles):
    if len(t.strip()) > 3:
        print("•", t.strip())

print("\n=== RESUMO DOS 5 PILARES E MARCAS DA CAMPANHA ===")
lines = text.split("\n")
for line in lines:
    if any(k in line.lower() for k in ["pilar", "eixo", "marca", "prioridade", "compromisso", "saúde", "emprego", "jovem", "educação", "segurança", "entorno"]):
        if len(line.strip()) > 30 and len(line.strip()) < 120:
            print("->", line.strip())
