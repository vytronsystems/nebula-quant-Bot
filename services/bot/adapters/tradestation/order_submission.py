# NEBULA-QUANT v1 | Phase 88 — TradeStation order submission
# Submit orders to TradeStation. Stub until live API wired.

from __future__ import annotations

from typing import Any


def submit_order(
    symbol: str,
    side: str,
    qty: int,
    order_type: str = "Market",
    limit_price: float | None = None,
    account_id: str | None = None,
) -> dict[str, Any]:
    """Submit order to TradeStation. Stub: returns simulated result."""
    return {
        "order_id": None,
        "status": "simulated",
        "message": "TradeStation order submission not wired",
    }
