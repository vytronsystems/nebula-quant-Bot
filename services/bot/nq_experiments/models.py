# NEBULA-QUANT v1 | nq_experiments models

from dataclasses import dataclass, field
from typing import Any


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
