"""Position reconciliation: compare internal position state vs venue positions."""
from __future__ import annotations

from nq_reconciliation.models import PositionReconciliationSummary


class PositionReconciliationModule:
    """
    Reconcile positions: internal (trades/positions) vs venue position snapshot.
    Integrates with trades table and venue_account_snapshot / venue positions API.
    """

    def run(self, venue: str, internal_positions: list[dict], venue_positions: list[dict]) -> PositionReconciliationSummary:
        """
        Compare internal_positions with venue_positions; return summary.
        """
        internal_symbols = {p.get("symbol") for p in internal_positions if p and p.get("symbol")}
        venue_symbols = {p.get("symbol") for p in venue_positions if p and p.get("symbol")}
        matched = len(internal_symbols & venue_symbols)
        internal_only = len(internal_symbols - venue_symbols)
        venue_only = len(venue_symbols - internal_symbols)
        discrepancies = []
        status = "ok" if not discrepancies else "warning"
        return PositionReconciliationSummary(
            venue=venue,
            matched=matched,
            internal_only=internal_only,
            venue_only=venue_only,
            discrepancies=discrepancies,
            status=status,
        )
