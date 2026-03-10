# NEBULA-QUANT v1 | nq_exec router — skeleton, no external calls

from typing import Any

from nq_exec.models import ExecutionOrder, ExecutionResult


def route_order(
    order: ExecutionOrder | None = None,
    adapter: Any = None,
) -> ExecutionResult:
    """Skeleton: return safe placeholder routing result. No external systems."""
    if order is None:
        stub = ExecutionOrder(
            order_id="ord_0", symbol="QQQ", side="long", qty=0.0, order_type="skeleton",
            limit_price=0.0, status="rejected", created_ts=0.0, metadata={"skeleton": True},
        )
        return ExecutionResult(order=stub, fills=[], status="rejected", message="skeleton", metadata={"skeleton": True})
    if adapter is None:
        return ExecutionResult(order=order, fills=[], status="skeleton", message="skeleton", metadata={"skeleton": True})
    return adapter.submit(order)
