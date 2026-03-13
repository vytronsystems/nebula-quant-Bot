# Non-Negotiables

- Preserve the existing Python quant core in `services/bot/`.
- No rewrite-from-zero behavior.
- Fail closed on validation, risk, venue state, and promotion logic.
- No hardcoded secrets in committed files.
- Every phase must leave evidence.
- Every test must be runnable from the repo root.
- Package/import behavior must work without fragile manual path tricks.
- No live-routing without explicit venue/account/reconciliation readiness.
- No frontend screen without real backend contract.
- No backend contract without typed DTO/schema definition.
- Operator and Executive modes are both mandatory.
- BTCUSDT first, but instrument registry must support more pairs and more underlyings.
- TradeStation must support long calls and long puts only in initial release.
- DTE is dynamic and policy-driven, not hardcoded.
