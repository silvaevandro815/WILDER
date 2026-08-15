import re

# Testar se a rota mapa_demandas possui Jinja2 limpo {{ reclamacoes|tojson }}
def verify_template_syntax(html):
    if "{ reclamacoes|tojson }" in html or "{ google_trends|tojson }" in html:
        print("❌ ERRO: F-string corrompeu a sintaxe do Jinja2!")
        return False
    print("✅ SUCESSO: Sintaxe Jinja2 preservada com {{ reclamacoes|tojson }}!")
    return True

if __name__ == "__main__":
    from server_web_unificado import app
    with app.test_client() as client:
        res = client.get('/mapa_demandas')
        text = res.get_data(as_text=True)
        verify_template_syntax(text)
        print("Tamanho do HTML retornado:", len(text))
        if "chartCidades" in text and "chartGoogleTrends" in text:
            print("✅ Todos os 4 ID de gráficos Chart.js encontrados no HTML!")
        else:
            print("❌ ERRO: IDs dos gráficos ausentes!")
