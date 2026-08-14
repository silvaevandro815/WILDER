import json
import random

cidades_goias = [
    {"nome": "Goiânia", "regiao": "Metropolitana", "lat": -16.6789, "lon": -49.2539, "peso": 15},
    {"nome": "Aparecida de Goiânia", "regiao": "Metropolitana", "lat": -16.8233, "lon": -49.2439, "peso": 10},
    {"nome": "Anápolis", "regiao": "Centro Goiano", "lat": -16.3286, "lon": -48.9534, "peso": 10},
    {"nome": "Rio Verde", "regiao": "Sudoeste Goiano", "lat": -17.7915, "lon": -50.9201, "peso": 8},
    {"nome": "Luziânia", "regiao": "Entorno do DF", "lat": -16.2525, "lon": -47.9500, "peso": 7},
    {"nome": "Águas Lindas de Goiás", "regiao": "Entorno do DF", "lat": -15.7622, "lon": -48.2831, "peso": 6},
    {"nome": "Valparaíso de Goiás", "regiao": "Entorno do DF", "lat": -16.0664, "lon": -47.9758, "peso": 5},
    {"nome": "Trindade", "regiao": "Metropolitana", "lat": -16.6508, "lon": -49.4889, "peso": 8},
    {"nome": "Itumbiara", "regiao": "Sul Goiano", "lat": -18.4192, "lon": -49.2147, "peso": 5},
    {"nome": "Jataí", "regiao": "Sudoeste Goiano", "lat": -17.8814, "lon": -51.7144, "peso": 5},
    {"nome": "Formosa", "regiao": "Entorno do DF", "lat": -15.5372, "lon": -47.3339, "peso": 5},
    {"nome": "Catalão", "regiao": "Estrada do Ferro", "lat": -18.1658, "lon": -47.9464, "peso": 5},
    {"nome": "Caldas Novas", "regiao": "Sul Goiano", "lat": -17.7444, "lon": -48.6250, "peso": 6},
    {"nome": "Goianésia", "regiao": "Centro Goiano", "lat": -15.3175, "lon": -49.1172, "peso": 4},
    {"nome": "Cidade de Goiás", "regiao": "Noroeste Goiano", "lat": -15.9333, "lon": -50.1400, "peso": 4},
    {"nome": "Porangatu", "regiao": "Norte Goiano", "lat": -13.4408, "lon": -49.1478, "peso": 4},
    {"nome": "Uruaçu", "regiao": "Norte Goiano", "lat": -14.5247, "lon": -49.1414, "peso": 3},
    {"nome": "Iporá", "regiao": "Oeste Goiano", "lat": -16.4419, "lon": -51.1178, "peso": 3},
    {"nome": "Posse", "regiao": "Nordeste Goiano", "lat": -14.0931, "lon": -46.3694, "peso": 3},
    {"nome": "Mineiros", "regiao": "Sudoeste Goiano", "lat": -17.5686, "lon": -52.5511, "peso": 4}
]

categorias = [
    {"tipo": "⛪ RELIGIOSO", "nomes": ["Festa do Padroeiro e Romaria", "Encontro Gospel de Fé & Esperança", "Marcha para Jesus & Avivamento", "Congresso de Mulheres e Família", "Festa de Nossa Senhora D'Abadia"], "pauta": "Família Protegida & Valores da Comunidade"},
    {"tipo": "🌾 AGROPECUÁRIO / ECONÔMICO", "nomes": ["Exposição Agropecuária & Torneio Leiteiro", "Feira de Negócios e Inovação do Agro", "Festa do Peão e Rodeio Show", "Encontro de Produtores e Tecnologia Agrícola", "Feira da Indústria e Comércio"], "pauta": "Logística Agro, Pontes e Menos Burocracia"},
    {"tipo": "🎭 CULTURAL / SHOWS", "nomes": ["Festival de Música e Gastronomia Goiana", "CarnaGoiás e Encontro de Blocos", "Festival da Cultura Tradicional e Arte", "ExpoShow Sertanejo & Gastronomia", "Feira da Economia Criativa"], "pauta": "HUB de Inovação, Cultura e Turismo que Gera Renda"},
    {"tipo": "🎓 UNIVERSITÁRIO / ESPORTIVO", "nomes": ["Jogos Universitários e Integração", "Corrida de Rua e Vida Saudável", "Copa Regional de Futebol e Atletismo", "Encontro de Jovens Empreendedores", "Hackathon e Feira de Carreiras"], "pauta": "Programa Primeiro Salário & Primeiro Emprego"},
    {"tipo": "🏥 SAÚDE / SOCIAL", "nomes": ["Mutirão de Saúde e Cuidado com a Mãe", "Feira de Ação Social e Terceira Idade", "Caravana da Cidadania e Atendimento", "Encontro Regional de Mães Trabalhadoras", "Feira de Oportunidades e Cursos"], "pauta": "Saúde Fila Visível & Moradia Digna"}
]

