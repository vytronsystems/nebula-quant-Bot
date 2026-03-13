# Alert Routing — Dashboard, Telegram, Email

## Channels

- **Dashboard**: Alerts surface in the frontend (Operator: Audit & Evidence Center, Incidents; Executive: Incident summary widgets). Control plane or bot can write to a store (e.g. audit_run, incident table) consumed by the UI.
- **Telegram**: Configured via `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. Run `docker/scripts/nq-alertmanager-telegram-enable.sh` after compose up to generate Alertmanager config and restart. Prometheus alerts are routed to Alertmanager, which sends to Telegram when so configured.
- **Email**: Not yet implemented. To add: extend Alertmanager config with `email_configs` receiver and SMTP env vars; or add a separate notification service that consumes alert events and sends email. Prefer env-based SMTP (no secrets in repo).

## Routing policy

- Critical/risk alerts: Telegram + dashboard (and email when wired).
- Operational alerts: dashboard + optional Telegram.
- Audit/release evidence: dashboard and artifact store; optional Telegram on release gates.

## Security

- No hardcoded Telegram token or email credentials. Use `.env` and secret validation (`scripts/check_secrets.py`).
