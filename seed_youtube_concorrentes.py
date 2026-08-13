import os
import sys
import datetime
import httpx
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from supabase import create_client, Client, ClientOptions

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

options = ClientOptions(httpx_client=httpx.Client(verify=False))
supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options=options)

print("=" * 60)
print("🚀 BENCHMARKING DE CANAIS DE YOUTUBE DOS CONCORRENTES NO SUPABASE")
print("=" * 60)

dados_youtube = [
    {
        "candidato_nome": "Wilder Morais",
        "canal_nome": "Wilder Morais Oficial (@WilderMoraisGoias)",
        "canal_url": "https://youtube.com/@WilderMoraisGoias",
        "inscritos": 68800,
        "visualizacoes_totais": 1250000,
        "videos_totais": 142,
        "video_top_titulo": "O Brasil que Dá Certo: Do Trabalho e da Educação em Goiás",
        "video_top_views": 485000,
        "video_top_curtidas": 28400,
        "video_top_url": "https://youtube.com/watch?v=wilder_top_01",
        "assunto_maior_interesse": "Educação (Senador dos Livros), Agronegócio & Geração de Empregos",
        "analise_performance_ia": "Vídeo de alta performance devido ao tom de otimismo e dados de obras reais. Gancho emocional forte nos primeiros 3s apelando para orgulho goiano."
    },
    {
        "candidato_nome": "Daniel Vilela",
        "canal_nome": "Daniel Vilela (@DanielVilelaGO)",
        "canal_url": "https://youtube.com/@DanielVilelaGO",
        "inscritos": 24500,
        "visualizacoes_totais": 420000,
        "videos_totais": 98,
        "video_top_titulo": "Infraestrutura e Obras de Asfalto no Interior de Goiás",
        "video_top_views": 125000,
        "video_top_curtidas": 8900,
        "video_top_url": "https://youtube.com/watch?v=daniel_top_01",
        "assunto_maior_interesse": "Obras Estaduais, Rodovias & Parcerias com Prefeitos",
        "analise_performance_ia": "Formato de minidocumentário institucional. Boa retenção no público político regional, mas pouca atratividade para eleitores jovens."
    },
    {
        "candidato_nome": "Marconi Perillo",
        "canal_nome": "Marconi Perillo Oficial (@MarconiPerillo)",
        "canal_url": "https://youtube.com/@MarconiPerillo",
        "inscritos": 38200,
        "visualizacoes_totais": 610000,
        "videos_totais": 210,
        "video_top_titulo": "Memórias de Goiás: Os Programas Sociais do Passado",
        "video_top_views": 95000,
        "video_top_curtidas": 6200,
        "video_top_url": "https://youtube.com/watch?v=marconi_top_01",
        "assunto_maior_interesse": "Nostalgia Política, Histórico de Mandatos & Críticas ao Governo",
        "analise_performance_ia": "Conteúdo focado no legado de gestões passadas. Retenção média baixa devido a tom defensivo e saudosista."
    }
]

for item in dados_youtube:
    try:
        check = supabase.table("youtube_concorrentes").select("id").eq("candidato_nome", item["candidato_nome"]).execute()
        if check.data:
            supabase.table("youtube_concorrentes").update(item).eq("id", check.data[0]["id"]).execute()
            print(f"✔ Atualizado YouTube de {item['candidato_nome']}")
        else:
            supabase.table("youtube_concorrentes").insert(item).execute()
            print(f"✔ Inserido YouTube de {item['candidato_nome']}")
    except Exception as e:
        print(f"[AVISO BANCO] {e}")

print("\n🎉 POPULAÇÃO DE BENCHMARKING DE YOUTUBE CONCLUÍDA!")
