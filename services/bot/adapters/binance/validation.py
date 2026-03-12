from __future__ import annotations

from typing import Any

from adapters.binance.config import BINANCE_FUTURES_CONFIG
from adapters.binance.enums import BinanceOrderType, BinancePositionMode
from adapters.binance.models import BinanceAdapterError, BinanceOrderRequest, BinanceValidationError


def validate_symbol(symbol: str) -> None:
    if symbol not in BINANCE_FUTURES_CONFIG.allowed_symbols:
        raise BinanceValidationError(f"symbol {symbol!r} not allowed in this phase")


def validate_leverage(leverage: int) -> None:
    if leverage < 1:
        raise BinanceValidationError("leverage must be >= 1")
    if leverage > BINANCE_FUTURES_CONFIG.max_leverage:
        raise BinanceValidationError(f"leverage {leverage} exceeds max {BINANCE_FUTURES_CONFIG.max_leverage}")


def validate_position_mode(mode: str) -> None:
    if mode != BinancePositionMode.ONE_WAY.value:
        raise BinanceValidationError("only ONE_WAY position mode is supported in this phase")


def validate_order_type(order_type: str) -> None:
    if order_type not in BINANCE_FUTURES_CONFIG.supported_order_types:
        raise BinanceValidationError(f"unsupported order_type {order_type!r}")


def validate_order_request(order: BinanceOrderRequest) -> None:
    validate_symbol(order.symbol)
    validate_leverage(order.leverage)
    validate_order_type(order.order_type)

    if order.quantity is None or order.quantity <= 0:
        raise BinanceValidationError("quantity must be positive")

    if order.order_type == BinanceOrderType.LIMIT.value:
        if order.price is None or order.price <= 0:
            raise BinanceValidationError("price must be positive for LIMIT orders")

    if order.order_type == BinanceOrderType.STOP_MARKET.value:
        if order.stop_price is None or order.stop_price <= 0:
            raise BinanceValidationError("stop_price must be positive for STOP_MARKET orders")


def validate_binance_order_payload(payload: dict[str, Any]) -> None:
    """
    Minimal validation for Binance-like order payloads coming from the exchange.
    Fail-closed on missing required fields.
    """
    required_keys = {"symbol", "orderId", "clientOrderId", "status", "side", "type", "origQty", "price"}
    missing = [k for k in required_keys if k not in payload]
    if missing:
        raise BinanceAdapterError(f"missing fields in order payload: {missing}")


def validate_account_payload(payload: dict[str, Any]) -> None:
    """Minimal validation for account payloads."""
    if not isinstance(payload, dict):
        raise BinanceAdapterError("account payload must be a dict")
    if "assets" not in payload or "positions" not in payload:
        raise BinanceAdapterError("account payload must contain 'assets' and 'positions'")

