# NEBULA-QUANT v1 | nq_edge_decay — edge decay detection models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EdgeDecayError(Exception):
    """Deterministic exception for invalid edge decay inputs or state."""


class EdgeDecaySeverity(str, Enum):
    """Severity of an edge decay finding."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# Finding categories (deterministic, documented).
CATEGORY_PNL_DECAY = "pnl_decay"
CATEGORY_WIN_RATE_DECAY = "win_rate_decay"
CATEGORY_EXPECTANCY_DECAY = "expectancy_decay"
CATEGORY_SLIPPAGE_DECAY = "slippage_decay"
CATEGORY_EXPERIMENT_QUALITY_DECAY = "experiment_quality_decay"
CATEGORY_EXECUTION_QUALITY_DECAY = "execution_quality_decay"
CATEGORY_MIXED_EDGE_DECAY = "mixed_edge_decay"
CATEGORY_INSUFFICIENT_BASELINE = "insufficient_baseline"
CATEGORY_INCONSISTENT_EDGE_INPUT = "inconsistent_edge_input"


@dataclass(slots=True)
class EdgeDecayInput:
    """Structured input for edge decay analysis (recent vs baseline)."""

    strategy_id: str | None
    window_id: str | None
    baseline_window_id: str | None
    recent_pnl: float | None
    baseline_pnl: float | None
    recent_win_rate: float | None
    baseline_win_rate: float | None
    recent_expectancy: float | None
    baseline_expectancy: float | None
    recent_slippage: float | None
    baseline_slippage: float | None
    recent_failed_experiments: int | None
    baseline_failed_experiments: int | None
    recent_degraded_experiments: int | None
    baseline_degraded_experiments: int | None
    repeated_trade_review_findings: int | None
    repeated_audit_findings: int | None
    regime_label: str | None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class EdgeDecayEvidence:
    """Evidence item supporting an edge decay finding."""

    evidence_id: str
    category: str
    value: Any
    description: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class EdgeDecayFinding:
    """Single edge decay finding with rationale and evidence linkage."""

    finding_id: str
    category: str
    severity: str
    title: str
    description: str
    strategy_id: str | None
    evidence_ids: list[str]
    rationale: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class EdgeDecaySummary:
    """Summary of edge decay analysis."""

    total_findings: int
    info_count: int
    warning_count: int
    critical_count: int
    strategies_seen: list[str]
    categories_seen: list[str]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class EdgeDecayReport:
    """Deterministic edge decay report."""

    report_id: str
    generated_at: float
    findings: list[EdgeDecayFinding]
    summary: EdgeDecaySummary
    metadata: dict[str, Any] | None = field(default_factory=dict)
