"""PnL reconciliation: compare internal PnL vs venue PnL."""
from __future__ import annotations

from nq_reconciliation.models import PnLReconciliationSummary


class PnLReconciliationModule:
    """
    Reconcile PnL: internal (from trades/executions) vs venue-reported PnL.
    Integrates with trades table and venue_account_snapshot equity / venue API.
    """

    def run(
        self,
        venue: str,
        internal_pnl: float,
        venue_pnl: float,
        tolerance: float = 0.01,
    ) -> PnLReconciliationSummary:
        """
        Compare internal_pnl with venue_pnl; return summary.
        tolerance: absolute diff allowed before status is 'mismatch'.
        """
        diff = abs(internal_pnl - venue_pnl)
        status = "ok" if diff <= tolerance else "mismatch"
        return PnLReconciliationSummary(
            venue=venue,
            internal_pnl=internal_pnl,
            venue_pnl=venue_pnl,
            diff=diff,
            tolerance_used=tolerance,
            status=status,
        )
