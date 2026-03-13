# Instrument Registry — API Contract (Control Plane)

Used by the Spring Boot control plane (Phase 66) and by the Instruments Control UI (Phase 67+). The Python core in `nq_instrument_registry` implements the persistence layer; the control plane exposes REST APIs that delegate to Python or replicate this contract.

## DTOs (typed)

### InstrumentRecord (response)

| Field       | Type   | Description                          |
|------------|--------|--------------------------------------|
| venue      | string | e.g. `binance`, `tradestation`       |
| symbol     | string | e.g. `BTCUSDT`, `SPY`                |
| asset_type | string | `spot`, `option`, etc.               |
| active     | boolean| Whether the instrument is active     |
| created_at | string | ISO 8601 datetime                    |
| updated_at | string | ISO 8601 datetime                    |
| meta       | object | Optional metadata                    |

### ActivationLogEntry (response)

| Field     | Type   | Description        |
|----------|--------|--------------------|
| venue    | string | Venue id            |
| symbol   | string | Symbol              |
| action   | string | `add`, `activate`, `deactivate` |
| created_at | string | ISO 8601 datetime |
| meta     | object | Optional            |

### AddInstrumentRequest (body)

| Field      | Type   | Required | Description   |
|-----------|--------|----------|---------------|
| venue     | string | yes      | Venue id       |
| symbol    | string | yes      | Symbol         |
| asset_type| string | no       | Default `spot` |
| active    | boolean| no       | Default `true` |

### SetActiveRequest (body)

| Field  | Type    | Required |
|--------|---------|----------|
| active | boolean | yes      |

## Endpoints (REST, to be implemented in control plane)

- `GET /api/instruments?venue={venue}&active_only={bool}` — list instruments (list of InstrumentRecord).
- `GET /api/instruments/{venue}/{symbol}` — get one (InstrumentRecord or 404).
- `POST /api/instruments` — add or upsert (AddInstrumentRequest → InstrumentRecord).
- `PATCH /api/instruments/{venue}/{symbol}/active` — set active (SetActiveRequest → InstrumentRecord).
- `GET /api/instruments/activation-log?venue=&symbol=&limit=` — list activation log (list of ActivationLogEntry).

All timestamps in UTC, ISO 8601.
