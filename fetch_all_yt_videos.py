import requests
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_channel_videos(handle):
    url = f"https://www.youtube.com/{handle}/videos"
    try:
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        matches = re.findall(r'"title":{"runs":\[{"text":"([^"]+)"}\].*?"navigationEndpoint":{"clickTrackingParams":"[^"]*","commandMetadata":{"webCommandMetadata":{"url":"/(watch\?v=[^"]+|shorts/[^"]+)"', r.text)
        
        results = []
        seen = set()
        for title, link in matches:
            if title not in seen and len(title) > 3:
                seen.add(title)
                full_url = f"https://www.youtube.com/{link}"
                results.append({
                    "titulo": title,
                    "url": full_url
                })
        return results
    except Exception as e:
        print(f"Erro no canal {handle}: {e}")
        return []

if __name__ == "__main__":
    v_wilder = get_channel_videos("@WilderMoraisGoias")
    print(f"=== WILDER MORAIS: {len(v_wilder)} VÍDEOS ENCONTRADOS ===")
    for v in v_wilder[:5]:
        print(f" 🎬 {v['titulo']} -> {v['url']}")

    v_daniel = get_channel_videos("@danielvilela15")
    print(f"\n=== DANIEL VILELA: {len(v_daniel)} VÍDEOS ENCONTRADOS ===")
    for v in v_daniel[:5]:
        print(f" 🎬 {v['titulo']} -> {v['url']}")
