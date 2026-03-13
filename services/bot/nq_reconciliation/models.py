"""DTOs for reconciliation summaries (control plane and UI)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class OrderReconciliationSummary:
    """Summary of order reconciliation (internal vs venue)."""
    venue: str
    matched: int
    internal_only: int
    venue_only: int
    discrepancies: list[dict[str, Any]]
    status: str  # ok / warning / error


@dataclass
class PositionReconciliationSummary:
    """Summary of position reconciliation."""
    venue: str
    matched: int
    internal_only: int
    venue_only: int
    discrepancies: list[dict[str, Any]]
    status: str


@dataclass
class PnLReconciliationSummary:
    """Summary of PnL reconciliation."""
    venue: str
    internal_pnl: float
    venue_pnl: float
    diff: float
    tolerance_used: float
    status: str  # ok / mismatch


@dataclass
class ReconciliationSummary:
    """Aggregate reconciliation for control plane / UI."""
    order: OrderReconciliationSummary | None
    position: PositionReconciliationSummary | None
    pnl: PnLReconciliationSummary | None
    overall_status: str
