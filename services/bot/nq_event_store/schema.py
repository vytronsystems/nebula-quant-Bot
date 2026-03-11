# NEBULA-QUANT v1 | nq_event_store schema (append-only events table)

from __future__ import annotations

from typing import Protocol


class _Executable(Protocol):
    def execute(self, sql: str, params: tuple | None = None) -> object: ...


EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,
    aggregate_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    payload TEXT NOT NULL,
    metadata TEXT NULL
)
"""

INDEX_AGGREGATE_ID = "CREATE INDEX IF NOT EXISTS idx_events_aggregate_id ON events (aggregate_id)"
INDEX_EVENT_TYPE = "CREATE INDEX IF NOT EXISTS idx_events_event_type ON events (event_type)"
INDEX_AGGREGATE_TYPE = "CREATE INDEX IF NOT EXISTS idx_events_aggregate_type ON events (aggregate_type)"
INDEX_TIMESTAMP = "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events (timestamp)"

SCHEMA_STATEMENTS: tuple[str, ...] = (
    EVENTS_TABLE,
    INDEX_AGGREGATE_ID,
    INDEX_EVENT_TYPE,
    INDEX_AGGREGATE_TYPE,
    INDEX_TIMESTAMP,
)


def apply_schema(conn_or_engine: _Executable) -> None:
    """Apply event store schema (events table + indexes). Fail-fast on SQL errors."""
    for stmt in SCHEMA_STATEMENTS:
        conn_or_engine.execute(stmt)