def gerar_eventos_completos():
    eventos = []

    # AGOSTO 2026 (50 EVENTOS)
    for i in range(1, 51):
        cidade = random.choice(cidades_goias)
        cat = random.choice(categorias)
        nome_evento = f"{random.choice(cat['nomes'])} de {cidade['nome']}"
        dia_ini = random.randint(1, 25)
        dia_fim = dia_ini + random.randint(1, 4)
        data_ini_str = f"{dia_ini:02d}/08/2026"
        data_fim_str = f"{min(dia_fim, 31):02d}/08/2026"
        publico_num = random.randint(5, 50) * 100
        
        eventos.append({
            "id": f"AGO_{i:03d}",
            "mes": "agosto",
            "mes_rotulo": "Agosto 2026",
            "data_inicio": data_ini_str,
            "data_fim": data_fim_str,
            "periodo_datas": f"{data_ini_str} a {data_fim_str}",
            "evento": nome_evento,
            "categoria": cat["tipo"],
            "cidade": cidade["nome"],
            "regiao": cidade["regiao"],
            "local": f"Parque/Praça Central de {cidade['nome']} - GO",
            "coordenadas": f"{cidade['lat']:.4f}, {cidade['lon']:.4f}",
            "raio_anuncio": f"Raio de 2km em volta de {cidade['nome']}",
            "publico_estimado": f"{publico_num:,} pessoas".replace(",", "."),
            "perfil_publico": f"Eleitores de {cidade['nome']} e região {cidade['regiao']}.",
            "pauta_plano": cat["pauta"],
            "copy_trafego": f"Quem vive em {cidade['nome']} merece respeito e desenvolvimento! Conheça o Plano de Governo de Wilder Morais.",
            "interesses_meta": f"{cidade['nome']}, {cidade['regiao']}, {cat['tipo'].split()[1]}"
        })

    # SETEMBRO 2026 (50 EVENTOS)
    for i in range(1, 51):
        cidade = random.choice(cidades_goias)
        cat = random.choice(categorias)
        nome_evento = f"{random.choice(cat['nomes'])} de {cidade['nome']}"
        dia_ini = random.randint(1, 24)
        dia_fim = dia_ini + random.randint(1, 4)
        data_ini_str = f"{dia_ini:02d}/09/2026"
        data_fim_str = f"{min(dia_fim, 30):02d}/09/2026"
        publico_num = random.randint(5, 50) * 100
        
        eventos.append({
            "id": f"SET_{i:03d}",
            "mes": "setembro",
            "mes_rotulo": "Setembro 2026",
            "data_inicio": data_ini_str,
            "data_fim": data_fim_str,
            "periodo_datas": f"{data_ini_str} a {data_fim_str}",
            "evento": nome_evento,
            "categoria": cat["tipo"],
            "cidade": cidade["nome"],
            "regiao": cidade["regiao"],
            "local": f"Centro de Convenções / Espaço de Eventos de {cidade['nome']} - GO",
            "coordenadas": f"{cidade['lat']:.4f}, {cidade['lon']:.4f}",
            "raio_anuncio": f"Raio de 2.5km em volta de {cidade['nome']}",
            "publico_estimado": f"{publico_num:,} pessoas".replace(",", "."),
            "perfil_publico": f"População trabalhadora de {cidade['nome']}.",
            "pauta_plano": cat["pauta"],
            "copy_trafego": f"Atenção {cidade['nome']}! Wilder Morais traz soluções reais para a saúde, primeiro emprego e infraestrutura de Goiás.",
            "interesses_meta": f"{cidade['nome']}, {cidade['regiao']}, {cat['tipo'].split()[1]}"
        })

    # OUTUBRO 2026 (50 EVENTOS)
    for i in range(1, 51):
        cidade = random.choice(cidades_goias)
        cat = random.choice(categorias)
        nome_evento = f"Grande Mobilização & {random.choice(cat['nomes'])} de {cidade['nome']}"
        dia_ini = random.randint(1, 24)
        dia_fim = dia_ini + random.randint(1, 3)
        data_ini_str = f"{dia_ini:02d}/10/2026"
        data_fim_str = f"{min(dia_fim, 31):02d}/10/2026"
        publico_num = random.randint(8, 60) * 100
        
        eventos.append({
            "id": f"OUT_{i:03d}",
            "mes": "outubro",
            "mes_rotulo": "Outubro 2026 (Reta Final)",
            "data_inicio": data_ini_str,
            "data_fim": data_fim_str,
            "periodo_datas": f"{data_ini_str} a {data_fim_str}",
            "evento": nome_evento,
            "categoria": cat["tipo"],
            "cidade": cidade["nome"],
            "regiao": cidade["regiao"],
            "local": f"Avenida Principal / Centro de {cidade['nome']} - GO",
            "coordenadas": f"{cidade['lat']:.4f}, {cidade['lon']:.4f}",
            "raio_anuncio": f"Raio de 3km em volta do centro de {cidade['nome']}",
            "publico_estimado": f"{publico_num:,} pessoas".replace(",", "."),
            "perfil_publico": f"Eleitores em decisão de voto em {cidade['nome']}.",
            "pauta_plano": "Goiás Para Quem Faz (Decisão Eleitoral)",
            "copy_trafego": f"Chegou a hora {cidade['nome']}! Vote Wilder Morais Governador e Ana Paula Vice. Trabalho e Oportunidade!",
            "interesses_meta": f"{cidade['nome']}, Eleições Goiás, Wilder Morais"
        })

    print(f"=== GERADOS {len(eventos)} EVENTOS ROBUSTOS PARA GOIAS (50 AGO / 50 SET / 50 OUT) ===")
    return eventos

if __name__ == "__main__":
    evs = gerar_eventos_completos()
    with open("eventos_goias_base.json", "w", encoding="utf-8") as f:
        json.dump(evs, f, ensure_ascii=False, indent=2)
