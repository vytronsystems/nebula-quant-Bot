# Instruments Control — UI Data Contract

For the Instruments Control screen (Operator Cockpit): list Binance pairs and TradeStation underlyings, show activation state, and support add/activate/deactivate.

## Data shape (for UI)

### Instrument row (table/list)

| Field       | Type    | Description                                  |
|------------|---------|----------------------------------------------|
| venue      | string  | `binance` \| `tradestation`                   |
| symbol     | string  | Pair or underlying symbol                    |
| asset_type | string  | `spot` \| `option`                           |
| active     | boolean | Currently active for trading/paper           |
| created_at | string  | ISO 8601 (display only)                       |
| updated_at | string  | ISO 8601 (display only)                      |

### Eligibility / operational state (future)

- `paper_eligible`, `live_eligible`, `current_operational_state` can be added when promotion/venue readiness is wired; for Phase 61 the UI can show `active` only.

## Actions

- Add instrument (venue + symbol; asset_type optional).
- Activate / Deactivate (toggle `active`).
- Filter by venue; filter by active/all.

## API source

Data is loaded from control plane `GET /api/instruments` (see `docs/contracts/instrument_registry_api.md`). Until the control plane exists, the frontend can use a mock that returns `[]` or fixture data tagged as non-production.
