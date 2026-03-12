from __future__ import annotations

import unittest

from adapters.binance.account import BinanceAccountAdapter


class TestAccountAdapter(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = BinanceAccountAdapter()

    def _account_payload(self) -> dict:
        return {
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

    def test_account_state_normalization(self) -> None:
        payload = self._account_payload()
        state = self.adapter.normalize_account_state(payload)
        self.assertEqual(len(state.balances), 1)
        self.assertEqual(len(state.positions), 1)

    def test_balances_and_positions_helpers(self) -> None:
        payload = self._account_payload()
        balances = self.adapter.normalize_balances(payload)
        positions = self.adapter.normalize_positions(payload)
        self.assertEqual(balances[0].asset, "USDT")
        self.assertEqual(positions[0].symbol, "BTCUSDT")


if __name__ == "__main__":
    unittest.main()

