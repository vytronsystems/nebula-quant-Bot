# nq_walkforward — Walk-Forward Validation (Skeleton)

## Purpose

`nq_walkforward` provides the architectural foundation for walk-forward validation in NEBULA-QUANT. It is **research infrastructure only**: no execution logic, no broker integration, no live trading. It validates that a strategy holds up across time (train/test splits) before paper or live.

## Role in the Validation Pipeline

The pipeline is:

```
nq_data → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_exec
```

- **nq_walkforward** sits after backtesting: each window has a train period and a test (out-of-sample) period. Results (pass/fail per window, pass rate) feed strategy approval gates, research reviews, and dashboards.
- A strategy is not promoted to paper trading unless backtesting **and** walk-forward confirm temporal robustness (see Research Framework and Backtesting Standard).

## Why a Skeleton?

- **Clean foundation**: Fixed public API (`WalkForwardEngine`, `WalkForwardConfig`, `WalkForwardResult`, etc.) and data models so that real window splitting, train/test backtest runs, and pass criteria can be added in later iterations without breaking callers.
- **No premature logic**: Window execution is placeholder; no real optimization or out-of-sample runs yet. Full implementation will follow, aligned with the Backtesting Standard (no look-ahead, clear train/test separation).
- **Governance**: The module is designed to remain compatible with the institutional promotion rule: Research → Backtesting → Walk-Forward → Paper (weekly audited) → Live.

## Why Walk-Forward Before Paper Trading?

Walk-forward checks that the strategy is not overfit to a single period: it must hold up on unseen time windows. Without it, a strategy can pass backtest on one span and fail in paper. Requiring walk-forward before paper reduces the risk of promoting fragile strategies and keeps the pipeline aligned with institutional standards.
