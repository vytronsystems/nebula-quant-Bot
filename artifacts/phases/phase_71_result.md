# Phase 71 — Binance Testnet Integration — Audit & Result

## Step 1 — Audit: Current Binance Support

### Current adapters/modules (services/bot/adapters/binance/)
- **config.py**: `BinanceFuturesConfig` with hardcoded **live** URLs (`https://fapi.binance.com`, `wss://fstream.binance.com`). No testnet switch, no API key/secret.
- **account.py**: `BinanceAccountAdapter` — normalizes account payload to `BinanceAccountState` (no HTTP).
- **account_sync.py**: Persists normalized state to `venue_account_snapshot` (DB). No live fetch.
- **market_data.py**: Normalizers only (`normalize_kline`, `normalize_ticker`, `normalize_order_book`). No HTTP client.
- **mapper.py**: Maps internal ↔ Binance payloads. No network.
- **models.py**: DTOs (BinanceBalance, BinancePosition, BinanceAccountState, BinanceTicker, BinanceOrderBookSnapshot, etc.).
- **execution.py**: `BinanceExecutionAdapter` — submit_order is **simulated** (returns stub). No real REST order submission.
- **validation.py**: Payload validation. No credentials.
- **activation.py**, **safeguards.py**, **paper.py**: Paper/shadow and safeguards. No testnet.

### Current config/env keys
- **None** for Binance API. No `BINANCE_API_KEY`, `BINANCE_API_SECRET`, or testnet base URLs in repo.
- Bot uses `PG_DSN`, `REDIS_HOST`, `NQ_*` only.

### What already works
- Normalization of account, ticker, order book, klines from **payloads** (caller-supplied).
- Persistence of account snapshot to DB (venue_account_snapshot).
- Paper/simulation and safeguards; activation engine; no live routing.

### What is missing for Testnet
1. **Config**: Env-based `BINANCE_API_KEY`, `BINANCE_API_SECRET`, `BINANCE_TESTNET`, `BINANCE_FUTURES_TESTNET_BASE_URL`, `BINANCE_FUTURES_TESTNET_WS_URL`.
2. **HTTP client**: No code that performs GET/POST to Binance (testnet or live). Need signed (HMAC) and public endpoints.
3. **Account fetch**: GET /fapi/v2/account (signed).
4. **Market fetch**: GET /fapi/v1/ticker/price, /fapi/v1/depth, /fapi/v1/trades (public/signed as per Binance).
5. **Open orders**: GET /fapi/v1/openOrders (signed).
6. **Open positions**: GET /fapi/v2/positionRisk (signed).
7. **Backend API**: No endpoints today that serve this to the UI. Control plane has /api/instruments only; no /api/binance/*.
8. **Degraded mode**: No explicit NOT_CONFIGURED/DEGRADED when credentials missing or connection fails.
9. **Tests**: No Testnet connectivity or degraded-mode tests.

---

## Steps 2–5 (implementation summary)

- **Step 2**: Testnet config module and env keys; venue status NOT_CONFIGURED when credentials missing.
- **Step 3**: Binance Testnet REST client (account, ticker, depth, trades, open orders, positions); normalize with existing adapters.
- **Step 4**: Backend endpoints (Python FastAPI or control plane proxy) for venue overview, account, market, order book, orders, positions, health.
- **Step 5**: Fail-closed and degraded: no crash on missing/invalid creds; clear health/error state; no order path unless valid.

Details in phase_71_audit_report.html and docs/BINANCE_TESTNET_INTEGRATION.md.
