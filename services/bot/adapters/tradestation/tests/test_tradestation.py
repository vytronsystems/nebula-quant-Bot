"""Tests for TradeStation adapter (models and option selection)."""
from __future__ import annotations

import unittest
from datetime import date

from adapters.tradestation.models import (
    TSOptionContract,
    TSOptionSelectionRequest,
    TSOptionSelectionResult,
)
from adapters.tradestation.option_selection import TradeStationOptionSelector


class TestTSOptionContract(unittest.TestCase):
    def test_dte(self) -> None:
        c = TSOptionContract(symbol="SPY_012524C450", underlying="SPY", expiry=date(2025, 1, 25), strike=450.0, right="Call")
        self.assertEqual(c.dte(date(2025, 1, 25)), 0)
        self.assertEqual(c.dte(date(2025, 1, 24)), 1)


class TestTradeStationOptionSelector(unittest.TestCase):
    def test_long_call_only(self) -> None:
        sel = TradeStationOptionSelector()
        from datetime import timedelta
        future = date.today() + timedelta(days=30)
        candidates = [
            TSOptionContract(symbol="SPY_C450", underlying="SPY", expiry=future, strike=450.0, right="Call"),
            TSOptionContract(symbol="SPY_P450", underlying="SPY", expiry=future, strike=450.0, right="Put"),
        ]
        req = TSOptionSelectionRequest(underlying="SPY", direction="call", dte_policy_min=0, dte_policy_max=60)
        result = sel.select(req, candidates)
        self.assertIsInstance(result, TSOptionSelectionResult)
        self.assertEqual(len(result.selected), 1)
        self.assertEqual(result.selected[0].right, "Call")

    def test_invalid_direction_empty(self) -> None:
        sel = TradeStationOptionSelector()
        result = sel.select(TSOptionSelectionRequest(underlying="SPY", direction="straddle"), [])
        self.assertEqual(len(result.selected), 0)
        self.assertIn("error", result.filter_used)
