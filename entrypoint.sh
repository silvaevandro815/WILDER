#!/bin/sh

echo "============================================================"
echo "🚀 INICIANDO CONTAINER - INTELIGÊNCIA ELEITORAL (COOLIFY)"
echo "============================================================"

# Cria o arquivo de log para o cron
touch /var/log/cron.log

# Configura a tabela CRON do Linux com PATH explícito
cat <<EOF > /etc/cron.d/eleitoral-cron
PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin
SHELL=/bin/sh

*/15 * * * * root cd /app && /usr/local/bin/python /app/monitor_crises.py >> /var/log/cron.log 2>&1
0 0 * * * root cd /app && /usr/local/bin/python /app/coleta_metricas.py >> /var/log/cron.log 2>&1
0 6,18 * * * root cd /app && /usr/local/bin/python /app/coleta_trends.py >> /var/log/cron.log 2>&1
0 12 * * * root cd /app && /usr/local/bin/python /app/coleta_youtube.py >> /var/log/cron.log 2>&1
30 7 * * * root cd /app && /usr/local/bin/python /app/gerar_briefing_diario.py >> /var/log/cron.log 2>&1
EOF

# Aplica as permissões estritas exigidas pelo cron do Linux
chmod 0644 /etc/cron.d/eleitoral-cron
crontab /etc/cron.d/eleitoral-cron

echo "[CRON] Serviço configurado com sucesso e verificado:"
echo " 🕒 monitor_crises.py        -> a cada 15 minutos (*/15 * * * *)"
echo " 🕒 coleta_metricas.py      -> diariamente à 00:00 (0 0 * * *)"
echo " 🕒 coleta_trends.py        -> 2x ao dia às 06:00 e 18:00 (0 6,18 * * *)"
echo " 🕒 coleta_youtube.py       -> diariamente às 12:00 (0 12 * * *)"
echo " 🕒 gerar_briefing_diario.py -> diariamente às 07:30 (30 7 * * *)"
echo "============================================================"

# Inicia o serviço do Cron no container
cron

# Transmite o arquivo de log para a saída padrão (stdout) para exibição no Coolify
exec tail -f /var/log/cron.log
