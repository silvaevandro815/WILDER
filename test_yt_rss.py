import requests
import xml.etree.ElementTree as ET
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_channel_id(handle):
    url = f"https://www.youtube.com/{handle}"
    r = requests.get(url, headers=headers, verify=False, timeout=10)
    match = re.search(r'itemprop="channelId" content="([^"]+)"', r.text)
    if match:
        return match.group(1)
    match2 = re.search(r'browse_id":"([^"]+)"', r.text)
    if match2:
        return match2.group(1)
    return None

import re
cid_wilder = get_channel_id("@WilderMoraisGoias")
print("Channel ID Wilder Morais:", cid_wilder)

if cid_wilder:
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid_wilder}"
    r = requests.get(rss_url, verify=False, timeout=10)
    root = ET.fromstring(r.text)
    ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
    for entry in root.findall('atom:entry', ns)[:5]:
        title = entry.find('atom:title', ns).text
        link = entry.find('atom:link', ns).attrib['href']
        published = entry.find('atom:published', ns).text
        print(f"🎬 VÍDEO REAL YOUTUBE: {title} | DATA: {published} | URL: {link}")
