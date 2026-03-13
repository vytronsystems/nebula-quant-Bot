"""Tests for Binance account sync (snapshot persistence and history)."""
from __future__ import annotations

import unittest
from datetime import datetime

from adapters.binance.account_sync import (
    BinanceAccountSyncService,
    VenueAccountSnapshotRecord,
    _balance_equity_from_state,
)
from adapters.binance.models import BinanceAccountState, BinanceBalance, BinancePosition


def _minimal_account_payload() -> dict:
    return {"assets": [{"asset": "USDT", "walletBalance": "5000", "availableBalance": "4000", "crossWalletBalance": "5000"}], "positions": []}


class TestBalanceEquityFromState(unittest.TestCase):
    def test_usdt_balance_and_equity(self) -> None:
        state = BinanceAccountState(
            balances=[BinanceBalance(asset="USDT", balance=1000.0, available=800.0, cross_wallet_balance=1000.0)],
            positions=[BinancePosition(symbol="BTCUSDT", position_amt=0.01, entry_price=20000.0, unrealized_pnl=10.0, leverage=2, isolated=False)],
            metadata={},
        )
        balance, equity = _balance_equity_from_state(state)
        self.assertEqual(balance, 1000.0)
        self.assertAlmostEqual(equity, 1010.0)


class TestBinanceAccountSyncService(unittest.TestCase):
    def test_save_and_get_latest_skipped_without_db(self) -> None:
        try:
            import psycopg  # noqa: F401
        except ImportError:
            self.skipTest("psycopg not installed")
            return
        svc = BinanceAccountSyncService()
        payload = _minimal_account_payload()
        try:
            rec = svc.save_snapshot_from_payload("binance", "test-account", payload)
            self.assertIsInstance(rec, VenueAccountSnapshotRecord)
            self.assertEqual(rec.venue, "binance")
            self.assertEqual(rec.account_id, "test-account")
            latest = svc.get_latest_snapshot("binance")
            self.assertIsNotNone(latest)
            self.assertEqual(latest.venue, "binance")
        except Exception as e:
            if "connection" in str(e).lower() or "connect" in str(e).lower():
                self.skipTest("DB not available")
            raise
