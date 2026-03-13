# TradeStation Options Adapter Foundation

First-class TradeStation support for NEBULA-QUANT: options-focused adapter foundation.

## Scope (initial release)

- **Long calls and long puts only** (no spreads, no short options in this phase).
- **Dynamic DTE selection**: policy-driven via `TSOptionSelectionRequest.dte_policy_min` and `dte_policy_max` (supports 0DTE/1DTE when justified).
- **Min contract size**: 1.

## Models

- `TSAccountSummary`: account id, equity, buying power, cash balance.
- `TSPosition`: symbol, asset type, quantity, average price, market value.
- `TSOptionContract`: symbol, underlying, expiry, strike, right (Call/Put), multiplier; `.dte(as_of)` for days to expiry.
- `TSOptionSelectionRequest`: underlying, direction (call/put), DTE policy, and optional contract filter inputs: liquidity, spread, risk, capital, momentum.
- `TSOptionSelectionResult`: selected contracts, DTE used, filter used.

## Option selection

`TradeStationOptionSelector.select(request, candidates)` filters candidates by:

- Direction (call or put only).
- DTE policy (min/max).
- Optional: liquidity_min, max_spread_bps, max_risk_per_contract, capital_allocated, momentum_filter (inputs; full filter logic can be extended later).

## Integration

- Market data normalization: use existing `nq_data` providers; TradeStation OHLCV stub exists.
- Account sync: similar pattern to Binance (venue_account_snapshot) when TS account API is wired.
- No live order routing in this phase.
