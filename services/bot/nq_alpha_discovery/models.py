# NEBULA-QUANT v1 | nq_alpha_discovery — alpha hypothesis models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AlphaDiscoveryError(Exception):
    """Deterministic exception for invalid alpha discovery inputs or state."""


class AlphaEvidenceSource(str, Enum):
    """Source of evidence for alpha hypotheses."""

    LEARNING = "learning"
    EXPERIMENT = "experiment"
    AUDIT = "audit"
    TRADE_REVIEW = "trade_review"
    RESEARCH = "research"
    OTHER = "other"


class AlphaHypothesisPriority(str, Enum):
    """Priority of an alpha hypothesis."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class AlphaObservation:
    """Single normalized observation from a supported source."""

    observation_id: str
    source_type: str
    category: str
    strategy_id: str | None
    module: str | None
    title: str
    description: str
    severity: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class AlphaEvidence:
    """Evidence item linked to observations; used for hypothesis traceability."""

    evidence_id: str
    source_type: str
    source_id: str
    category: str
    strategy_id: str | None
    module: str | None
    weight: float
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class AlphaHypothesis:
    """Explicit alpha hypothesis with rationale and evidence linkage."""

    hypothesis_id: str
    title: str
    description: str
    category: str
    related_strategy_id: str | None
    related_module: str | None
    priority: str
    confidence_score: float
    evidence_ids: list[str]
    rationale: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class AlphaDiscoverySummary:
    """Summary of an alpha discovery run."""

    total_observations: int
    total_hypotheses: int
    low_count: int
    medium_count: int
    high_count: int
    critical_count: int
    categories_seen: list[str]
    strategies_seen: list[str]
    modules_seen: list[str]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class AlphaDiscoveryReport:
    """Deterministic alpha discovery report."""

    report_id: str
    generated_at: float
    summary: AlphaDiscoverySummary
    hypotheses: list[AlphaHypothesis]
    metadata: dict[str, Any] | None = field(default_factory=dict)
