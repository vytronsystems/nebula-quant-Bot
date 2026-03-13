# Security and Secrets Standard

## Required corrections
- Move all secrets out of committed files.
- Replace hardcoded Telegram bot config with env-based configuration.
- Replace hardcoded DB credentials with env-driven config for non-local defaults.
- Add `.env.example` files where needed.
- Add secret validation checks to CI/local verification.

## Access policy
- Single-user system initially.
- MFA required for frontend sensitive actions.
- IP allowlist for live-sensitive actions.
- Reauthentication required for:
  - enable live
  - disable kill switch
  - increase venue capital ceiling
  - modify global risk limits
