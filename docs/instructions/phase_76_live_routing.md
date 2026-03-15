NEBULA-QUANT v1 | Phase 76 — Live Routing

Objective:
Route orders depending on deployment state.

If stage = live:
- use production credentials

If stage != live:
- use testnet/paper routing

Ensure fail‑closed safety.