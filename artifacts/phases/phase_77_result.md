# Phase 77 — Strategy Degradation Engine — Result

## Summary

Detect loss of statistical edge; set state to degraded, trading_enabled = false; emit alerts.

## Implementation

- **Bot**: `nq_degradation` — DegradationEngine.evaluate(rolling_win_rate, rolling_pnl, drawdown, profit_factor) returns DegradationResult (should_degrade, trading_enabled, signal, alerts_emitted). Thresholds: MIN_ROLLING_WIN_RATE, MAX_DRAWDOWN, MIN_PROFIT_FACTOR.

## Modules Affected

- services/bot/nq_degradation/
