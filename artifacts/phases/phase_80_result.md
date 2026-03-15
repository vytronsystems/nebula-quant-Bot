# Phase 80 — Reconciliation Engine — Result

## Summary

Continuously reconcile orders, positions, balances; raise alerts on divergence.

## Implementation

- **Bot**: `nq_reconciliation/runner.py` — run_reconciliation(venue, internal_orders, venue_orders, internal_positions, venue_positions, internal_pnl, venue_pnl, on_alert). Calls OrderReconciliationModule, PositionReconciliationModule, PnLReconciliationModule; invokes on_alert(reason, payload) on divergence.

## Modules Affected

- services/bot/nq_reconciliation/runner.py
