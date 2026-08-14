import urllib.parse

def make_exact_news_link(candidato, manchete, portal):
    # Constrói link de busca exata e direta no Google News e no portal oficial
    query = f"{candidato} {manchete}"
    encoded_q = urllib.parse.quote(query)
    google_news_url = f"https://news.google.com/search?q={encoded_q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    portal_search_url = f"https://www.google.com/search?q=site:{portal}+{urllib.parse.quote(candidato)}"
    return google_news_url, portal_search_url

if __name__ == "__main__":
    gn, ps = make_exact_news_link("Wilder Morais", "emendas saude Goias", "opopular.com.br")
    print("Google News Exact URL:", gn)
    print("Portal Search URL:", ps)
