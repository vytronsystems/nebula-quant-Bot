# NEBULA-QUANT v1 | nq_paper tests — session init, simulated execution, deterministic

from __future__ import annotations

import unittest
from typing import Any

from nq_paper import PaperEngine, PaperSessionResult


def make_bar(ts: float, close: float, symbol: str = "QQQ") -> dict[str, Any]:
    return {"ts": ts, "close": close, "symbol": symbol}


def hold_strategy(bar: Any) -> str:
    return "hold"


def long_strategy(bar: Any) -> str:
    return "long"


class TestPaperEngineInit(unittest.TestCase):
    """Paper engine initialization."""

    def test_engine_creates(self) -> None:
        engine = PaperEngine()
        self.assertIsNotNone(engine)

    def test_engine_with_initial_capital(self) -> None:
        engine = PaperEngine(initial_capital=50_000.0)
        self.assertIsNotNone(engine)


class TestPaperSessionRun(unittest.TestCase):
    """Session run; empty input safe."""

    def test_empty_bars_returns_session_result(self) -> None:
        engine = PaperEngine()
        result = engine.run_session(bars=[], strategy=hold_strategy)
        self.assertIsInstance(result, PaperSessionResult)
        self.assertEqual(len(result.trades), 0)

    def test_none_bars_safe(self) -> None:
        engine = PaperEngine()
        result = engine.run_session(bars=None, strategy=None)
        self.assertEqual(len(result.trades), 0)

    def test_single_bar_hold_no_trades(self) -> None:
        engine = PaperEngine()
        bars = [make_bar(1000.0, 100.0)]
        result = engine.run_session(bars=bars, strategy=hold_strategy)
        self.assertEqual(len(result.trades), 0)


class TestDeterminism(unittest.TestCase):
    """Same inputs produce same session result."""

    def test_same_bars_same_trade_count(self) -> None:
        engine = PaperEngine()
        bars = [make_bar(float(i), 100.0) for i in range(5)]
        r1 = engine.run_session(bars=bars, strategy=hold_strategy)
        r2 = engine.run_session(bars=bars, strategy=hold_strategy)
        self.assertEqual(len(r1.trades), len(r2.trades))

    def test_result_has_expected_fields(self) -> None:
        engine = PaperEngine()
        result = engine.run_session(bars=[], strategy=None)
        self.assertIsInstance(result.trades, list)
        self.assertIsInstance(result.positions, list)
        self.assertIsInstance(result.account_state, object)
        self.assertIsInstance(result.summary, dict)
