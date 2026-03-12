from __future__ import annotations

"""
NEBULA-QUANT v1 | Binance USDT-M Futures adapters.

This package provides a deterministic, fail-closed adapter layer for Binance
USDT-M Futures (One-Way mode, BTCUSDT-only in Phase 51). It defines models,
enums, validation rules, and mapping utilities, plus stubbed execution/account
adapters suitable for unit testing and future transport wiring.
"""

from adapters.binance.config import BINANCE_FUTURES_CONFIG
from adapters.binance.execution import BinanceExecutionAdapter
from adapters.binance.account import BinanceAccountAdapter
from adapters.binance.models import (
    BinanceAdapterError,
    BinanceValidationError,
    BinanceOrderRequest,
    BinanceOrderResponse,
    BinanceAccountState,
    BinancePosition,
    BinanceBalance,
)
from adapters.binance.enums import (
    BinanceOrderSide,
    BinanceOrderType,
    BinanceTimeInForce,
    BinancePositionMode,
)

__all__ = [
    "BINANCE_FUTURES_CONFIG",
    "BinanceExecutionAdapter",
    "BinanceAccountAdapter",
    "BinanceAdapterError",
    "BinanceValidationError",
    "BinanceOrderRequest",
    "BinanceOrderResponse",
    "BinanceAccountState",
    "BinancePosition",
    "BinanceBalance",
    "BinanceOrderSide",
    "BinanceOrderType",
    "BinanceTimeInForce",
    "BinancePositionMode",
]

