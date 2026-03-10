# NEBULA-QUANT v1 | nq_exec engine — validation, routing, fail-closed, no live broker

from __future__ import annotations

import time
from typing import Any

from nq_exec.config import (
    DEFAULT_BROKER,
    DEFAULT_EXECUTION_ENABLED,
    DEFAULT_ORDER_TYPE,
)
from nq_exec.models import ExecutionOrder, ExecutionFill, ExecutionResult
from nq_exec.router import route_order


def _validate_order(order: ExecutionOrder | None) -> tuple[bool, str]:
    """Validate order; return (valid, reason)."""
    if order is None:
        return False, "order is None"
    if not getattr(order, "order_id", ""):
        return False, "missing order_id"
    if not getattr(order, "symbol", ""):
        return False, "missing symbol"
    if not getattr(order, "side", ""):
        return False, "missing side"
    qty = getattr(order, "qty", 0)
    if qty is None or (hasattr(qty, "__float__") and float(qty) <= 0):
        return False, "qty must be positive"
    return True, "ok"


def _rejected_result(
    order: ExecutionOrder | None,
    message: str,
    broker: str = DEFAULT_BROKER,
) -> ExecutionResult:
    """Build a rejected result; no fills."""
    if order is None:
        stub = ExecutionOrder(
            order_id="ord_0", symbol="", side="", qty=0.0, order_type="",
            limit_price=0.0, status="rejected", created_ts=0.0, metadata={},
        )
        return ExecutionResult(order=stub, fills=[], status="rejected", message=message, metadata={"broker": broker})
    o = ExecutionOrder(
        order_id=order.order_id,
        symbol=order.symbol,
        side=order.side,
        qty=order.qty,
        order_type=getattr(order, "order_type", DEFAULT_ORDER_TYPE),
        limit_price=getattr(order, "limit_price", 0.0),
        status="rejected",
        created_ts=getattr(order, "created_ts", 0.0),
        metadata={**getattr(order, "metadata", {}), "reject_reason": message},
    )
    return ExecutionResult(order=o, fills=[], status="rejected", message=message, metadata={"broker": broker})


class ExecutionEngine:
    """
    Execution engine: validates orders, routes via adapter, returns deterministic results.
    Fail-closed: when execution_enabled is False or adapter unavailable, rejects and no fill.
    """

    def __init__(
        self,
        adapter: Any = None,
        execution_enabled: bool | None = None,
        **kwargs: Any,
    ) -> None:
        self._adapter = adapter
        self._execution_enabled = (
            execution_enabled if execution_enabled is not None else DEFAULT_EXECUTION_ENABLED
        )
        self._kwargs = kwargs

    def submit_order(
        self,
        order: ExecutionOrder | None = None,
        **kwargs: Any,
    ) -> ExecutionResult:
        """
        Validate order; if execution disabled or adapter unavailable, return rejected (no fill).
        Otherwise route to adapter and return result.
        """
        order = order or kwargs.get("order")
        valid, reason = _validate_order(order)
        if not valid:
            return _rejected_result(order, reason)

        if not self._execution_enabled:
            return _rejected_result(order, "execution disabled")

        if self._adapter is None:
            return _rejected_result(order, "no adapter")

        # Normalize: ensure created_ts set
        created_ts = getattr(order, "created_ts", None) or 0.0
        if created_ts <= 0:
            created_ts = time.time()
        order = ExecutionOrder(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            qty=order.qty,
            order_type=getattr(order, "order_type", DEFAULT_ORDER_TYPE),
            limit_price=getattr(order, "limit_price", 0.0),
            status="pending",
            created_ts=created_ts,
            metadata=getattr(order, "metadata", {}),
        )
        return route_order(order, self._adapter)

    def cancel_order(self, order_id: str = "") -> ExecutionResult:
        """Cancel by order_id. Fail-closed when disabled or no adapter."""
        if not order_id:
            return _rejected_result(None, "missing order_id")
        if not self._execution_enabled:
            stub = ExecutionOrder(
                order_id=order_id, symbol="", side="", qty=0.0, order_type="",
                limit_price=0.0, status="rejected", created_ts=0.0,
                metadata={"reject_reason": "execution disabled"},
            )
            return ExecutionResult(order=stub, fills=[], status="rejected", message="execution disabled", metadata={})
        if self._adapter is None:
            stub = ExecutionOrder(
                order_id=order_id, symbol="", side="", qty=0.0, order_type="",
                limit_price=0.0, status="rejected", created_ts=0.0,
                metadata={"reject_reason": "no adapter"},
            )
            return ExecutionResult(order=stub, fills=[], status="rejected", message="no adapter", metadata={})
        return self._adapter.cancel(order_id)

    def get_order_status(self, order_id: str = "") -> ExecutionResult:
        """Status lookup. Returns not_found when no adapter."""
        if not order_id:
            stub = ExecutionOrder(
                order_id="ord_0", symbol="", side="", qty=0.0, order_type="",
                limit_price=0.0, status="unknown", created_ts=0.0, metadata={},
            )
            return self._build_result(stub, [], "unknown", "missing order_id")
        if self._adapter is None:
            stub = ExecutionOrder(
                order_id=order_id, symbol="", side="", qty=0.0, order_type="",
                limit_price=0.0, status="not_found", created_ts=0.0, metadata={},
            )
            return self._build_result(stub, [], "not_found", "no adapter")
        return self._adapter.status(order_id)

    def _build_result(
        self,
        order: ExecutionOrder,
        fills: list[ExecutionFill],
        status: str,
        message: str,
    ) -> ExecutionResult:
        return ExecutionResult(
            order=order,
            fills=fills,
            status=status,
            message=message,
            metadata={"broker": DEFAULT_BROKER, "simulated": True},
        )
