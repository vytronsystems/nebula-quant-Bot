from __future__ import annotations

import unittest

from adapters.binance.config import BINANCE_FUTURES_CONFIG
from adapters.binance.enums import BinanceOrderSide, BinanceOrderType, BinanceTimeInForce
from adapters.binance.models import NormalizedOrderRequest


class TestBinanceModels(unittest.TestCase):
    def test_normalized_order_request_fields(self) -> None:
        order = NormalizedOrderRequest(
            symbol="BTCUSDT",
            side=BinanceOrderSide.BUY,
            order_type=BinanceOrderType.MARKET,
            quantity=0.01,
            time_in_force=BinanceTimeInForce.GTC,
            leverage=1,
            client_order_id="test-1",
        )
        self.assertEqual(order.symbol, "BTCUSDT")
        self.assertEqual(order.side, BinanceOrderSide.BUY)
        self.assertEqual(order.order_type, BinanceOrderType.MARKET)
        self.assertEqual(order.quantity, 0.01)
        self.assertEqual(order.time_in_force, BinanceTimeInForce.GTC)
        self.assertEqual(order.leverage, 1)

    def test_config_scope(self) -> None:
        self.assertIn("BTCUSDT", BINANCE_FUTURES_CONFIG.allowed_symbols)
        self.assertEqual(BINANCE_FUTURES_CONFIG.max_leverage, 2)
        self.assertIn("MARKET", BINANCE_FUTURES_CONFIG.supported_order_types)
        self.assertIn("LIMIT", BINANCE_FUTURES_CONFIG.supported_order_types)
        self.assertIn("STOP_MARKET", BINANCE_FUTURES_CONFIG.supported_order_types)


if __name__ == "__main__":
    unittest.main()

