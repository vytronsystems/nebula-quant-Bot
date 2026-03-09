# NEBULA-QUANT v1 | nq_data config
# Initial provider: TradeStation. Final architecture: hybrid (multiple sources).

import os

# Allowed timeframes (frozen for v1)
ALLOWED_TIMEFRAMES = ("1m", "5m", "15m", "1h", "1d")

# Default provider for OHLCV (TradeStation; future: configurable)
DEFAULT_PROVIDER = "tradestation"

def get_data_provider() -> str:
    return os.getenv("NQ_DATA_PROVIDER", DEFAULT_PROVIDER)
