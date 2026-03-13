# nq_reconciliation — Order, Position, PnL Reconciliation

Dedicated reconciliation layers for NEBULA-QUANT:

- **Order reconciliation**: Compare internal order state (bot `orders` / `executions`) with venue order state (from API or snapshot). Produces `OrderReconciliationSummary`.
- **Position reconciliation**: Compare internal positions (e.g. from `trades` or position store) with venue position snapshot. Produces `PositionReconciliationSummary`.
- **PnL reconciliation**: Compare internal PnL (from `trades` or reporting) with venue-reported PnL (e.g. from `venue_account_snapshot` equity). Produces `PnLReconciliationSummary`.

## Integration

- **Event/archive/reporting**: Callers supply inputs from existing layers (e.g. read `orders`/`executions`/`trades` from bot DB; read venue snapshots from `venue_account_snapshot` or venue API). This package does not persist; it computes summaries.
- **Control plane / UI**: Summaries are typed DTOs (`OrderReconciliationSummary`, etc.) suitable for REST responses and UI. Aggregate with `ReconciliationSummary` for a single reconciliation report.

## Usage

```python
from nq_reconciliation import (
    OrderReconciliationModule,
    PositionReconciliationModule,
    PnLReconciliationModule,
)

order_mod = OrderReconciliationModule()
summary = order_mod.run("binance", internal_orders=[...], venue_orders=[...])
```
