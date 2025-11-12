# N8N con Cloudflare Tunnel para Telegram Bot

## 📋 Requisitos Previos

1. **Docker y Docker Compose** instalados
2. **Cloudflared** instalado:
   ```bash
   # En Windows con Chocolatey:
   choco install cloudflared
   
   # O descarga desde: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
   ```

## 🚀 Uso

### Iniciar n8n con tunnel

```bash
chmod +x start-n8n.sh
./start-n8n.sh
```

Este script hará:
1. ✅ Crear un túnel de Cloudflare hacia localhost:5678
2. ✅ Capturar la URL pública generada (https://xxxxx.trycloudflare.com)
3. ✅ Configurar n8n con esa URL en el `.env`
4. ✅ Iniciar el contenedor Docker de n8n

### Detener todo

```bash
chmod +x stop-n8n.sh
./stop-n8n.sh
```

## 🤖 Configurar Telegram Bot en n8n

1. **Accede a n8n** usando la URL del tunnel que te muestra el script
2. **Crea tu workflow** con el nodo "Telegram Trigger"
3. **Configura el webhook**:
   - n8n te dará un webhook ID único
   - La URL completa será: `https://xxxxx.trycloudflare.com/webhook/[webhook-id]/webhook`
   - Copia esta URL y pégala en la configuración de tu bot de Telegram

### URLs importantes:

- **UI de n8n**: La URL del tunnel base
- **Webhook URL Test**: `https://xxxxx.trycloudflare.com/webhook-test/[webhook-id]/webhook`
- **Webhook URL Producción**: `https://xxxxx.trycloudflare.com/webhook/[webhook-id]/webhook`

## 📝 Notas

- ⚠️ **La URL del tunnel cambia cada vez que reinicias**: Tendrás que actualizar el webhook en Telegram cada vez
- 🔄 Para evitar cambios de URL, considera usar [Cloudflare Tunnel con dominio propio](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- 📊 Ver logs: `docker-compose logs -f` o `tail -f tunnel.log`

## 🔧 Troubleshooting

### El tunnel no se crea
```bash
# Verifica que cloudflared esté instalado
cloudflared --version

# Prueba manualmente
cloudflared tunnel --url http://localhost:5678
```

### n8n no arranca
```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart
```

### El webhook de Telegram no funciona
1. ✅ Verifica que la URL del tunnel esté activa (abre en navegador)
2. ✅ Asegúrate de usar la URL de **producción**, no la de test
3. ✅ El formato correcto es: `https://xxxxx.trycloudflare.com/webhook/[webhook-id]/webhook`
4. ✅ Actualiza el webhook en Telegram si la URL del tunnel cambió
