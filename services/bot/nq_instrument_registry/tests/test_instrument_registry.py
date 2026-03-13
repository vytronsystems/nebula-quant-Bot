"""Tests for instrument registry service and models."""
from __future__ import annotations

import unittest
from datetime import datetime

from nq_instrument_registry.models import ActivationLogEntry, InstrumentRecord


class TestInstrumentRecord(unittest.TestCase):
    def test_to_api(self) -> None:
        rec = InstrumentRecord(
            venue="binance",
            symbol="BTCUSDT",
            asset_type="spot",
            active=True,
            created_at=datetime(2025, 1, 1, 12, 0),
            updated_at=datetime(2025, 1, 1, 12, 0),
            meta=None,
        )
        out = rec.to_api()
        self.assertEqual(out["venue"], "binance")
        self.assertEqual(out["symbol"], "BTCUSDT")
        self.assertEqual(out["active"], True)


class TestActivationLogEntry(unittest.TestCase):
    def test_to_api(self) -> None:
        entry = ActivationLogEntry(
            venue="binance",
            symbol="BTCUSDT",
            action="activate",
            created_at=datetime(2025, 1, 1, 12, 0),
            meta=None,
        )
        out = entry.to_api()
        self.assertEqual(out["action"], "activate")


class TestInstrumentRegistryService(unittest.TestCase):
    def test_list_instruments_returns_list(self) -> None:
        try:
            from nq_instrument_registry.service import InstrumentRegistryService
        except ImportError:
            self.skipTest("psycopg not installed")
            return
        svc = InstrumentRegistryService()
        result = svc.list_instruments(active_only=False)
        self.assertIsInstance(result, list)
