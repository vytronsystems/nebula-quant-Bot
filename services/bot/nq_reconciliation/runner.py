# NEBULA-QUANT v1 | Phase 80 — Reconciliation Engine runner
# Continuously reconcile orders, positions, balances; raise alerts on divergence.

from __future__ import annotations

from typing import Any, Callable

from nq_reconciliation.models import (
    OrderReconciliationSummary,
    PnLReconciliationSummary,
    PositionReconciliationSummary,
)
from nq_reconciliation.order_reconciliation import OrderReconciliationModule
from nq_reconciliation.pnl_reconciliation import PnLReconciliationModule
from nq_reconciliation.position_reconciliation import PositionReconciliationModule


def run_reconciliation(
    venue: str,
    internal_orders: list[Any],
    venue_orders: list[Any],
    internal_positions: list[Any],
    venue_positions: list[Any],
    internal_pnl: float = 0.0,
    venue_pnl: float = 0.0,
    on_alert: Callable[[str, dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """
    Run order, position, and PnL reconciliation. Call on_alert(reason, payload) on divergence.
    Returns summary for UI/API.
    """
    order_mod = OrderReconciliationModule()
    pos_mod = PositionReconciliationModule()
    pnl_mod = PnLReconciliationModule()

    order_summary = order_mod.run(venue, internal_orders, venue_orders)
    pos_summary = pos_mod.run(venue, internal_positions, venue_positions)
    pnl_summary = pnl_mod.run(venue, internal_pnl, venue_pnl, tolerance=0.01)

    if on_alert:
        if order_summary.status != "ok":
            on_alert("order_divergence", {"summary": order_summary.__dict__})
        if pos_summary.status != "ok":
            on_alert("position_divergence", {"summary": pos_summary.__dict__})
        if pnl_summary.status == "mismatch":
            on_alert("pnl_divergence", {"summary": pnl_summary.__dict__})

    return {
        "order": order_summary.__dict__,
        "position": pos_summary.__dict__,
        "pnl": pnl_summary.__dict__,
    }
