# NEBULA-QUANT v1 | nq_exec engine — skeleton only, no broker calls

from typing import Any

from nq_exec.config import DEFAULT_BROKER, DEFAULT_ORDER_TYPE
from nq_exec.models import ExecutionOrder, ExecutionFill, ExecutionResult
from nq_exec.router import route_order


class ExecutionEngine:
    """Skeleton execution engine. Accepts order placeholders; returns safe ExecutionResult. No broker calls."""

    def __init__(self, adapter: Any = None, **kwargs: Any) -> None:
        _ = kwargs
        self._adapter = adapter

    def submit_order(
        self,
        order: ExecutionOrder | None = None,
        **kwargs: Any,
    ) -> ExecutionResult:
        """Skeleton: return safe result. No broker call."""
        _ = kwargs
        if order is None:
            stub = ExecutionOrder(
                order_id="ord_0", symbol="QQQ", side="long", qty=0.0, order_type=DEFAULT_ORDER_TYPE,
                limit_price=0.0, status="skeleton", created_ts=0.0, metadata={"skeleton": True},
            )
            return self._build_result(stub, [])
        return route_order(order, self._adapter)

    def cancel_order(self, order_id: str = "") -> ExecutionResult:
        """Skeleton: return safe result. No broker call."""
        if not order_id:
            stub = ExecutionOrder(
                order_id="ord_0", symbol="", side="", qty=0.0, order_type="skeleton",
                limit_price=0.0, status="rejected", created_ts=0.0, metadata={"skeleton": True},
            )
            return self._build_result(stub, [])
        if self._adapter is not None:
            return self._adapter.cancel(order_id)
        stub = ExecutionOrder(
            order_id=order_id, symbol="", side="", qty=0.0, order_type="skeleton",
            limit_price=0.0, status="skeleton", created_ts=0.0, metadata={"skeleton": True},
        )
        return self._build_result(stub, [])

    def get_order_status(self, order_id: str = "") -> ExecutionResult:
        """Skeleton: return safe result. No broker call."""
        if not order_id:
            stub = ExecutionOrder(
                order_id="ord_0", symbol="", side="", qty=0.0, order_type="skeleton",
                limit_price=0.0, status="skeleton", created_ts=0.0, metadata={"skeleton": True},
            )
            return self._build_result(stub, [])
        if self._adapter is not None:
            return self._adapter.status(order_id)
        stub = ExecutionOrder(
            order_id=order_id, symbol="", side="", qty=0.0, order_type="skeleton",
            limit_price=0.0, status="skeleton", created_ts=0.0, metadata={"skeleton": True},
        )
        return self._build_result(stub, [])

    def _build_result(self, order: ExecutionOrder, fills: list[ExecutionFill]) -> ExecutionResult:
        """Build ExecutionResult from order and fills."""
        return ExecutionResult(
            order=order,
            fills=fills,
            status=order.status,
            message="skeleton",
            metadata={"skeleton": True, "broker": DEFAULT_BROKER},
        )
