#!/usr/bin/env python3
"""
viral_trends_engine.py — Motor de Inteligência de Tendências Virais & Estratégias dos Adversários
Monitora influenciadores nacionais de alta relevância política, tendências virais
e movimentos estratégicos de Marconi Perillo e Daniel Vilela em Goiás 2026.

Atualização: a cada 4 horas via APScheduler em live_engine.py
"""

import urllib.request
import ssl
import json
import re
import time
import threading
from datetime import datetime
from xml.etree import ElementTree as ET

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

_cache_lock = threading.Lock()

# ──────────────────────────────────────────────────────────────────────────────
# CACHE CENTRAL
# ──────────────────────────────────────────────────────────────────────────────
VIRAL_CACHE = {
    "influenciadores": {
        "atualizado_em": None,
        "ciclos": 0,
        "data": {}
    },
    "adversarios": {
        "atualizado_em": None,
        "ciclos": 0,
        "data": {}
    },
    "tendencias_nacionais": {
        "atualizado_em": None,
        "ciclos": 0,
        "data": []
    },
    "briefing_estrategico": {
        "atualizado_em": None,
        "ciclos": 0,
        "data": {}
    }
}

def _agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M")

# ──────────────────────────────────────────────────────────────────────────────
# UTILITÁRIO: BUSCA RSS
# ──────────────────────────────────────────────────────────────────────────────
def _buscar_rss(query, max_items=5):
    """Busca artigos no Google News RSS para uma query específica."""
    resultados = []
    try:
        url = f"https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=10) as r:
            root = ET.fromstring(r.read())
        for item in root.findall(".//item")[:max_items]:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pub = item.findtext("pubDate", "")[:16].strip()
            source = item.findtext("source", "").strip()
            if title:
                resultados.append({
                    "titulo": title.split(" - ")[0][:120],
                    "link": link,
                    "publicado": pub,
                    "fonte": source
                })
    except Exception:
        pass
    return resultados

# ──────────────────────────────────────────────────────────────────────────────
# MÓDULO 1: MONITOR DE INFLUENCIADORES VIRAIS
# ──────────────────────────────────────────────────────────────────────────────
INFLUENCIADORES_MONITORADOS = [
    {
        "nome": "Virginia Fonseca",
        "query": "Virginia+Fonseca+Instagram+Reels+viral",
        "estrategia": "Humanização extrema, linguagem 'povo', humor família/Nordeste, stories autênticos, parcerias massivas. Fórmula: problema real do povo → solução simples → reação emocional.",
        "aplicacao_wilder": "Wilder deve adotar o tom 'pai de família que resolve' — mostrar esposa, filhos, casa real. Falar sobre propostas como um pai fala para o filho. Sem palanque.",
        "tipo": "influenciadora_nacional"
    },
    {
        "nome": "Raquel Lira",
        "query": "Raquel+Lira+governadora+estrategia+comunicacao",
        "estrategia": "Governadora de Pernambuco. Comunicação direta, presença em obra e resultado real. Evita polarização. Foca em entrega de serviço. Viraliza com vídeos curtos de resultado ('antes e depois').",
        "aplicacao_wilder": "Wilder, como Engenheiro, deve mostrar obras prontas e em execução. Vídeos de 30s no canteiro de obra: 'Esse buraco aqui? Em 60 dias resolve assim.' Resultado tangível, não promessa.",
        "tipo": "politica_referencia"
    },
    {
        "nome": "ACM Neto",
        "query": "ACM+Neto+discurso+estrategia+oposicao+2026",
        "estrategia": "Comunicação de oposição cirúrgica. Ataca pontos cegos do governo com dados reais. Usa humor seco e ironia para expor contradições. Mobiliza base com senso de urgência.",
        "aplicacao_wilder": "Para atacar Daniel Vilela (governador em exercício): usar dados reais de fila do SUS, buracos em estrada, salários atrasados de professores. Não atacar a pessoa — atacar o resultado entregue (ou não entregue).",
        "tipo": "politico_referencia_oposicao"
    },
    {
        "nome": "Gustavo Lima",
        "query": "Gustavo+Lima+Goias+aparicao+politica+evento",
        "estrategia": "Artista goiano de enorme apelo popular. Qualquer aliança ou aparição com candidato impacta diretamente no eleitorado do interior de Goiás (agro, evangélico, sertanejo).",
        "aplicacao_wilder": "Monitorar aparições e declarações políticas. Uma foto/vídeo com Gustavo Lima em evento no interior de Goiás vale mais do que 10 carros de som.",
        "tipo": "influenciador_goiano"
    },
    {
        "nome": "Nikolas Ferreira",
        "query": "Nikolas+Ferreira+estrategia+viral+redes+sociais+2026",
        "estrategia": "Fenômeno do engajamento jovem conservador. Fórmula: corte de discurso + legenda de impacto + resposta a adversário. Alta velocidade de produção. ASR cirúrgico.",
        "aplicacao_wilder": "Wilder deve aprender a usar 'cortes de discurso' nos Reels. Máximo 45 segundos, uma ideia só, legenda impactante, call-to-action 'manda esse vídeo pra quem você conhece em Goiás'.",
        "tipo": "referencia_engajamento_digital"
    },
    {
        "nome": "Pablo Marçal",
        "query": "Pablo+Marcal+estrategia+marketing+politico+viral",
        "estrategia": "Polêmica controlada como amplificação. Cada ataque do adversário vira conteúdo de resposta. Comunidade de apoiadores como exército orgânico de compartilhamento.",
        "aplicacao_wilder": "Monitorar como Marcal responde a ataques — modelo para usar quando Daniel ou Marconi atacarem o Wilder.",
        "tipo": "referencia_engajamento_digital"
    }
]

