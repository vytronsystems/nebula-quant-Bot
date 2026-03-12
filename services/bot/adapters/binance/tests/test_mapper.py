from __future__ import annotations

import unittest

from adapters.binance.enums import BinanceOrderSide, BinanceOrderType
from adapters.binance.mapper import (
    build_binance_order_payload,
    map_account_payload_to_state,
    map_binance_order_response,
    map_internal_order_to_binance,
)
from adapters.binance.models import NormalizedOrderRequest


class TestBinanceMapper(unittest.TestCase):
    def _base_order(self, order_type: BinanceOrderType) -> NormalizedOrderRequest:
        return NormalizedOrderRequest(
            symbol="BTCUSDT",
            side=BinanceOrderSide.BUY,
            order_type=order_type,
            quantity=0.01,
            price=20_000.0,
            stop_price=19_500.0,
            leverage=1,
        )

    def test_market_order_maps_correctly(self) -> None:
        internal = self._base_order(BinanceOrderType.MARKET)
        req = map_internal_order_to_binance(internal)
        payload = build_binance_order_payload(req)
        self.assertEqual(payload["symbol"], "BTCUSDT")
        self.assertEqual(payload["side"], "BUY")
        self.assertEqual(payload["type"], "MARKET")
        self.assertEqual(payload["quantity"], 0.01)
        self.assertNotIn("price", payload)

    def test_limit_order_maps_correctly(self) -> None:
        internal = self._base_order(BinanceOrderType.LIMIT)
        req = map_internal_order_to_binance(internal)
        payload = build_binance_order_payload(req)
        self.assertEqual(payload["type"], "LIMIT")
        self.assertEqual(payload["price"], 20_000.0)
        self.assertIn("timeInForce", payload)

    def test_stop_market_order_maps_correctly(self) -> None:
        internal = self._base_order(BinanceOrderType.STOP_MARKET)
        req = map_internal_order_to_binance(internal)
        payload = build_binance_order_payload(req)
        self.assertEqual(payload["type"], "STOP_MARKET")
        self.assertEqual(payload["stopPrice"], 19_500.0)

    def test_order_response_normalization(self) -> None:
        payload = {
            "symbol": "BTCUSDT",
            "orderId": 123,
            "clientOrderId": "cid-1",
            "status": "NEW",
            "side": "BUY",
            "type": "LIMIT",
            "origQty": "0.01",
            "executedQty": "0",
            "price": "20000",
            "avgPrice": "0",
        }
        resp = map_binance_order_response(payload)
        self.assertEqual(resp.symbol, "BTCUSDT")
        self.assertEqual(resp.order_id, 123)
        self.assertEqual(resp.side, "BUY")
        self.assertEqual(resp.order_type, "LIMIT")

    def test_account_payload_normalization(self) -> None:
        payload = {
            "assets": [
                {"asset": "USDT", "walletBalance": "1000", "availableBalance": "800", "crossWalletBalance": "1000"},
            ],
            "positions": [
                {
                    "symbol": "BTCUSDT",
                    "positionAmt": "0.01",
                    "entryPrice": "20000",
                    "unRealizedProfit": "10",
                    "leverage": "2",
                    "isolated": False,
                }
            ],
        }
        state = map_account_payload_to_state(payload)
        self.assertEqual(len(state.balances), 1)
        self.assertEqual(len(state.positions), 1)
        self.assertEqual(state.positions[0].symbol, "BTCUSDT")


if __name__ == "__main__":
    unittest.main()

