# NEBULA-QUANT v1 | nq_promotion models

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PromotionInput:
    """Structured input for a promotion evaluation."""

    strategy_id: str
    current_status: str
    backtest_summary: dict[str, Any] = field(default_factory=dict)
    walkforward_summary: dict[str, Any] = field(default_factory=dict)
    paper_summary: dict[str, Any] = field(default_factory=dict)
    guardrail_summary: dict[str, Any] = field(default_factory=dict)
    metrics_summary: dict[str, Any] = field(default_factory=dict)
    experiment_summary: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PromotionDecision:
    """Decision for a single promotion request."""

    allowed: bool
    from_status: str
    to_status: str
    reason: str
    blocking_issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PromotionResult:
    """Result of a promotion evaluation."""

    strategy_id: str
    decision: PromotionDecision
    evaluated_at: float
    metadata: dict[str, Any] = field(default_factory=dict)
