from __future__ import annotations

import unittest

from adapters.binance.enums import BinanceOrderSide, BinanceOrderType
from adapters.binance.execution import BinanceExecutionAdapter
from adapters.binance.models import NormalizedOrderRequest, BinanceValidationError


def _base_order(order_type: BinanceOrderType) -> NormalizedOrderRequest:
    return NormalizedOrderRequest(
        symbol="BTCUSDT",
        side=BinanceOrderSide.BUY,
        order_type=order_type,
        quantity=0.01,
        price=20_000.0,
        stop_price=19_500.0,
        leverage=1,
    )


class TestExecutionAdapter(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = BinanceExecutionAdapter()

    def test_market_order_submit_simulated(self) -> None:
        order = _base_order(BinanceOrderType.MARKET)
        result = self.adapter.submit_order(order)
        self.assertEqual(result.request.symbol, "BTCUSDT")
        self.assertEqual(result.response.status, "NEW")
        self.assertTrue(result.metadata.get("simulated", False))

    def test_unsupported_order_type_fails_closed(self) -> None:
        # Use an invalid type by constructing a NormalizedOrderRequest with raw value
        order = _base_order(BinanceOrderType.MARKET)
        order.order_type = BinanceOrderType("MARKET")  # still valid
        # Simulate unsupported by editing underlying request after mapping
        req, _ = self.adapter.map_order(order)
        req.order_type = "UNKNOWN"
        with self.assertRaises(BinanceValidationError):
            from adapters.binance.validation import validate_order_request

            validate_order_request(req)


if __name__ == "__main__":
    unittest.main()

