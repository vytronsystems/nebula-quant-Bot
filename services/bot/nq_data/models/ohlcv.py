# NEBULA-QUANT v1 | nq_data canonical OHLCV model

from datetime import datetime
from decimal import Decimal

try:  # pragma: no cover - import branch
    from pydantic import BaseModel, Field  # type: ignore

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
        source: str  # tradestation, polygon, etc.

        class Config:
            frozen = True

except ImportError:  # pragma: no cover - test environment without pydantic
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Bar:
        """Canonical OHLCV bar (dataclass fallback when pydantic is unavailable)."""

        ts: datetime
        open: Decimal
        high: Decimal
        low: Decimal
        close: Decimal
        volume: int
        symbol: str
        timeframe: str  # 1m, 5m, 15m, 1h, 1d
        source: str  # tradestation, polygon, etc.

        def __post_init__(self) -> None:
            # Minimal validation to keep fail-closed semantics for obviously bad input.
            if self.volume < 0:
                raise ValueError("volume must be >= 0")
