# NEBULA-QUANT v1 | nq_sre — operational reliability models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SREError(Exception):
    """Deterministic exception for invalid SRE inputs or state."""


class ReliabilityStatus(str, Enum):
    """Overall reliability status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class IncidentSeverity(str, Enum):
    """Incident severity."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# Incident categories (deterministic, documented).
CATEGORY_COMPONENT_UNAVAILABLE = "component_unavailable"
CATEGORY_COMPONENT_DEGRADED = "component_degraded"
CATEGORY_STALE_SIGNAL = "stale_signal"
CATEGORY_MISSING_HEARTBEAT = "missing_heartbeat"
CATEGORY_EXCESSIVE_ERRORS = "excessive_errors"
CATEGORY_REPEATED_FAILURES = "repeated_failures"
CATEGORY_QUEUE_BACKLOG = "queue_backlog"
CATEGORY_STALE_DATA = "stale_data"
CATEGORY_RELEASE_HEALTH_RISK = "release_health_risk"
CATEGORY_INCONSISTENT_SRE_INPUT = "inconsistent_sre_input"


@dataclass(slots=True)
class SREInput:
    """Structured input for reliability evaluation."""

    component_name: str | None
    component_type: str | None
    status: str | None
    healthy: bool | None
    degraded: bool | None
    unavailable: bool | None
    last_update: float | None
    stale: bool | None
    missing_heartbeat: bool | None
    error_count: int | None
    failed_jobs: int | None
    repeated_failures: int | None
    queue_backlog: int | None
    stale_data: bool | None
    criticality: str | None
    impacted_modules: list[str] | None
    impacted_strategies: list[str] | None
    release_status: str | None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class SREEvidence:
    """Evidence item for reliability evaluation."""

    evidence_id: str
    category: str
    value: Any
    description: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class SREIncident:
    """Single incident with rationale and evidence linkage."""

    incident_id: str
    component_name: str | None
    category: str
    severity: str
    title: str
    description: str
    evidence_ids: list[str]
    rationale: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class SRESummary:
    """Summary of reliability evaluation."""

    total_inputs: int
    healthy_components: int
    degraded_components: int
    unavailable_components: int
    total_incidents: int
    info_count: int
    warning_count: int
    critical_count: int
    components_seen: list[str]
    categories_seen: list[str]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class SREReport:
    """Deterministic SRE report."""

    report_id: str
    generated_at: float
    overall_status: str
    incidents: list[SREIncident]
    summary: SRESummary
    metadata: dict[str, Any] | None = field(default_factory=dict)
