# NEBULA-QUANT v1 | nq_db config

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(slots=True)
class DatabaseConfig:
    """Configuration for nq_db persistence layer."""

    db_path: str


def default_db_path() -> str:
    """Default path for the SQLite database file (relative to repo root)."""
    root = Path(os.getenv("NQ_DB_ROOT", Path.cwd()))
    return str(root / "nq_db.sqlite3")


DEFAULT_DB_CONFIG = DatabaseConfig(db_path=os.getenv("NQ_DB_PATH", default_db_path()))
