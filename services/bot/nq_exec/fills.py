# NEBULA-QUANT v1 | nq_exec fills — placeholder fills, deterministic, no persistence

from __future__ import annotations

import time
from typing import Any

from nq_exec.models import ExecutionFill, ExecutionOrder


def build_placeholder_fill(
    order: ExecutionOrder | None = None,
    order_id: str = "",
    symbol: str = "",
    qty: float = 0.0,
    price: float = 0.0,
    filled_ts: float | None = None,
    fill_price_mode: str = "limit",
    **kwargs: Any,
) -> ExecutionFill:
    """
    Build a deterministic placeholder fill. If order is provided, derive order_id, symbol, qty;
    price from order.limit_price when fill_price_mode == "limit", else use price arg.
    """
    _ = kwargs
    if order is not None:
        order_id = order_id or order.order_id
        symbol = symbol or order.symbol
        qty = qty if qty > 0 else order.qty
        if fill_price_mode == "limit" and order.limit_price > 0:
            price = price if price > 0 else order.limit_price
    ts = filled_ts if filled_ts is not None else time.time()
    fill_id = f"fill_{order_id}_{int(ts * 1000)}"
    return ExecutionFill(
        fill_id=fill_id,
        order_id=order_id or "ord_0",
        symbol=symbol or "QQQ",
        qty=qty,
        price=price,
        filled_ts=ts,
        metadata={"simulated": True},
    )


def build_fill_summary(fills: list[ExecutionFill]) -> dict[str, Any]:
    """Summary of fills. Safe on empty."""
    if not fills:
        return {"total_fills": 0, "total_qty": 0.0, "avg_price": 0.0}
    total_qty = sum(f.qty for f in fills)
    total_value = sum(f.qty * f.price for f in fills)
    return {
        "total_fills": len(fills),
        "total_qty": total_qty,
        "avg_price": total_value / total_qty if total_qty else 0.0,
    }
