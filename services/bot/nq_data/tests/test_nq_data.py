# NEBULA-QUANT v1 | nq_data tests — feed, bar validation, fail-closed

from __future__ import annotations

import unittest
from datetime import datetime
from decimal import Decimal

from nq_data import Bar, DataError, get_bars, get_latest


class TestBarStructure(unittest.TestCase):
    """Bar model validation."""

    def test_bar_valid_creation(self) -> None:
        bar = Bar(
            ts=datetime(2025, 1, 1, 12, 0),
            open=Decimal("100.0"),
            high=Decimal("101.0"),
            low=Decimal("99.0"),
            close=Decimal("100.5"),
            volume=1000,
            symbol="QQQ",
            timeframe="1m",
            source="test",
        )
        self.assertEqual(bar.symbol, "QQQ")
        self.assertEqual(bar.volume, 1000)
        self.assertEqual(float(bar.close), 100.5)

    def test_bar_negative_volume_fails(self) -> None:
        with self.assertRaises(Exception):  # pydantic ValidationError
            Bar(
                ts=datetime(2025, 1, 1),
                open=Decimal("100"),
                high=Decimal("100"),
                low=Decimal("100"),
                close=Decimal("100"),
                volume=-1,
                symbol="X",
                timeframe="1m",
                source="test",
            )


class TestFeedValidation(unittest.TestCase):
    """Feed API input validation and fail-closed."""

    def test_get_bars_invalid_timeframe_raises(self) -> None:
        since = datetime(2025, 1, 1)
        until = datetime(2025, 1, 2)
        with self.assertRaises(DataError) as ctx:
            get_bars("QQQ", "invalid", since, until)
        self.assertIn("invalid", str(ctx.exception))
        self.assertIn("not in", str(ctx.exception).lower() or "")

    def test_get_bars_valid_timeframe_returns_list(self) -> None:
        since = datetime(2025, 1, 1)
        until = datetime(2025, 1, 2)
        bars = get_bars("QQQ", "1m", since, until)
        self.assertIsInstance(bars, list)
        # Stub provider returns empty
        self.assertEqual(len(bars), 0)

    def test_get_latest_invalid_n_raises(self) -> None:
        with self.assertRaises(DataError) as ctx:
            get_latest("QQQ", "1m", n=0)
        self.assertIn("n", str(ctx.exception).lower())

    def test_get_latest_valid_returns_list(self) -> None:
        out = get_latest("QQQ", "1m", n=5)
        self.assertIsInstance(out, list)
        self.assertEqual(len(out), 0)


class TestDeterminism(unittest.TestCase):
    """Same inputs produce same outputs."""

    def test_get_bars_deterministic(self) -> None:
        since = datetime(2025, 1, 1)
        until = datetime(2025, 1, 2)
        a = get_bars("QQQ", "1m", since, until)
        b = get_bars("QQQ", "1m", since, until)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 0)
