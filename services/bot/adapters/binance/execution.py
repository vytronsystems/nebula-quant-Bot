from __future__ import annotations

from typing import Any

from adapters.binance.mapper import build_binance_order_payload, map_binance_order_response, map_internal_order_to_binance
from adapters.binance.models import (
    BinanceCancelResponse,
    BinanceExecutionResult,
    BinanceOrderRequest,
    BinanceOrderResponse,
    NormalizedOrderRequest,
)
from adapters.binance.validation import validate_order_request, validate_binance_order_payload


class BinanceExecutionAdapter:
    """
    Architecture-level execution adapter for Binance USDT-M Futures.

    In Phase 51 this adapter:
    - validates normalized internal orders,
    - maps them to Binance REST payloads,
    - simulates deterministic responses for unit testing.

    No real network calls or secrets are used.
    """

    def __init__(self) -> None:
        pass

    def validate_order(self, order: NormalizedOrderRequest) -> None:
        req = map_internal_order_to_binance(order)
        validate_order_request(req)

    def map_order(self, order: NormalizedOrderRequest) -> tuple[BinanceOrderRequest, dict[str, Any]]:
        """Return BinanceOrderRequest and REST payload for an internal order."""
        req = map_internal_order_to_binance(order)
        validate_order_request(req)
        payload = build_binance_order_payload(req)
        return req, payload

    def submit_order(self, order: NormalizedOrderRequest) -> BinanceExecutionResult:
        """
        Validate and map an order, returning a deterministic simulated response.

        The response shape mirrors Binance but is generated locally.
        """
        req, payload = self.map_order(order)
        # Simulate deterministic "NEW" response; orderId derived from hash of payload.
        order_id = abs(hash(tuple(sorted(payload.items())))) % 10_000_000
        response_payload = {
            "symbol": req.symbol,
            "orderId": order_id,
            "clientOrderId": req.client_order_id or f"sim-{order_id}",
            "status": "NEW",
            "side": req.side,
            "type": req.order_type,
            "origQty": req.quantity,
            "executedQty": 0,
            "price": req.price or 0,
            "avgPrice": 0,
        }
        validate_binance_order_payload(response_payload)
        response = map_binance_order_response(response_payload)
        return BinanceExecutionResult(request=req, response=response, metadata={"simulated": True})

    def cancel_order(self, order_id: int, symbol: str) -> BinanceCancelResponse:
        """Return a deterministic simulated cancel response."""
        return BinanceCancelResponse(
            symbol=symbol,
            order_id=order_id,
            client_order_id=f"sim-{order_id}",
            status="CANCELED",
            metadata={"simulated": True},
        )

    def get_order_status(self, order_id: int, symbol: str) -> BinanceOrderResponse:
        """
        Return a deterministic simulated order status.

        In Phase 51 this simply echoes a filled order with zero price.
        """
        payload = {
            "symbol": symbol,
            "orderId": order_id,
            "clientOrderId": f"sim-{order_id}",
            "status": "FILLED",
            "side": "BUY",
            "type": "MARKET",
            "origQty": 1,
            "executedQty": 1,
            "price": 0,
            "avgPrice": 0,
        }
        validate_binance_order_payload(payload)
        return map_binance_order_response(payload)

