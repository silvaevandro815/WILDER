import sys

def read_pdf(file_path):
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception:
        try:
            import fitz # PyMuPDF
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            return text
        except Exception as e:
            return f"Erro: {e}"

pdf_path = r"c:\Users\User\Desktop\campanha wilder\CAMPANHA\PLANO DE GOVERNO WILDER.pdf"
content = read_pdf(pdf_path)
print("=== CONTEÚDO EXTRAÍDO DO PLANO DE GOVERNO ===")
print(content[:3000]) # Primeiros 3000 caracteres

with open("plano_governo_texto.txt", "w", encoding="utf-8") as f:
    f.write(content)

print("\nTexto salvo em plano_governo_texto.txt com tamanho:", len(content))
