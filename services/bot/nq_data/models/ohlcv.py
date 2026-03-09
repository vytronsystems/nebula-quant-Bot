# NEBULA-QUANT v1 | nq_data canonical OHLCV model

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class Bar(BaseModel):
    """Canonical OHLCV bar. All providers normalize to this."""
    ts: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int = Field(ge=0)
    symbol: str
    timeframe: str  # 1m, 5m, 15m, 1h, 1d
    source: str     # tradestation, polygon, etc.

    class Config:
        frozen = True
