# NEBULA-QUANT v1 | Phase 79 — Binance market data WebSocket stream
# Trades, orderbook depth, mark price. Persist for analytics (callback or Redis).

from __future__ import annotations

import json
import os
import threading
from typing import Any, Callable

# Optional: use websocket-client if available
try:
    import websocket
    _HAS_WS = True
except ImportError:
    _HAS_WS = False


def _ws_base_url() -> str:
    return os.getenv("BINANCE_FUTURES_TESTNET_WS_URL", "").strip() or "wss://stream.binancefuture.com"


def _stream_url(symbol: str, streams: list[str]) -> str:
    # Combined stream: e.g. btcusdt@trade, btcusdt@depth, btcusdt@markPrice
    parts = [f"{symbol.lower()}@{s}" for s in streams]
    return f"{_ws_base_url()}/stream?streams={'/'.join(parts)}"


def run_market_data_stream(
    symbol: str = "btcusdt",
    on_message: Callable[[str, dict[str, Any]], None] | None = None,
    streams: list[str] | None = None,
) -> None:
    """
    Run WebSocket stream for trades, depth, mark price (testnet).
    on_message(stream_name, payload) for persistence/analytics.
    Runs in background thread; returns when connection ends.
    """
    if not _HAS_WS:
        return
    streams = streams or ["trade", "depth@100ms", "markPrice"]
    url = _stream_url(symbol, streams)

    def _on_msg(ws: Any, raw: str) -> None:
        try:
            data = json.loads(raw)
            stream = data.get("stream", "")
            payload = data.get("data", data)
            if on_message:
                on_message(stream, payload)
        except Exception:
            pass

    def _on_error(ws: Any, err: Any) -> None:
        pass

    def _run() -> None:
        ws = websocket.WebSocketApp(
            url,
            on_message=_on_msg,
            on_error=_on_error,
        )
        ws.run_forever()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
