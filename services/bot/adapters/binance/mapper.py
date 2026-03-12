from __future__ import annotations

from typing import Any

from adapters.binance.enums import BinanceOrderSide, BinanceOrderType, BinanceTimeInForce
from adapters.binance.models import (
    BinanceAccountState,
    BinanceBalance,
    BinanceOrderRequest,
    BinanceOrderResponse,
    BinancePosition,
    BinanceAdapterError,
    NormalizedOrderRequest,
)


def map_internal_order_to_binance(order: NormalizedOrderRequest) -> BinanceOrderRequest:
    """
    Map a normalized internal order request into a BinanceOrderRequest.

    This function performs a pure structural translation; validation is handled
    separately in validation.py.
    """
    tif = order.time_in_force.value if order.time_in_force is not None else None
    return BinanceOrderRequest(
        symbol=order.symbol,
        side=order.side.value,
        order_type=order.order_type.value,
        quantity=order.quantity,
        price=order.price,
        stop_price=order.stop_price,
        time_in_force=tif,
        leverage=order.leverage,
        client_order_id=order.client_order_id,
        metadata=dict(order.metadata),
    )


def build_binance_order_payload(req: BinanceOrderRequest) -> dict[str, Any]:
    """
    Build a Binance REST order payload from BinanceOrderRequest.

    This is the shape that would be sent to the /fapi/v1/order endpoint,
    excluding authentication fields.
    """
    payload: dict[str, Any] = {
        "symbol": req.symbol,
        "side": req.side,
        "type": req.order_type,
        "quantity": req.quantity,
    }
    if req.client_order_id is not None:
        payload["newClientOrderId"] = req.client_order_id
    if req.order_type == BinanceOrderType.LIMIT.value:
        payload["price"] = req.price
        payload["timeInForce"] = req.time_in_force or BinanceTimeInForce.GTC.value
    if req.order_type == BinanceOrderType.STOP_MARKET.value:
        payload["stopPrice"] = req.stop_price
    return payload


def map_binance_order_response(payload: dict[str, Any]) -> BinanceOrderResponse:
    """Map a Binance order response payload into BinanceOrderResponse."""
    try:
        return BinanceOrderResponse(
            symbol=str(payload["symbol"]),
            order_id=int(payload["orderId"]),
            client_order_id=str(payload["clientOrderId"]),
            status=str(payload["status"]),
            side=str(payload["side"]),
            order_type=str(payload["type"]),
            price=float(payload.get("price", 0) or 0),
            orig_qty=float(payload.get("origQty", 0) or 0),
            executed_qty=float(payload.get("executedQty", 0) or 0),
            avg_price=float(payload.get("avgPrice", 0) or 0),
            metadata={},
        )
    except Exception as exc:  # noqa: BLE001
        raise BinanceAdapterError(f"failed to map order response: {exc}") from exc


def map_account_payload_to_state(payload: dict[str, Any]) -> BinanceAccountState:
    """
    Map a Binance account payload into BinanceAccountState.

    Expected payload structure (subset of /fapi/v2/account):
    - assets: list of dicts with 'asset', 'walletBalance', 'availableBalance'
    - positions: list of dicts with 'symbol', 'positionAmt', 'entryPrice',
      'unRealizedProfit', 'leverage', 'isolated' or 'isolatedMargin'
    """
    try:
        balances: list[BinanceBalance] = []
        for asset in payload.get("assets", []):
            balances.append(
                BinanceBalance(
                    asset=str(asset.get("asset", "")),
                    balance=float(asset.get("walletBalance", 0) or 0),
                    available=float(asset.get("availableBalance", 0) or 0),
                    cross_wallet_balance=float(asset.get("crossWalletBalance", 0) or 0),
                    metadata={},
                )
            )
        positions: list[BinancePosition] = []
        for p in payload.get("positions", []):
            isolated_flag = bool(p.get("isolated", False))
            positions.append(
                BinancePosition(
                    symbol=str(p.get("symbol", "")),
                    position_amt=float(p.get("positionAmt", 0) or 0),
                    entry_price=float(p.get("entryPrice", 0) or 0),
                    unrealized_pnl=float(p.get("unRealizedProfit", 0) or 0),
                    leverage=int(p.get("leverage", 1) or 1),
                    isolated=isolated_flag,
                    metadata={},
                )
            )
        return BinanceAccountState(balances=balances, positions=positions, metadata={})
    except Exception as exc:  # noqa: BLE001
        raise BinanceAdapterError(f"failed to map account payload: {exc}") from exc

