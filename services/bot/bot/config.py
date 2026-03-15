import os

def env(name: str, default: str) -> str:
    return os.getenv(name, default)

# Single source of truth for DB connection (psycopg runtime)
# See docs/15_DB_ACCESS_STANDARD.md
PG_DSN = env("PG_DSN", "postgresql://nebula:nebula123@postgres:5432/trading")

NQ_ENV = env("NQ_ENV", "local")
NQ_VERSION = env("NQ_VERSION", "dev")
NQ_SYMBOL = env("NQ_SYMBOL", "QQQ")
NQ_TIMEFRAME = env("NQ_TIMEFRAME", "5m")

# loop cadence
HEARTBEAT_SECONDS = int(env("HEARTBEAT_SECONDS", "10"))

# IMPORTANT: snapshot throttling (reduce DB spam)
SNAPSHOT_EVERY_N_HEARTBEATS = int(env("SNAPSHOT_EVERY_N_HEARTBEATS", "6"))  # default: 60s

# Paper runner: run paper sessions for eligible deployments every N heartbeats (0 = disabled)
PAPER_RUNNER_INTERVAL_HEARTBEATS = int(env("PAPER_RUNNER_INTERVAL_HEARTBEATS", "6"))  # default: every 60s
