from server_web_unificado import app
import json

def test_flask_routes():
    print("=== TESTANDO INSTANCIACAO DA APLICACAO FLASK — QG DIGITAL WILDER MORAIS 2026 ===")
    print(f"App Name: {app.name}")
    client = app.test_client()

    routes = [
        "/", "/dashboard", "/download_pdf", "/radar_noticias",
        "/mapa_demandas", "/plano_governo", "/eventos",
        "/api/status", "/api/noticias", "/api/tendencias",
        "/engajamento", "/api/palavras_magneticas"
    ]
    for route in routes:
        response = client.get(route)
        print(f"GET {route} -> Status Code: {response.status_code}")
        assert response.status_code in [200, 302], f"Rota {route} falhou com codigo {response.status_code}"

    # Teste de forccar atualizacao
    res_post = client.post("/api/forcar_atualizacao")
    print(f"POST /api/forcar_atualizacao -> Status Code: {res_post.status_code}")
    assert res_post.status_code == 200, "Falha na rota /api/forcar_atualizacao"

    # Teste do gerador de roteiro viral (POST)
    payload_roteiro = {
        "tema": "saude e filas do SUS",
        "estimulo": "furar_bolha",
        "formato": "reels_30s",
        "cidade": "Goiania"
    }
    res_roteiro = client.post(
        "/api/gerar_roteiro_viral",
        data=json.dumps(payload_roteiro),
        content_type="application/json"
    )
    print(f"POST /api/gerar_roteiro_viral -> Status Code: {res_roteiro.status_code}")
    assert res_roteiro.status_code == 200, f"Falha na rota /api/gerar_roteiro_viral: {res_roteiro.status_code}"
    roteiro_data = json.loads(res_roteiro.data)
    assert "titulo_estrategico" in roteiro_data or "erro" not in roteiro_data, f"Resposta inesperada: {roteiro_data}"
    print(f"  -> Roteiro gerado: {roteiro_data.get('titulo_estrategico', '(sem titulo)')}")

    # Teste do auditor de roteiro (POST)
    payload_auditoria = {
        "roteiro": "Caros eleitores, neste pleito me comprometo com a reestruturacao sistematica e o plano plurianual de investimentos. Vote no numero 12."
    }
    res_auditoria = client.post(
        "/api/auditar_roteiro",
        data=json.dumps(payload_auditoria),
        content_type="application/json"
    )
    print(f"POST /api/auditar_roteiro -> Status Code: {res_auditoria.status_code}")
    assert res_auditoria.status_code == 200, f"Falha na rota /api/auditar_roteiro: {res_auditoria.status_code}"
    audit_data = json.loads(res_auditoria.data)
    print(f"  -> Score obtido: {audit_data.get('score_viral', '?')}/100 | Classificacao: {audit_data.get('classificacao', '?')}")

    print("")
    print("TODAS AS ROTAS DO SERVIDOR E APIS DO MOTOR DE ENGAJAMENTO RESPONDERAM COM SUCESSO!")

if __name__ == "__main__":
    test_flask_routes()
