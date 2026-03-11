# NEBULA-QUANT v1 | nq_db schema

from __future__ import annotations

from typing import Protocol


class _ExecConnection(Protocol):
    def execute(self, sql: str, params: tuple | None = None) -> object: ...


SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS strategies (
        strategy_id TEXT PRIMARY KEY,
        lifecycle_state TEXT NOT NULL,
        enabled INTEGER NOT NULL,
        created_at REAL NOT NULL,
        updated_at REAL NOT NULL,
        metadata TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS executions (
        execution_id TEXT PRIMARY KEY,
        strategy_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        status TEXT NOT NULL,
        timestamp REAL NOT NULL,
        metadata TEXT,
        FOREIGN KEY (strategy_id) REFERENCES strategies(strategy_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS observability_snapshots (
        snapshot_id TEXT PRIMARY KEY,
        generated_at REAL NOT NULL,
        system_summary TEXT NOT NULL,
        metadata TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS experiments (
        experiment_id TEXT PRIMARY KEY,
        strategy_id TEXT NOT NULL,
        start_time REAL NOT NULL,
        end_time REAL NOT NULL,
        result_status TEXT NOT NULL,
        metrics TEXT NOT NULL,
        metadata TEXT,
        FOREIGN KEY (strategy_id) REFERENCES strategies(strategy_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS decisions (
        decision_id TEXT PRIMARY KEY,
        module_name TEXT NOT NULL,
        decision_type TEXT NOT NULL,
        strategy_id TEXT NOT NULL,
        timestamp REAL NOT NULL,
        reason_codes TEXT NOT NULL,
        metadata TEXT
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_executions_strategy_ts ON executions (strategy_id, timestamp)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_decisions_strategy_ts ON decisions (strategy_id, timestamp)
    """,
)


def apply_schema(conn: _ExecConnection) -> None:
    """Apply all schema statements using the given connection. Fail-fast on SQL errors."""
    for stmt in SCHEMA_STATEMENTS:
        conn.execute(stmt)
