#!/usr/bin/env python3
"""
Alertmanager webhook → Telegram. Recibe POST de Alertmanager, formatea y envía a Telegram.
Uso: TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... python3 scripts/telegram_webhook.py
     Opción: cargar desde .env en la raíz del repo.
Puerto por defecto: 9094. Variable PORT para cambiar.
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_dotenv(root: str) -> None:
    env_path = os.path.join(root, ".env")
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


def send_telegram(text: str) -> bool:
    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    chat_id = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat_id:
        return False
    import urllib.request
    import urllib.parse
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.getcode() < 300
    except Exception:
        return False


def format_alert_payload(data: dict) -> str:
    """Formatea el JSON de Alertmanager para un mensaje legible."""
    alerts = data.get("alerts") or []
    status = data.get("status", "")
    lines = [f"NEBULA-QUANT Alert ({status})"]
    for a in alerts:
        lab = a.get("labels") or {}
        ann = a.get("annotations") or {}
        name = lab.get("alertname", "alert")
        summary = ann.get("summary") or lab.get("alertname", "")
        desc = ann.get("description") or ""
        lines.append(f"• {name}: {summary}")
        if desc:
            lines.append(f"  {desc}")
    return "\n".join(lines)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if urlparse(self.path).path != "/webhook":
            self.send_response(404)
            self.end_headers()
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode("utf-8"))
            text = format_alert_payload(data)
            ok = send_telegram(text)
        except Exception as e:
            text = str(e)
            ok = False
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok" if ok else b"send_failed")

    def log_message(self, format, *args):
        pass  # reduce noise


def main():
    load_dotenv(REPO_ROOT)
    port = int(os.getenv("PORT", "9094"))
    if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"):
        print("ERROR: TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID requeridos.", file=sys.stderr)
        sys.exit(1)
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Telegram webhook listening on 0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
