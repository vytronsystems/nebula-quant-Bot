# Venue and Reconciliation Spec

## Binance
Extend existing Binance adapter foundation into real venue wiring plan with:
- account sync service
- market data service boundary
- position snapshot persistence
- order state snapshot persistence
- reconciliation hooks

## TradeStation
Create adapter foundation for:
- market data normalization
- account sync
- contract selection
- long calls and long puts only
- dynamic DTE selection (including 0DTE/1DTE when justified)
- min contract size = 1

## Reconciliation modules
Build dedicated layers for:
- order reconciliation
- position reconciliation
- PnL reconciliation

## Cross-venue
Build explicit abstraction for:
- venue account views
- venue capital separation
- cross-venue monitoring
- risk movement logic within approved limits