def atualizar_influenciadores():
    """Busca notícias recentes sobre cada influenciador monitorado."""
    print(f"[VIRAL ENGINE] 📡 Monitorando influenciadores e tendências virais... ({_agora()})")
    dados = {}

    for inf in INFLUENCIADORES_MONITORADOS:
        noticias = _buscar_rss(inf["query"], max_items=3)
        dados[inf["nome"]] = {
            "nome": inf["nome"],
            "tipo": inf["tipo"],
            "estrategia_geral": inf["estrategia"],
            "aplicacao_para_wilder": inf["aplicacao_wilder"],
            "noticias_recentes": noticias,
            "total_noticias": len(noticias)
        }
        time.sleep(0.4)

    with _cache_lock:
        VIRAL_CACHE["influenciadores"]["data"] = dados
        VIRAL_CACHE["influenciadores"]["atualizado_em"] = _agora()
        VIRAL_CACHE["influenciadores"]["ciclos"] += 1

    print(f"[VIRAL ENGINE] ✅ {len(dados)} influenciadores monitorados.")

# ──────────────────────────────────────────────────────────────────────────────
# MÓDULO 2: MONITOR DE ESTRATÉGIAS DOS ADVERSÁRIOS
# ──────────────────────────────────────────────────────────────────────────────
ADVERSARIOS = {
    "Daniel Vilela (MDB)": {
        "queries": [
            "Daniel+Vilela+governador+Goias+2026",
            "Daniel+Vilela+campanha+proposta+evento",
            "Daniel+Vilela+critica+polemia+2026"
        ],
        "vulnerabilidades_conhecidas": [
            "Ausência no debate da BandNews em 12/08/2026 — gerou 9.565 views de cobertura crítica",
            "Governador em exercício: toda falha de serviço público em Goiás é associada diretamente a ele",
            "Canal no YouTube com apenas 976 inscritos — comunicação digital fraca",
            "Gestão da saúde: filas do SUS e demora em atendimentos especializados são queixas frequentes em Goiânia e Anápolis"
        ],
        "narrativa_atual": "Candidato da continuidade e estabilidade. Tenta mostrar realizações do governo atual.",
        "pontos_de_ataque": [
            "Apresentar dados reais de fila do SUS vs. promessas do governo atual",
            "Mostrar buracos em rodovias estaduais vs. obras prometidas",
            "Usar ausência no debate como prova de arrogância de quem já se acha governador"
        ]
    },
    "Marconi Perillo (PSDB)": {
        "queries": [
            "Marconi+Perillo+PSDB+Goias+2026",
            "Marconi+Perillo+campanha+estrategia",
            "Marconi+Perillo+ex+governador+critica"
        ],
        "vulnerabilidades_conhecidas": [
            "Ex-governador com histórico longo — pode ser atacado por erros da gestão passada",
            "Candidato de 'terceira via' — eleitorado fragmentado entre ele e Wilder no campo conservador",
            "Canal no YouTube com 2.130 inscritos mas engajamento atual muito baixo (55 curtidas em debate)"
        ],
        "narrativa_atual": "Experiência e moderação. Tenta recuperar eleitores do centro que rejeitam Daniel Vilela.",
        "pontos_de_ataque": [
            "Mostrar que votar em Marconi 'divide o voto da mudança' — se Marconi e Wilder somam ~44%, o voto em Marconi pode eleger Daniel",
            "Questionar qual a inovação real de um ex-governador que já teve sua chance",
            "Usar dados do período Marconi governador para questionar sua eficiência"
        ]
    }
}

