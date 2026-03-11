# nq_event_store

Append-only event persistence layer for NEBULA-QUANT v1. Records normalized system events deterministically for audit and replay; does not implement business logic, metrics, or execution.

## Purpose

- **Record** important system events (strategy, risk, guardrail, portfolio, promotion, execution, observability, experiment, system) in a single, ordered log.
- **Support** retrieval by `event_id`, `aggregate_id`, `event_type`, `aggregate_type`, and global sequence.
- **Support** replay-friendly reading (e.g. `fetch_all`, `fetch_after_sequence`) with deterministic order.
- **Preserve** auditability via immutable, append-only storage.

## Append-only design

- Events are **inserted** only; there are no `update_event` or `delete_event` APIs.
- The store never mutates or silently deletes existing events.
- Duplicate `event_id` is rejected (fail closed).

## Event ordering / replay

- Each event gets a **sequence_id** (integer, auto-increment) as the primary key.
- All read APIs that return lists use **ORDER BY sequence_id ASC** unless documented otherwise (e.g. `fetch_recent` returns newest first but still deterministic).
- Replay order is deterministic: process events in `sequence_id` order (e.g. `fetch_all()` or `fetch_after_sequence(last_seen)`).

## Relationship with nq_db

- **nq_db** is the shared persistence foundation (strategies, executions, decisions, experiments, observability snapshots).
- **nq_event_store** reuses **nq_db**’s `DatabaseEngine` and applies its own schema (single `events` table + indexes) so the same SQLite file can host both when using the same path.
- Event store does not replace nq_db repositories; it complements them with an append-only event log for decisions and key system events. Integration with nq_risk, nq_guardrails, nq_exec, etc. will be added in later phases.

## Intended future integration points

- **nq_risk**: record `risk_decision` events after decisions.
- **nq_guardrails**: record `guardrail_decision` events.
- **nq_exec**: record `execution_event` when orders/executions occur.
- **nq_portfolio** / **nq_promotion**: record `portfolio_decision` and `promotion_decision` events.
- **nq_metrics** / **nq_obs**: optionally record `observability_event` or rely on existing nq_obs/nq_metrics; event store remains optional for audit.
- **nq_experiments**: record `experiment_event` for experiment lifecycle.

No deep wiring into these modules is done in this phase; the store is ready for callers to append events when integration is implemented.

## Usage example

```python
from nq_event_store import (
    EventStoreEngine,
    EventStoreRepository,
    EventRecord,
    EVENT_TYPE_RISK_DECISION,
)

engine = EventStoreEngine(db_path="/path/to/nq_db.sqlite3")
repo = EventStoreRepository(engine.engine)

record = EventRecord(
    event_id="ev-uuid-1",
    event_type=EVENT_TYPE_RISK_DECISION,
    aggregate_type="risk",
    aggregate_id="strategy-1",
    timestamp="2025-03-11T12:00:00Z",
    payload={"action": "allow", "reason_codes": ["OK"]},
    metadata={"trace_id": "tr-1"},
)
with engine.engine.transaction():
    appended = repo.append_event(record)

# Replay in order
for ev in repo.fetch_all(limit=1000):
    process(ev)
```

## Configuration

- `NQ_EVENT_STORE_PATH`: SQLite path for the event store (defaults to same as `NQ_DB_PATH` when set).
- `NQ_DB_PATH` / `NQ_DB_ROOT`: used as fallback for the DB path (see `config.py`).
- **nq_config integration**: `engine_from_config(app_config.event_store)` builds the engine from `AppConfig` (requires `event_store.db_path` set; use shared DB or env).

## Fail-closed behavior

Invalid inputs or storage failures raise `EventStoreError`; the store does not silently skip or fabricate events. Duplicate `event_id`, malformed payload (non-dict or non-JSON-serializable), and missing required fields all result in exceptions.
