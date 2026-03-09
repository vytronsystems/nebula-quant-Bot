# NEBULA-QUANT v1 | TradeStation data provider (stub)
# No real API calls in this iteration.

from datetime import datetime
from typing import Iterator

from nq_data.providers.base import DataProviderProtocol, RawBar


class TradeStationProvider(DataProviderProtocol):
    """Stub: TradeStation OHLCV. Real integration in a later iteration."""

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since: datetime,
        until: datetime,
    ) -> Iterator[RawBar]:
        # Stub: no network calls in this iteration.
        yield from ()
