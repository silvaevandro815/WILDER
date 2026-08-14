import requests
import re
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

def get_real_youtube_stats(channel_handle):
    url = f"https://www.youtube.com/{channel_handle}/videos"
    try:
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        # Buscar views e titulos reais no HTML publico do YouTube
        matches = re.findall(r'"title":{"runs":\[{"text":"([^"]+)"}\].*?"viewCountText":{"simpleText":"([^"]+)"}', r.text)
        
        results = []
        for title, views in matches[:5]:
            results.append({
                "title": title,
                "views": views
            })
        print(f"=== YOUTUBE REAL DADOS PARA {channel_handle} ===")
        for res in results:
            print(f" -> {res['title']} | Views Reais: {res['views']}")
        return results
    except Exception as e:
        print(f"Erro ao buscar YouTube {channel_handle}: {e}")
        return []

if __name__ == "__main__":
    get_real_youtube_stats("@WilderMoraisGoias")
    get_real_youtube_stats("@danielvilela15")
