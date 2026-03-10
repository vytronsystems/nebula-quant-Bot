# nq_paper — Paper Trading (Skeleton)

## Purpose

`nq_paper` provides the architectural foundation for paper trading simulation in NEBULA-QUANT: paper positions, paper trades, and session results that can be tracked and audited. It is **paper trading infrastructure only**: no broker connection, no real orders, no live execution.

## Role in the Pipeline

The pipeline is:

```
nq_data → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_exec
```

- **nq_paper** sits after walk-forward validation. Strategies that pass backtest and walk-forward run in paper mode with simulated fills and positions. Results feed weekly audit and promotion decisions toward live trading.
- A strategy is not promoted to live unless paper trading confirms the edge under weekly audit (see Weekly Audit Standard and Research Framework).

## Why Paper Trading Before Live Trading

Paper trading validates behavior and performance with real-time (or replay) data and simulated execution, without capital at risk. It exposes operational issues, slippage assumptions, and edge decay before going live. Requiring a successful paper phase and weekly audit reduces the risk of deploying fragile or untested strategies.

## Why Paper Trading Is Weekly Audited

Paper sessions are reviewed weekly (see docs/14_WEEKLY_AUDIT_STANDARD.md). The audit covers entries, exits, TP/SL, RR, slippage, winning/losing setups, and edge decay. Findings drive adjustments, strategy pauses, or new hypotheses. No strategy moves to live on intuition alone; promotion requires documented audit and re-validation.

## Why a Skeleton

- **Clean foundation**: Fixed public API (`PaperEngine`, `PaperTrade`, `PaperPosition`, `PaperAccountState`, `PaperSessionResult`) and ledger/reporter hooks so that real signal processing, fills, and persistence can be added in later iterations.
- **No broker logic**: No real orders, no external APIs, no nq_exec coupling. Full implementation will integrate with data feed and risk in a future iteration.
