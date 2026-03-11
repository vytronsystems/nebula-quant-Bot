# NEBULA-QUANT v1 | nq_improvement models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ImprovementError(Exception):
    """Deterministic exception for invalid improvement inputs or state."""


class ImprovementPriority(str, Enum):
    """Priority for improvement actions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImprovementType(str, Enum):
    """Type of improvement action."""

    STRATEGY_REVIEW = "strategy_review"
    MODULE_REVIEW = "module_review"
    PARAMETER_REVIEW = "parameter_review"
    EXECUTION_REVIEW = "execution_review"
    RISK_REVIEW = "risk_review"
    PORTFOLIO_REVIEW = "portfolio_review"
    PROMOTION_REVIEW = "promotion_review"
    DATA_QUALITY_REVIEW = "data_quality_review"
    OBSERVABILITY_REVIEW = "observability_review"
    DOCUMENTATION_REVIEW = "documentation_review"


@dataclass(slots=True)
class ImprovementAction:
    """Single structured improvement action."""

    action_id: str
    title: str
    description: str
    priority: str
    improvement_type: str
    related_strategy_id: str | None = None
    related_module: str | None = None
    source_categories: list[str] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    rationale: str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ImprovementPlanSummary:
    """Summary of an improvement plan."""

    total_actions: int
    low_count: int
    medium_count: int
    high_count: int
    critical_count: int
    affected_strategies: list[str] = field(default_factory=list)
    affected_modules: list[str] = field(default_factory=list)
    categories_seen: list[str] = field(default_factory=list)
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ImprovementPlan:
    """Full deterministic improvement plan."""

    plan_id: str
    generated_at: float
    summary: ImprovementPlanSummary
    actions: list[ImprovementAction]
    metadata: dict[str, Any] | None = field(default_factory=dict)
