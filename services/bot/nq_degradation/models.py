# NEBULA-QUANT v1 | Phase 77 — Degradation Engine models

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DegradationSignal:
    deployment_id: str
    reason: str
    rolling_win_rate: float | None
    rolling_pnl: float | None
    drawdown: float | None
    profit_factor: float | None
    metadata: dict[str, Any] | None = None


@dataclass
class DegradationResult:
    should_degrade: bool
    trading_enabled: bool
    signal: DegradationSignal | None
    alerts_emitted: list[str]
