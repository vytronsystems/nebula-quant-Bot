# Phase 90 — BTCUSDT Paper Trading Validation

## How BTCUSDT Was Registered

BTCUSDT was not present at validation start. It was created via the control-plane API:

```bash
curl -X POST http://localhost:8081/api/instruments \
  -H "Content-Type: application/json" \
  -d '{"venue":"Binance","symbol":"BTCUSDT","assetType":"futures","active":true}'
```

- **Venue**: Binance (Futures)
- **Asset type**: futures
- **Status**: Active

## Deployment Created

- **ID**: `3ae0121f-3c5e-4409-a9e0-d4d8baa0c138`
- **Strategy**: validation v1.0
- **Stage**: paper
- **Environment**: testnet
- **Meta**: `paper_run_days: 15`, `lifecycle_state: paper`

## Binance Futures Testnet Connectivity

- **Health**: `GET /api/binance/health` returns `status: NOT_CONFIGURED` when `BINANCE_API_KEY` or `BINANCE_API_SECRET` are missing.
- **To enable**: Set env vars on the binance-api service: `BINANCE_TESTNET=true`, `BINANCE_API_KEY`, `BINANCE_API_SECRET`.
- **Endpoints**: /account, /market, /orderbook, /trades, /orders, /positions — all proxy through control-plane to binance-api.

## 15-Day Paper Run / Automatic Paper Runner

- Deployment meta includes `paper_run_days: 15`.
- **Automatic execution**: The bot runs a **paper runner** every N heartbeats (default: every 6 heartbeats ≈ 60s when HEARTBEAT_SECONDS=10). It:
  - Loads deployments with `stage=paper` and `enabled=true`
  - Ensures the instrument is active in the instrument registry
  - For venue Binance: fetches klines from Binance Testnet (requires `BINANCE_API_KEY`/`BINANCE_API_SECRET` in binance-api or bot env), runs a minimal paper session, and persists trades to the `trades` table
  - Triggers the strategy metrics job so `/api/metrics` and recommendations update
- Tune via env: `PAPER_RUNNER_INTERVAL_HEARTBEATS` (0 = disabled). Data accumulates in `trades` and `paper_trading_daily_snapshot` over the 15-day window.

## Metrics

- **Control-plane**: `GET /api/metrics`, `GET /api/metrics/by-deployment/{deploymentId}`
- **Compute**: `strategy_metrics_job` (nq_metrics) reads trades and writes `strategy_metrics`
- **Current**: Empty until trades exist; recommendations show `requires_more_data`

## UI

- Operator → Instruments: shows BTCUSDT
- Operator → Promotion Queue: shows deployment with `requires_more_data`
- Executive Dashboard: links to deployments, metrics, positions, instruments
