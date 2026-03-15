NEBULA-QUANT v1 | Phase 77 — Strategy Degradation Engine

Objective:
Detect loss of statistical edge.

Monitor:
- rolling winrate
- rolling pnl
- drawdown
- profit factor

If thresholds violated:
state → degraded
trading_enabled → false

Emit alerts.