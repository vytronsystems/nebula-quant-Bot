# NEBULA-QUANT v1 | nq_exec adapters — skeleton stubs, no external connectivity

from typing import Protocol

from nq_exec.models import ExecutionOrder, ExecutionResult


class ExecutionAdapterProtocol(Protocol):
    """Protocol for execution adapters. No broker calls in skeleton."""

    def submit(self, order: ExecutionOrder) -> ExecutionResult:
        ...

    def cancel(self, order_id: str) -> ExecutionResult:
        ...

    def status(self, order_id: str) -> ExecutionResult:
        ...


def _stub_result(order: ExecutionOrder, status: str, message: str) -> ExecutionResult:
    return ExecutionResult(order=order, fills=[], status=status, message=message, metadata={"skeleton": True})


class TradeStationAdapter:
    """Stub adapter. No external connectivity."""

    def submit(self, order: ExecutionOrder) -> ExecutionResult:
        return _stub_result(order, "skeleton", "skeleton")

    def cancel(self, order_id: str) -> ExecutionResult:
        stub = ExecutionOrder(
            order_id=order_id, symbol="", side="", qty=0.0, order_type="skeleton",
            limit_price=0.0, status="cancelled", created_ts=0.0, metadata={"skeleton": True},
        )
        return _stub_result(stub, "cancelled", "skeleton")

    def status(self, order_id: str) -> ExecutionResult:
        stub = ExecutionOrder(
            order_id=order_id, symbol="", side="", qty=0.0, order_type="skeleton",
            limit_price=0.0, status="skeleton", created_ts=0.0, metadata={"skeleton": True},
        )
        return _stub_result(stub, "skeleton", "skeleton")


class BinanceAdapter:
    """Stub adapter. No external connectivity."""

    def submit(self, order: ExecutionOrder) -> ExecutionResult:
        return _stub_result(order, "skeleton", "skeleton")

    def cancel(self, order_id: str) -> ExecutionResult:
        stub = ExecutionOrder(
            order_id=order_id, symbol="", side="", qty=0.0, order_type="skeleton",
            limit_price=0.0, status="cancelled", created_ts=0.0, metadata={"skeleton": True},
        )
        return _stub_result(stub, "cancelled", "skeleton")

    def status(self, order_id: str) -> ExecutionResult:
        stub = ExecutionOrder(
            order_id=order_id, symbol="", side="", qty=0.0, order_type="skeleton",
            limit_price=0.0, status="skeleton", created_ts=0.0, metadata={"skeleton": True},
        )
        return _stub_result(stub, "skeleton", "skeleton")
