# Phase 63 — Reconciliation Layer — Result

## Objective
Introduce dedicated reconciliation modules.

## Completed tasks

1. **Order reconciliation module** — `nq_reconciliation.order_reconciliation.OrderReconciliationModule`: compares internal order list vs venue order list; returns `OrderReconciliationSummary` (matched, internal_only, venue_only, discrepancies, status).
2. **Position reconciliation module** — `nq_reconciliation.position_reconciliation.PositionReconciliationModule`: compares internal vs venue positions; returns `PositionReconciliationSummary`.
3. **PnL reconciliation module** — `nq_reconciliation.pnl_reconciliation.PnLReconciliationModule`: compares internal PnL vs venue PnL with tolerance; returns `PnLReconciliationSummary`.
4. **Integration** — README documents integration with event/archive/reporting (callers supply data from bot DB and venue snapshots); summaries are DTOs for control plane and UI.
5. **Expose summaries** — Typed DTOs (`OrderReconciliationSummary`, `PositionReconciliationSummary`, `PnLReconciliationSummary`, `ReconciliationSummary`) for control plane and UI.

## Code

- `services/bot/nq_reconciliation/` (new package: models, order_reconciliation, position_reconciliation, pnl_reconciliation, README, tests).