def atualizar_adversarios():
    """Busca notícias recentes e monitora estratégias dos adversários."""
    print(f"[VIRAL ENGINE] 🎯 Monitorando estratégias dos adversários... ({_agora()})")
    dados = {}

    for nome, info in ADVERSARIOS.items():
        todas_noticias = []
        for query in info["queries"]:
            noticias = _buscar_rss(query, max_items=3)
            todas_noticias.extend(noticias)
            time.sleep(0.3)

        # Deduplicação por título
        visto = set()
        noticias_unicas = []
        for n in todas_noticias:
            if n["titulo"] not in visto:
                visto.add(n["titulo"])
                noticias_unicas.append(n)

        dados[nome] = {
            "nome": nome,
            "vulnerabilidades": info["vulnerabilidades_conhecidas"],
            "narrativa_atual": info["narrativa_atual"],
            "pontos_de_ataque": info["pontos_de_ataque"],
            "noticias_recentes": noticias_unicas[:6],
            "total_noticias": len(noticias_unicas)
        }

    with _cache_lock:
        VIRAL_CACHE["adversarios"]["data"] = dados
        VIRAL_CACHE["adversarios"]["atualizado_em"] = _agora()
        VIRAL_CACHE["adversarios"]["ciclos"] += 1

    print(f"[VIRAL ENGINE] ✅ {len(dados)} adversários monitorados com {sum(d['total_noticias'] for d in dados.values())} notícias captadas.")

# ──────────────────────────────────────────────────────────────────────────────
# MÓDULO 3: TENDÊNCIAS NACIONAIS VIRAIS
# ──────────────────────────────────────────────────────────────────────────────
QUERIES_TENDENCIAS_VIRAIS = [
    {"query": "viral+Instagram+Reels+Brasil+2026", "categoria": "🎬 Viral Instagram"},
    {"query": "meme+politica+Brasil+semana", "categoria": "😂 Meme Político"},
    {"query": "governador+eleicao+2026+estrategia+digital", "categoria": "🗳️ Eleição 2026"},
    {"query": "governador+Goias+eleicao+2026+tendencia", "categoria": "🗺️ Goiás Eleição"},
    {"query": "Nikolas+Ferreira+viral+2026", "categoria": "⚡ Referência Digital"},
    {"query": "eleicao+2026+influenciador+apoio+candidato", "categoria": "👥 Influenciadores x Candidatos"},
    {"query": "campanha+eleitoral+viral+redes+sociais+2026", "categoria": "📱 Marketing Eleitoral Digital"}
]

