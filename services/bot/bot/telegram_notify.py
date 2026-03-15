# NEBULA-QUANT v1 | Telegram notifications (test, trade closed, etc.). No secrets in code.

from __future__ import annotations

import os
import urllib.parse
import urllib.request
from typing import Any


def _config() -> tuple[str, str]:
    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    chat_id = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    return token, chat_id


def send_telegram_message(text: str) -> dict[str, Any]:
    """
    Send a plain text message to the configured Telegram chat.
    Returns {"ok": True} on success, {"ok": False, "error": "..."} on failure.
    """
    token, chat_id = _config()
    if not token or not chat_id:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set"}
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if 200 <= resp.getcode() < 300:
                return {"ok": True}
            return {"ok": False, "error": f"HTTP {resp.getcode()}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def send_trade_closed(symbol: str, qty: float, pnl_usd: float, pnl_pct: float) -> dict[str, Any]:
    """Notify Telegram: trade closed with pair, amount, PnL and % profit."""
    qty_str = f"{qty:.4f}".rstrip("0").rstrip(".")
    pnl_str = f"${pnl_usd:+.2f}"
    pct_str = f"{pnl_pct:+.2f}%"
    text = (
        f"Trade cerrado NEBULA-QUANT\n"
        f"Par: {symbol}\n"
        f"Monto: {qty_str}\n"
        f"PnL: {pnl_str}\n"
        f"% profit: {pct_str}"
    )
    return send_telegram_message(text)


def send_trade_opened(symbol: str, side: str, qty: float, price: float) -> dict[str, Any]:
    """Notify Telegram: trade opened (execution)."""
    qty_str = f"{qty:.4f}".rstrip("0").rstrip(".")
    text = (
        f"Trade abierto NEBULA-QUANT\n"
        f"Par: {symbol}\n"
        f"Lado: {side}\n"
        f"Monto: {qty_str}\n"
        f"Precio: {price}"
    )
    return send_telegram_message(text)
