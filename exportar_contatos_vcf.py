import os
import sys
import datetime
import urllib3
from dotenv import load_dotenv
from supabase import create_client, Client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

is_supabase_configurado = (
    SUPABASE_URL and SUPABASE_KEY and
    "your-supabase" not in SUPABASE_URL and
    "your-supabase" not in SUPABASE_KEY
)

supabase: Client = None
if is_supabase_configurado:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[AVISO] Não foi possível inicializar cliente Supabase: {e}")

def exportar_contatos_vcf():
    """
    Exporta todos os eleitores cadastrados na tabela 'eleitores_cadastrados' do Supabase
    para um arquivo de agenda telefônica padrão .vcf (vCard).
    Permite importar milhares de contatos no celular (Android / iPhone / Google Contacts) em 1 clique!
    """
    print("\n" + "=" * 60)
    print("📲 EXPORTANDO AGENDA DE CONTATOS (.VCF) PARA O CELULAR DA CAMPANHA")
    print("=" * 60)

    contatos = []
    if supabase:
        try:
            res = supabase.table("eleitores_cadastrados").select("nome, whatsapp, cidade, pauta_interesse").execute()
            if res and res.data:
                contatos = res.data
        except Exception as e:
            print(f"[ERRO] Falha ao consultar eleitores no Supabase: {e}")

    # Fallback de demonstração com contatos de exemplo se o banco estiver vazio
    if not contatos:
        print("[INFO] Gerando arquivo .vcf de exemplo para teste de importação...")
        contatos = [
            {"nome": "João Silva", "whatsapp": "64999998888", "cidade": "Rio Verde", "pauta_interesse": "Agro"},
            {"nome": "Maria Souza", "whatsapp": "61988887777", "cidade": "Luziânia", "pauta_interesse": "Entorno/Saúde"},
            {"nome": "Carlos Eduardo", "whatsapp": "62977776666", "cidade": "Goiânia", "pauta_interesse": "Educação"}
        ]

    vcf_filename = "contatos_eleitores_wilder.vcf"
    total_exportados = 0

    with open(vcf_filename, "w", encoding="utf-8") as f:
        for c in contatos:
            nome = c.get("nome", "Eleitor Wilder").strip()
            phone = str(c.get("whatsapp", "")).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            cidade = c.get("cidade", "Goiás").strip()
            pauta = c.get("pauta_interesse", "Geral").strip()

            if not phone:
                continue

            # Formata número para código internacional +55 se necessário
            if not phone.startswith("+"):
                if not phone.startswith("55"):
                    phone = "55" + phone
                phone = "+" + phone

            # Entrada em formato vCard 3.0 padronizado
            vcard_entry = f"""BEGIN:VCARD
VERSION:3.0
FN:[Wilder GO] {nome} - {cidade}
TEL;TYPE=CELL:{phone}
NOTE:Cidade: {cidade} | Pauta: {pauta} | Campanha Wilder Morais 2026
END:VCARD
"""
            f.write(vcard_entry)
            total_exportados += 1

    print(f"[OK] Arquivo '{vcf_filename}' gerado com sucesso!")
    print(f"[INFO] {total_exportados} contatos prontos para importação em 1 clique no celular/Google Contacts.")
    print("=" * 60)

if __name__ == "__main__":
    exportar_contatos_vcf()
