# NEBULA-QUANT v1 | Phase 86 — Risk Guardrails models

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GuardrailLimits:
    max_drawdown_pct: float = 0.20
    max_margin_usage_pct: float = 0.80
    max_exposure_per_strategy_pct: float = 0.25


@dataclass
class GuardrailCheck:
    passed: bool
    limit_name: str
    current_value: float
    limit_value: float
    reason: str
    metadata: dict[str, Any] | None = None
