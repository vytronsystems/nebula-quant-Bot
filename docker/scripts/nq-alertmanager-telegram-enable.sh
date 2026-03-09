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

echo "== write telegram alertmanager config =="
cat > "$CFG" <<YAML
global:
  resolve_timeout: 5m

route:
  receiver: telegram
  group_wait: 10s
  group_interval: 1m
  repeat_interval: 3h

receivers:
- name: telegram
  telegram_configs:
  - bot_token: "${TOKEN}"
    chat_id: ${CHAT}
    parse_mode: "Markdown"
    send_resolved: true
YAML

echo "== restart alertmanager =="
docker compose up -d --no-deps --force-recreate alertmanager

echo "== status =="
docker compose ps alertmanager
