# NEBULA-QUANT v1 | nq_db models

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class StrategyRecord:
    strategy_id: str
    lifecycle_state: str
    enabled: bool
    created_at: float
    updated_at: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionRecord:
    execution_id: str
    strategy_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    status: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ObservabilitySnapshotRecord:
    snapshot_id: str
    generated_at: float
    system_summary: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExperimentRecord:
    experiment_id: str
    strategy_id: str
    start_time: float
    end_time: float
    result_status: str
    metrics: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DecisionRecord:
    decision_id: str
    module_name: str
    decision_type: str
    strategy_id: str
    timestamp: float
    reason_codes: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)
