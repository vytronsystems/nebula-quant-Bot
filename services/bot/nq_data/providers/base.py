# NEBULA-QUANT v1 | nq_data provider interface

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterator

# Stub type for raw provider response (before normalization)
RawBar = dict


class DataProviderProtocol(ABC):
    """Interface for OHLCV data providers. TradeStation, Polygon, Databento implement this."""

    @abstractmethod
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since: datetime,
        until: datetime,
    ) -> Iterator[RawBar]:
        """Fetch OHLCV bars. Yields raw bars; caller normalizes to Bar."""
        ...

    def supports_streaming(self) -> bool:
        """Override to True if provider supports streaming."""
        return False
