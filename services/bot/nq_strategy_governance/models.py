from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StrategyGovernanceError(Exception):
    """Deterministic exception for invalid strategy governance inputs or state."""


class StrategyGovernanceDecision(str, Enum):
    """Final lifecycle decision for a strategy."""

    APPROVED_FOR_LIVE = "approved_for_live"
    REMAIN_IN_PAPER = "remain_in_paper"
    RETURN_TO_RESEARCH = "return_to_research"
    REJECT_STRATEGY = "reject_strategy"


@dataclass(slots=True)
class StrategyGovernanceInput:
    """Aggregated evidence used for final readiness evaluation."""

    strategy_id: str
    backtest_summary: dict[str, Any] | None = None
    walkforward_summary: dict[str, Any] | None = None
    paper_summary: dict[str, Any] | None = None
    metrics_summary: dict[str, Any] | None = None
    edge_decay_summary: dict[str, Any] | None = None
    audit_summary: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyGovernanceFinding:
    """Single structured governance finding contributing to the decision."""

    finding_id: str
    category: str
    severity: str
    title: str
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyGovernanceReport:
    """Deterministic strategy governance report."""

    report_id: str
    generated_at: float
    strategy_id: str
    decision: StrategyGovernanceDecision
    findings: list[StrategyGovernanceFinding]
    rationale: str
    metadata: dict[str, Any] = field(default_factory=dict)

