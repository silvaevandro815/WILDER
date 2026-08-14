import requests
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_wilder_yt():
    url = "https://www.youtube.com/@WilderMoraisGoias/videos"
    r = requests.get(url, headers=headers, verify=False, timeout=10)
    
    # Busca por links de shorts e vídeos no HTML público do Wilder Morais
    matches = re.findall(r'href="/(watch\?v=[^"]+|shorts/[^"]+)"', r.text)
    unique_links = list(dict.fromkeys(matches))
    print(f"=== YOUTUBE VÍDEOS REAIS WILDER MORAIS (@WilderMoraisGoias) ===")
    for l in unique_links[:6]:
        full_url = f"https://www.youtube.com/{l}"
        print(" 🎬", full_url)

fetch_wilder_yt()
