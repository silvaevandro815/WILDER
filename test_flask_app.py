from server_web_unificado import app

def test_flask_routes():
    print("=== TESTANDO INSTANCIAÇÃO DA APLICAÇÃO FLASK COM RADAR DE EVENTOS & TRÁFEGO PAGO ===")
    print(f"App Name: {app.name}")
    client = app.test_client()

    routes = [
        "/", "/dashboard", "/download_pdf", "/radar_noticias",
        "/mapa_demandas", "/plano_governo", "/eventos",
        "/api/status", "/api/noticias", "/api/tendencias"
    ]
    for route in routes:
        response = client.get(route)
        print(f"GET {route} -> Status Code: {response.status_code}")
        assert response.status_code in [200, 302], f"Rota {route} falhou com código {response.status_code}"

    # Teste de forçar atualização
    res_post = client.post("/api/forcar_atualizacao")
    print(f"POST /api/forcar_atualizacao -> Status Code: {res_post.status_code}")
    assert res_post.status_code == 200, "Falha na rota /api/forcar_atualizacao"

    print("🎉 TODAS AS ROTAS DO SERVIDOR E APIS DO MOTOR AUTÔNOMO RESPONDERAM COM SUCESSO!")

if __name__ == "__main__":
    test_flask_routes()
