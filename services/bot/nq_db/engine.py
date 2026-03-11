# NEBULA-QUANT v1 | nq_db engine (SQLite)

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any, Iterable, Protocol

from nq_db.config import DEFAULT_DB_CONFIG
from nq_db.schema import apply_schema


class DbPathConfig(Protocol):
    """Protocol for config with db_path (e.g. nq_config.DatabaseModuleConfig)."""

    db_path: str


class DatabaseError(Exception):
    """Base error for nq_db persistence failures."""


def engine_from_config(config: DbPathConfig) -> DatabaseEngine:
    """Build DatabaseEngine from a config with db_path (e.g. AppConfig.db from nq_config)."""
    path = getattr(config, "db_path", None)
    if path is None or not str(path).strip():
        raise DatabaseError("config.db_path must be non-empty")
    return DatabaseEngine(db_path=path.strip())


class DatabaseEngine:
    """Thin wrapper around sqlite3 for deterministic persistence.

    Uses a single connection per engine instance; schema is applied on initialization.
    """

    def __init__(self, db_path: str | None = None) -> None:
        path = db_path or DEFAULT_DB_CONFIG.db_path
        try:
            self._conn = sqlite3.connect(path, isolation_level="DEFERRED", check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            apply_schema(self._conn)
            self._conn.commit()
        except sqlite3.Error as exc:
            raise DatabaseError(f"failed to initialize database at {path!r}: {exc}") from exc

    def close(self) -> None:
        try:
            self._conn.close()
        except sqlite3.Error as exc:
            raise DatabaseError(f"failed to close database: {exc}") from exc

    def execute(self, sql: str, params: Iterable[Any] | None = None) -> sqlite3.Cursor:
        try:
            cur = self._conn.execute(sql, tuple(params or ()))
            return cur
        except sqlite3.Error as exc:
            raise DatabaseError(f"execute failed: {exc}") from exc

    def executemany(self, sql: str, seq_of_params: Iterable[Iterable[Any]]) -> sqlite3.Cursor:
        try:
            cur = self._conn.executemany(sql, [tuple(p) for p in seq_of_params])
            return cur
        except sqlite3.Error as exc:
            raise DatabaseError(f"executemany failed: {exc}") from exc

    def fetch_one(self, sql: str, params: Iterable[Any] | None = None) -> dict[str, Any] | None:
        cur = self.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row is not None else None

    def fetch_many(self, sql: str, params: Iterable[Any] | None = None) -> list[dict[str, Any]]:
        cur = self.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def commit(self) -> None:
        try:
            self._conn.commit()
        except sqlite3.Error as exc:
            raise DatabaseError(f"commit failed: {exc}") from exc

    def rollback(self) -> None:
        try:
            self._conn.rollback()
        except sqlite3.Error as exc:
            raise DatabaseError(f"rollback failed: {exc}") from exc

    @contextmanager
    def transaction(self) -> Any:
        """Context manager for a transaction; rolls back on error."""
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise
