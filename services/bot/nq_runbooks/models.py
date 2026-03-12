# NEBULA-QUANT v1 | nq_runbooks — operational runbook models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RunbookError(Exception):
    """Deterministic exception for invalid runbook or incident inputs."""


class RunbookSeverity(str, Enum):
    """Runbook severity level."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# Action types for runbook steps (documentation + recommendation only).
ACTION_CHECK = "check"
ACTION_RESTART = "restart"
ACTION_INSPECT = "inspect"
ACTION_VALIDATE = "validate"
ACTION_NOTIFY = "notify"
ACTION_MANUAL = "manual"


@dataclass(slots=True)
class RunbookStep:
    """Single step in a runbook procedure."""

    step_id: str
    description: str
    action_type: str
    expected_outcome: str | None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class Runbook:
    """Structured operational runbook."""

    runbook_id: str
    title: str
    description: str
    incident_category: str
    applicable_modules: list[str]
    severity: str
    steps: list[RunbookStep]
    version: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class RunbookMatch:
    """Match between an incident category and a runbook."""

    match_id: str
    incident_category: str
    matched_runbook_id: str
    confidence: str
    rationale: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class RunbookRecommendation:
    """Recommendation to apply a runbook for an incident."""

    recommendation_id: str
    incident_id: str
    runbook_id: str
    steps: list[RunbookStep]
    rationale: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class RunbookSummary:
    """Summary of runbook recommendation generation."""

    total_runbooks: int
    categories_covered: list[str]
    modules_covered: list[str]
    recommendations_generated: int
    unmatched_incidents: int
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class RunbookReport:
    """Deterministic runbook recommendation report."""

    report_id: str
    generated_at: float
    recommendations: list[RunbookRecommendation]
    unmatched_incidents: list[Any]
    summary: RunbookSummary
    metadata: dict[str, Any] | None = field(default_factory=dict)
