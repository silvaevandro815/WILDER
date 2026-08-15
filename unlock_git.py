import os
import sys

lock_file = r"c:\Users\User\Desktop\campanha wilder\.git\index.lock"
if os.path.exists(lock_file):
    try:
        os.remove(lock_file)
        print("✅ Trava .git/index.lock removida com sucesso!")
    except Exception as e:
        print(f"Erro ao remover: {e}")
else:
    print("Nenhuma trava encontrada.")
