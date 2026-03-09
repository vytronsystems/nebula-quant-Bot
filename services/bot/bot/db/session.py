"""
DEPRECATED / UNUSED: This module is outside the current runtime flow.

The bot uses psycopg direct with bot.config.PG_DSN. See docs/15_DB_ACCESS_STANDARD.md.
Do not import SessionLocal or engine in production code.
Kept for potential future Alembic or ORM migration only.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from configs.settings import DB_DSN

engine = create_engine(DB_DSN, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
