# nq_backtest — Backtesting Module (Skeleton)

## Purpose

`nq_backtest` provides the architectural foundation for reproducible backtesting in NEBULA-QUANT. It is **research infrastructure only**: no execution logic, no broker integration, no live trading.

## Role in the Trading Pipeline

The pipeline is:

```
nq_data → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_exec
```

- **nq_backtest** sits in the validation layer: strategies and risk decisions are tested on historical data here before any paper or live step.
- Results feed walk-forward validation, paper trading audits, and reporting (PDF, dashboards).
- A strategy is not promoted to paper or live unless backtesting (and later walk-forward) confirms statistical edge (see Research Framework and Backtesting Standard).

## Why a Skeleton?

- **Clean foundation**: Fixed public API (`BacktestEngine`, `BacktestConfig`, `BacktestResult`, etc.) and data models so that future work (real data loading, strategy/risk wiring, metrics, reporting) can be added without breaking callers.
- **No premature logic**: Simulation, cost models, and metrics are placeholders with safe defaults. Full implementation will follow in later iterations, aligned with the Backtesting Standard (no look-ahead, costs/slippage, train/test split, minimal metrics).
- **Governance**: The module is designed to remain compatible with the institutional promotion rule: Research → Backtesting → Walk-Forward → Paper (weekly audited) → Live.
