# NEBULA-QUANT v1 | nq_audit models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AuditError(Exception):
    """Deterministic exception for invalid audit inputs or state."""


class AuditFindingSeverity(str, Enum):
    """Severity of an audit finding."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(slots=True)
class AuditInput:
    """Typed aggregate input for audit analysis. Optional sections may be empty or None."""

    events: list[dict[str, Any]] = field(default_factory=list)
    decision_records: list[dict[str, Any]] = field(default_factory=list)
    execution_records: list[dict[str, Any]] = field(default_factory=list)
    strategy_health: list[dict[str, Any]] = field(default_factory=list)
    control_summary: dict[str, Any] | None = None
    experiment_summary: dict[str, Any] | None = None
    registry_records: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.events is None:
            object.__setattr__(self, "events", [])
        if self.decision_records is None:
            object.__setattr__(self, "decision_records", [])
        if self.execution_records is None:
            object.__setattr__(self, "execution_records", [])
        if self.strategy_health is None:
            object.__setattr__(self, "strategy_health", [])


@dataclass(slots=True)
class AuditFinding:
    """Single structured audit finding."""

    finding_id: str
    category: str
    severity: str
    title: str
    description: str
    related_strategy_id: str | None = None
    related_module: str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class AuditSummary:
    """Summary counts and scope of an audit run."""

    total_findings: int
    info_count: int
    warning_count: int
    critical_count: int
    modules_reviewed: list[str]
    strategies_reviewed: list[str]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class AuditReport:
    """Full deterministic audit report."""

    audit_id: str
    generated_at: float
    summary: AuditSummary
    findings: list[AuditFinding]
    recommendations: list[str]
    metadata: dict[str, Any] | None = field(default_factory=dict)
