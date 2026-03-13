"""Cross-venue DTOs for dashboard aggregation and control plane."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class VenueSummary:
    """Single venue in abstraction (id, name, enabled)."""
    venue_id: str
    name: str
    enabled: bool
    meta: dict[str, Any] | None = None


@dataclass
class VenueAccountSummary:
    """Account summary for one venue (from snapshot or API)."""
    venue_id: str
    account_id: str | None
    balance: float | None
    equity: float | None
    updated_at: datetime | None
    meta: dict[str, Any] | None = None


@dataclass
class SeparatedCapitalView:
    """Per-venue capital (separated capital tracking)."""
    venue_id: str
    balance: float
    equity: float
    allocated: float
    meta: dict[str, Any] | None = None


@dataclass
class DashboardAggregationContract:
    """Contract for dashboard aggregation (control plane / UI)."""
    venues: list[VenueSummary]
    account_summaries: list[VenueAccountSummary]
    separated_capital: list[SeparatedCapitalView]
    total_equity: float
    meta: dict[str, Any] | None = None
