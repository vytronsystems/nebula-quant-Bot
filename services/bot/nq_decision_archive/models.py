# NEBULA-QUANT v1 | nq_decision_archive — decision archival models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DecisionArchiveError(Exception):
    """Deterministic exception for invalid archive inputs or state."""


class DecisionSourceType(str, Enum):
    """Source module type for archived decisions."""

    RISK = "risk"
    GUARDRAILS = "guardrails"
    PORTFOLIO = "portfolio"
    PROMOTION = "promotion"
    OTHER = "other"


class DecisionOutcomeType(str, Enum):
    """Canonical decision outcome for archival."""

    ALLOW = "allow"
    BLOCK = "block"
    REDUCE = "reduce"
    THROTTLE = "throttle"
    APPROVE = "approve"
    REJECT = "reject"
    UNKNOWN = "unknown"


VALID_SOURCE_TYPES = frozenset(s.value for s in DecisionSourceType)
VALID_OUTCOME_TYPES = frozenset(o.value for o in DecisionOutcomeType)


@dataclass(slots=True)
class DecisionRecord:
    """Single normalized decision record for archival."""

    archive_id: str
    source_module: str
    source_type: str
    decision_type: str
    decision_outcome: str
    strategy_id: str | None
    symbol: str | None
    timestamp: float
    reason_codes: list[str]
    source_id: str | None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class DecisionQuery:
    """Query parameters for filtering archived decisions."""

    strategy_id: str | None = None
    source_module: str | None = None
    decision_outcome: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    limit: int | None = None


@dataclass(slots=True)
class DecisionArchiveSummary:
    """Deterministic summary of archived decisions."""

    total_records: int
    by_module: dict[str, int]
    by_outcome: dict[str, int]
    strategies_seen: list[str]
    reason_code_counts: dict[str, int]
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class DecisionArchiveReport:
    """Deterministic report over archived decisions."""

    report_id: str
    generated_at: float
    records: list[DecisionRecord]
    summary: DecisionArchiveSummary
    metadata: dict[str, Any] | None = field(default_factory=dict)
