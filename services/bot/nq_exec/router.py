# NEBULA-QUANT v1 | nq_exec router — deterministic routing, no external calls

from __future__ import annotations

from typing import Any

from nq_exec.models import ExecutionOrder, ExecutionResult


def route_order(
    order: ExecutionOrder,
    adapter: Any,
) -> ExecutionResult:
    """
    Route order to adapter. Fail-closed: if adapter is None or health_check() is False,
    return rejected result. Otherwise dispatch to adapter.submit(order).
    """
    if adapter is None:
        o = ExecutionOrder(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            qty=order.qty,
            order_type=order.order_type,
            limit_price=order.limit_price,
            status="rejected",
            created_ts=order.created_ts,
            metadata={**order.metadata, "reason": "no_adapter"},
        )
        return ExecutionResult(
            order=o,
            fills=[],
            status="rejected",
            message="no adapter",
            metadata={"simulated": True},
        )
    if not getattr(adapter, "health_check", lambda: False)():
        o = ExecutionOrder(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            qty=order.qty,
            order_type=order.order_type,
            limit_price=order.limit_price,
            status="rejected",
            created_ts=order.created_ts,
            metadata={**order.metadata, "reason": "adapter_unavailable"},
        )
        return ExecutionResult(
            order=o,
            fills=[],
            status="rejected",
            message="adapter unavailable",
            metadata={"simulated": True},
        )
    return adapter.submit(order)
