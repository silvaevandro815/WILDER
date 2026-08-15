import os

def test_map_code():
    from server_web_unificado import HTML_MAPA_DEMANDAS, HTML_RADAR_EVENTOS
    assert "custom-pin" in HTML_MAPA_DEMANDAS
    assert "svg-map-container" in HTML_MAPA_DEMANDAS or "leaflet" in HTML_MAPA_DEMANDAS
    print("✅ Código do Mapa validado com sucesso!")

if __name__ == "__main__":
    test_map_code()
