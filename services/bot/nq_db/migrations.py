# NEBULA-QUANT v1 | nq_db migrations (placeholder)

from __future__ import annotations

from typing import Protocol

from nq_db.schema import apply_schema


class _Conn(Protocol):
    def execute(self, sql: str, params: tuple | None = None) -> object: ...


def run_initial_migration(conn: _Conn) -> None:
    """Initial migration: apply base schema. Future migrations can build on this."""
    apply_schema(conn)
