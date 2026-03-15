# NEBULA-QUANT v1 | Phase 83 — Strategy Optimizer models

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class OptimizationProposal:
    strategy_id: str
    parameter: str
    current_value: Any
    proposed_value: Any
    reason: str
    metadata: dict[str, Any] | None = None


@dataclass
class OptimizationResult:
    strategy_id: str
    proposals: list[OptimizationProposal]
    market_regime: str | None
    metadata: dict[str, Any] | None = None
