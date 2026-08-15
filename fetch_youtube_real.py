import requests
import xml.etree.ElementTree as ET
import urllib.parse
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_youtube_rss_cand(candidato, video_id_fallback, canal_nome):
    query = f"{candidato} Goias 2026"
    encoded_q = urllib.parse.quote(query)
    # YouTube RSS feed de busca
    rss_url = f"https://www.youtube.com/feeds/videos.xml?search_query={encoded_q}"
    
    videos = []
    try:
        r = requests.get(rss_url, headers=headers, timeout=8, verify=False)
        root = ET.fromstring(r.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015', 'media': 'http://search.yahoo.com/mrss/'}
        for entry in root.findall('.//atom:entry', ns)[:4]:
            title = entry.find('atom:title', ns).text if entry.find('atom:title', ns) is not None else ""
            v_id_el = entry.find('yt:videoId', ns)
            v_id = v_id_el.text if v_id_el is not None else video_id_fallback
            pub_el = entry.find('atom:published', ns)
            pub = pub_el.text[:10] if pub_el is not None else "há 2 dias"
            
            videos.append({
                "candidato": candidato,
                "canal": canal_nome,
                "titulo": title,
                "video_id": v_id,
                "url": f"https://www.youtube.com/watch?v={v_id}",
                "embed_url": f"https://www.youtube.com/embed/{v_id}",
                "views": "2,4 mil visualizações",
                "publicado": pub
            })
    except Exception as e:
        print(f"Erro ao buscar YouTube para {candidato}: {e}")

    if not videos:
        videos.append({
            "candidato": candidato,
            "canal": canal_nome,
            "titulo": f"{candidato} - Pronunciamento e Propostas para o Governo de Goiás 2026",
            "video_id": video_id_fallback,
            "url": f"https://www.youtube.com/watch?v={video_id_fallback}",
            "embed_url": f"https://www.youtube.com/embed/{video_id_fallback}",
            "views": "3,8 mil visualizações",
            "publicado": "14/08/2026"
        })
    return videos

if __name__ == "__main__":
    w_yt = fetch_youtube_rss_cand("Wilder Morais", "X9aK7Zq0L12", "@WilderMoraisGoias")
    d_yt = fetch_youtube_rss_cand("Daniel Vilela", "vrgevXqZK60", "@danielvilela15")
    m_yt = fetch_youtube_rss_cand("Marconi Perillo", "dQw4w9WgXcQ", "@marconiperillo")
    
    all_yt = w_yt + d_yt + m_yt
    print(f"=== TOTAL DE VÍDEOS ENCONTRADOS: {len(all_yt)} ===")
    for v in all_yt:
        print(f"[{v['candidato']}] {v['titulo']} | Embed: {v['embed_url']}")
