# NEBULA-QUANT v1 | nq_regime — regime classification models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RegimeError(Exception):
    """Deterministic exception for invalid regime inputs or state."""


class RegimeLabel(str, Enum):
    """Explicit regime classification labels."""

    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGE_BOUND = "range_bound"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    MOMENTUM_UP = "momentum_up"
    MOMENTUM_DOWN = "momentum_down"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class RegimeInput:
    """Structured market context input for regime classification."""

    observation_id: str | None
    symbol: str | None
    timestamp: float | None
    price: float | None
    moving_average_short: float | None
    moving_average_long: float | None
    trend_strength: float | None
    volatility: float | None
    volatility_percentile: float | None
    momentum_score: float | None
    structure_hint: str | None
    liquidity_hint: str | None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class RegimeEvidence:
    """Evidence item supporting a regime classification."""

    evidence_id: str
    category: str
    value: Any
    description: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class RegimeClassification:
    """Single regime classification with rationale and evidence linkage."""

    classification_id: str
    symbol: str | None
    timestamp: float | None
    primary_regime: str
    secondary_regimes: list[str]
    confidence_score: float
    rationale: str
    evidence_ids: list[str]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class RegimeSummary:
    """Summary of regime classifications."""

    total_classifications: int
    by_primary_regime: dict[str, int]
    symbols_seen: list[str]
    high_confidence_count: int
    low_confidence_count: int
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class RegimeReport:
    """Deterministic regime report."""

    report_id: str
    generated_at: float
    classifications: list[RegimeClassification]
    summary: RegimeSummary
    metadata: dict[str, Any] | None = field(default_factory=dict)
