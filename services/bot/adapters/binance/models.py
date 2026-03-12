from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapters.binance.enums import BinanceOrderSide, BinanceOrderType, BinanceTimeInForce


class BinanceAdapterError(Exception):
    """Base adapter error for Binance integration."""


class BinanceValidationError(BinanceAdapterError):
    """Raised when validation fails for orders or payloads."""


@dataclass(slots=True)
class BinanceKline:
    symbol: str
    interval: str
    open_time: int
    close_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    trades: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinanceTicker:
    symbol: str
    last_price: float
    price_change_percent: float
    volume: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinanceOrderBookSnapshot:
    symbol: str
    last_update_id: int
    bids: list[tuple[float, float]]
    asks: list[tuple[float, float]]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinanceContractSpec:
    symbol: str
    base_asset: str
    quote_asset: str
    contract_type: str
    margin_asset: str
    max_leverage: int
    min_qty: float
    step_size: float
    tick_size: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinanceBalance:
    asset: str
    balance: float
    available: float
    cross_wallet_balance: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinancePosition:
    symbol: str
    position_amt: float
    entry_price: float
    unrealized_pnl: float
    leverage: int
    isolated: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinanceAccountState:
    balances: list[BinanceBalance]
    positions: list[BinancePosition]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinanceOrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float | None = None
    stop_price: float | None = None
    time_in_force: str | None = None
    leverage: int = 1
    client_order_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinanceOrderResponse:
    symbol: str
    order_id: int
    client_order_id: str
    status: str
    side: str
    order_type: str
    price: float
    orig_qty: float
    executed_qty: float
    avg_price: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinanceCancelResponse:
    symbol: str
    order_id: int
    client_order_id: str
    status: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinanceExecutionResult:
    request: BinanceOrderRequest
    response: BinanceOrderResponse
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class NormalizedOrderRequest:
    """
    Minimal internal order intent used for adapter tests.
    This is local to the Binance adapter and not a global NEBULA-QUANT type.
    """

    symbol: str
    side: BinanceOrderSide
    order_type: BinanceOrderType
    quantity: float
    price: float | None = None
    stop_price: float | None = None
    time_in_force: BinanceTimeInForce | None = None
    leverage: int = 1
    client_order_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