def atualizar_tendencias_nacionais():
    """Busca tendências virais e de marketing político nacional."""
    print(f"[VIRAL ENGINE] 🌐 Captando tendências nacionais virais... ({_agora()})")
    tendencias = []

    for item in QUERIES_TENDENCIAS_VIRAIS:
        noticias = _buscar_rss(item["query"], max_items=2)
        for n in noticias:
            tendencias.append({
                "categoria": item["categoria"],
                "titulo": n["titulo"],
                "link": n["link"],
                "publicado": n["publicado"],
                "fonte": n["fonte"]
            })
        time.sleep(0.3)

    with _cache_lock:
        VIRAL_CACHE["tendencias_nacionais"]["data"] = tendencias
        VIRAL_CACHE["tendencias_nacionais"]["atualizado_em"] = _agora()
        VIRAL_CACHE["tendencias_nacionais"]["ciclos"] += 1

    print(f"[VIRAL ENGINE] ✅ {len(tendencias)} tendências nacionais captadas.")

# ──────────────────────────────────────────────────────────────────────────────
# MÓDULO 4: BRIEFING ESTRATÉGICO AUTOMÁTICO
# ──────────────────────────────────────────────────────────────────────────────
def gerar_briefing_estrategico():
    """Gera um briefing estratégico consolidado com base em todos os dados coletados."""
    print(f"[VIRAL ENGINE] 📋 Gerando briefing estratégico... ({_agora()})")

    with _cache_lock:
        inf_data = VIRAL_CACHE["influenciadores"]["data"]
        adv_data = VIRAL_CACHE["adversarios"]["data"]
        trend_data = VIRAL_CACHE["tendencias_nacionais"]["data"]

    # Noticias adversários mais recentes
    noticias_daniel = []
    noticias_marconi = []
    if "Daniel Vilela (MDB)" in adv_data:
        noticias_daniel = adv_data["Daniel Vilela (MDB)"]["noticias_recentes"][:3]
    if "Marconi Perillo (PSDB)" in adv_data:
        noticias_marconi = adv_data["Marconi Perillo (PSDB)"]["noticias_recentes"][:3]

    # Tendências mais relevantes
    top_trends = trend_data[:5]

    # Estratégias de influenciadores
    estrategias_influenciadores = []
    for nome, dados in inf_data.items():
        if dados.get("aplicacao_para_wilder"):
            estrategias_influenciadores.append({
                "influenciador": nome,
                "aplicacao": dados["aplicacao_para_wilder"],
                "noticias": dados.get("noticias_recentes", [])[:2]
            })

    briefing = {
        "atualizado_em": _agora(),
        "cenario_eleitoral": {
            "lider": "Daniel Vilela (MDB) — 43,5%",
            "segundo_lugar": "Wilder Morais (PL) — 22,0% (empate técnico com Marconi 21,9%)",
            "diagnostico_neutro": "Wilder está em empate técnico pelo 2º turno mas a 21,5 pontos do líder. Para vencer, precisa de crescimento significativo e que Marconi perca força.",
            "oportunidade_critica": "Se o eleitorado conservador/centro-direita (Wilder + Marconi = ~44%) se unir, o 2º turno é certo."
        },
        "oportunidades_de_ataque": [
            {
                "alvo": "Daniel Vilela",
                "argumento": "Governador em exercício = responsável direto por toda fila do SUS, buraco em estrada e salário atrasado. Use dados reais, não acusações genéricas.",
                "formato_sugerido": "Reels de 30s: 'Esse buraco aqui é da gestão Daniel Vilela. Há X meses esperando conserto. Quando eu for governador: [solução prática]'"
            },
            {
                "alvo": "Marconi Perillo",
                "argumento": "Votar em Marconi é dividir o voto da mudança. Se Wilder + Marconi = 44%, isso garante 2º turno, mas dividido entre dois candidatos um pode perder. Quem é mais novo, mais forte digitalmente?",
                "formato_sugerido": "Infográfico simples: '44% dos goianos querem mudança. Só um deles vai ao 2º turno. Qual é o mais preparado para ganhar?'"
            }
        ],
        "aprendizados_de_influenciadores": estrategias_influenciadores,
        "tendencias_virais_semana": top_trends,
        "checklist_48h": [
            "🎯 Gravar 3 Reels de 30-45s com 'antes e depois' de problemas reais + solução proposta pelo Wilder",
            "📱 Criar 1 vídeo no estilo 'corte de discurso' respondendo à última declaração de Daniel Vilela",
            "🤝 Mapear se há aparição de Gustavo Lima ou artista goiano em evento próximo — oportunidade de foto estratégica",
            "📊 Usar dado de fila do SUS do Google Trends como gancho de Reel viral (ASR: 'fila do SUS')",
            "🗺️ Fazer pelo menos 1 visita filmada em município do interior com queixa real identificada no mapa de demandas",
            "⚡ Responder ao próximo ataque de adversário dentro de 2 horas com vídeo curto — não ignorar"
        ],
        "noticias_adversarios": {
            "daniel_vilela": noticias_daniel,
            "marconi_perillo": noticias_marconi
        }
    }

    with _cache_lock:
        VIRAL_CACHE["briefing_estrategico"]["data"] = briefing
        VIRAL_CACHE["briefing_estrategico"]["atualizado_em"] = _agora()
        VIRAL_CACHE["briefing_estrategico"]["ciclos"] += 1

    print(f"[VIRAL ENGINE] ✅ Briefing estratégico gerado com sucesso.")
    return briefing

