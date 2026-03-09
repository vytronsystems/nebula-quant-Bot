import os

def env(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None or v == "":
        raise RuntimeError(f"Missing required env var: {name}")
    return v

# Single source of truth for DB DSN (Alembic + App)
DB_DSN = env("PG_DSN", "postgresql+psycopg2://nebula:nebula123@postgres:5432/trading")
