# NEBULA-QUANT v1 | nq_experiments models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExperimentError(Exception):
    """Deterministic exception for invalid experiment inputs or state."""


class ExperimentStatus(str, Enum):
    """Status of an experiment."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    DEGRADED = "degraded"
    INVALID = "invalid"


VALID_STATUSES = frozenset(s.value for s in ExperimentStatus)


class ExperimentType(str, Enum):
    """Type of experiment."""

    BACKTEST = "backtest"
    WALKFORWARD = "walkforward"
    PAPER = "paper"
    RESEARCH = "research"
    OTHER = "other"


VALID_EXPERIMENT_TYPES = frozenset(t.value for t in ExperimentType)


class ExperimentFindingSeverity(str, Enum):
    """Severity of an experiment finding."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# Finding categories (deterministic, documented).
CATEGORY_EXPERIMENT_FAILED = "experiment_failed"
CATEGORY_EXPERIMENT_DEGRADED = "experiment_degraded"
CATEGORY_EXPERIMENT_INVALID = "experiment_invalid"
CATEGORY_UNSTABLE_RESULT = "unstable_result"
CATEGORY_WEAK_RESULT = "weak_result"
CATEGORY_MISSING_METRICS = "missing_metrics"
CATEGORY_INCONSISTENT_RECORD = "inconsistent_experiment_record"


@dataclass(slots=True)
class ExperimentFinding:
    """Single structured experiment finding."""

    finding_id: str
    category: str
    severity: str
    title: str
    description: str
    experiment_id: str
    strategy_id: str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ExperimentSummary:
    """Summary of experiment analysis."""

    total_experiments: int
    successful_experiments: int
    failed_experiments: int
    degraded_experiments: int
    invalid_experiments: int
    strategies_seen: list[str] = field(default_factory=list)
    categories_seen: list[str] = field(default_factory=list)
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ExperimentReport:
    """Full deterministic experiment analysis report."""

    report_id: str
    generated_at: float
    summary: ExperimentSummary
    findings: list[ExperimentFinding]
    experiment_records: list[Any] = field(default_factory=list)
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass
class ExperimentRecord:
    """Single experiment record (skeleton)."""

    experiment_id: str
    strategy_id: str
    strategy_version: str
    experiment_type: str
    status: str
    parameters: dict[str, Any]
    metrics: dict[str, Any]
    notes: str
    created_at: float
    updated_at: float
    owner: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentComparisonResult:
    """Result of comparing two experiments (skeleton)."""

    baseline_experiment_id: str
    candidate_experiment_id: str
    metric_deltas: dict[str, float]
    winner: str
    summary: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentsRegistryResult:
    """Aggregate registry of experiments (skeleton)."""

    experiments: list[ExperimentRecord]
    total_experiments: int
    active_experiments: int
    completed_experiments: int
    failed_experiments: int
    metadata: dict[str, Any] = field(default_factory=dict)
