#!/bin/sh

echo "============================================================"
echo "🚀 INICIANDO CONTAINER - INTELIGÊNCIA ELEITORAL (COOLIFY)"
echo "============================================================"

# Cria o arquivo de log para o cron
touch /var/log/cron.log

# Configura a tabela CRON do Linux
# 1. Executa monitor_crises.py a cada 15 minutos
# 2. Executa coleta_metricas.py diariamente à meia-noite (00:00)
cat <<EOF > /etc/cron.d/eleitoral-cron
*/15 * * * * root cd /app && /usr/local/bin/python /app/monitor_crises.py >> /var/log/cron.log 2>&1
0 0 * * * root cd /app && /usr/local/bin/python /app/coleta_metricas.py >> /var/log/cron.log 2>&1
EOF

# Aplica as permissões estritas exigidas pelo cron
chmod 0644 /etc/cron.d/eleitoral-cron
crontab /etc/cron.d/eleitoral-cron

echo "[CRON] Serviço configurado com sucesso:"
echo " 🕒 monitor_crises.py  -> a cada 15 minutos (*/15 * * * *)"
echo " 🕒 coleta_metricas.py -> diariamente à 00:00 (0 0 * * *)"
echo "============================================================"

# Inicia o serviço do Cron no container
cron

# Transmite o arquivo de log para a saída padrão (stdout) para exibição no Coolify
exec tail -f /var/log/cron.log
