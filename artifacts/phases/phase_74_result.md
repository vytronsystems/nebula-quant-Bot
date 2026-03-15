# Phase 74 — Metrics Engine — Result

## Summary

Automated performance metrics (WinRate, PnL, Trades, Days, Profit Factor, Max Drawdown) with persistence and API exposure for UI and recommendation engine.

## Implementation

- **Database**: Migration `005_strategy_metrics.sql` — table `strategy_metrics` with deployment_id (FK to strategy_deployment), computed_at, win_rate, pnl, trades_count, days_count, profit_factor, max_drawdown, meta. One row per deployment (upsert by deployment_id).

- **Control Plane**: 
  - **StrategyMetrics** JPA entity, **StrategyMetricsRepository** (findByDeploymentId)
  - **MetricsController**: GET `/api/metrics` (list all or filter by deploymentId), GET `/api/metrics/by-deployment/{deploymentId}`

- **Bot (nq_metrics)**:
  - **strategy_metrics_job.py**: `compute_and_persist_strategy_metrics()` — loads deployments and trades from Postgres, converts trades to TradePerformance, runs existing **MetricsEngine.compute_metrics()**, upserts strategy_metrics. Entry point `run_metrics_job()` for scheduling or on-demand.

- **Metrics computed**: WinRate, PnL, Trades, Days, Profit Factor, Max Drawdown (from existing MetricsEngine + equity/drawdown).

## Modules Affected

- `docker/db/migrations/005_strategy_metrics.sql`
- `services/control-plane/` — StrategyMetrics entity, repository, MetricsController
- `services/bot/nq_metrics/strategy_metrics_job.py`

## Services Created or Modified

- None (control plane and bot existing).

## UI Changes

- Promotion Queue (Phase 73) can consume GET /api/metrics to display WinRate, PnL, Trades, Days per deployment (meta fallback already in place).

## Infrastructure

- Run migration 005 before using. Schedule or call `nq_metrics.strategy_metrics_job.run_metrics_job()` to refresh metrics.
