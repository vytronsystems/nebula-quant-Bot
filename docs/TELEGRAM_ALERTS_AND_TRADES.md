# Telegram: prueba, alertas (bot caído) y notificaciones de trades

## Credenciales

Puedes usar **`.env`** en la raíz del repo o en **`docker/.env`**. El script de prueba y Docker Compose buscan en ambos. Añade:

```bash
TELEGRAM_BOT_TOKEN=123456:ABC-def...
TELEGRAM_CHAT_ID=-1001234567890
```

- **Token**: lo obtienes de [@BotFather](https://t.me/BotFather).
- **Chat ID**: número del chat o grupo donde quieres recibir los mensajes (p. ej. negativo para grupos).

El archivo `.env` no se sube a Git.

---

## 1. Enviar mensaje de prueba

Desde la raíz del repo:

```bash
python3 scripts/send_telegram_test.py
```

Si todo está bien, verás: `OK: mensaje de prueba enviado a Telegram` y en Telegram el mensaje **"test nebula-quant"**. (El script carga las variables desde la raíz del repo o desde `docker/.env`).

---

## 2. Alertas cuando el bot está caído

Las alertas de Prometheus (p. ej. "Bot Down") se envían a Alertmanager y este reenvía al webhook que manda los mensajes a Telegram.

1. **Subir el servicio webhook** (usa las variables de Telegram del `.env`):
   ```bash
   cd docker
   docker compose --env-file ../.env up -d telegram-webhook
   ```

2. **Configurar Alertmanager** para que use ese webhook:
   ```bash
   cd docker
   source ../.env   # o export TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=...
   ./scripts/nq-alertmanager-telegram-enable.sh
   ```

Con esto, cuando el bot lleve más de 1 minuto sin responder, Prometheus dispara la alerta y recibirás un mensaje en Telegram.

---

## 3. Notificaciones de trades (abierto y cerrado)

El **bot** ya está configurado para enviar a Telegram:

- **Trade abierto**: par, lado, monto, precio.
- **Trade cerrado**: par, monto, PnL (USD), % profit.

El contenedor del bot recibe `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` desde el `docker-compose` (que toma el `.env` de la raíz). No hace falta configurar nada más.

Cada vez que el paper runner cierra un trade, se envían automáticamente los dos mensajes (apertura y cierre) al chat configurado.

---

## Resumen de flujo

| Qué                | Cómo |
|--------------------|------|
| Mensaje de prueba  | `python3 scripts/send_telegram_test.py` (desde raíz, con `.env`) |
| Bot caído          | Alertmanager → webhook → Telegram (servicio `telegram-webhook` + script `nq-alertmanager-telegram-enable.sh`) |
| Trades (abierto/cerrado) | Bot (paper runner) → `bot.telegram_notify` → Telegram (mismo token/chat del `.env`) |
