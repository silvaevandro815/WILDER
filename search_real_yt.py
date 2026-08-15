import urllib.request
import urllib.parse
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9"
}

def search_youtube_videos(query):
    encoded_q = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded_q}"
    req = urllib.request.Request(url, headers=headers)
    
    videos = []
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8')
            # Extrair videoId e title usando regex em ytInitialData
            matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})".*?"title":\{"runs":\[\{"text":"([^"]+)"\}', html)
            seen_ids = set()
            for vid, title in matches:
                if vid not in seen_ids and len(vid) == 11:
                    seen_ids.add(vid)
                    videos.append({"video_id": vid, "titulo": title})
                if len(videos) >= 5:
                    break
    except Exception as e:
        print(f"Erro ao buscar {query}: {e}")
    return videos

if __name__ == "__main__":
    print("=== BUSCANDO VÍDEOS REAIS DO WILDER MORAIS ===")
    wilder_vids = search_youtube_videos("Wilder Morais Goias")
    print(json.dumps(wilder_vids, ensure_ascii=False, indent=2))

    print("\n=== BUSCANDO VÍDEOS REAIS DO DANIEL VILELA ===")
    daniel_vids = search_youtube_videos("Daniel Vilela Goias")
    print(json.dumps(daniel_vids, ensure_ascii=False, indent=2))

    print("\n=== BUSCANDO VÍDEOS REAIS DO MARCONI PERILLO ===")
    marconi_vids = search_youtube_videos("Marconi Perillo Goias")
    print(json.dumps(marconi_vids, ensure_ascii=False, indent=2))
