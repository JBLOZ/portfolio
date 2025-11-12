#!/bin/bash

echo "🚀 Iniciando cloudflared tunnel..."

# Detener procesos anteriores si existen
pkill cloudflared 2>/dev/null
docker-compose down 2>/dev/null

# Iniciar cloudflared en segundo plano y capturar la salida
cloudflared tunnel --url http://localhost:5678 > tunnel.log 2>&1 &
CLOUDFLARED_PID=$!

echo "⏳ Esperando a que se genere la URL del tunnel..."

# Esperar hasta que aparezca la URL en el log (máximo 30 segundos)
SECONDS=0
TUNNEL_URL=""
while [ $SECONDS -lt 30 ]; do
    if [ -f tunnel.log ]; then
        # Buscar la URL en el log (formato: https://xxxxx.trycloudflare.com)
        TUNNEL_URL=$(grep -oP 'https://[a-zA-Z0-9\-]+\.trycloudflare\.com' tunnel.log | head -1)
        
        if [ ! -z "$TUNNEL_URL" ]; then
            echo "✅ Tunnel creado exitosamente!"
            echo "📡 URL del tunnel: $TUNNEL_URL"
            break
        fi
    fi
    sleep 1
done

if [ -z "$TUNNEL_URL" ]; then
    echo "❌ Error: No se pudo obtener la URL del tunnel"
    kill $CLOUDFLARED_PID 2>/dev/null
    exit 1
fi

# Guardar la URL en el archivo .env
echo "💾 Guardando configuración en .env..."
cat > .env << EOF
WEBHOOK_URL=${TUNNEL_URL}
N8N_HOST=${TUNNEL_URL#https://}
TUNNEL_URL=${TUNNEL_URL}
EOF

echo "📝 Contenido del .env:"
cat .env
echo ""

# Actualizar docker-compose.yml temporalmente o usar el .env
echo "🐳 Iniciando n8n con Docker Compose..."
docker-compose up -d

echo ""
echo "✨ ¡Todo listo!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 URL del tunnel:     $TUNNEL_URL"
echo "🔗 n8n UI:             $TUNNEL_URL"
echo "🤖 Webhook URL base:   $TUNNEL_URL/webhook/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Para el trigger de Telegram en n8n:"
echo "   - Usa esta URL en la configuración del webhook:"
echo "   - $TUNNEL_URL/webhook/[tu-webhook-id]/webhook"
echo ""
echo "🛑 Para detener todo: ./stop-n8n.sh"
echo "📊 Ver logs del tunnel: tail -f tunnel.log"
echo "📊 Ver logs de n8n: docker-compose logs -f"
