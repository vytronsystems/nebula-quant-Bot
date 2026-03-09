import os

def env(name: str, default: str) -> str:
    return os.getenv(name, default)

NQ_ENV = env("NQ_ENV", "local")
NQ_VERSION = env("NQ_VERSION", "dev")
NQ_SYMBOL = env("NQ_SYMBOL", "QQQ")
NQ_TIMEFRAME = env("NQ_TIMEFRAME", "5m")

# loop cadence
HEARTBEAT_SECONDS = int(env("HEARTBEAT_SECONDS", "10"))

# IMPORTANT: snapshot throttling (reduce DB spam)
SNAPSHOT_EVERY_N_HEARTBEATS = int(env("SNAPSHOT_EVERY_N_HEARTBEATS", "6"))  # default: 60s
