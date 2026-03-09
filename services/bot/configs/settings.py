import os

def env(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None or v == "":
        raise RuntimeError(f"Missing required env var: {name}")
    return v

# DEPRECATED: Only used by bot/db/session.py (unused, outside runtime flow).
# Runtime uses bot.config.PG_DSN + psycopg direct. See docs/15_DB_ACCESS_STANDARD.md
# Converts postgresql:// to postgresql+psycopg:// for SQLAlchemy 2 + psycopg3
_pg_dsn = env("PG_DSN", "postgresql://nebula:nebula123@postgres:5432/trading")
DB_DSN = _pg_dsn.replace("postgresql://", "postgresql+psycopg://", 1)
