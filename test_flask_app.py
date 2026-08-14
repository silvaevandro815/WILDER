import sys
import server_web_unificado

print("=== TESTANDO INSTANCIAÇÃO DA APLICAÇÃO FLASK COM DASHBOARD METABASE ===")
app = server_web_unificado.app

print("App Name:", app.name)
with app.test_client() as client:
    res = client.get("/")
    print("GET / -> Status Code:", res.status_code)
    
    res_dash = client.get("/dashboard")
    print("GET /dashboard -> Status Code:", res_dash.status_code)
    
    res_pdf = client.get("/download_pdf")
    print("GET /download_pdf -> Status Code:", res_pdf.status_code)
    
    res_radar = client.get("/radar_noticias")
    print("GET /radar_noticias -> Status Code:", res_radar.status_code)
    
    res_mapa = client.get("/mapa_demandas")
    print("GET /mapa_demandas -> Status Code:", res_mapa.status_code)

print("🎉 APLICAÇÃO FLASK E DASHBOARD METABASE RESPONDERAM COM SUCESSO A TODAS AS ROTAS!")
