# NEBULA-QUANT v1 | Phase 78 — Capital Allocation models

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AllocationInput:
    strategy_id: str
    momentum: float | None = None
    pnl_stability: float | None = None
    drawdown: float | None = None
    volatility: float | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class AllocationResult:
    strategy_id: str
    weight: float
    risk_pct: float
    reason: str
    metadata: dict[str, Any] | None = None
