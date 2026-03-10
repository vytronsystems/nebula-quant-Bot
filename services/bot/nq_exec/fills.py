# NEBULA-QUANT v1 | nq_exec fills — skeleton, safe defaults

from typing import Any

from nq_exec.models import ExecutionFill


def build_placeholder_fill(
    order_id: str = "",
    symbol: str = "",
    qty: float = 0.0,
    price: float = 0.0,
    filled_ts: float = 0.0,
    **kwargs: Any,
) -> ExecutionFill:
    """Skeleton: build a placeholder fill. No persistence."""
    _ = kwargs
    return ExecutionFill(
        fill_id=f"fill_{int(filled_ts)}",
        order_id=order_id or "ord_0",
        symbol=symbol or "QQQ",
        qty=qty,
        price=price,
        filled_ts=filled_ts,
        metadata={"skeleton": True},
    )


def build_fill_summary(fills: list[ExecutionFill]) -> dict[str, Any]:
    """Skeleton: summary of fills. Safe on empty."""
    if not fills:
        return {"total_fills": 0, "total_qty": 0.0, "avg_price": 0.0}
    total_qty = sum(f.qty for f in fills)
    total_value = sum(f.qty * f.price for f in fills)
    return {
        "total_fills": len(fills),
        "total_qty": total_qty,
        "avg_price": total_value / total_qty if total_qty else 0.0,
    }
