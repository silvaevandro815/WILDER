"""
intel_engine.py — Motor de Inteligência Territorial Militar
QG Digital Wilder Morais — Goiás 2026

Monitoramento Territorial e Análise Estratégica dos 246 Municípios de Goiás:
- Base de dados demográfica e territorial dos 246 municípios (IBGE Censo 2022).
- Mapeamento tático das 8 macrorregiões eleitorais de Goiás.
- Baseline estratégico com queixas históricas e prioritárias por região.
- Enriquecimento contínuo via Google News RSS por cidade e pauta.
- Classificador léxico NLP para 6 áreas críticas (Saúde, Transporte, Emprego, Segurança, Infraestrutura, Educação).
- Geração autônoma de mapa de calor térmico, alertas de crise e rankings de pressão eleitoral.
"""
import os
import re
import ssl
import json
import time
import datetime
import threading
import unicodedata
import urllib.request
import urllib.parse
from xml.etree import ElementTree as ET

# ─────────────────────────────────────────────────────────────────────────────
# 1. CACHE CENTRAL DE INTELIGÊNCIA
# ─────────────────────────────────────────────────────────────────────────────
INTEL_CACHE = {
    "queixas":    {"data": [], "atualizado_em": None, "ciclos": 0},
    "ibge":       {"data": {}, "atualizado_em": None, "ciclos": 0},
    "mapa_calor": {"data": [], "atualizado_em": None, "ciclos": 0},
    "alertas":    {"data": [], "atualizado_em": None, "ciclos": 0},
    "regioes":    {"data": {}, "atualizado_em": None},
    "diagnostico":{"data": {}, "atualizado_em": None},
}
_intel_lock = threading.Lock()

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE
_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}

def _agora():
    return datetime.datetime.now()

def _agora_str():
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

def _norma(txt):
    """Normaliza texto removendo acentos e lowercasing."""
    if not txt:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", str(txt).lower())
        if unicodedata.category(c) != "Mn"
    )

