# NEBULA-QUANT v1 | nq_exec models

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionOrder:
    """Order submitted to execution layer."""

    order_id: str
    symbol: str
    side: str
    qty: float
    order_type: str
    limit_price: float
    status: str
    created_ts: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionFill:
    """Single fill event."""

    fill_id: str
    order_id: str
    symbol: str
    qty: float
    price: float
    filled_ts: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of an execution operation."""

    order: ExecutionOrder
    fills: list[ExecutionFill]
    status: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
