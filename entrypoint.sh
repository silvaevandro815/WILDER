#!/bin/sh

echo "============================================================"
echo "🚀 INICIANDO CONTAINER - INTELIGÊNCIA ELEITORAL (GUNICORN)"
echo "============================================================"

# Cria o arquivo de log para o cron
touch /var/log/cron.log

# Configura a tabela CRON do Linux
cat <<EOF > /etc/cron.d/eleitoral-cron
PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin
SHELL=/bin/sh

*/15 * * * * root cd /app && /usr/local/bin/python /app/monitor_crises.py >> /var/log/cron.log 2>&1
0 0 * * * root cd /app && /usr/local/bin/python /app/coleta_metricas.py >> /var/log/cron.log 2>&1
0 6,18 * * * root cd /app && /usr/local/bin/python /app/coleta_trends.py >> /var/log/cron.log 2>&1
0 12 * * * root cd /app && /usr/local/bin/python /app/coleta_youtube.py >> /var/log/cron.log 2>&1
0 8,16 * * * root cd /app && /usr/local/bin/python /app/monitor_reclamacoes_goias.py >> /var/log/cron.log 2>&1
30 7 * * * root cd /app && /usr/local/bin/python /app/gerar_briefing_diario.py >> /var/log/cron.log 2>&1
0 7 * * * root cd /app && /usr/local/bin/python /app/gerar_relatorio_pdf_360.py >> /var/log/cron.log 2>&1
EOF

chmod 0644 /etc/cron.d/eleitoral-cron
crontab /etc/cron.d/eleitoral-cron

# Inicia o serviço de tarefas em segundo plano (cron)
cron

echo "[GUNICORN] Servidor Unificado rodando na porta 5000 com 3 trabalhadores industriais..."
exec gunicorn --workers 3 --bind 0.0.0.0:5000 --timeout 120 --access-logfile - --error-logfile - server_web_unificado:app
