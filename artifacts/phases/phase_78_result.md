# Phase 78 — Capital Allocation Engine — Result

## Summary

Dynamic capital allocation across strategies from momentum, pnl stability, drawdown, volatility.

## Implementation

- **Bot**: `nq_capital_allocation` — CapitalAllocationEngine.allocate(inputs) returns list of AllocationResult (weight, risk_pct). _score() uses momentum, pnl_stability, drawdown, volatility.

## Modules Affected

- services/bot/nq_capital_allocation/
