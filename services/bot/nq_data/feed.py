# NEBULA-QUANT v1 | nq_data feed (unified API for strategies, backtest, paper, live)

from datetime import datetime
from typing import List

from nq_data.config import ALLOWED_TIMEFRAMES, get_data_provider
from nq_data.models.ohlcv import Bar
from nq_data.providers.tradestation import TradeStationProvider
from nq_data.exceptions import DataError


def _get_provider():
    """Resolve provider from config. Currently only TradeStation stub."""
    name = get_data_provider()
    if name == "tradestation":
        return TradeStationProvider()
    raise DataError(f"Unknown data provider: {name}")


def get_bars(
    symbol: str,
    timeframe: str,
    since: datetime,
    until: datetime,
) -> List[Bar]:
    """Fetch OHLCV bars. Stub: no cache, no resampling; returns empty list."""
    if timeframe not in ALLOWED_TIMEFRAMES:
        raise DataError(f"Timeframe {timeframe!r} not in {ALLOWED_TIMEFRAMES}")
    provider = _get_provider()
    # Stub: raw bars are not normalized yet; return empty
    list(provider.fetch_ohlcv(symbol, timeframe, since, until))
    return []


def get_latest(symbol: str, timeframe: str, n: int = 1) -> List[Bar]:
    """Fetch latest n bars. Stub: returns empty list."""
    if timeframe not in ALLOWED_TIMEFRAMES:
        raise DataError(f"Timeframe {timeframe!r} not in {ALLOWED_TIMEFRAMES}")
    if n < 1:
        raise DataError("n must be >= 1")
    return []
