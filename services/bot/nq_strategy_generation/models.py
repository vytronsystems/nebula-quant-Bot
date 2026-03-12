from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StrategyGenerationError(Exception):
    """Deterministic exception for invalid strategy generation inputs or state."""


class StrategyFamily(str, Enum):
    """Supported strategy families for automatic generation."""

    BREAKOUT = "breakout"
    MOMENTUM_CONTINUATION = "momentum_continuation"
    MEAN_REVERSION = "mean_reversion"
    OPENING_RANGE_BREAKOUT = "opening_range_breakout"
    PULLBACK_CONTINUATION = "pullback_continuation"
    REVERSAL = "reversal"
    VOLATILITY_EXPANSION = "volatility_expansion"
    SESSION_BIAS = "session_bias"


@dataclass(slots=True)
class StrategyTemplate:
    """Static, deterministic description of a strategy structure."""

    template_id: str
    family: str
    title: str
    description: str
    regime_constraints: list[str] = field(default_factory=list)
    entry_conditions: dict[str, Any] = field(default_factory=dict)
    exit_conditions: dict[str, Any] = field(default_factory=dict)
    stop_loss_rule: dict[str, Any] = field(default_factory=dict)
    take_profit_rule: dict[str, Any] = field(default_factory=dict)
    sizing_rule: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyParameterSet:
    """Deterministic parameter configuration for a template."""

    parameter_set_id: str
    parameters: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyCandidate:
    """Single generated candidate strategy."""

    candidate_id: str
    strategy_id: str
    family: str
    template_id: str
    parameter_set_id: str
    regime: str
    rationale: str
    feature_snapshot: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyGenerationSummary:
    """Summary of one generation run."""

    total_templates: int
    total_parameter_sets: int
    total_candidates: int
    families_seen: list[str] = field(default_factory=list)
    regimes_seen: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyGenerationReport:
    """Deterministic strategy generation report."""

    report_id: str
    generated_at: float
    templates: list[StrategyTemplate]
    parameter_sets: list[StrategyParameterSet]
    candidates: list[StrategyCandidate]
    summary: StrategyGenerationSummary
    metadata: dict[str, Any] = field(default_factory=dict)

