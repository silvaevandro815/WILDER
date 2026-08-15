import os
import shutil

src = r"C:\Users\User\.gemini\antigravity\brain\fd42555c-ef3f-45fa-a159-871486c39791\.user_uploaded\media_1786753389317.jpg"
dest_dir = r"c:\Users\User\Desktop\campanha wilder\static"
dest = os.path.join(dest_dir, "wilder_3d.jpg")

os.makedirs(dest_dir, exist_ok=True)
if os.path.exists(src):
    shutil.copy(src, dest)
    print(f"=== FOTO 3D DO WILDER COPIADA COM SUCESSO PARA: {dest} ===")
else:
    print(f"Erro: Arquivo fonte nao encontrado em {src}")
