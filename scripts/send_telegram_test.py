#!/usr/bin/env python3
"""
Send a test Telegram message "test nebula-quant".
Loads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from .env (raíz del repo o docker/.env).
Usage: from repo root: python3 scripts/send_telegram_test.py
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_dotenv(directory: str) -> None:
    env_path = os.path.join(directory, ".env")
    if not os.path.isfile(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip()
            if k and v and not os.environ.get(k):
                os.environ[k] = v


def main() -> int:
    load_dotenv(REPO_ROOT)
    if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"):
        load_dotenv(os.path.join(REPO_ROOT, "docker"))
    if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"):
        print(
            "ERROR: Configura TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en .env (raíz del repo o docker/.env).",
            file=sys.stderr,
        )
        print("Ejemplo: TELEGRAM_BOT_TOKEN=123:xxx  TELEGRAM_CHAT_ID=-1001234567890", file=sys.stderr)
        return 1
    # Use bot's telegram_notify so we share the same logic
    sys.path.insert(0, os.path.join(REPO_ROOT, "services", "bot"))
    from bot.telegram_notify import send_telegram_message

    result = send_telegram_message("test nebula-quant")
    if result.get("ok"):
        print("OK: mensaje de prueba enviado a Telegram.")
        return 0
    print("ERROR:", result.get("error", "unknown"), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
