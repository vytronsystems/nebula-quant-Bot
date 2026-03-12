from __future__ import annotations

from enum import Enum


class BinanceOrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class BinanceOrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_MARKET = "STOP_MARKET"


class BinanceTimeInForce(str, Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"


class BinancePositionMode(str, Enum):
    ONE_WAY = "ONE_WAY"
    HEDGE = "HEDGE"


class BinanceMarginType(str, Enum):
    ISOLATED = "ISOLATED"
    CROSSED = "CROSSED"

