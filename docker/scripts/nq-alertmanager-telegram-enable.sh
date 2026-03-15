#!/usr/bin/env bash
set -euo pipefail

CFG="./alertmanager/alertmanager.yml"
BK="./alertmanager/alertmanager.yml.bak.telegram.$(date +%Y%m%d-%H%M%S)"

TOKEN="${TELEGRAM_BOT_TOKEN:-}"
CHAT="${TELEGRAM_CHAT_ID:-}"

# Guard: si falta algo, no tocamos nada.
if [[ -z "$TOKEN" || -z "$CHAT" ]]; then
  echo "SKIP: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID vacío. No habilito Telegram."
  exit 0
fi

# Guard: chat id debe ser numérico (puede ser negativo)
if ! [[ "$CHAT" =~ ^-?[0-9]+$ ]]; then
  echo "ERROR: TELEGRAM_CHAT_ID debe ser numérico (ej: -1001234567890). Valor='$CHAT'"
  exit 1
fi

echo "== backup =="
cp -v "$CFG" "$BK"

echo "== write alertmanager config (webhook -> Telegram) =="
# Official Alertmanager has no telegram_configs; we use webhook -> telegram_webhook service
cat > "$CFG" <<YAML
global:
  resolve_timeout: 5m

route:
  receiver: telegram_webhook
  group_wait: 10s
  group_interval: 1m
  repeat_interval: 3h

receivers:
- name: telegram_webhook
  webhook_configs:
  - url: http://telegram-webhook:9094/webhook
    send_resolved: true
YAML

echo "== (re)start telegram-webhook and alertmanager =="
docker compose up -d --no-deps telegram-webhook 2>/dev/null || true
docker compose up -d --no-deps --force-recreate alertmanager

echo "== status =="
docker compose ps alertmanager telegram-webhook 2>/dev/null || docker compose ps alertmanager
