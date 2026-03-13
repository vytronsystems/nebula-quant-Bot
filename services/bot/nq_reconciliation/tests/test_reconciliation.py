"""Tests for reconciliation modules."""
from __future__ import annotations

import unittest

from nq_reconciliation import (
    OrderReconciliationModule,
    PnLReconciliationModule,
    PositionReconciliationModule,
)
from nq_reconciliation.models import OrderReconciliationSummary, PnLReconciliationSummary, PositionReconciliationSummary


class TestOrderReconciliation(unittest.TestCase):
    def test_empty_ok(self) -> None:
        mod = OrderReconciliationModule()
        s = mod.run("binance", [], [])
        self.assertIsInstance(s, OrderReconciliationSummary)
        self.assertEqual(s.venue, "binance")
        self.assertEqual(s.matched, 0)
        self.assertEqual(s.internal_only, 0)
        self.assertEqual(s.venue_only, 0)


class TestPositionReconciliation(unittest.TestCase):
    def test_empty_ok(self) -> None:
        mod = PositionReconciliationModule()
        s = mod.run("binance", [], [])
        self.assertIsInstance(s, PositionReconciliationSummary)
        self.assertEqual(s.venue, "binance")


class TestPnLReconciliation(unittest.TestCase):
    def test_match_ok(self) -> None:
        mod = PnLReconciliationModule()
        s = mod.run("binance", 100.0, 100.0, tolerance=0.01)
        self.assertIsInstance(s, PnLReconciliationSummary)
        self.assertEqual(s.status, "ok")

    def test_mismatch(self) -> None:
        mod = PnLReconciliationModule()
        s = mod.run("binance", 100.0, 200.0, tolerance=0.01)
        self.assertEqual(s.status, "mismatch")
        self.assertAlmostEqual(s.diff, 100.0)