# ──────────────────────────────────────────────────────────────────────────────
# INTERFACE PÚBLICA
# ──────────────────────────────────────────────────────────────────────────────
def get_influenciadores():
    with _cache_lock:
        return dict(VIRAL_CACHE["influenciadores"]["data"])

def get_adversarios():
    with _cache_lock:
        return dict(VIRAL_CACHE["adversarios"]["data"])

def get_tendencias_nacionais():
    with _cache_lock:
        return list(VIRAL_CACHE["tendencias_nacionais"]["data"])

def get_briefing_estrategico():
    with _cache_lock:
        return dict(VIRAL_CACHE["briefing_estrategico"]["data"])

def get_status():
    with _cache_lock:
        return {
            "influenciadores": {
                "total": len(VIRAL_CACHE["influenciadores"]["data"]),
                "atualizado_em": VIRAL_CACHE["influenciadores"]["atualizado_em"]
            },
            "adversarios": {
                "total": len(VIRAL_CACHE["adversarios"]["data"]),
                "atualizado_em": VIRAL_CACHE["adversarios"]["atualizado_em"]
            },
            "tendencias_nacionais": {
                "total": len(VIRAL_CACHE["tendencias_nacionais"]["data"]),
                "atualizado_em": VIRAL_CACHE["tendencias_nacionais"]["atualizado_em"]
            },
            "briefing": {
                "atualizado_em": VIRAL_CACHE["briefing_estrategico"]["atualizado_em"]
            }
        }

def atualizar_tudo():
    """Executa todos os módulos de monitoramento."""
    atualizar_influenciadores()
    atualizar_adversarios()
    atualizar_tendencias_nacionais()
    gerar_briefing_estrategico()

# ──────────────────────────────────────────────────────────────────────────────
# EXECUÇÃO DIRETA (TESTE)
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print("=" * 60)
    print("🛰️ VIRAL TRENDS ENGINE — TESTE DIRETO")
    print("=" * 60)
    atualizar_tudo()
    briefing = get_briefing_estrategico()
    print("\n📋 BRIEFING GERADO:")
    print(json.dumps(briefing, ensure_ascii=False, indent=2)[:2000])
    print("\n✅ Viral Trends Engine operacional!")
