import requests
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

def get_real_youtube_videos(channel_handle):
    url = f"https://www.youtube.com/{channel_handle}/videos"
    try:
        r = requests.get(url, headers=headers, timeout=12, verify=False)
        # Extrai os títulos e videoIds diretamente do HTML público do canal
        vids_titles = re.findall(r'"videoId":"([A-Za-z0-9_-]{11})".*?"title":{"runs":\[{"text":"([^"]+)"}\]', r.text)
        
        blacklist = {"ef2HN_TrD6g", "5vFccfWqKfY", "YOUTUBE_ID"}
        results = []
        seen = set()
        for vid, title in vids_titles:
            if vid not in seen and vid not in blacklist and len(title) > 3:
                seen.add(vid)
                results.append({
                    "id": vid,
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={vid}"
                })
        print(f"=== {channel_handle}: Encontrados {len(results)} videos ===")
        for res in results[:5]:
            print(f"  ID: {res['id']} | Titulo: {res['title']} | URL: {res['url']}")
        return results
    except Exception as e:
        print(f"Erro no canal {channel_handle}: {e}")
        return []

if __name__ == "__main__":
    get_real_youtube_videos("@WilderMoraisGoias")
    get_real_youtube_videos("@danielvilela15")
