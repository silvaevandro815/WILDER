import requests
import xml.etree.ElementTree as ET
import urllib.parse
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_rss_news_cand(candidato):
    query = f"{candidato} Goias"
    encoded_q = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    
    try:
        r = requests.get(rss_url, headers=headers, timeout=10, verify=False)
        root = ET.fromstring(r.text)
        items = []
        for item in root.findall('.//item')[:6]:
            title = item.find('title').text if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
            source = item.find('source').text if item.find('source') is not None else "Imprensa de Goiás"
            
            clean_title = title.split(" - ")[0] if " - " in title else title
            
            t_lower = title.lower()
            if any(k in t_lower for k in ["crítica", "critica", "aponta", "investiga", "oposição", "oposicao", "preso", "denúncia", "denuncia", "processo", "atraso", "crise", "desgaste"]):
                tipo = "🔴 CRÍTICA / ALERTA"
            elif any(k in t_lower for k in ["lidera", "cresce", "apoio", "obras", "entrega", "avanço", "avanco", "vence", "pesquisa", "aliança", "alianca", "posse"]):
                tipo = "🟢 POSITIVA"
            else:
                tipo = "NEUTRA"

            items.append({
                "candidato": candidato,
                "veiculo": source,
                "manchete": clean_title,
                "data": pub_date[:16] if len(pub_date) > 16 else pub_date,
                "tipo_noticia": tipo,
                "url_noticia": link,
                "url_google_news": link
            })
        return items
    except Exception as e:
        print(f"Erro ao buscar RSS para {candidato}: {e}")
        return []

def get_all_real_news():
    w = fetch_rss_news_cand("Wilder Morais")
    d = fetch_rss_news_cand("Daniel Vilela")
    m = fetch_rss_news_cand("Marconi Perillo")
    todas = w + d + m
    print(f"=== TOTAL DE NOTICIAS REAIS CAPTURADAS AO VIVO: {len(todas)} ===")
    for n in todas:
        print(f"[{n['candidato']}] [{n['veiculo']}] {n['manchete']} | Link: {n['url_noticia']}")
    return todas

if __name__ == "__main__":
    news = get_all_real_news()
    with open("noticias_reais_goias.json", "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
