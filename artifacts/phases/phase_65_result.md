# Phase 65 — Cross-Venue Services — Result

## Objective
Create venue abstraction and separated-capital views.

## Completed tasks

1. **Venue abstraction service** — `VenueAbstractionService.list_venues()` returns VenueSummary list (binance, tradestation).
2. **Venue account summary service** — `VenueAccountSummaryService.get_latest_per_venue()` reads latest snapshot per venue from `venue_account_snapshot`; `build_dashboard_contract()` returns `DashboardAggregationContract`.
3. **Separated capital tracking** — `SeparatedCapitalView` per venue; populated in dashboard contract from snapshots.
4. **Controlled risk movement hooks** — `risk_movement_hook(RiskMovementRequest)` returns rejected by default (policy to be wired in control plane/Drools).
5. **Dashboard aggregation contracts** — `DashboardAggregationContract`: venues, account_summaries, separated_capital, total_equity.

## Code

- `services/bot/nq_cross_venue/` (models, venue_service, account_summary_service, risk_movement, tests).
