route:
  receiver: telegram
  group_wait: 10s
  group_interval: 1m
  repeat_interval: 3h

receivers:
- name: telegram
  telegram_configs:
  - bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: ${TELEGRAM_CHAT_ID}
    parse_mode: "Markdown"
    send_resolved: true
