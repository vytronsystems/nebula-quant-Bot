# NEBULA-QUANT v1 | Phase 75 — Recommendation Engine models

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class RecommendedState(str, Enum):
    READY_FOR_LIVE = "ready_for_live"
    REQUIRES_MORE_DATA = "requires_more_data"
    KEEP_IN_PAPER = "keep_in_paper"
    DEGRADED = "degraded"
    REJECTED = "rejected"


@dataclass
class RecommendationResult:
    deployment_id: str
    current_stage: str
    recommended_state: RecommendedState
    reason: str
    metrics_used: dict[str, Any]
    metadata: dict[str, Any] | None = None
