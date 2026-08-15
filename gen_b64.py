import base64
import os

img_path = r"c:\Users\User\Desktop\campanha wilder\static\wilder_3d.jpg"
if os.path.exists(img_path):
    with open(img_path, "rb") as f:
        b64_str = base64.b64encode(f.read()).decode('utf-8')
    data_uri = f"data:image/jpeg;base64,{b64_str}"
    print(f"=== BASE64 GERADO COM SUCESSO! Tamanho: {len(data_uri)} caracteres ===")
    with open("avatar_b64.txt", "w") as f_out:
        f_out.write(data_uri)
else:
    print("Erro: Imagem nao encontrada.")
