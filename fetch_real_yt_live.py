import requests
import json
import re
import xml.etree.ElementTree as ET
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_youtube_channel_live(handle):
    print(f"\n=== CONSULTANDO DADOS REAIS DO YOUTUBE PARA: {handle} ===")
    url = f"https://www.youtube.com/{handle}/videos"
    try:
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        
        # Extrair títulos e views reais do HTML do canal
        video_matches = re.findall(r'"title":{"runs":\[{"text":"([^"]+)"}\].*?"viewCountText":{"simpleText":"([^"]+)"}', r.text)
        
        real_videos = []
        seen = set()
        for title, views in video_matches:
            if title not in seen:
                seen.add(title)
                # Tentar pegar videoId se disponível no trecho
                real_videos.append({
                    "titulo": title,
                    "views": views,
                    "canal": handle,
                    "url": f"https://www.youtube.com/{handle}/videos"
                })
        
        if not real_videos:
            # Fallback via RSS XML público do YouTube
            print("Tentando RSS XML público...")
            rss_url = f"https://www.youtube.com/feeds/videos.xml?user={handle.replace('@','')}"
            r_rss = requests.get(rss_url, headers=headers, timeout=10, verify=False)
            if r_rss.status_code == 200:
                root = ET.fromstring(r_rss.text)
                ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
                for entry in root.findall('atom:entry', ns)[:5]:
                    t = entry.find('atom:title', ns).text
                    l = entry.find('atom:link', ns).attrib['href']
                    real_videos.append({
                        "titulo": t,
                        "views": "Dados ao vivo no YouTube",
                        "canal": handle,
                        "url": l
                    })

        print(f"Obtidos {len(real_videos)} vídeos reais de {handle}:")
        for v in real_videos[:4]:
            print(f" -> [{v['canal']}] {v['titulo']} | Views: {v['views']} | URL: {v['url']}")
        return real_videos
    except Exception as e:
        print(f"Erro ao consultar YouTube {handle}: {e}")
        return []

if __name__ == "__main__":
    fetch_youtube_channel_live("@WilderMoraisGoias")
    fetch_youtube_channel_live("@danielvilela15")
