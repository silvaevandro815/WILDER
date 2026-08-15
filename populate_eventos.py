import json

cidades_goias = [
    ("Goiânia", -16.6789, -49.2539, "Metropolitana"),
    ("Aparecida de Goiânia", -16.8233, -49.2439, "Metropolitana"),
    ("Anápolis", -16.3286, -48.9534, "Centro Goiano"),
    ("Rio Verde", -17.7915, -50.9201, "Sudoeste Goiano"),
    ("Luziânia", -16.2525, -47.9500, "Entorno DF"),
    ("Valparaíso de Goiás", -16.0664, -47.9758, "Entorno DF"),
    ("Itumbiara", -18.4192, -49.2147, "Sul Goiano"),
    ("Catalão", -18.1658, -47.9464, "Estrada do Ferro"),
    ("Jataí", -17.8814, -51.7144, "Sudoeste Goiano"),
    ("Formosa", -15.5372, -47.3347, "Entorno DF"),
    ("Caldas Novas", -17.7444, -48.6256, "Sul Goiano"),
    ("Trindade", -16.6492, -49.4889, "Metropolitana"),
    ("Goianésia", -15.3175, -49.1172, "Centro Goiano"),
    ("Porangatu", -13.4414, -49.1486, "Norte Goiano"),
    ("Uruaçu", -14.5247, -49.1408, "Norte Goiano"),
    ("Pirenópolis", -15.8522, -48.9592, "Centro Goiano"),
    ("Cidade de Goiás", -15.9333, -50.1403, "Oeste Goiano"),
    ("Iporá", -16.4419, -51.1178, "Oeste Goiano"),
    ("São Luís de Montes Belos", -16.5250, -50.3708, "Oeste Goiano"),
    ("Cristalina", -16.7686, -47.6139, "Entorno DF"),
    ("Mineiros", -17.5689, -52.5511, "Sudoeste Goiano"),
    ("Posse", -14.0931, -46.3694, "Nordeste Goiano"),
    ("Niquelândia", -14.4739, -48.4597, "Norte Goiano"),
    ("Morrinhos", -17.7311, -49.1006, "Sul Goiano"),
    ("Quirinópolis", -18.4483, -50.4517, "Sudoeste Goiano")
]

tipos_eventos = [
    ("Exposição Agropecuária & Pecuária", "🌾 AGRO"),
    ("Festa Religiosa e Romaria", "⛪ RELIGIOSO"),
    ("Festival Cultural & Gastronômico", "🎵 SHOW / FESTIVAL"),
    ("Encontro Político & Convenção de Lideranças", "🏛️ POLÍTICO"),
    ("Cavalgada & Encontro de Comitivas", "🐎 TRADIÇÃO / CAVALGADA")
]

eventos = []
id_evt = 1

meses = [("Agosto/2026", 31), ("Setembro/2026", 30), ("Outubro/2026", 15)]

for mes_nome, max_dias in meses:
    for cid, lat, lon, reg in cidades_goias:
        for t_nome, t_cat in tipos_eventos:
            dia = ((id_evt * 3) % max_dias) + 1
            data_str = f"{dia:02d}/{mes_nome[:2]}/2026"
            
            pub_est = 5000 + (id_evt * 1500) % 45000
            
            eventos.append({
                "id": id_evt,
                "nome": f"{t_nome} de {cid}",
                "cidade": cid,
                "regiao": reg,
                "lat": lat,
                "lon": lon,
                "data": data_str,
                "mes": mes_nome,
                "categoria": t_cat,
                "publico_estimado": f"{pub_est:,}".replace(",", ".") + " pessoas",
                "raio_meta_ads": "Raio 2km no Meta Ads",
                "estrategia_trafego": f"Anúncios hiperlocalizados para {cid} durante o evento de {t_cat}."
            })
            id_evt += 1
            if len(eventos) >= 150:
                break
        if len(eventos) >= 150:
            break
    if len(eventos) >= 150:
        break

print(f"=== TOTAL DE EVENTOS GERADOS: {len(eventos)} ===")

with open("eventos_150_goias.json", "w", encoding="utf-8") as f:
    json.dump(eventos, f, ensure_ascii=False, indent=2)
