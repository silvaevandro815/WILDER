#!/bin/sh

echo "============================================================"
echo "🚀 INICIANDO CONTAINER - INTELIGÊNCIA ELEITORAL (GUNICORN)"
echo "============================================================"

# Inicia o cron em segundo plano de forma totalmente resiliente
if command -v cron > /dev/null 2>&1; then
    cron || true
fi

echo "[GUNICORN] Servidor Unificado rodando na porta 5000 com 3 trabalhadores industriais..."
exec gunicorn --workers 3 --bind 0.0.0.0:5000 --timeout 120 --access-logfile - --error-logfile - server_web_unificado:app
