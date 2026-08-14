import requests
import json
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_yt_initial_data(handle):
    url = f"https://www.youtube.com/{handle}/videos"
    r = requests.get(url, headers=headers, timeout=10, verify=False)
    
    # Extrair ytInitialData
    match = re.search(r'var ytInitialData = ({.*?});</script>', r.text)
    if match:
        data = json.loads(match.group(1))
        videos = []
        try:
            tabs = data['contents']['twoColumnBrowseResultsRenderer']['tabs']
            for tab in tabs:
                if 'tabRenderer' in tab and tab['tabRenderer'].get('selected'):
                    contents = tab['tabRenderer']['content']['richGridRenderer']['contents']
                    for item in contents:
                        if 'richItemRenderer' in item:
                            video_data = item['richItemRenderer']['content'].get('videoRenderer')
                            if video_data:
                                vid = video_data['videoId']
                                title = video_data['title']['runs'][0]['text']
                                views = video_data.get('viewCountText', {}).get('simpleText', 'Dados em tempo real')
                                published = video_data.get('publishedTimeText', {}).get('simpleText', 'Recente')
                                videos.append({
                                    "titulo": title,
                                    "video_id": vid,
                                    "url": f"https://www.youtube.com/watch?v={vid}",
                                    "views": views,
                                    "publicado": published,
                                    "canal": handle
                                })
        except Exception as e:
            print(f"Erro ao extrair JSON para {handle}: {e}")
        return videos
    return []

if __name__ == "__main__":
    v_w = fetch_yt_initial_data("@WilderMoraisGoias")
    print(f"=== VÍDEOS ENCONTRADOS PARA WILDER MORAIS (@WilderMoraisGoias): {len(v_w)} ===")
    for v in v_w[:5]:
        print(f" 🎬 {v['titulo']} | Views: {v['views']} | Data: {v['publicado']} | URL: {v['url']}")

    v_d = fetch_yt_initial_data("@danielvilela15")
    print(f"\n=== VÍDEOS ENCONTRADOS PARA DANIEL VILELA (@danielvilela15): {len(v_d)} ===")
    for v in v_d[:5]:
        print(f" 🎬 {v['titulo']} | Views: {v['views']} | Data: {v['publicado']} | URL: {v['url']}")
