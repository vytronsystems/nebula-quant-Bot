from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StrategyAdaptationError(Exception):
    """Deterministic exception for invalid strategy adaptation inputs or state."""


class AdaptationActionType(str, Enum):
    """Supported adaptation actions."""

    SUPPRESS_FAMILY = "suppress_family"
    PREFER_FAMILY = "prefer_family"
    EXCLUDE_REGIME = "exclude_regime"
    REQUIRE_REGIME = "require_regime"
    ADJUST_PARAMETER_RANGE = "adjust_parameter_range"
    REDUCE_PRIORITY = "reduce_priority"
    INCREASE_PRIORITY = "increase_priority"
    FLAG_FOR_REVIEW = "flag_for_review"


@dataclass(slots=True)
class AdaptationDirective:
    """Single adaptation directive derived from internal feedback."""

    directive_id: str
    action_type: str
    target_family: str | None = None
    target_parameter: str | None = None
    target_regime: str | None = None
    value: Any | None = None
    rationale: str = ""
    source_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyAdaptationSummary:
    """Summary of adaptation directives for a run."""

    total_directives: int
    suppressed_families: list[str] = field(default_factory=list)
    preferred_families: list[str] = field(default_factory=list)
    excluded_regimes: list[str] = field(default_factory=list)
    parameter_adjustments: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyAdaptationReport:
    """Deterministic strategy adaptation report."""

    report_id: str
    generated_at: float
    directives: list[AdaptationDirective]
    summary: StrategyAdaptationSummary
    metadata: dict[str, Any] = field(default_factory=dict)

