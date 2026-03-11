# NEBULA-QUANT v1 | nq_event_store engine

from __future__ import annotations

from typing import Protocol

from nq_db.engine import DatabaseEngine
from nq_event_store.config import DEFAULT_EVENT_STORE_CONFIG
from nq_event_store.schema import apply_schema


class EventStorePathConfig(Protocol):
    """Protocol for config with db_path (e.g. nq_config.EventStoreConfig with db_path set)."""

    db_path: str | None


class EventStoreError(Exception):
    """Base error for nq_event_store failures (schema, insert, validation)."""


def engine_from_config(config: EventStorePathConfig) -> EventStoreEngine:
    """Build EventStoreEngine from a config with db_path (e.g. AppConfig.event_store from nq_config)."""
    path = getattr(config, "db_path", None)
    if path is None or not str(path).strip():
        raise EventStoreError("config.db_path must be set for event store (use shared DB or set NQ_EVENT_STORE_PATH)")
    return EventStoreEngine(db_path=path.strip())


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
