# Phase 90 — Functional System Validation: Binance Futures Testnet — Result

## Summary

Full functional validation of NEBULA-QUANT using Binance Futures Testnet with the registered instrument BTCUSDT.

## A. Instrument Validation

- **BTCUSDT was not present** in the instrument registry at validation start.
- **Created** via `POST /api/instruments`:
  - Venue: Binance
  - Instrument: BTCUSDT
  - Asset type: futures
  - Status: Active
- **Confirmed** in instrument management layer; available for strategy deployment.

## B. Strategy Deployment for Paper

- **Created** paper deployment via `POST /api/deployments`:
  - Deployment ID: `3ae0121f-3c5e-4409-a9e0-d4d8baa0c138`
  - venue: Binance
  - instrument: BTCUSDT
  - environment: testnet
  - stage: paper
  - lifecycle_state (in meta): paper
  - trading_enabled (enabled): true
  - meta.paper_run_days: 15
- Uses strategy `validation` v1.0 (minimal validation placeholder).

## C. Binance Futures Testnet Connectivity

- **Status**: NOT_CONFIGURED
- **Reason**: `BINANCE_API_KEY` or `BINANCE_API_SECRET` missing (no credentials set in environment).
- **Behavior validated**:
  - Endpoints return clear degraded status: `{"status":"NOT_CONFIGURED","message":"BINANCE_API_KEY or BINANCE_API_SECRET missing",...}`
  - No crash; fail-closed design respected.
- **What would be validated with credentials**:
  - Account connection status, wallet/available balance
  - BTCUSDT current price, order book, recent trades
  - Open orders, open positions, venue health

## D. API + UI Data Flow Validation

### Endpoints validated (200 OK)

| Endpoint | Status |
|----------|--------|
| GET /api/instruments | 200 |
| GET /api/deployments | 200 |
| GET /api/dashboard | 200 |
| GET /api/metrics | 200 |
| GET /api/recommendations | 200 |
| GET /api/alerts | 200 |
| GET /api/binance/health | 200 |
| GET /api/binance/account | 200 |
| GET /api/binance/market | 200 |
| GET /api/binance/orderbook | 200 |
| GET /api/binance/trades | 200 |
| GET /api/binance/orders | 200 |
| GET /api/binance/positions | 200 |

### UI routes validated (200 OK)

| Route | Status |
|-------|--------|
| /operator | 200 |
| /operator/instruments | 200 |
| /executive | 200 |
| /operator/promotion-queue | 200 |

BTCUSDT appears in Operator → Instruments and is available for promotion/deployment views.

## E. Paper Trading Run

- **15-day paper run configured** in deployment meta: `paper_run_days: 15`.
- **Architecture**: Paper execution is triggered by workflows (e.g. research pipeline), not a standalone continuous daemon. The bot main loop performs heartbeats and decision snapshots; paper sessions run when the research pipeline or scheduler invokes `PaperEngine` / adapter paper engine.
- **What was done**:
  1. Deployment registered with stage=paper, enabled=true, meta.paper_run_days=15.
  2. Scheduler/runner: `nq_scheduler/engine.py` and `nq_paper/engine.py` are in place; paper is workflow-triggered.
  3. Persistence: `paper_trading_daily_snapshot`, `trades`, and related tables exist for recording.
- **How the 15-day run continues**:
  - Configure the research pipeline or a scheduled job to invoke paper sessions for the validation deployment.
  - Data accumulates in `trades` and `paper_trading_daily_snapshot` as sessions run.
  - Metrics are computed by `strategy_metrics_job` when trades exist.

## F. Metrics Validation

- **Pipeline**: `strategy_metrics_job.compute_and_persist_strategy_metrics()` reads `strategy_deployment`, loads trades per instrument, computes via `MetricsEngine`, upserts into `strategy_metrics`.
- **Metrics exposed**: control-plane `GET /api/metrics`, `GET /api/metrics/by-deployment/{id}`.
- **Current availability**: Empty (no trades yet for validation deployment).
- **Pending accumulation**: WinRate, PnL (absolute/%), trade count, days observed, drawdown, profit factor — will populate as trades are generated.
- **Recommendation pipeline**: `GET /api/recommendations` returns `requires_more_data` for the BTCUSDT deployment (correct: no metrics yet).

## G. Recommendation Readiness

- Recommendation states supported: Ready for Live, Requires More Data, Keep in Paper, Degraded, Rejected.
- Current state for BTCUSDT paper deployment: `requires_more_data` (reason: no_metrics).
- No live recommendation forced.

## H. Reconciliation + Risk Validation

- Risk engine (`nq_risk/engine.py`), reconciliation (`nq_reconciliation/runner.py`) exist; paper path respects routing safety and fail-closed behavior.
- No structural changes required.

## I. Fixes Automatically Applied

1. **DB migrations 004, 005, 006**: `strategy_deployment` and `strategy_metrics` tables did not exist. Ran `docker/scripts/nq-db-migrate.sh` to apply migrations 004–006.
2. **Deployments API 500**: Resolved by creating missing `strategy_deployment` table via migration.

## Remaining Time-Based Dependencies

- Binance Testnet live data: requires `BINANCE_API_KEY` and `BINANCE_API_SECRET` in binance-api service env.
- Metrics: require trade data from paper sessions; `strategy_metrics_job` must run periodically.
- 15-day paper run: requires workflow/scheduler to invoke paper sessions over the period.
