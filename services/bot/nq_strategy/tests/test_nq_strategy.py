# NEBULA-QUANT v1 | nq_strategy tests — signal, engine, fail-closed

from __future__ import annotations

import unittest
from typing import Any

from nq_strategy import EngineError, ExampleStrategy, Signal, Strategy, StrategyEngine


class TestSignalValues(unittest.TestCase):
    """Signal enum values."""

    def test_signal_values(self) -> None:
        self.assertEqual(Signal.LONG.value, "long")
        self.assertEqual(Signal.SHORT.value, "short")
        self.assertEqual(Signal.HOLD.value, "hold")
        self.assertEqual(Signal.EXIT.value, "exit")


class TestExampleStrategy(unittest.TestCase):
    """Example strategy returns HOLD deterministically."""

    def test_example_strategy_on_bar_returns_hold(self) -> None:
        strat = ExampleStrategy()
        bar = {"ts": 1000, "close": 100.0}
        out = strat.on_bar(bar)
        self.assertEqual(out, Signal.HOLD)

    def test_same_bar_same_signal(self) -> None:
        strat = ExampleStrategy()
        bar = {"close": 50.0}
        a = strat.on_bar(bar)
        b = strat.on_bar(bar)
        self.assertEqual(a, b)


class TestStrategyEngine(unittest.TestCase):
    """Engine runs strategy on bar; fail-closed on strategy exception."""

    def test_engine_on_bar_returns_signal(self) -> None:
        strat = ExampleStrategy()
        engine = StrategyEngine(strategy=strat)
        bar: Any = {"close": 100}
        signal = engine.on_bar(bar)
        self.assertIn(signal, (Signal.LONG, Signal.SHORT, Signal.HOLD, Signal.EXIT))

    def test_engine_deterministic_same_bar(self) -> None:
        strat = ExampleStrategy()
        engine = StrategyEngine(strategy=strat)
        bar = {"close": 100}
        self.assertEqual(engine.on_bar(bar), engine.on_bar(bar))

    def test_engine_raises_engine_error_on_strategy_failure(self) -> None:
        class FailingStrategy(Strategy):
            def on_bar(self, bar: Any) -> Signal:
                raise ValueError("bad bar")

        engine = StrategyEngine(strategy=FailingStrategy())
        with self.assertRaises(EngineError):
            engine.on_bar({"close": 100})
