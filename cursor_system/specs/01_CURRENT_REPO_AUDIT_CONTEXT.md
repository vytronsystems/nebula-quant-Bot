# Current Repo Audit Context

## What already exists and must be preserved
- Python-based quant core in `services/bot/`.
- Broad set of `nq_*` modules with tests and READMEs.
- Docker local stack with Postgres, Redis, Grafana, Prometheus, Alertmanager.
- Documentation-heavy repo with prior phases and system governance.
- Binance adapter foundation in `services/bot/adapters/binance/`.

## What the audit concluded
- 615 tests pass when root pathing is configured correctly.
- 3 packaging-related failures remain around importing `scripts` in tests.
- No frontend exists.
- No TradeStation adapter exists.
- No dedicated reconciliation layer exists.
- No cross-venue layer exists.
- Security hygiene must be corrected immediately.

## Required philosophy
Enhance, harden, and extend the current codebase.
Do not destabilize the current engine modules.
