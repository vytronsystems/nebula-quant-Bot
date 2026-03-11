# NEBULA-QUANT v1 | nq_event_store models

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Event type categories supported by the store (normalized, append-only).
EVENT_TYPE_STRATEGY = "strategy_event"
EVENT_TYPE_RISK_DECISION = "risk_decision"
EVENT_TYPE_GUARDRAIL_DECISION = "guardrail_decision"
EVENT_TYPE_PORTFOLIO_DECISION = "portfolio_decision"
EVENT_TYPE_PROMOTION_DECISION = "promotion_decision"
EVENT_TYPE_EXECUTION = "execution_event"
EVENT_TYPE_OBSERVABILITY = "observability_event"
EVENT_TYPE_EXPERIMENT = "experiment_event"
EVENT_TYPE_SYSTEM = "system_event"

EVENT_TYPES: frozenset[str] = frozenset({
    EVENT_TYPE_STRATEGY,
    EVENT_TYPE_RISK_DECISION,
    EVENT_TYPE_GUARDRAIL_DECISION,
    EVENT_TYPE_PORTFOLIO_DECISION,
    EVENT_TYPE_PROMOTION_DECISION,
    EVENT_TYPE_EXECUTION,
    EVENT_TYPE_OBSERVABILITY,
    EVENT_TYPE_EXPERIMENT,
    EVENT_TYPE_SYSTEM,
})


@dataclass(slots=True)
class EventRecord:
    """Immutable record for a single append-only event."""

    event_id: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    timestamp: str
    payload: dict[str, Any]
    metadata: dict[str, Any] | None = None
    sequence_id: int | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


@dataclass(slots=True)
class EventFilter:
    """Optional helper for query constraints (event_type, aggregate_id, aggregate_type, limit)."""

    event_type: str | None = None
    aggregate_type: str | None = None
    aggregate_id: str | None = None
    limit: int | None = None
