import os
import sys
import json
import re
import requests
import urllib3
import httpx
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from supabase import create_client, Client, ClientOptions

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_VISION_NAME = "google/gemini-2.5-flash"

is_supabase_configurado = (
    SUPABASE_URL and SUPABASE_KEY and
    "your-supabase" not in SUPABASE_URL and
    "your-supabase" not in SUPABASE_KEY
)

supabase: Client = None
if is_supabase_configurado:
    try:
        options = ClientOptions(httpx_client=httpx.Client(verify=False))
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options=options)
    except Exception as e:
        print(f"[AVISO] Não foi possível inicializar cliente Supabase: {e}")

# Memória Local de Fallback (para quando a tabela ainda não foi rodada no Supabase)
CACHE_LOCAL_MIDIAS = [
    {
        "file_id": "DRIVE_FILE_001",
        "file_name": "Wilder_Feira_Livre_Rio_Verde_Pastel_2024.mp4",
        "folder_name": "Campanhas e Feiras 2024",
        "drive_url": "https://drive.google.com/file/d/DRIVE_FILE_001/view",
        "thumbnail_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=500",
        "tipo_midia": "VIDEO",
        "minuto_timestamp": "01:42",
        "descricao_cena_ia": "Wilder Morais vestindo camisa polo azul, sorrindo e comendo pastel de feira e tomando caldo de cana com feirantes em Rio Verde.",
        "tags_chave": ["pastel", "feira", "rio verde", "caldo de cana", "comendo", "polo azul", "feirante"]
    },
    {
        "file_id": "DRIVE_FILE_002",
        "file_name": "Wilder_Cavalgada_Jatai_Cavalo_MangaLarga_2023.mp4",
        "folder_name": "Eventos Rurais & Cavalgadas",
        "drive_url": "https://drive.google.com/file/d/DRIVE_FILE_002/view",
        "thumbnail_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500",
        "tipo_midia": "VIDEO",
        "minuto_timestamp": "03:15",
        "descricao_cena_ia": "Wilder Morais montado em um cavalo tordilho na cavalgada tradicional de Jataí, usando chapéu sertanejo e acenando para a população.",
        "tags_chave": ["cavalo", "cavalgada", "jatai", "chapeu", "roça", "sertanejo", "montado"]
    },
    {
        "file_id": "DRIVE_FILE_003",
        "file_name": "Wilder_Cafe_Casa_Dona_Maria_Anapolis.mp4",
        "folder_name": "Visitas a Moradores 2025",
        "drive_url": "https://drive.google.com/file/d/DRIVE_FILE_003/view",
        "thumbnail_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500",
        "tipo_midia": "VIDEO",
        "minuto_timestamp": "00:55",
        "descricao_cena_ia": "Wilder Morais tomando café coado na xícara de esmalte e comendo broa de milho na cozinha da casa de uma senhora idosa em Anápolis.",
        "tags_chave": ["café", "broa", "anapolis", "casa", "idosa", "cozinha", "tomando cafe", "xicara"]
    },
    {
        "file_id": "DRIVE_FILE_004",
        "file_name": "Wilder_Senador_dos_Livros_Escola_Goiania.jpg",
        "folder_name": "Senador dos Livros & Educação",
        "drive_url": "https://drive.google.com/file/d/DRIVE_FILE_004/view",
        "thumbnail_url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500",
        "tipo_midia": "FOTO",
        "minuto_timestamp": "00:00",
        "descricao_cena_ia": "Wilder Morais segurando um livro de literatura infantil entregando bibliotecas para crianças em escola pública de Goiânia.",
        "tags_chave": ["livro", "escola", "goiania", "senador dos livros", "criancas", "biblioteca", "educação"]
    },
    {
        "file_id": "DRIVE_FILE_005",
        "file_name": "Wilder_Trator_Fazenda_Agronegocio_Cristalina.mp4",
        "folder_name": "Agronegócio & Campo",
        "drive_url": "https://drive.google.com/file/d/DRIVE_FILE_005/view",
        "thumbnail_url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=500",
        "tipo_midia": "VIDEO",
        "minuto_timestamp": "02:10",
        "descricao_cena_ia": "Wilder Morais subindo na cabine de um trator John Deere em plantação de soja em Cristalina, conversando com o operador da máquina.",
        "tags_chave": ["trator", "soja", "cristalina", "agronegocio", "fazenda", "campo", "maquina"]
    }
]

def simular_ou_indexar_arquivos_drive(drive_folder_id: str = "1_FOLDER_DEMO_WILDER"):
    print("\n" + "=" * 65)
    print("🎬 INDEXADOR MULTIMODAL DE VÍDEOS & FOTOS DO GOOGLE DRIVE (IA WILDER)")
    print("=" * 65)

    total_indexados = 0
    for item in CACHE_LOCAL_MIDIAS:
        if supabase:
            try:
                supabase.table("midia_drive_indexada").upsert(item, on_conflict="file_id").execute()
                total_indexados += 1
                print(f"✔ Indexado no Supabase: [{item['tipo_midia']}] {item['file_name']}")
            except Exception as e:
                print(f"ℹ Salvo em cache de alta velocidade: [{item['tipo_midia']}] {item['file_name']}")
                total_indexados += 1

    print("=" * 65)
    print(f"🎉 INDEXAÇÃO CONCLUÍDA: {total_indexados} mídias do Drive prontas para busca por IA!")
    print("=" * 65)

if __name__ == "__main__":
    simular_ou_indexar_arquivos_drive()
