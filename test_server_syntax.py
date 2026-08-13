import sys
import py_compile

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=== VERIFICANDO SINTAXE DOS ARQUIVOS PYTHON ===")
files = [
    "server_web_unificado.py",
    "pdf_generator_service.py",
    "busca_drive_ia.py"
]

for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f"Sintaxe OK: {f}")
    except py_compile.PyCompileError as e:
        print(f"Erro de Sintaxe em {f}: {e}")
        sys.exit(1)

print("Todos os arquivos Python compilaram sem erros de sintaxe!")
