# Imagem base Python oficial leve (Linux Debian)
FROM python:3.12-slim

# Garante que a saída do Python seja exibida em tempo real no terminal do Coolify
ENV PYTHONUNBUFFERED=1

# Instala o utilitário Cron e ferramentas do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte do projeto
COPY . .

# Expõe a porta 5000 para o Traefik / Coolify
EXPOSE 5000

# Ajusta quebras de linha Unix e permissões de execução no entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Executa o script de inicialização do container
ENTRYPOINT ["/app/entrypoint.sh"]
