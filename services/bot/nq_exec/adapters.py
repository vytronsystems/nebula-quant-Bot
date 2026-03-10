# NEBULA-QUANT v1 | nq_exec adapters — in-memory only, no external connectivity

from __future__ import annotations

import time
from typing import Any, Protocol

from nq_exec.fills import build_placeholder_fill
from nq_exec.models import ExecutionFill, ExecutionOrder, ExecutionResult


class ExecutionAdapterProtocol(Protocol):
    """Protocol for execution adapters. submit, cancel, status, health_check."""

    def submit(self, order: ExecutionOrder) -> ExecutionResult:
        ...

    def cancel(self, order_id: str) -> ExecutionResult:
        ...

    def status(self, order_id: str) -> ExecutionResult:
        ...

    def health_check(self) -> bool:
        ...


def _result(
    order: ExecutionOrder,
    fills: list[ExecutionFill],
    status: str,
    message: str,
    broker: str = "none",
) -> ExecutionResult:
    return ExecutionResult(
        order=order,
        fills=fills,
        status=status,
        message=message,
        metadata={"broker": broker, "simulated": True},
    )


class _BaseAdapter:
    """In-memory adapter: stores orders by order_id, simulates accept/cancel/status."""

    def __init__(self, broker_id: str = "none", available: bool = True) -> None:
        self._broker_id = broker_id
        self._available = available
        self._orders: dict[str, ExecutionOrder] = {}

    def health_check(self) -> bool:
        return self._available

    def submit(self, order: ExecutionOrder) -> ExecutionResult:
        if not self._available:
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
            return _result(o, [], "rejected", "adapter unavailable", self._broker_id)
        order = ExecutionOrder(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            qty=order.qty,
            order_type=order.order_type,
            limit_price=order.limit_price,
            status="accepted",
            created_ts=order.created_ts,
            metadata=order.metadata,
        )
        self._orders[order.order_id] = order
        fill = build_placeholder_fill(order=order, fill_price_mode="limit")
        return _result(order, [fill], "accepted", "simulated fill", self._broker_id)

    def cancel(self, order_id: str) -> ExecutionResult:
        if not self._available:
            stub = ExecutionOrder(
                order_id=order_id, symbol="", side="", qty=0.0, order_type="",
                limit_price=0.0, status="rejected", created_ts=0.0,
                metadata={"reason": "adapter_unavailable"},
            )
            return _result(stub, [], "rejected", "adapter unavailable", self._broker_id)
        if order_id in self._orders:
            o = self._orders[order_id]
            cancelled = ExecutionOrder(
                order_id=o.order_id, symbol=o.symbol, side=o.side, qty=o.qty,
                order_type=o.order_type, limit_price=o.limit_price, status="cancelled",
                created_ts=o.created_ts, metadata=o.metadata,
            )
            self._orders[order_id] = cancelled
            return _result(cancelled, [], "cancelled", "cancelled", self._broker_id)
        stub = ExecutionOrder(
            order_id=order_id, symbol="", side="", qty=0.0, order_type="",
            limit_price=0.0, status="not_found", created_ts=0.0, metadata={},
        )
        return _result(stub, [], "not_found", "order not found", self._broker_id)

    def status(self, order_id: str) -> ExecutionResult:
        if not self._available:
            stub = ExecutionOrder(
                order_id=order_id, symbol="", side="", qty=0.0, order_type="",
                limit_price=0.0, status="rejected", created_ts=0.0,
                metadata={"reason": "adapter_unavailable"},
            )
            return _result(stub, [], "rejected", "adapter unavailable", self._broker_id)
        if order_id in self._orders:
            o = self._orders[order_id]
            return _result(o, [], o.status, o.status, self._broker_id)
        stub = ExecutionOrder(
            order_id=order_id, symbol="", side="", qty=0.0, order_type="",
            limit_price=0.0, status="not_found", created_ts=0.0, metadata={},
        )
        return _result(stub, [], "not_found", "order not found", self._broker_id)


class TradeStationAdapter(_BaseAdapter):
    """In-memory TradeStation-style adapter. No external connectivity."""

    def __init__(self, available: bool = True) -> None:
        super().__init__(broker_id="tradestation", available=available)


class BinanceAdapter(_BaseAdapter):
    """In-memory Binance-style adapter. No external connectivity."""

    def __init__(self, available: bool = True) -> None:
        super().__init__(broker_id="binance", available=available)
