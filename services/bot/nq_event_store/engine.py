# NEBULA-QUANT v1 | nq_event_store engine

from __future__ import annotations

from nq_db.engine import DatabaseEngine
from nq_event_store.config import DEFAULT_EVENT_STORE_CONFIG
from nq_event_store.schema import apply_schema


class EventStoreError(Exception):
    """Base error for nq_event_store failures (schema, insert, validation)."""


class EventStoreEngine:
    """Manages DB access for the event store. Uses nq_db engine and applies event store schema."""

    def __init__(self, db_path: str | None = None) -> None:
        path = db_path or DEFAULT_EVENT_STORE_CONFIG.db_path
        self._engine = DatabaseEngine(db_path=path)
        apply_schema(self._engine)
        self._engine.commit()

    @property
    def engine(self) -> DatabaseEngine:
        """Underlying nq_db engine for repository use."""
        return self._engine

    def close(self) -> None:
        self._engine.close()
