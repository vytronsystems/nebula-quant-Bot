# NEBULA-QUANT v1 | nq_release — release governance models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReleaseError(Exception):
    """Deterministic exception for invalid release inputs or state."""


class ReleaseStatus(str, Enum):
    """Release decision status."""

    DRAFT = "draft"
    READY = "ready"
    BLOCKED = "blocked"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReleaseValidationStatus(str, Enum):
    """Per-check validation status."""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    NOT_EVALUATED = "not_evaluated"


@dataclass(slots=True)
class ReleaseModuleRecord:
    """Single module entry in a release candidate."""

    module_name: str
    included: bool
    implemented: bool
    integrated: bool
    validation_status: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ReleaseEvidence:
    """Evidence item for release evaluation."""

    evidence_id: str
    category: str
    value: Any
    description: str
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ReleaseBlocker:
    """Blocker that prevents or qualifies release."""

    blocker_id: str
    category: str
    severity: str  # WARNING | CRITICAL
    title: str
    description: str
    related_module: str | None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ReleaseManifest:
    """Structured release manifest."""

    manifest_id: str
    release_name: str
    version_label: str
    branch: str | None
    commit_hash: str | None
    included_modules: list[str]
    module_records: list[ReleaseModuleRecord]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ReleaseDecision:
    """Release decision with rationale and linkage."""

    decision_id: str
    status: str
    rationale: str
    blocker_ids: list[str]
    evidence_ids: list[str]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ReleaseSummary:
    """Summary of release evaluation."""

    total_modules: int
    included_modules_count: int
    implemented_modules_count: int
    integrated_modules_count: int
    blockers_count: int
    warnings_count: int
    critical_blockers_count: int
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ReleaseReport:
    """Deterministic release report."""

    report_id: str
    generated_at: float
    manifest: ReleaseManifest
    decision: ReleaseDecision
    summary: ReleaseSummary
    blockers: list[ReleaseBlocker]
    evidence: list[ReleaseEvidence]
    metadata: dict[str, Any] | None = field(default_factory=dict)
