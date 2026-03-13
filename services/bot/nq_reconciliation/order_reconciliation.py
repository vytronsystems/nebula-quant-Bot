"""Order reconciliation: compare internal order state vs venue order state."""
from __future__ import annotations

from nq_reconciliation.models import OrderReconciliationSummary


class OrderReconciliationModule:
    """
    Reconcile orders: internal (bot orders/executions) vs venue snapshot/API.
    Integrates with existing orders/executions tables and venue order snapshots (when available).
    """

    def run(self, venue: str, internal_orders: list[dict], venue_orders: list[dict]) -> OrderReconciliationSummary:
        """
        Compare internal_orders with venue_orders; return summary.
        Inputs can come from bot/db (orders + executions) and venue API or snapshot.
        """
        internal_ids = {o.get("id") or o.get("broker_order_id") for o in internal_orders if o}
        venue_ids = {o.get("orderId") or o.get("order_id") for o in venue_orders if o}
        matched = len(internal_ids & venue_ids) if venue_ids else 0
        internal_only = len(internal_ids - venue_ids) if venue_ids else len(internal_ids)
        venue_only = len(venue_ids - internal_ids) if internal_ids else len(venue_ids)
        discrepancies = []
        status = "ok" if not discrepancies and (internal_only == 0 or venue_only == 0) else ("warning" if internal_only or venue_only else "ok")
        return OrderReconciliationSummary(
            venue=venue,
            matched=matched,
            internal_only=internal_only,
            venue_only=venue_only,
            discrepancies=discrepancies,
            status=status,
        )
