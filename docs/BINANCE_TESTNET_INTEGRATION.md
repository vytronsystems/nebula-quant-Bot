# Binance Testnet Integration

This document describes how to configure and verify the Binance Futures **Testnet** integration. **Live Binance is never used** unless you explicitly change code and config (not recommended).

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BINANCE_TESTNET` | Yes | Must be `true`, `1`, or `yes` (case-insensitive). If not set or false, the client will not connect and APIs return `NOT_CONFIGURED`. |
| `BINANCE_API_KEY` | Yes | Testnet API key from [Binance Futures Testnet](https://testnet.binancefuture.com). |
| `BINANCE_API_SECRET` | Yes | Testnet API secret. |
| `BINANCE_FUTURES_TESTNET_BASE_URL` | No | Default: `https://testnet.binancefuture.com`. Override only if using a custom testnet endpoint. |
| `BINANCE_FUTURES_TESTNET_WS_URL` | No | Default: `wss://stream.binancefuture.com`. Override for custom WebSocket testnet. |

For Docker Compose, set in `.env` or export before `docker compose up`:

```bash
export BINANCE_TESTNET=true
export BINANCE_API_KEY=your_testnet_key
export BINANCE_API_SECRET=your_testnet_secret
```

## Services

- **Binance API (Python)** — FastAPI on port **8082**. Endpoints: `/health`, `/venue-overview`, `/account`, `/market`, `/orderbook`, `/trades`, `/orders`, `/positions`. Reads from Binance Futures Testnet only when `BINANCE_TESTNET=true` and credentials are set.
- **Control plane** — Proxies Binance requests at `/api/binance/*` to the Binance API service. Configure `BINANCE_API_URL` (default in Docker: `http://binance-api:8082`).

## Verifying

1. **Without credentials**  
   Leave `BINANCE_TESTNET` unset or set `BINANCE_API_KEY`/`BINANCE_API_SECRET` empty.  
   - `GET http://localhost:8082/health` or `GET http://localhost:8081/api/binance/health` should return `status: "NOT_CONFIGURED"` and a message (e.g. missing env).

2. **With testnet credentials**  
   Set `BINANCE_TESTNET=true` and valid testnet API key/secret.  
   - `GET http://localhost:8082/venue-overview` (or via control plane `/api/binance/venue-overview`) should return `status: "CONNECTED"` when the testnet is reachable.  
   - Use `/account`, `/market`, `/orders`, `/positions` to confirm data.

3. **Unit tests**  
   From repo root:
   ```bash
   PYTHONPATH=services/bot python3 -m pytest services/bot/adapters/binance/tests/test_testnet.py -v
   ```
   Or: `make test` (includes bot tests).

## Fail-closed and degraded behaviour

- If `BINANCE_TESTNET` is not `true`, the client refuses to run (raises); APIs return `NOT_CONFIGURED`.
- If API key or secret is missing, same behaviour.
- If the testnet is unreachable or returns 4xx/5xx, the API returns `status: "ERROR"` or `"DEGRADED"` with a message; no crash.
- Control plane proxy returns **502** with a JSON body when the Binance API service is down or unreachable.

## Security

- Do **not** put live Binance keys in `.env` or any tracked file. Use testnet keys for development only.
- Secrets are read from the environment only; they are not hardcoded.
