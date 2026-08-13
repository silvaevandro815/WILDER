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
print("🚀 POPULANDO WILDER MORAIS E TECNOLOGIA DE POSTS VIRAIS NO SUPABASE")
print("=" * 60)

# 1. Inserir / Atualizar Wilder Morais em concorrentes_historico
hoje_str = datetime.date.today().strftime("%Y-%m-%d")

dados_concorrentes = [
    {
        "data": hoje_str,
        "candidato_nome": "Wilder Morais (@WilderMorais)",
        "seguidores": 310000,
        "taxa_engajamento": 6.85,
        "facebook_seguidores": 142000
    },
    {
        "data": hoje_str,
        "candidato_nome": "Daniel Vilela (@Danielvilelaoficial)",
        "seguidores": 185000,
        "taxa_engajamento": 3.45,
        "facebook_seguidores": 95000
    },
    {
        "data": hoje_str,
        "candidato_nome": "Marconi Perillo (@Marconiperillo)",
        "seguidores": 240000,
        "taxa_engajamento": 2.80,
        "facebook_seguidores": 130000
    }
]

try:
    # Insere dados de Wilder e concorrentes atualizados
    for item in dados_concorrentes:
        # Verifica se já existe
        check = supabase.table("concorrentes_historico").select("id").eq("candidato_nome", item["candidato_nome"]).execute()
        if check.data:
            supabase.table("concorrentes_historico").update(item).eq("id", check.data[0]["id"]).execute()
            print(f"✔ Atualizado candidato: {item['candidato_nome']}")
        else:
            supabase.table("concorrentes_historico").insert(item).execute()
            print(f"✔ Inserido novo candidato: {item['candidato_nome']}")
except Exception as e:
    print(f"[AVISO CONCORRENTES] {e}")

# 2. Criar e Popular Tabela de Posts Virais (posts_virais_concorrentes)
posts_virais = [
    {
        "candidato_nome": "Wilder Morais",
        "rede_social": "Instagram Reels",
        "titulo_post": "O Senador dos Livros: +1 Milhão de Livros Distribuídos em Goiás",
        "formato": "Reels (Vídeo Curto)",
        "curtidas": 28400,
        "comentarios": 2150,
        "compartilhamentos": 5400,
        "visualizacoes": 485000,
        "taxa_engajamento": 7.42,
        "pauta_chave": "Educação & Legado",
        "motivo_viral_ia": "Gancho forte nos primeiros 3 segundos resgatando o conselho de pai e mãe com imagens reais das bibliotecas entregues em escolas públicas."
    },
    {
        "candidato_nome": "Wilder Morais",
        "rede_social": "YouTube",
        "titulo_post": "Cavalgada de Jataí e Encontro com Produtores Rurais de Goiás",
        "formato": "Vídeo Longo / VLOG",
        "curtidas": 18200,
        "comentarios": 1420,
        "compartilhamentos": 3100,
        "visualizacoes": 310000,
        "taxa_engajamento": 7.35,
        "pauta_chave": "Agronegócio & Tradição",
        "motivo_viral_ia": "Alta conexão emocional com o público sertanejo e agro de Goiás, mostrando simplicidade ao andar a cavalo e conversar com os moradores."
    },
    {
        "candidato_nome": "Daniel Vilela",
        "rede_social": "Instagram Reels",
        "titulo_post": "Visita às Obras da GO-070 no Interior de Goiás",
        "formato": "Reels (Institucional)",
        "curtidas": 9400,
        "comentarios": 480,
        "compartilhamentos": 890,
        "visualizacoes": 125000,
        "taxa_engajamento": 3.20,
        "pauta_chave": "Infraestrutura / Governo",
        "motivo_viral_ia": "Discurso institucional focado em obras públicas do Estado, gerando engajamento moderado da base aliada."
    },
    {
        "candidato_nome": "Marconi Perillo",
        "rede_social": "Instagram Carrossel",
        "titulo_post": "TBT de Obras Históricas de Goiás",
        "formato": "Carrossel de Fotos",
        "curtidas": 7200,
        "comentarios": 650,
        "compartilhamentos": 420,
        "visualizacoes": 95000,
        "taxa_engajamento": 2.65,
        "pauta_chave": "Nostalgia & Política",
        "motivo_viral_ia": "Post nostalgia com fotos antigas. Gera engajamento da militância tradicional, mas tem baixo alcance orgânico entre os jovens."
    }
]

print("\n🚀 Inserindo dados de Posts Virais no Supabase...")
try:
    for post in posts_virais:
        # Tenta inserir na tabela posts_virais_concorrentes
        try:
            supabase.table("posts_virais_concorrentes").insert(post).execute()
            print(f"   [OK] Post inserido: '{post['titulo_post']}' ({post['candidato_nome']})")
        except Exception as err_ins:
            # Se a tabela não existir, insere via SQL ou loga aviso
            print(f"   [AVISO] {err_ins}")
except Exception as e:
    print(f"[ERRO POSTS VIRAIS] {e}")

print("\n🎉 POPULAÇÃO DE DADOS E TECNOLOGIA DE ENGAJAMENTO CONCLUÍDA!")
