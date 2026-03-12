from __future__ import annotations

import unittest

from adapters.binance.enums import BinanceOrderSide, BinanceOrderType
from adapters.binance.models import BinanceOrderRequest, BinanceValidationError
from adapters.binance.validation import (
    validate_leverage,
    validate_order_request,
    validate_position_mode,
    validate_symbol,
)


class TestBinanceValidation(unittest.TestCase):
    def _base_request(self, order_type: BinanceOrderType) -> BinanceOrderRequest:
        return BinanceOrderRequest(
            symbol="BTCUSDT",
            side=BinanceOrderSide.BUY.value,
            order_type=order_type.value,
            quantity=0.01,
            price=20_000.0,
            stop_price=19_500.0,
            leverage=1,
            time_in_force=None,
        )

    def test_symbol_validation_rejects_unsupported(self) -> None:
        with self.assertRaises(BinanceValidationError):
            validate_symbol("ETHUSDT")

    def test_leverage_validation_rejects_above_cap(self) -> None:
        with self.assertRaises(BinanceValidationError):
            validate_leverage(3)

    def test_position_mode_validation_rejects_hedge(self) -> None:
        with self.assertRaises(BinanceValidationError):
            validate_position_mode("HEDGE")

    def test_limit_order_requires_price(self) -> None:
        req = self._base_request(BinanceOrderType.LIMIT)
        req.price = None
        with self.assertRaises(BinanceValidationError):
            validate_order_request(req)

    def test_stop_market_order_requires_stop_price(self) -> None:
        req = self._base_request(BinanceOrderType.STOP_MARKET)
        req.stop_price = None
        with self.assertRaises(BinanceValidationError):
            validate_order_request(req)

    def test_quantity_must_be_positive(self) -> None:
        req = self._base_request(BinanceOrderType.MARKET)
        req.quantity = 0
        with self.assertRaises(BinanceValidationError):
            validate_order_request(req)


if __name__ == "__main__":
    unittest.main()

