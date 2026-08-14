from server_web_unificado import app

def test_flask_routes():
    print("=== TESTANDO INSTANCIAÇÃO DA APLICAÇÃO FLASK COM RADAR DE EVENTOS & TRÁFEGO PAGO ===")
    print(f"App Name: {app.name}")
    client = app.test_client()

    routes = ["/", "/dashboard", "/download_pdf", "/radar_noticias", "/mapa_demandas", "/plano_governo", "/eventos"]
    for route in routes:
        response = client.get(route)
        print(f"GET {route} -> Status Code: {response.status_code}")
        assert response.status_code in [200, 302], f"Rota {route} falhou com código {response.status_code}"

    print("🎉 APLICAÇÃO FLASK, DASHBOARD & RADAR DE EVENTOS RESPONDERAM COM SUCESSO A TODAS AS ROTAS!")

if __name__ == "__main__":
    test_flask_routes()
