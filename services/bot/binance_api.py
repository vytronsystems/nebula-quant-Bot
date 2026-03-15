"""
Binance Testnet API — FastAPI app for UI/control-plane.
Read-only; testnet only; fail-closed. Run: PYTHONPATH=. uvicorn binance_api:app --host 0.0.0.0 --port 8082
"""
from __future__ import annotations

import os
from typing import Any

# Ensure adapters are importable when run from services/bot
if __name__ != "__main__":
    pass
_sys_path = os.environ.get("PYTHONPATH", "")
if _sys_path and "services/bot" not in _sys_path:
    import sys
    _bot = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    if _bot not in sys.path:
        sys.path.insert(0, _bot)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NEBULA-QUANT Binance Testnet API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

SYMBOL = os.environ.get("BINANCE_SYMBOL", "BTCUSDT")


def _safe_client():
    from adapters.binance.testnet_client import BinanceTestnetClient, BinanceTestnetClientError
    from adapters.binance.testnet_config import get_binance_testnet_config
    cfg = get_binance_testnet_config()
    if not cfg.testnet or not cfg.is_configured:
        return None, "NOT_CONFIGURED", "Testnet not enabled or credentials missing"
    try:
        return BinanceTestnetClient(cfg), None, None
    except BinanceTestnetClientError as e:
        return None, e.status, str(e)


@app.get("/health")
def health() -> dict[str, Any]:
    from adapters.binance.testnet_client import get_venue_status_safe
    status, message = get_venue_status_safe()
    return {"status": status, "message": message, "venue": "binance", "testnet": True}


@app.get("/account")
def account() -> dict[str, Any]:
    client, err_status, err_msg = _safe_client()
    if client is None:
        return {"status": err_status, "message": err_msg, "account": None}
    try:
        raw = client.get_account()
        from adapters.binance.account import BinanceAccountAdapter
        adapter = BinanceAccountAdapter()
        state = adapter.normalize_account_state(raw)
        usdt = next((b for b in state.balances if b.asset == "USDT"), None)
        return {
            "status": "CONNECTED",
            "account": {
                "wallet_balance": usdt.balance if usdt else 0,
                "available_balance": usdt.available if usdt else 0,
                "positions_count": len(state.positions),
                "raw_assets_count": len(state.balances),
            },
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e), "account": None}


@app.get("/market")
def market() -> dict[str, Any]:
    client, err_status, err_msg = _safe_client()
    if client is None:
        return {"status": err_status, "message": err_msg, "price": None}
    try:
        ticker = client.get_ticker_price(SYMBOL)
        price = float(ticker.get("price", 0) or 0)
        return {"status": "CONNECTED", "symbol": SYMBOL, "price": price, "testnet": True}
    except Exception as e:
        return {"status": "ERROR", "message": str(e), "price": None}


@app.get("/orderbook")
def orderbook(limit: int = 10) -> dict[str, Any]:
    client, err_status, err_msg = _safe_client()
    if client is None:
        return {"status": err_status, "message": err_msg, "bids": [], "asks": []}
    try:
        raw = client.get_order_book(SYMBOL, limit=limit)
        bids = [(float(p), float(q)) for p, q in raw.get("bids", [])[:limit]]
        asks = [(float(p), float(q)) for p, q in raw.get("asks", [])[:limit]]
        return {"status": "CONNECTED", "symbol": SYMBOL, "bids": bids, "asks": asks}
    except Exception as e:
        return {"status": "ERROR", "message": str(e), "bids": [], "asks": []}


@app.get("/trades")
def trades(limit: int = 10) -> dict[str, Any]:
    client, err_status, err_msg = _safe_client()
    if client is None:
        return {"status": err_status, "message": err_msg, "trades": []}
    try:
        trades_list = client.get_recent_trades(SYMBOL, limit=limit)
        return {"status": "CONNECTED", "symbol": SYMBOL, "trades": trades_list[:limit]}
    except Exception as e:
        return {"status": "ERROR", "message": str(e), "trades": []}


@app.get("/orders")
def orders() -> dict[str, Any]:
    client, err_status, err_msg = _safe_client()
    if client is None:
        return {"status": err_status, "message": err_msg, "orders": []}
    try:
        orders_list = client.get_open_orders(SYMBOL)
        return {"status": "CONNECTED", "symbol": SYMBOL, "orders": orders_list}
    except Exception as e:
        return {"status": "ERROR", "message": str(e), "orders": []}


@app.get("/positions")
def positions() -> dict[str, Any]:
    client, err_status, err_msg = _safe_client()
    if client is None:
        return {"status": err_status, "message": err_msg, "positions": []}
    try:
        pos_list = client.get_position_risk(SYMBOL)
        return {"status": "CONNECTED", "symbol": SYMBOL, "positions": pos_list}
    except Exception as e:
        return {"status": "ERROR", "message": str(e), "positions": []}


@app.get("/venue-overview")
def venue_overview() -> dict[str, Any]:
    from adapters.binance.testnet_client import get_venue_status_safe
    status, message = get_venue_status_safe()
    return {
        "venue": "binance",
        "testnet": True,
        "status": status,
        "message": message,
        "live_forbidden": True,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