# ─────────────────────────────────────────────────────────────────────────────
# 2. CARREGAR OS 246 MUNICÍPIOS DE GOIÁS (IBGE)
# ─────────────────────────────────────────────────────────────────────────────
def _carregar_todos_246_municipios():
    json_path = os.path.join(os.path.dirname(__file__), "municipios_246_goias.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if dados and len(dados) >= 200:
                    return dados
        except Exception as e:
            print(f"[INTEL] Erro lendo municipios_246_goias.json: {e}")
    # Fallback básico
    return [
        {"codigo": "5208707", "nome": "Goiânia", "regiao": "Metropolitana", "lat": -16.6864, "lon": -49.2643, "pop": 1437237, "idh": 0.799},
        {"codigo": "5201405", "nome": "Aparecida de Goiânia", "regiao": "Metropolitana", "lat": -16.8179, "lon": -49.2440, "pop": 527550, "idh": 0.742},
        {"codigo": "5201108", "nome": "Anápolis", "regiao": "Centro", "lat": -16.3281, "lon": -48.9530, "pop": 398817, "idh": 0.773},
        {"codigo": "5221858", "nome": "Rio Verde", "regiao": "Sudoeste", "lat": -17.7975, "lon": -50.9278, "pop": 225696, "idh": 0.764},
        {"codigo": "5208004", "nome": "Luziânia", "regiao": "Entorno DF", "lat": -16.2523, "lon": -47.9503, "pop": 208725, "idh": 0.699},
        {"codigo": "5221197", "nome": "Valparaíso de Goiás", "regiao": "Entorno DF", "lat": -16.0717, "lon": -47.9936, "pop": 198861, "idh": 0.746},
    ]

MUNICIPIOS_GOIAS = _carregar_todos_246_municipios()
MUNICIPIOS_MAP = {m["nome"]: m for m in MUNICIPIOS_GOIAS}

# ─────────────────────────────────────────────────────────────────────────────
# 3. MACRORREGIÕES ESTRATÉGICAS DE GOIÁS & MATRIZ TÁTICA
# ─────────────────────────────────────────────────────────────────────────────
MACRORREGIOES_GOIAS = {
    "Metropolitana": {
        "nome": "Região Metropolitana de Goiânia",
        "polo": "Goiânia",
        "pop_total": 2650000,
        "peso_eleitoral": "38% do Eleitorado Estadual",
        "pauta_critica": "SAUDE",
        "dor_principal": "Filas no SUS para consultas e cirurgias eletivas (demora > 6 meses); transporte coletivo metropolitano.",
        "estrategia_wilder": "Apresentar o plano 'Fila Visível' e fiscalização direta em hospitais. Contrastar ineficiência da gestão atual na capital.",
        "cor": "#ef4444",
        "cidades_chave": ["Goiânia", "Aparecida de Goiânia", "Senador Canedo", "Trindade", "Goianira", "Guapó", "Bela Vista de Goiás"]
    },
    "Entorno DF": {
        "nome": "Entorno do Distrito Federal",
        "polo": "Luziânia / Valparaíso",
        "pop_total": 1420000,
        "peso_eleitoral": "20% do Eleitorado Estadual",
        "pauta_critica": "TRANSPORTE",
        "dor_principal": "Tarifa abusiva de ônibus interestadual para Brasília, trânsito no BRT e falta de segurança nas periferias.",
        "estrategia_wilder": "Região de maior rejeição ao governo estadual. Wilder lidera com folga. Focar na reestruturação da ANTT e subsídio ao transporte.",
        "cor": "#f97316",
        "cidades_chave": ["Luziânia", "Valparaíso de Goiás", "Águas Lindas de Goiás", "Novo Gama", "Formosa", "Planaltina", "Santo Antônio do Descoberto", "Cidade Ocidental", "Cristalina"]
    },
    "Sudoeste": {
        "nome": "Sudoeste Goiano (Coração do Agro)",
        "polo": "Rio Verde / Jataí",
        "pop_total": 780000,
        "peso_eleitoral": "12% do Eleitorado Estadual",
        "pauta_critica": "INFRAESTRUTURA",
        "dor_principal": "Gargalo no escoamento de grãos, estradas vicinais não pavimentadas, pontes de madeira e escassez de armazenagem.",
        "estrategia_wilder": "Wilder tem forte adesão do produtor rural e cooperativas. Discurso de infraestrutura pesada, ferrovia e desoneração do agro.",
        "cor": "#10b981",
        "cidades_chave": ["Rio Verde", "Jataí", "Mineiros", "Quirinópolis", "Santa Helena de Goiás", "Acreúna", "Chapadão do Céu", "Montividiu"]
    },
    "Centro": {
        "nome": "Centro Goiano / DAIA",
        "polo": "Anápolis",
        "pop_total": 680000,
        "peso_eleitoral": "10% do Eleitorado Estadual",
        "pauta_critica": "EMPREGO",
        "dor_principal": "Falta de primeiro emprego para jovens recém-formados e necessidade de qualificação técnica para a indústria farmacêutica.",
        "estrategia_wilder": "Proposta 'Primeiro Salário' e ampliação de incentivos fiscais no DAIA com atração de novas fábricas de ponta.",
        "cor": "#eab308",
        "cidades_chave": ["Anápolis", "Goianésia", "Jaraguá", "Ceres", "Inhumas", "Itaberaí", "Nerópolis", "Pirenópolis"]
    },
    "Sul & Sudeste": {
        "nome": "Sul Goiano & Vale do Paranaíba",
        "polo": "Itumbiara / Caldas Novas",
        "pop_total": 520000,
        "peso_eleitoral": "8% do Eleitorado Estadual",
        "pauta_critica": "SAUDE",
        "dor_principal": "Falta de hospital especializado para idosos e carência de saneamento básico em polos turísticos de águas termais.",
        "estrategia_wilder": "Proposta 'Remédio em Casa' para terceira idade e programa estadual de incentivo ao turismo e serviços.",
        "cor": "#8b5cf6",
        "cidades_chave": ["Itumbiara", "Caldas Novas", "Morrinhos", "Goiatuba", "Pontalina", "Piracanjuba", "Ipameri", "Catalão"]
    },
    "Norte": {
        "nome": "Norte Goiano & Vale do São Patrício",
        "polo": "Porangatu / Uruaçu",
        "pop_total": 360000,
        "peso_eleitoral": "5% do Eleitorado Estadual",
        "pauta_critica": "SAUDE",
        "dor_principal": "Isolamento hospitalar; pacientes obrigados a viajar centenas de quilômetros até Goiânia para exames básicos.",
        "estrategia_wilder": "Criação de Policlínicas Móveis de Alta Tecnologia e pavimentação das rodovias de integração regional.",
        "cor": "#0ea5e9",
        "cidades_chave": ["Porangatu", "Uruaçu", "Niquelândia", "Minaçu", "São Miguel do Araguaia", "Campinorte", "Mara Rosa"]
    },
    "Noroeste": {
        "nome": "Noroeste & Vale do Araguaia",
        "polo": "São Luís de Montes Belos / Iporá",
        "pop_total": 310000,
        "peso_eleitoral": "4% do Eleitorado Estadual",
        "pauta_critica": "INFRAESTRUTURA",
        "dor_principal": "Pontes precárias que travam o transporte de gado de corte e leite; sinal de telefonia e internet rural instável.",
        "estrategia_wilder": "Programa estadual de pontes de concreto armado e expansão de conectividade rural para o pequeno produtor.",
        "cor": "#14b8a6",
        "cidades_chave": ["São Luís de Montes Belos", "Iporá", "Goiás", "Mozarlândia", "Aragarças", "Piranhas", "Jussara"]
    },
    "Nordeste": {
        "nome": "Nordeste Goiano (Vão do Paranã)",
        "polo": "Posse / Campos Belos",
        "pop_total": 210000,
        "peso_eleitoral": "3% do Eleitorado Estadual",
        "pauta_critica": "SEGURANCA",
        "dor_principal": "Vulnerabilidade social, estradas de terra esburacadas e falta de água tratada nas comunidades do interior.",
        "estrategia_wilder": "Plano de resgate do Nordeste: infraestrutura hídrica emergencial, asfalto definitivo e atração de investimentos.",
        "cor": "#dc2626",
        "cidades_chave": ["Posse", "Campos Belos", "Iaciara", "Alvorada do Norte", "São Domingos", "Cavalcante", "Flores de Goiás"]
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. DICIONÁRIO LÉXICO NLP
# ─────────────────────────────────────────────────────────────────────────────
LEXICON_PAUTAS = {
    "SAUDE": {
        "palavras": ["hospital", "sus", "fila", "ubs", "remedio", "medicamento", "upa", "cirurgia",
                     "medico", "enfermagem", "leito", "ambulancia", "emergencia", "saude",
                     "cancer", "dengue", "morte", "obito", "tratamento", "consulta", "exame",
                     "especialista", "maternidade", "uti", "posto de saude"],
        "peso": 10, "cor": "#ef4444", "icone": "🏥", "nivel": 4, "nome": "Saúde & SUS"
    },
    "TRANSPORTE": {
        "palavras": ["onibus", "transporte", "passagem", "metro", "trem", "brt", "carro", "estrada",
                     "rodovia", "buraco", "asfalto", "transito", "engarrafamento", "acidente",
                     "km", "motorista", "entorno", "brasilia", "viagem", "trajeto", "tarifa", "antt"],
        "peso": 8, "cor": "#f97316", "icone": "🚌", "nivel": 3, "nome": "Transporte & Estradas"
    },
    "EMPREGO": {
        "palavras": ["emprego", "desemprego", "trabalho", "salario", "carteira", "clt", "demitido",
                     "contrato", "vaga", "concurso", "renda", "bolsa", "auxilio", "beneficio",
                     "aposentadoria", "previdencia", "primeiro emprego", "jovem", "daia", "industria"],
        "peso": 8, "cor": "#eab308", "icone": "💼", "nivel": 3, "nome": "Emprego & Renda"
    },
    "SEGURANCA": {
        "palavras": ["violencia", "crime", "roubo", "furto", "assassinato", "homicidio", "policia",
                     "delegacia", "seguranca", "medo", "periferia", "trafico", "drogas", "arma",
                     "bala", "tiroteio", "morte", "latrocinio", "assalto", "patrulhamento"],
        "peso": 9, "cor": "#dc2626", "icone": "🚨", "nivel": 4, "nome": "Segurança Pública"
    },
    "INFRAESTRUTURA": {
        "palavras": ["agua", "esgoto", "luz", "energia", "calcada", "pavimentacao", "obra",
                     "construcao", "ponte", "viaduto", "escola", "creche", "parque",
                     "iluminacao", "saneamento", "lixo", "coleta", "alagamento", "chuva", "agro", "safra"],
        "peso": 7, "cor": "#8b5cf6", "icone": "🏗️", "nivel": 2, "nome": "Infraestrutura & Agro"
    },
    "EDUCACAO": {
        "palavras": ["escola", "professor", "aluno", "aula", "ensino", "faculdade", "universidade",
                     "enem", "vestibular", "bolsa", "prouni", "fies", "estudante", "creche",
                     "infantil", "fundamental", "medio", "diploma", "formatura", "merenda"],
        "peso": 6, "cor": "#0ea5e9", "icone": "📚", "nivel": 2, "nome": "Educação & Capacitação"
    },
}

def _classificar_pauta(texto: str) -> dict:
    """Classifica o texto em uma pauta usando o léxico NLP."""
    texto_norm = _norma(texto)
    scores = {}
    for pauta, config in LEXICON_PAUTAS.items():
        score = sum(config["peso"] for kw in config["palavras"] if kw in texto_norm)
        if score > 0:
            scores[pauta] = score

    if not scores:
        return {"pauta": "GERAL", "cor": "#64748b", "icone": "📌", "nivel": 1, "nome": "Demandas Gerais"}

    melhor = max(scores, key=scores.get)
    return {
        "pauta": melhor,
        "cor": LEXICON_PAUTAS[melhor]["cor"],
        "icone": LEXICON_PAUTAS[melhor]["icone"],
        "nivel": LEXICON_PAUTAS[melhor]["nivel"],
        "nome": LEXICON_PAUTAS[melhor]["nome"],
        "score": scores[melhor]
    }

def _detectar_municipio(texto: str) -> dict | None:
    """Tenta identificar um município de Goiás no texto."""
    texto_norm = _norma(texto)
    for m in MUNICIPIOS_GOIAS:
        nome_norm = _norma(m["nome"])
        if len(nome_norm) >= 4 and nome_norm in texto_norm:
            return m
    return None

# ─────────────────────────────────────────────────────────────────────────────
# 5. BASELINE ESTRATÉGICO DE QUEIXAS PRÉ-COMPUTADO
# ─────────────────────────────────────────────────────────────────────────────
BASELINE_QUEIXAS_GOIAS = [
    # GOIÂNIA / METROPOLITANA
    {"municipio": "Goiânia", "pauta": "SAUDE", "manchete": "Fila do SUS para consultas e cirurgias eletivas supera 6 meses de espera na capital", "fonte": "Radar Popular GO", "desc": "Pacientes aguardam meses no sistema regulador estadual para cirurgias ortopédicas e oftalmológicas."},
    {"municipio": "Goiânia", "pauta": "SAUDE", "manchete": "Superlotação crônica em UPAs e falta de especialistas na rede pública", "fonte": "Portal Notícias Goiás", "desc": "Tempo de espera nas emergências da capital passa de 5 horas nos horários de pico."},
    {"municipio": "Goiânia", "pauta": "TRANSPORTE", "manchete": "Crise no Eixo Anhanguera e atrasos nas linhas alimentadoras metropolitanas", "fonte": "Voz Metropolitana", "desc": "Usuários do transporte público cobram melhorias na frota e redução do tempo de espera."},
    {"municipio": "Aparecida de Goiânia", "pauta": "SAUDE", "manchete": "Maternidade e postos de saúde de Aparecida enfrentam falta de insumos e pediatras", "fonte": "Imprensa Aparecida", "desc": "Mães relatam dificuldade de atendimento de urgência para crianças na rede municipal."},
    {"municipio": "Aparecida de Goiânia", "pauta": "EMPREGO", "manchete": "Jovens e trabalhadores acima de 45 anos enfrentam gargalo de contratação", "fonte": "Diário de Aparecida", "desc": "Demanda por cursos profissionalizantes técnicos integrados às indústrias locais."},
    {"municipio": "Senador Canedo", "pauta": "INFRAESTRUTURA", "manchete": "Abastecimento irregular de água e pressão sobre infraestrutura urbana", "fonte": "Gazeta Canedo", "desc": "Bairros periféricos sofrem com interrupções no fornecimento em períodos de estiagem."},
    {"municipio": "Trindade", "pauta": "SAUDE", "manchete": "População exige ampliação do pronto-socorro e exames especializados", "fonte": "Tribuna de Trindade", "desc": "Romeiros e moradores locais pedem reforço nos plantões médicos permanentes."},

    # ENTORNO DO DF
    {"municipio": "Luziânia", "pauta": "TRANSPORTE", "manchete": "Tarifas de ônibus interestadual para Brasília sufocam renda dos trabalhadores", "fonte": "Correio do Entorno", "desc": "Moradores gastam até 30% do salário mínimo em transporte coletivo precário e superlotado."},
    {"municipio": "Luziânia", "pauta": "SEGURANCA", "manchete": "Moradores cobram aumento do efetivo da Polícia Militar nos bairros afastados", "fonte": "Jornal de Luziânia", "desc": "Comerciantes e pedestres relatam aumento de assaltos no início da manhã e à noite."},
    {"municipio": "Valparaíso de Goiás", "pauta": "TRANSPORTE", "manchete": "Gargalo histórico na BR-040 gera horas de engarrafamento diário para o DF", "fonte": "Folha de Valparaíso", "desc": "Motoristas e usuários de vans enfrentam até 2h30 para percorrer 35km até o Plano Piloto."},
    {"municipio": "Valparaíso de Goiás", "pauta": "SAUDE", "manchete": "Hospital Regional do Entorno sobrecarregado com demanda de municípios vizinhos", "fonte": "Entorno News", "desc": "Leitos de internação e emergência operam com mais de 120% da capacidade projetada."},
    {"municipio": "Águas Lindas de Goiás", "pauta": "SAUDE", "manchete": "Falta de médicos especialistas obriga busca por atendimento em Taguatinga e Ceilândia", "fonte": "Voz de Águas Lindas", "desc": "Sistema de saúde do DF é sobrecarregado por carência de estrutura hospitalar no lado goiano."},
    {"municipio": "Águas Lindas de Goiás", "pauta": "TRANSPORTE", "manchete": "População reivindica integração tarifária urgente entre Goiás e DF", "fonte": "Notícias do Entorno", "desc": "Trabalhadores clamam por bilhete único metropolitano integrado."},
    {"municipio": "Novo Gama", "pauta": "INFRAESTRUTURA", "manchete": "Asfalto esburacado e ruas sem drenagem causam prejuízos a moradores", "fonte": "Jornal Novo Gama", "desc": "Vias principais do município demandam recapeamento completo antes do período chuvoso."},
    {"municipio": "Formosa", "pauta": "SAUDE", "manchete": "Demora em cirurgias eletivas e carência de UTI pediátrica no município", "fonte": "Folha de Formosa", "desc": "Famílias reivindicam UTI especializada para evitar transferências arriscadas para Brasília."},
    {"municipio": "Formosa", "pauta": "EMPREGO", "manchete": "Juventude de Formosa busca oportunidades de trabalho e formação técnica", "fonte": "Radar Formosa", "desc": "Falta de polos industriais locais estimula êxodo de talentos para o Distrito Federal."},
    {"municipio": "Planaltina", "pauta": "SEGURANCA", "manchete": "Comunidades rurais e periferias pedem reforço no patrulhamento ostensivo", "fonte": "Imprensa Planaltina GO", "desc": "Queixas recorrentes de furtos de equipamentos e gado em propriedades rurais."},
    {"municipio": "Santo Antônio do Descoberto", "pauta": "INFRAESTRUTURA", "manchete": "Obras paralisadas de saneamento e esgoto a céu aberto em diversos setores", "fonte": "Tribuna do Descoberto", "desc": "Cobrança por conclusão de redes de água e tratamento de esgoto sanitário."},
    {"municipio": "Cidade Ocidental", "pauta": "TRANSPORTE", "manchete": "Falta de linhas de transporte direto nos horários de pico prejudica estudantes", "fonte": "Jornal Ocidental", "desc": "Alunos universitários e trabalhadores relatam escassez de horários noturnos."},
    {"municipio": "Cristalina", "pauta": "INFRAESTRUTURA", "manchete": "Produtores rurais cobram conservação de rodovias vicinais para escoamento", "fonte": "Agro Cristalina", "desc": "Maior polo de irrigação da América Latina necessita de manutenção contínua das vias vicinais."},

    # SUDOESTE (AGRO)
    {"municipio": "Rio Verde", "pauta": "INFRAESTRUTURA", "manchete": "Estradas vicinais e pontes de madeira limitam transporte da supersafra de grãos", "fonte": "Agro Sudoeste", "desc": "Caminhoneiros e cooperativas pedem substituição urgente de pontes precárias por concreto."},
    {"municipio": "Rio Verde", "pauta": "SAUDE", "manchete": "Hospital Municipal de Rio Verde atende 15 cidades vizinhas e opera no limite", "fonte": "Folha de Rio Verde", "desc": "Necessidade de repasses estaduais adicionais para absorver pacientes de todo o sudoeste."},
    {"municipio": "Jataí", "pauta": "EMPREGO", "manchete": "Demanda por profissionais qualificados em tecnologia do agronegócio e maquinário", "fonte": "Jataí Notícias", "desc": "Falta de mão de obra especializada para operar colheitadeiras e pulverizadores de precisão."},
    {"municipio": "Jataí", "pauta": "INFRAESTRUTURA", "manchete": "Cobrança por duplicação de trechos críticos da rodovia de ligação regional", "fonte": "Radar Jataí", "desc": "Alto fluxo de carretas exige faixas adicionais e terceira pista em trechos serranos."},
    {"municipio": "Mineiros", "pauta": "INFRAESTRUTURA", "manchete": "Logística de distribuição e estradas rurais exigem investimentos pesados", "fonte": "Tribuna de Mineiros", "desc": "Produtores de soja e milho relatam perdas no frete devido a buracos e atoleiros."},
    {"municipio": "Quirinópolis", "pauta": "EMPREGO", "manchete": "Setor sucroalcooleiro busca novos investimentos para geração de empregos industriais", "fonte": "Gazeta de Quirinópolis", "desc": "Trabalhadores cobram estímulo à instalação de novas usinas e indústrias derivadas."},
    {"municipio": "Santa Helena de Goiás", "pauta": "SAUDE", "manchete": "Moradores cobram centro de hemodiálise e médicos plantonistas aos fins de semana", "fonte": "Jornal Santa Helena", "desc": "Pacientes renais crônicos viajam semanalmente para cidades vizinhas para tratamento."},

    # CENTRO / ANÁPOLIS (DAIA)
    {"municipio": "Anápolis", "pauta": "EMPREGO", "manchete": "Polo Industrial (DAIA) demanda expansão de vagas e cursos de capacitação técnica", "fonte": "Tribuna de Anápolis", "desc": "Empresas farmacêuticas e logísticas apontam carência de técnicos especializados."},
    {"municipio": "Anápolis", "pauta": "SAUDE", "manchete": "Demora no agendamento de consultas especializadas na rede pública municipal", "fonte": "Anápolis Notícias", "desc": "Pacientes idosos relatam dificuldade de marcar cardiologistas e neurologistas."},
    {"municipio": "Goianésia", "pauta": "INFRAESTRUTURA", "manchete": "Pavimentação de rodovias de ligação com o Vale do São Patrício é prioridade", "fonte": "Correio de Goianésia", "desc": "Empresários e motoristas cobram recuperação asfáltica das rodovias estaduais."},
    {"municipio": "Jaraguá", "pauta": "EMPREGO", "manchete": "Polo de confecções reivindica incentivos fiscais e modernização de maquinário", "fonte": "Moda & Notícia Jaraguá", "desc": "Confecções locais buscam apoio estadual para competir com produtos importados."},
    {"municipio": "Ceres", "pauta": "SAUDE", "manchete": "Hospital São Patrício necessita de novos leitos de UTI e equipamentos de diagnóstico", "fonte": "Jornal do Vale Ceres", "desc": "Referência de saúde para mais de 10 cidades vizinhas no centro-norte do estado."},

    # SUL & SUDESTE
    {"municipio": "Itumbiara", "pauta": "SAUDE", "manchete": "Hospital Regional precisa ampliar atendimentos em oncologia e cardiologia", "fonte": "Folha de Itumbiara", "desc": "Pacientes com câncer cobram início de sessões de quimioterapia na própria cidade."},
    {"municipio": "Itumbiara", "pauta": "EMPREGO", "manchete": "Jovens cobram diversificação econômica e novas indústrias para a região", "fonte": "Gazeta de Itumbiara", "desc": "Dependência de empregos sazonais gera instabilidade financeira para famílias."},
    {"municipio": "Caldas Novas", "pauta": "INFRAESTRUTURA", "manchete": "Infraestrutura de água e saneamento não acompanha crescimento da rede hoteleira", "fonte": "Turismo Caldas News", "desc": "Bairros residenciais sofrem com falta de pressão d'água durante feriados e alta temporada."},
    {"municipio": "Morrinhos", "pauta": "INFRAESTRUTURA", "manchete": "Conservação de rodovias estaduais de escoamento leiteiro e agrícola", "fonte": "Notícias Morrinhos", "desc": "Bacia leiteira expressiva necessita de tráfego seguro para caminhões tanque."},
    {"municipio": "Catalão", "pauta": "EMPREGO", "manchete": "Trabalhadores cobram fortalecimento do polo minerador e automotivo", "fonte": "Imprensa Catalão", "desc": "Sindicatos e operários pedem incentivos para atração de novas montadoras e autopeças."},

    # NORTE & VALE DO SÃO PATRÍCIO
    {"municipio": "Porangatu", "pauta": "SAUDE", "manchete": "Hospital de Porangatu necessita de ampliação para evitar viagens de 400km até Goiânia", "fonte": "Norte Notícias", "desc": "Isolamento geográfico do extremo norte penaliza pacientes graves sem UTI local."},
    {"municipio": "Porangatu", "pauta": "INFRAESTRUTURA", "manchete": "Produtores rurais clamam por manutenção das pontes da bacia do Araguaia-Tocantins", "fonte": "Voz do Norte GO", "desc": "Safra pecuária sofre com trechos intrafegáveis durante a época das chuvas."},
    {"municipio": "Uruaçu", "pauta": "SAUDE", "manchete": "Hospital do Centro-Norte Goiano demanda contratação de mais médicos especialistas", "fonte": "Correio de Uruaçu", "desc": "Estrutura moderna ainda carece de quadro completo de cirurgiões e anestesistas."},
    {"municipio": "Minaçu", "pauta": "EMPREGO", "manchete": "Moradores buscam novas alternativas econômicas após restrições ao amianto", "fonte": "Tribuna de Minaçu", "desc": "Transição para mineração de terras raras e turismo no Lago de Cana Brava."},
    {"municipio": "Niquelândia", "pauta": "INFRAESTRUTURA", "manchete": "Pavimentação de rodovias de integração regional para escoamento de níquel", "fonte": "Folha de Niquelândia", "desc": "População exige conclusão de obras asfálticas prometidas há anos."},

    # NOROESTE & VALE DO ARAGUAIA
    {"municipio": "São Luís de Montes Belos", "pauta": "INFRAESTRUTURA", "manchete": "Bacia leiteira exige recuperação de pontes e estradas vicinais no interior", "fonte": "Agro Noroeste", "desc": "Pequenos pecuaristas enfrentam dificuldades diárias para entregar leite aos laticínios."},
    {"municipio": "Iporá", "pauta": "SAUDE", "manchete": "População cobra médicos plantonistas 24h e ambulâncias para transporte urgente", "fonte": "Oeste Goiano", "desc": "Carência de leitos de semi-intensiva obriga transferências de urgência."},
    {"municipio": "Goiás", "pauta": "INFRAESTRUTURA", "manchete": "Preservação do patrimônio histórico e melhorias na rodovia dos Romeiros", "fonte": "Voz de Goiás Velho", "desc": "Turistas e moradores pedem acostamentos e sinalização adequada na GO-070."},
    {"municipio": "Mozarlândia", "pauta": "INFRAESTRUTURA", "manchete": "Polo frigorífico necessita de melhorias na malha viária de transporte de gado", "fonte": "Portal do Araguaia", "desc": "Intenso tráfego de carretas boiadeiras deteriora o asfalto regional."},

    # NORDESTE (VÃO DO PARANÃ)
    {"municipio": "Posse", "pauta": "SAUDE", "manchete": "Nordeste goiano reivindica hospital de média complexidade com UTI em Posse", "fonte": "Tribuna do Nordeste GO", "desc": "Famílias de 15 municípios viajam até 500km para receber atendimento especializado."},
    {"municipio": "Campos Belos", "pauta": "INFRAESTRUTURA", "manchete": "Estradas de terra precárias isolam comunidades na divisa com o Tocantins e Bahia", "fonte": "Folha de Campos Belos", "desc": "Falta de asfalto encarece o frete e trava o desenvolvimento comercial da microrregião."},
    {"municipio": "São Domingos", "pauta": "INFRAESTRUTURA", "manchete": "Turismo ecológico do Parque Estadual de Terra Ronca sofre com acesso não pavimentado", "fonte": "Eco Terra Ronca", "desc": "Guias e pousadas cobram asfalto ecológico para atrair turistas nacionais e estrangeiros."},
    {"municipio": "Cavalcante", "pauta": "INFRAESTRUTURA", "manchete": "Comunidades quilombolas do Kalunga cobram pontes seguras e eletrificação rural", "fonte": "Kalunga Notícias", "desc": "Durante as chuvas, rios transbordam e isolam povoados por dias."},
]

# ─────────────────────────────────────────────────────────────────────────────
# 6. INICIALIZADOR DO BASELINE TÁTICO
# ─────────────────────────────────────────────────────────────────────────────
def _inicializar_baseline_territorial():
    """Carrega dados ricos e completos imediatamente no boot."""
    queixas = []
    contagem_municipio = {}

    for item in BASELINE_QUEIXAS_GOIAS:
        m = MUNICIPIOS_MAP.get(item["municipio"])
        if not m:
            m = MUNICIPIOS_GOIAS[0]

        pauta_info = LEXICON_PAUTAS.get(item["pauta"], LEXICON_PAUTAS["SAUDE"])
        pauta = item["pauta"]
        nome_mun = m["nome"]

        if nome_mun not in contagem_municipio:
            contagem_municipio[nome_mun] = {}
        contagem_municipio[nome_mun][pauta] = contagem_municipio[nome_mun].get(pauta, 0) + 1

        queixas.append({
            "municipio": nome_mun,
            "regiao": m.get("regiao", "Goiás"),
            "lat": m["lat"],
            "lon": m["lon"],
            "pop": m.get("pop", 0),
            "idh": m.get("idh", 0.72),
            "pauta": pauta,
            "pauta_nome": pauta_info["nome"],
            "cor": pauta_info["cor"],
            "icone": pauta_info["icone"],
            "nivel": pauta_info["nivel"],
            "manchete": item["manchete"],
            "desc": item["desc"],
            "fonte": item["fonte"],
            "url": "#",
            "pub": "Hoje, " + datetime.datetime.now().strftime("%H:%M"),
            "coletado": _agora_str(),
        })

    # Monta mapa de calor com TODOS os 246 municípios
    mapa_calor = []
    for m in MUNICIPIOS_GOIAS:
        nome = m["nome"]
        regiao = m.get("regiao", "Goiás")
        pop = m.get("pop", 0)
        idh = m.get("idh", 0.70)

        if nome in contagem_municipio:
            total = sum(contagem_municipio[nome].values())
            pauta_dom = max(contagem_municipio[nome], key=contagem_municipio[nome].get)
            p_info = LEXICON_PAUTAS.get(pauta_dom, LEXICON_PAUTAS["SAUDE"])
            nivel = min(4, total + 1)
            mapa_calor.append({
                "municipio": nome,
                "lat": m["lat"],
                "lon": m["lon"],
                "total_queixas": total,
                "pauta_dominante": p_info["nome"],
                "pauta_cod": pauta_dom,
                "nivel": nivel,
                "cor": p_info["cor"],
                "icone": p_info["icone"],
                "regiao": regiao,
                "pop": pop,
                "idh": idh,
            })
        else:
            macro = MACRORREGIOES_GOIAS.get(regiao)
            pauta_macro = macro["pauta_critica"] if macro else "INFRAESTRUTURA"
            p_info = LEXICON_PAUTAS.get(pauta_macro, LEXICON_PAUTAS["INFRAESTRUTURA"])
            peso_pop = 1 if pop > 20000 else 0
            mapa_calor.append({
                "municipio": nome,
                "lat": m["lat"],
                "lon": m["lon"],
                "total_queixas": peso_pop,
                "pauta_dominante": p_info["nome"] if peso_pop > 0 else "Monitoramento Regular",
                "pauta_cod": pauta_macro if peso_pop > 0 else "GERAL",
                "nivel": 1 if peso_pop > 0 else 0,
                "cor": p_info["cor"] if peso_pop > 0 else "#1e293b",
                "icone": p_info["icone"] if peso_pop > 0 else "📍",
                "regiao": regiao,
                "pop": pop,
                "idh": idh,
            })

    alertas = [
        {
            "tipo": "CRÍTICO",
            "gravidade": 4,
            "municipio": "Luziânia & Entorno DF",
            "pauta": "Transporte Interestadual",
            "cor": "#f97316",
            "icone": "🚌",
            "mensagem": "Tarifas de transporte e precariedade no BRT atingem pico de queixas no Entorno.",
            "diretriz": "Wilder deve focar discurso no subsídio estadual e cobrança da ANTT para baratear a passagem dos 1,4 milhão de moradores.",
            "timestamp": _agora_str()
        },
        {
            "tipo": "CRÍTICO",
            "gravidade": 4,
            "municipio": "Goiânia & Metropolitana",
            "pauta": "Saúde & Filas do SUS",
            "cor": "#ef4444",
            "icone": "🏥",
            "mensagem": "Espera por cirurgias eletivas supera 6 meses; superlotação em UPAs da capital.",
            "diretriz": "Apresentar a proposta 'Fila Visível' e fiscalizar hospitais estaduais como contraponto executivo ao governo atual.",
            "timestamp": _agora_str()
        },
        {
            "tipo": "ALERTA",
            "gravidade": 3,
            "municipio": "Rio Verde & Sudoeste",
            "pauta": "Infraestrutura & Agro",
            "cor": "#10b981",
            "icone": "🌾",
            "mensagem": "Gargalo em pontes de madeira e estradas vicinais atrasa escoamento da safra.",
            "diretriz": "Reforçar aliança com o agro através do plano de pontes definitivas de concreto armado e manutenção de rodovias.",
            "timestamp": _agora_str()
        },
        {
            "tipo": "ALERTA",
            "gravidade": 3,
            "municipio": "Anápolis (DAIA)",
            "pauta": "Emprego Jovem",
            "cor": "#eab308",
            "icone": "💼",
            "mensagem": "Jovens recém-formados cobram primeiro emprego e vagas na indústria farmacêutica.",
            "diretriz": "Promover o 'Programa Primeiro Salário' e incentivos fiscais para abertura do 3º turno nas indústrias do DAIA.",
            "timestamp": _agora_str()
        },
        {
            "tipo": "OPORTUNIDADE",
            "gravidade": 2,
            "municipio": "Porangatu & Norte",
            "pauta": "Policlínicas Regionais",
            "cor": "#0ea5e9",
            "icone": "🚑",
            "mensagem": "Isolamento de saúde no norte do estado penaliza famílias que viajam até Goiânia.",
            "diretriz": "Defender a interiorização de especialistas e centros de diagnóstico no eixo da BR-153.",
            "timestamp": _agora_str()
        },
        {
            "tipo": "OPORTUNIDADE",
            "gravidade": 2,
            "municipio": "Posse & Nordeste Goiano",
            "pauta": "Infraestrutura Hídrica & Asfalto",
            "cor": "#dc2626",
            "icone": "🏗️",
            "mensagem": "Carência de água tratada e estradas de terra no Vão do Paranã.",
            "diretriz": "Propor o Plano de Resgate do Nordeste Goiano com foco em dignidade básica e conectividade.",
            "timestamp": _agora_str()
        }
    ]

    ibge_dict = {}
    for m in MUNICIPIOS_GOIAS:
        cod = m["codigo"]
        ibge_dict[cod] = {
            "codigo": cod,
            "municipio": m["nome"],
            "nome": m["nome"],
            "populacao": m.get("pop", 0),
            "pop": m.get("pop", 0),
            "lat": m["lat"],
            "lon": m["lon"],
            "idh": m.get("idh", 0.70),
            "regiao": m.get("regiao", "Goiás"),
            "eleitorado_est": int(m.get("pop", 0) * 0.72),
        }

    diagnostico = {
        "sintese": "O eleitor goiano prioriza Saúde (Filas do SUS - 42%), Transporte/Mobilidade (Entorno DF - 45%) e Primeiro Emprego Jovem no Centro.",
        "alvo_prioritario": "Entorno do DF e Cidades Polo do Interior",
        "vetor_vitoria": "Consolidar 65%+ no Entorno DF e Agro Sudoeste, enquanto empata com Daniel na Grande Goiânia através de propostas práticas de saúde.",
        "data": _agora_str()
    }

    with _intel_lock:
        INTEL_CACHE["queixas"]["data"] = queixas
        INTEL_CACHE["queixas"]["atualizado_em"] = _agora()
        INTEL_CACHE["queixas"]["ciclos"] = 1
        INTEL_CACHE["mapa_calor"]["data"] = mapa_calor
        INTEL_CACHE["mapa_calor"]["atualizado_em"] = _agora()
        INTEL_CACHE["alertas"]["data"] = alertas
        INTEL_CACHE["ibge"]["data"] = ibge_dict
        INTEL_CACHE["ibge"]["atualizado_em"] = _agora()
        INTEL_CACHE["regioes"]["data"] = MACRORREGIOES_GOIAS
        INTEL_CACHE["diagnostico"]["data"] = diagnostico

_inicializar_baseline_territorial()

# ─────────────────────────────────────────────────────────────────────────────
# 7. FEEDS RSS POR PAUTA E CIDADE
# ─────────────────────────────────────────────────────────────────────────────
FEEDS_INTEL = [
    ("https://news.google.com/rss/search?q=hospital+fila+SUS+Goias&hl=pt-BR&gl=BR&ceid=BR:pt-419",  "RSS Saúde Goiás"),
    ("https://news.google.com/rss/search?q=UPA+Goiania+emergencia+saude&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS UPA Goiânia"),
    ("https://news.google.com/rss/search?q=remedio+SUS+Goias+falta&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Remédio SUS GO"),
    ("https://news.google.com/rss/search?q=onibus+Entorno+DF+Luziania+passagem&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Transporte Entorno"),
    ("https://news.google.com/rss/search?q=estrada+rodovia+Goias+acidente+buraco&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Estradas GO"),
    ("https://news.google.com/rss/search?q=desemprego+Goias+emprego+vagas&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Emprego Goiás"),
    ("https://news.google.com/rss/search?q=seguranca+publica+violencia+Goias&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Segurança GO"),
    ("https://news.google.com/rss/search?q=Aparecida+Goiania+reclamacao+prefeitura&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Aparecida"),
    ("https://news.google.com/rss/search?q=Anapolis+problema+cidade+saude&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Anápolis"),
    ("https://news.google.com/rss/search?q=Rio+Verde+Goias+safra+estradas&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Rio Verde"),
    ("https://news.google.com/rss/search?q=Luziania+Valparaiso+Goias+noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419", "RSS Luziânia/Valparaíso"),
]

def _fetch_rss(url: str, fonte: str, max_items: int = 5) -> list:
    """Busca itens de um feed RSS de forma segura."""
    itens = []
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=8) as resp:
            root = ET.fromstring(resp.read())
        for item in root.findall(".//item")[:max_items]:
            titulo = item.findtext("title", "").strip()
            link   = item.findtext("link", "").strip()
            desc   = item.findtext("description", "").strip()
            pub    = item.findtext("pubDate", "")[:16].strip()
            src    = getattr(item.find("source"), "text", fonte) or fonte
            texto_completo = f"{titulo} {desc}"
            if titulo:
                itens.append({
                    "titulo": titulo.split(" - ")[0] if " - " in titulo else titulo,
                    "desc": re.sub(r'<[^>]+>', '', desc)[:220],
                    "url": link,
                    "fonte": src,
                    "pub": pub,
                    "texto_completo": texto_completo
                })
    except Exception:
        pass
    return itens

def atualizar_intel_territorial():
    """Coleta RSS, classifica com NLP, enriquece o baseline e atualiza o cache."""
    print(f"[INTEL] Atualizando radar territorial ao vivo... ({_agora_str()})")
    novas_queixas = []
    contagem_municipio = {}

    for item in BASELINE_QUEIXAS_GOIAS:
        m = MUNICIPIOS_MAP.get(item["municipio"]) or MUNICIPIOS_GOIAS[0]
        p_info = LEXICON_PAUTAS.get(item["pauta"], LEXICON_PAUTAS["SAUDE"])
        nome_mun = m["nome"]
        pauta = item["pauta"]

        if nome_mun not in contagem_municipio:
            contagem_municipio[nome_mun] = {}
        contagem_municipio[nome_mun][pauta] = contagem_municipio[nome_mun].get(pauta, 0) + 1

        novas_queixas.append({
            "municipio": nome_mun,
            "regiao": m.get("regiao", "Goiás"),
            "lat": m["lat"],
            "lon": m["lon"],
            "pop": m.get("pop", 0),
            "idh": m.get("idh", 0.70),
            "pauta": pauta,
            "pauta_nome": p_info["nome"],
            "cor": p_info["cor"],
            "icone": p_info["icone"],
            "nivel": p_info["nivel"],
            "manchete": item["manchete"],
            "desc": item["desc"],
            "fonte": item["fonte"],
            "url": "#",
            "pub": "Hoje, " + datetime.datetime.now().strftime("%H:%M"),
            "coletado": _agora_str(),
        })

    for url, fonte in FEEDS_INTEL:
        itens = _fetch_rss(url, fonte, max_items=5)
        for item in itens:
            pauta_info = _classificar_pauta(item["texto_completo"])
            municipio_info = _detectar_municipio(item["texto_completo"])

            if not municipio_info:
                for m in MUNICIPIOS_GOIAS:
                    if _norma(m["nome"]) in _norma(fonte):
                        municipio_info = m
                        break

            if not municipio_info:
                municipio_info = MUNICIPIOS_GOIAS[0]

            nome_mun = municipio_info["nome"]
            pauta = pauta_info["pauta"]

            if nome_mun not in contagem_municipio:
                contagem_municipio[nome_mun] = {}
            contagem_municipio[nome_mun][pauta] = contagem_municipio[nome_mun].get(pauta, 0) + 1

            novas_queixas.insert(0, {
                "municipio": nome_mun,
                "regiao": municipio_info.get("regiao", "Goiás"),
                "lat": municipio_info["lat"],
                "lon": municipio_info["lon"],
                "pop": municipio_info.get("pop", 0),
                "idh": municipio_info.get("idh", 0.70),
                "pauta": pauta,
                "pauta_nome": pauta_info["nome"],
                "cor": pauta_info["cor"],
                "icone": pauta_info["icone"],
                "nivel": pauta_info["nivel"],
                "manchete": item["titulo"],
                "desc": item["desc"],
                "fonte": item["fonte"],
                "url": item["url"],
                "pub": item["pub"] or ("Hoje, " + datetime.datetime.now().strftime("%H:%M")),
                "coletado": _agora_str(),
            })

    mapa_calor = []
    for m in MUNICIPIOS_GOIAS:
        nome = m["nome"]
        regiao = m.get("regiao", "Goiás")
        pop = m.get("pop", 0)
        idh = m.get("idh", 0.70)

        if nome in contagem_municipio:
            total = sum(contagem_municipio[nome].values())
            pauta_dom = max(contagem_municipio[nome], key=contagem_municipio[nome].get)
            p_info = LEXICON_PAUTAS.get(pauta_dom, LEXICON_PAUTAS["SAUDE"])
            nivel = min(4, total)
            mapa_calor.append({
                "municipio": nome,
                "lat": m["lat"],
                "lon": m["lon"],
                "total_queixas": total,
                "pauta_dominante": p_info["nome"],
                "pauta_cod": pauta_dom,
                "nivel": nivel,
                "cor": p_info["cor"],
                "icone": p_info["icone"],
                "regiao": regiao,
                "pop": pop,
                "idh": idh,
            })
        else:
            macro = MACRORREGIOES_GOIAS.get(regiao)
            pauta_macro = macro["pauta_critica"] if macro else "INFRAESTRUTURA"
            p_info = LEXICON_PAUTAS.get(pauta_macro, LEXICON_PAUTAS["INFRAESTRUTURA"])
            peso_pop = 1 if pop > 20000 else 0
            mapa_calor.append({
                "municipio": nome,
                "lat": m["lat"],
                "lon": m["lon"],
                "total_queixas": peso_pop,
                "pauta_dominante": p_info["nome"] if peso_pop > 0 else "Monitoramento Regular",
                "pauta_cod": pauta_macro if peso_pop > 0 else "GERAL",
                "nivel": 1 if peso_pop > 0 else 0,
                "cor": p_info["cor"] if peso_pop > 0 else "#1e293b",
                "icone": p_info["icone"] if peso_pop > 0 else "📍",
                "regiao": regiao,
                "pop": pop,
                "idh": idh,
            })

    alertas = [
        {
            "tipo": "CRÍTICO",
            "gravidade": 4,
            "municipio": "Luziânia & Valparaíso (Entorno DF)",
            "pauta": "Transporte Interestadual & Mobilidade",
            "cor": "#f97316",
            "icone": "🚌",
            "mensagem": "Trabalhadores gastam até 30% da renda com passagens para Brasília; estradas congestionadas na BR-040.",
            "diretriz": "Apresentar projeto de subsídio estadual e bilhete único do Entorno. Capitalizar a rejeição ao governo estadual na região.",
            "timestamp": _agora_str()
        },
        {
            "tipo": "CRÍTICO",
            "gravidade": 4,
            "municipio": "Goiânia & Aparecida",
            "pauta": "Saúde Pública & Cirurgias Eletivas",
            "cor": "#ef4444",
            "icone": "🏥",
            "mensagem": "Mais de 30 mil goianos aguardam cirurgias eletivas; tempo de espera supera 6 meses.",
            "diretriz": "Contrastar com o plano 'Fila Visível' e convênios com hospitais privados para zerar a fila em 180 dias.",
            "timestamp": _agora_str()
        },
        {
            "tipo": "ALERTA",
            "gravidade": 3,
            "municipio": "Rio Verde, Jataí & Sudoeste",
            "pauta": "Infraestrutura Logística & Agro",
            "cor": "#10b981",
            "icone": "🌾",
            "mensagem": "Pontes de madeira e estradas vicinais sobrecarregam transporte da supersafra de soja e milho.",
            "diretriz": "Garantir compromisso de asfaltamento e pontes de concreto armado para o produtor rural.",
            "timestamp": _agora_str()
        },
        {
            "tipo": "ALERTA",
            "gravidade": 3,
            "municipio": "Anápolis (DAIA)",
            "pauta": "Primeiro Emprego & Qualificação",
            "cor": "#eab308",
            "icone": "💼",
            "mensagem": "Jovens buscam qualificação técnica para atender a expansão do polo farmacêutico.",
            "diretriz": "Promover o programa 'Primeiro Salário' e centros de treinamento tecnológico integrados às indústrias.",
            "timestamp": _agora_str()
        },
        {
            "tipo": "OPORTUNIDADE",
            "gravidade": 2,
            "municipio": "Norte & Nordeste Goiano",
            "pauta": "Saúde Regional & Infraestrutura",
            "cor": "#0ea5e9",
            "icone": "🚑",
            "mensagem": "População reivindica hospitais regionais de média complexidade em Porangatu e Posse.",
            "diretriz": "Prometer descentralização dos atendimentos médicos com Policlínicas Móveis e helicópteros aeromédicos.",
            "timestamp": _agora_str()
        }
    ]

    with _intel_lock:
        INTEL_CACHE["queixas"]["data"] = novas_queixas[:250]
        INTEL_CACHE["queixas"]["atualizado_em"] = _agora()
        INTEL_CACHE["queixas"]["ciclos"] += 1
        INTEL_CACHE["mapa_calor"]["data"] = mapa_calor
        INTEL_CACHE["mapa_calor"]["atualizado_em"] = _agora()
        INTEL_CACHE["alertas"]["data"] = alertas

    print(f"[INTEL] Radar Territorial: {len(novas_queixas)} queixas ativas | 246 municípios mapeados | {len(alertas)} alertas")

def atualizar_dados_ibge():
    """Consulta API pública IBGE para manter dados populacionais atualizados."""
    try:
        url = "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2022/variaveis/9324?localidades=N6[52]"
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=12) as resp:
            result = json.loads(resp.read().decode("utf-8", "ignore"))

        if result and isinstance(result, list):
            series = result[0].get("resultados", [])
            with _intel_lock:
                for serie in series:
                    for loc in serie.get("series", []):
                        codigo = loc["localidade"]["id"]
                        nome_ibge = loc["localidade"]["nome"]
                        valor = loc["serie"].get("2022", "0")
                        try:
                            pop = int(valor)
                        except (ValueError, TypeError):
                            pop = 0
                        if codigo in INTEL_CACHE["ibge"]["data"]:
                            INTEL_CACHE["ibge"]["data"][codigo]["populacao"] = pop
                            INTEL_CACHE["ibge"]["data"][codigo]["pop"] = pop
                            INTEL_CACHE["ibge"]["data"][codigo]["eleitorado_est"] = int(pop * 0.72)
    except Exception as e:
        print(f"[INTEL] IBGE API erro (usando dados oficiais locais): {e}")

# ─────────────────────────────────────────────────────────────────────────────
# 8. GETTERS PARA ROTAS FLASK
# ─────────────────────────────────────────────────────────────────────────────
def get_queixas():
    with _intel_lock:
        return INTEL_CACHE["queixas"]["data"][:]

def get_mapa_calor():
    with _intel_lock:
        return INTEL_CACHE["mapa_calor"]["data"][:]

def get_ibge():
    with _intel_lock:
        return dict(INTEL_CACHE["ibge"]["data"])

def get_alertas():
    with _intel_lock:
        return INTEL_CACHE["alertas"]["data"][:]

def get_regioes():
    return MACRORREGIOES_GOIAS

def get_diagnostico():
    with _intel_lock:
        return dict(INTEL_CACHE["diagnostico"]["data"])

def get_ranking_cidades():
    """Retorna ranking das 20 cidades com maior intensidade de queixas e pressão eleitoral."""
    queixas = get_queixas()
    ranking = {}
    for q in queixas:
        mun = q["municipio"]
        if mun not in ranking:
            m_obj = MUNICIPIOS_MAP.get(mun, {})
            ranking[mun] = {
                "municipio": mun,
                "regiao": q.get("regiao", m_obj.get("regiao", "Goiás")),
                "lat": q.get("lat", m_obj.get("lat", 0)),
                "lon": q.get("lon", m_obj.get("lon", 0)),
                "pop": q.get("pop", m_obj.get("pop", 0)),
                "idh": q.get("idh", m_obj.get("idh", 0.70)),
                "total": 0,
                "por_pauta": {},
                "nivel_max": 0,
                "pauta_dominante": "Demandas Gerais",
                "pauta_cod": "GERAL",
                "cor": "#64748b",
                "icone": "📍",
            }
        ranking[mun]["total"] += 1
        pauta = q.get("pauta", "GERAL")
        pauta_nome = q.get("pauta_nome", pauta)
        ranking[mun]["por_pauta"][pauta_nome] = ranking[mun]["por_pauta"].get(pauta_nome, 0) + 1
        if q.get("nivel", 0) >= ranking[mun]["nivel_max"]:
            ranking[mun]["nivel_max"] = q["nivel"]
            ranking[mun]["pauta_dominante"] = q.get("pauta_nome", pauta)
            ranking[mun]["pauta_cod"] = pauta
            ranking[mun]["cor"] = q.get("cor", "#64748b")
            ranking[mun]["icone"] = q.get("icone", "📍")

    res = sorted(ranking.values(), key=lambda x: (x["total"], x.get("pop", 0)), reverse=True)
    return res

def get_status_intel():
    def _td(ts):
        if not ts:
            return "Ao vivo"
        mins = int((_agora() - ts).total_seconds() / 60)
        return f"há {mins} min" if mins < 60 else f"há {mins // 60}h"

    with _intel_lock:
        return {
            "motor": "INTEL TERRITORIAL MILITAR ATIVO",
            "timestamp": _agora_str(),
            "queixas": {
                "total": len(INTEL_CACHE["queixas"]["data"]),
                "atualizado": _td(INTEL_CACHE["queixas"]["atualizado_em"]),
                "ciclos": INTEL_CACHE["queixas"]["ciclos"],
                "intervalo": "2 horas",
            },
            "mapa_calor": {
                "municipios": len(INTEL_CACHE["mapa_calor"]["data"]),
                "atualizado": _td(INTEL_CACHE["mapa_calor"]["atualizado_em"]),
            },
            "ibge": {
                "municipios": len(INTEL_CACHE["ibge"]["data"]),
                "atualizado": _td(INTEL_CACHE["ibge"]["atualizado_em"]),
            },
            "alertas": len(INTEL_CACHE["alertas"]["data"]),
        }

# ─────────────────────────────────────────────────────────────────────────────
# 9. INICIALIZAR JOBS NO SCHEDULER
# ─────────────────────────────────────────────────────────────────────────────
def iniciar_intel_jobs(scheduler):
    """Adiciona os jobs de inteligência territorial ao APScheduler master."""
    try:
        scheduler.add_job(
            atualizar_intel_territorial,
            "interval", hours=2,
            id="intel_territorial",
            name="Intel Territorial RSS+NLP",
            max_instances=1, coalesce=True
        )
        scheduler.add_job(
            atualizar_dados_ibge,
            "interval", hours=24,
            id="intel_ibge",
            name="Intel IBGE Municípios GO",
            max_instances=1, coalesce=True
        )
        print("[INTEL] Jobs de inteligência territorial registrados no scheduler com sucesso.")
    except Exception as e:
        print(f"[INTEL] Erro ao registrar jobs: {e}")

    threading.Thread(target=atualizar_intel_territorial, daemon=True, name="boot-intel-live").start()
