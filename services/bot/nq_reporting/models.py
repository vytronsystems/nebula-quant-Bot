# NEBULA-QUANT v1 | nq_reporting models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReportError(Exception):
    """Deterministic exception for invalid report inputs or state."""


class ReportType(str, Enum):
    """Type of report."""

    AUDIT = "audit"
    TRADE_REVIEW = "trade_review"
    LEARNING = "learning"
    OBSERVABILITY = "observability"
    SYSTEM = "system"


@dataclass(slots=True)
class ReportMetadata:
    """Metadata for a report."""

    report_id: str
    report_type: str
    generated_at: float
    source_module: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class AuditSummaryReport:
    """Summary report derived from nq_audit AuditReport."""

    total_findings: int
    severity_distribution: dict[str, int]
    affected_strategies: list[str]
    affected_modules: list[str]
    recommendations: list[str]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class TradeReviewSummaryReport:
    """Summary report derived from one or more nq_trade_review TradeReviewReport."""

    total_trades_reviewed: int
    win_rate: float
    loss_rate: float
    breakeven_rate: float
    common_issues: list[str]
    severity_distribution: dict[str, int]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class LearningSummaryReport:
    """Summary report derived from nq_learning LearningReport."""

    total_patterns: int
    total_lessons: int
    total_improvement_candidates: int
    high_priority_items: int
    critical_priority_items: int
    categories_seen: list[str]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ObservabilitySummaryReport:
    """Summary report derived from observability inputs (nq_metrics / nq_obs)."""

    system_health_score: float | None
    degraded_strategies: list[str]
    inactive_strategies: list[str]
    event_anomalies: list[str]
    metrics_summary: dict[str, Any] | None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ImprovementSummaryReport:
    """Summary report derived from nq_improvement ImprovementPlan."""

    total_actions: int
    priority_distribution: dict[str, int]
    affected_strategies: list[str]
    affected_modules: list[str]
    categories_seen: list[str]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ExperimentSummaryReport:
    """Summary report derived from nq_experiments ExperimentReport."""

    total_experiments: int
    successful_experiments: int
    failed_experiments: int
    degraded_experiments: int
    invalid_experiments: int
    strategies_seen: list[str]
    categories_seen: list[str]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class SystemReport:
    """Top-level system report aggregating all subreports."""

    report_id: str
    generated_at: float
    # Existing analytical subreports
    audit_report: AuditSummaryReport | None = None
    trade_review_report: TradeReviewSummaryReport | None = None
    learning_report: LearningSummaryReport | None = None
    improvement_report: ImprovementSummaryReport | None = None
    experiment_report: ExperimentSummaryReport | None = None
    observability_report: ObservabilitySummaryReport | None = None
    # Operational governance subreports (Phase 45)
    sre_report: Any | None = None
    runbook_report: Any | None = None
    release_report: Any | None = None
    # High-level system summary for dashboards / governance
    summary: dict[str, Any] | None = field(default_factory=dict)
    metadata: dict[str, Any] | None = field(default_factory=dict)
