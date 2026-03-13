# Phase 61 — Instrument Registry and Activation Control — Result

## Objective
Create the persistent registry for Binance pairs and TradeStation underlyings.

## Completed tasks

1. **DB models for instrument registry**
   - Tables `instrument_registry` and `instrument_activation_log` already present (003_evidence_backbone). No new migration.

2. **Activation/deactivation logs**
   - `InstrumentRegistryService.set_active(venue, symbol, active)` updates registry and appends to `instrument_activation_log`. `list_activation_log(venue, symbol, limit)` for audit trail.

3. **Python/core services for instrument registry queries**
   - New package `services/bot/nq_instrument_registry`: `InstrumentRegistryService` with `list_instruments`, `get_instrument`, `add_instrument`, `set_active`, `list_activation_log`. DTOs: `InstrumentRecord`, `ActivationLogEntry` with `to_api()` for control plane/UI.

4. **Control-plane APIs for CRUD/activation**
   - API contract documented in `docs/contracts/instrument_registry_api.md`: DTOs and REST endpoints (GET/POST/PATCH) for list, get, add, set-active, activation-log. To be implemented in Spring Boot (Phase 66).

5. **UI data contracts for instrument control screen**
   - Documented in `docs/contracts/instrument_control_ui.md`: data shape and actions for Instruments Control screen.

## Required outputs

- Python service and tests: `nq_instrument_registry` with 3 tests (2 pass, 1 skipped when psycopg absent).
- API and UI contracts: written under `docs/contracts/`.
