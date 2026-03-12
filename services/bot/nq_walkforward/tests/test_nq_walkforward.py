# NEBULA-QUANT v1 | nq_walkforward tests — segmentation, integration with backtest, fail-closed

from __future__ import annotations

import unittest
from typing import Any

from nq_walkforward import WalkForwardEngine, WalkForwardResult


def make_bar(ts: float, close: float) -> dict[str, Any]:
    return {"ts": ts, "close": close}


def hold_strategy(bar: Any) -> str:
    return "hold"


class TestWalkForwardEngineInit(unittest.TestCase):
    """Engine initialization."""

    def test_engine_creates(self) -> None:
        engine = WalkForwardEngine()
        self.assertIsNotNone(engine)

    def test_engine_with_params(self) -> None:
        engine = WalkForwardEngine(train_size=10, test_size=3, symbol="SPY")
        self.assertIsNotNone(engine)


class TestWalkForwardRun(unittest.TestCase):
    """Empty or small input returns safe result; no crash."""

    def test_empty_bars_returns_result(self) -> None:
        engine = WalkForwardEngine()
        result = engine.run(bars=[], strategy=hold_strategy)
        self.assertIsInstance(result, WalkForwardResult)
        self.assertEqual(result.total_windows, 0)
        self.assertEqual(result.passed_windows, 0)

    def test_none_bars_safe(self) -> None:
        engine = WalkForwardEngine()
        result = engine.run(bars=None, strategy=None)
        self.assertEqual(result.total_windows, 0)

    def test_too_few_bars_returns_zero_windows(self) -> None:
        engine = WalkForwardEngine(train_size=20, test_size=5)
        bars = [make_bar(float(i), 100.0) for i in range(10)]
        result = engine.run(bars=bars, strategy=hold_strategy)
        self.assertEqual(result.total_windows, 0)


class TestDeterminism(unittest.TestCase):
    """Same inputs produce same WalkForwardResult."""

    def test_same_bars_same_result(self) -> None:
        engine = WalkForwardEngine(train_size=5, test_size=2)
        bars = [make_bar(float(i), 100.0 + (i % 3)) for i in range(30)]
        r1 = engine.run(bars=bars, strategy=hold_strategy)
        r2 = engine.run(bars=bars, strategy=hold_strategy)
        self.assertEqual(r1.total_windows, r2.total_windows)
        self.assertEqual(r1.passed_windows, r2.passed_windows)
        self.assertEqual(r1.pass_rate, r2.pass_rate)

    def test_result_has_expected_fields(self) -> None:
        engine = WalkForwardEngine()
        result = engine.run(bars=[], strategy=None)
        self.assertIsInstance(result.windows, list)
        self.assertIsInstance(result.pass_rate, float)
        self.assertIn("engine", result.metadata)
