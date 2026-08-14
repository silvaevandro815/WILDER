import requests
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_youtube_real_videos(channel_handle):
    print(f"=== BUSCANDO VÍDEOS REAIS DO YOUTUBE PARA: {channel_handle} ===")
    url = f"https://www.youtube.com/{channel_handle}/videos"
    try:
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        matches = re.findall(r'"videoId":"([^"]+)".*?"title":{"runs":\[{"text":"([^"]+)"}\]', r.text)
        unique_videos = []
        seen = set()
        for vid, title in matches:
            if vid not in seen and len(title) > 3:
                seen.add(vid)
                unique_videos.append({
                    "id": vid,
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={vid}"
                })
        print(f"Encontrados {len(unique_videos)} vídeos reais do YouTube!")
        for v in unique_videos[:5]:
            print(f" -> [{v['id']}] {v['title']} | URL: {v['url']}")
        return unique_videos
    except Exception as e:
        print(f"Erro ao buscar YouTube: {e}")
        return []

if __name__ == "__main__":
    fetch_youtube_real_videos("@WilderMoraisGoias")
    fetch_youtube_real_videos("@danielvilela15")
