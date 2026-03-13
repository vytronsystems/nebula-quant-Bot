# Phase 64 — TradeStation Options Adapter Foundation — Result

## Objective
Create first-class TradeStation support.

## Completed tasks

1. **Adapter package** — `services/bot/adapters/tradestation/`: models, option selection, README, tests.
2. **Models** — TSAccountSummary, TSPosition, TSOptionContract (with .dte()), TSOptionSelectionRequest, TSOptionSelectionResult.
3. **Long call / long put only** — TradeStationOptionSelector filters by direction (Call/Put); invalid direction returns empty selection.
4. **Dynamic DTE selection** — request.dte_policy_min, dte_policy_max; supports 0DTE/1DTE when in range.
5. **Contract filter inputs** — liquidity_min, max_spread_bps, max_risk_per_contract, capital_allocated, momentum_filter on request; recorded in filter_used (logic extendable later).
6. **Tests and README** — 3 tests (dte, long call only, invalid direction); README documents scope and integration.
