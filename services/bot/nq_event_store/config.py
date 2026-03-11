# NEBULA-QUANT v1 | nq_event_store config

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class EventStoreConfig:
    """Configuration for nq_event_store persistence."""

    db_path: str


def default_db_path() -> str:
    """Default path for the event store SQLite database (aligns with nq_db when shared)."""
    root = Path(os.getenv("NQ_DB_ROOT", Path.cwd()))
    return str(root / "nq_db.sqlite3")


DEFAULT_EVENT_STORE_CONFIG = EventStoreConfig(
    db_path=os.getenv("NQ_EVENT_STORE_PATH", os.getenv("NQ_DB_PATH", default_db_path()))
)
