# NEBULA-QUANT v1 | nq_db — Persistence Foundation

`nq_db` provides a deterministic, SQLite-based persistence layer for NEBULA-QUANT v1. It does **not** contain trading logic; it only stores and retrieves structured data for strategies, executions, observability snapshots, experiments and governance decisions.

## Design

- **Engine**: `DatabaseEngine` wraps `sqlite3` and applies the base schema on initialization.
- **Config**: `DatabaseConfig` and `DEFAULT_DB_CONFIG` define the database path (default: `nq_db.sqlite3` in the repo root, overridable via `NQ_DB_PATH`).
- **Schema**: `schema.py` defines the initial tables for `strategies`, `executions`, `observability_snapshots`, `experiments` and `decisions`.
- **Repositories**: `StrategyRepository`, `ExecutionRepository`, `ObservabilityRepository`, `ExperimentRepository`, `DecisionRepository` provide small, explicit CRUD-style methods.

## Principles

- Deterministic behavior; no random side effects.
- Fail-closed: schema/SQL/JSON errors raise `DatabaseError` instead of being ignored.
- Thin abstraction: explicit SQL, no heavy ORM.
- Ready for future migration to Postgres or other engines by swapping the engine/config.

## Usage sketch

```python
from nq_db import DatabaseEngine, StrategyRecord, StrategyRepository
import time

engine = DatabaseEngine()  # uses DEFAULT_DB_CONFIG
repo = StrategyRepository(engine)

record = StrategyRecord(
    strategy_id="s1",
    lifecycle_state="paper",
    enabled=True,
    created_at=time.time(),
    updated_at=time.time(),
)

with engine.transaction():
    repo.insert(record)

loaded = repo.fetch_by_id("s1")
```
