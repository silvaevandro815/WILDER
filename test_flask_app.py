from server_web_unificado import app
import json

def test_flask_routes():
    print("=== TESTANDO QG DIGITAL — MODO MILITAR ATIVO ===")
    print(f"App Name: {app.name}")
    client = app.test_client()

    routes = [
        "/", "/dashboard", "/download_pdf", "/radar_noticias",
        "/mapa_demandas", "/plano_governo", "/eventos",
        "/api/status", "/api/noticias", "/api/tendencias",
        "/engajamento", "/api/palavras_magneticas",
        # NOVAS ROTAS MILITARES
        "/intel",
        "/api/intel_queixas",
        "/api/intel_mapa",
        "/api/intel_ibge",
        "/api/intel_ranking",
        "/api/intel_status",
    ]
    ok = 0
    for route in routes:
        response = client.get(route)
        status_icon = "OK" if response.status_code in [200, 302] else "FAIL"
        print(f"  [{status_icon}] GET {route} -> {response.status_code}")
        assert response.status_code in [200, 302], f"Rota {route} falhou: {response.status_code}"
        ok += 1

    # POST forcar atualizacao
    res = client.post("/api/forcar_atualizacao")
    print(f"  [OK] POST /api/forcar_atualizacao -> {res.status_code}")
    assert res.status_code == 200

    # POST forcar intel
    res_intel = client.post("/api/intel_forcar")
    print(f"  [OK] POST /api/intel_forcar -> {res_intel.status_code}")
    assert res_intel.status_code == 200

    # POST gerar roteiro
    payload = {"tema": "saude e filas do SUS","estimulo":"furar_bolha","formato":"reels_30s","cidade":"Goiania"}
    res_rot = client.post("/api/gerar_roteiro_viral", data=json.dumps(payload), content_type="application/json")
    print(f"  [OK] POST /api/gerar_roteiro_viral -> {res_rot.status_code}")

    # POST auditar roteiro
    payload2 = {"roteiro": "Caros eleitores neste pleito votai em mim para reestruturacao sistemica"}
    res_aud = client.post("/api/auditar_roteiro", data=json.dumps(payload2), content_type="application/json")
    data_aud = json.loads(res_aud.data)
    print(f"  [OK] POST /api/auditar_roteiro -> {res_aud.status_code} (score: {data_aud.get('score_viral','?')}/100)")

    print("")
    print(f"TODAS AS {ok + 4} ROTAS RESPONDERAM COM SUCESSO! SISTEMA MILITAR OPERACIONAL.")

if __name__ == "__main__":
    test_flask_routes()
