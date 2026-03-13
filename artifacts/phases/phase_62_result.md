# Phase 62 — Binance Account Sync and Venue State Persistence — Result

## Objective
Extend Binance from foundation/simulation toward real account-state integration boundaries.

## Completed tasks

1. **Account snapshot persistence**
   - `venue_account_snapshot` table (from 003) used to store venue, account_id, balance, equity, meta per snapshot.

2. **Wire account normalization into persistent snapshots**
   - `BinanceAccountSyncService.save_snapshot_from_payload(venue, account_id, payload)` normalizes via `BinanceAccountAdapter.normalize_account_state`, derives balance/equity (USDT balance + unrealized PnL), and inserts into `venue_account_snapshot`.

3. **Define transport boundary and integration points**
   - Documented in `account_sync.py`: this layer accepts raw payload only; it does not perform REST calls. A future fetcher (REST client) will call `save_snapshot_from_payload` after obtaining payload from Binance /fapi/v2/account when live-ready.

4. **Service layer for venue account reading and state history**
   - `BinanceAccountSyncService`: `save_snapshot_from_payload`, `save_snapshot_from_state`, `get_latest_snapshot(venue)`, `get_snapshot_history(venue, limit)`.

5. **No unsafe live routing shortcuts**
   - No live HTTP; no API keys; payload-in only.

## Code

- `services/bot/adapters/binance/account_sync.py` (new)
- `services/bot/adapters/binance/tests/test_account_sync.py` (new)
