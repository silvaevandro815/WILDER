from server_web_unificado import app
import json

def test_flask_routes():
    print("=================================================================")
    print("🎖️ TESTANDO QG DIGITAL ELEITORAL — MONITORAMENTO MASTER AO VIVO")
    print("=================================================================")
    print(f"App Name: {app.name}")
    client = app.test_client()

    routes = [
        "/",
        "/dashboard",
        "/download_pdf",
        "/radar_noticias",
        "/mapa_demandas",
        "/plano_governo",
        "/eventos",
        "/engajamento",
        "/intel",
        # APIs DO MOTOR MASTER
        "/api/status",
        "/api/noticias",
        "/api/pesquisas",
        "/api/eventos_grandes",
        "/api/tendencias",
        "/api/palavras_magneticas",
        "/api/meta_algoritmo",
        # APIs DO MOTOR INTEL TERRITORIAL
        "/api/intel_queixas",
        "/api/intel_mapa",
        "/api/intel_ibge",
        "/api/intel_ranking",
        "/api/intel_status",
    ]
    ok = 0
    for route in routes:
        response = client.get(route)
        status_icon = "🟢 OK" if response.status_code in [200, 302] else "🔴 FAIL"
        print(f"  [{status_icon}] GET {route} -> Status Code: {response.status_code}")
        assert response.status_code in [200, 302], f"Rota {route} falhou com código {response.status_code}"
        ok += 1

    # POST forçar atualização master
    res_master = client.post("/api/forcar_atualizacao")
    print(f"  [🟢 OK] POST /api/forcar_atualizacao -> {res_master.status_code}")
    assert res_master.status_code == 200

    # POST forçar intel territorial
    res_intel = client.post("/api/intel_forcar")
    print(f"  [🟢 OK] POST /api/intel_forcar -> {res_intel.status_code}")
    assert res_intel.status_code == 200

    # POST gerar roteiro viral
    payload_rot = {
        "tema": "saude e filas do SUS",
        "estimulo": "furar_bolha",
        "formato": "reels_30s",
        "cidade": "Goiania"
    }
    res_rot = client.post("/api/gerar_roteiro_viral", data=json.dumps(payload_rot), content_type="application/json")
    print(f"  [🟢 OK] POST /api/gerar_roteiro_viral -> {res_rot.status_code}")
    assert res_rot.status_code == 200

    # POST auditar roteiro viral
    payload_aud = {
        "roteiro": "Caros eleitores deste pleito, venho propor a reestruturacao sistemica do aparato orcamentario."
    }
    res_aud = client.post("/api/auditar_roteiro", data=json.dumps(payload_aud), content_type="application/json")
    data_aud = json.loads(res_aud.data)
    print(f"  [🟢 OK] POST /api/auditar_roteiro -> {res_aud.status_code} (Score: {data_aud.get('score_viral', '?')}/100)")
    assert res_aud.status_code == 200

    # Teste do Chat da IA (Paulo com consciência do Algoritmo da Meta e do Projeto)
    payload_chat_meta = {
        "pergunta": "Como o algoritmo do Instagram entrega meus vídeos e como furar a bolha em Goiás?"
    }
    res_chat = client.post("/api/chat", data=json.dumps(payload_chat_meta), content_type="application/json")
    print(f"  [🟢 OK] POST /api/chat (Meta Algoritmo) -> {res_chat.status_code}")
    assert res_chat.status_code == 200

    # Validação do retorno de inteligência da Meta
    res_meta = client.get("/api/meta_algoritmo")
    data_meta = json.loads(res_meta.data)
    assert "diretrizes" in data_meta, "Chave 'diretrizes' ausente em /api/meta_algoritmo"
    print(f"  [🟢 OK] Radar Meta 2026: Status {data_meta.get('status','?')}")

    # Validação do retorno de pesquisas
    res_pesq = client.get("/api/pesquisas")
    data_pesq = json.loads(res_pesq.data)
    assert "consolidado" in data_pesq, "Chave 'consolidado' ausente em /api/pesquisas"
    print(f"  [🟢 OK] Dados de Pesquisas: Instituto {data_pesq.get('consolidado',{}).get('instituto','?')}")

    # Validação do retorno de tendências categorizadas
    res_tend = client.get("/api/tendencias")
    data_tend = json.loads(res_tend.data)
    assert "tendencias" in data_tend, "Chave 'tendencias' ausente em /api/tendencias"
    print(f"  [🟢 OK] Dados de Tendências: {data_tend.get('total',0)} buscas mapeadas")

    # Validação do retorno de eventos grandes (+500 pessoas)
    res_ev = client.get("/api/eventos_grandes")
    data_ev = json.loads(res_ev.data)
    assert "eventos" in data_ev, "Chave 'eventos' ausente em /api/eventos_grandes"
    print(f"  [🟢 OK] Radar de Eventos: {data_ev.get('total',0)} eventos cadastrados")

    print("")
    print(f"🎉 SUCESSO ABSOLUTO: TODAS AS {ok + 5} ROTAS E APIS RESPONDERAM 100% OPERACIONAIS!")

if __name__ == "__main__":
    test_flask_routes()
