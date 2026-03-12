from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ResearchPipelineError(Exception):
    """Deterministic exception for invalid research pipeline inputs or state."""


@dataclass
class ResearchCycleReport:
    """
    Aggregate output of a full research pipeline cycle.

    This is intentionally compact and stable for reporting and governance layers.
    """

    cycle_id: str
    generated_at: float
    candidate_count: int
    experiment_count: int
    approved_strategies: list[str] = field(default_factory=list)
    rejected_strategies: list[str] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

