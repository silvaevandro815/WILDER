import urllib.request
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

files = {
    "leaflet.css": "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css",
    "leaflet.js": "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js",
    "chart.js": "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"
}

headers = {'User-Agent': 'Mozilla/5.0'}

for filename, url in files.items():
    dest_path = os.path.join(static_dir, filename)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            print(f"Baixado com sucesso {filename}: {len(data)} bytes")
    except Exception as e:
        print(f"Erro ao baixar {filename}: {e}")
