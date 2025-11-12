#!/bin/bash

echo "🛑 Deteniendo servicios..."

# Detener Docker Compose
echo "Deteniendo n8n..."
docker-compose down

# Detener cloudflared
echo "Deteniendo cloudflared tunnel..."
pkill cloudflared

# Limpiar logs
if [ -f tunnel.log ]; then
    rm tunnel.log
    echo "Logs del tunnel eliminados"
fi

echo "✅ Todo detenido correctamente"
