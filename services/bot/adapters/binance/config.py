from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapters.binance.enums import BinanceMarginType, BinanceOrderType, BinancePositionMode


@dataclass(slots=True)
class BinanceSymbolConfig:
    symbol: str
    base_asset: str
    quote_asset: str
    contract_type: str = "PERPETUAL"
    margin_asset: str = "USDT"
    max_leverage: int = 2
    min_qty: float = 0.001
    step_size: float = 0.001
    tick_size: float = 0.1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinanceFuturesConfig:
    """Static configuration for Binance USDT-M futures adapter."""

    rest_base_url: str
    websocket_base_url: str
    allowed_symbols: list[str]
    max_leverage: int
    supported_order_types: list[str]
    position_mode: str
    margin_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


BINANCE_BTCUSDT_CONFIG = BinanceSymbolConfig(
    symbol="BTCUSDT",
    base_asset="BTC",
    quote_asset="USDT",
)

BINANCE_FUTURES_CONFIG = BinanceFuturesConfig(
    rest_base_url="https://fapi.binance.com",  # placeholder; no secrets
    websocket_base_url="wss://fstream.binance.com",  # placeholder
    allowed_symbols=["BTCUSDT"],
    max_leverage=2,
    supported_order_types=[
        BinanceOrderType.MARKET.value,
        BinanceOrderType.LIMIT.value,
        BinanceOrderType.STOP_MARKET.value,
    ],
    position_mode=BinancePositionMode.ONE_WAY.value,
    margin_type=BinanceMarginType.CROSSED.value,
    metadata={"exchange": "binance", "market": "USDT-M Futures"},
)


@dataclass(slots=True)
class BinanceOperationalConfig:
    """
    Binance operational mode and safeguard defaults.
    24/7/365: no market open/close; use UTC reset and rolling windows.
    No secrets; live disabled by default.
    """

    binance_paper_enabled: bool = True
    binance_shadow_enabled: bool = True
    binance_live_enabled: bool = False
    binance_kill_switch_enabled: bool = True
    binance_max_daily_loss: float = 5000.0
    binance_max_order_rate_per_minute: int = 10
    binance_max_position_size: float = 1.0
    binance_max_notional_per_order: float = 100_000.0
    binance_max_open_positions: int = 5
    binance_heartbeat_timeout_seconds: float = 60.0
    binance_reset_hour_utc: int = 0
    binance_rolling_window_minutes: int = 5
    metadata: dict[str, Any] = field(default_factory=dict)


BINANCE_OPERATIONAL_CONFIG = BinanceOperationalConfig()

