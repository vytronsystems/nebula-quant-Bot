# NEBULA-QUANT v1 | nq_backtest tests — engine, deterministic results, fail-closed

from __future__ import annotations

import unittest
from typing import Any

from nq_backtest import BacktestConfig, BacktestEngine, BacktestResult


def make_bar(ts: float, close: float) -> dict[str, Any]:
    return {"ts": ts, "close": close, "open": close, "high": close, "low": close, "volume": 100}


def hold_strategy(bar: Any) -> str:
    return "hold"


def long_strategy(bar: Any) -> str:
    return "long"


class TestBacktestEngineInit(unittest.TestCase):
    """Engine initialization."""

    def test_engine_with_config(self) -> None:
        config = BacktestConfig(
            symbol="QQQ",
            timeframe="1d",
            initial_capital=100_000.0,
            commission_per_trade=0.0,
            slippage_bps=0.0,
            start_ts=0.0,
            end_ts=0.0,
            qty=1.0,
        )
        engine = BacktestEngine(config=config)
        self.assertIsNotNone(engine)

    def test_engine_with_kwargs(self) -> None:
        engine = BacktestEngine(symbol="SPY", initial_capital=50_000.0)
        self.assertIsNotNone(engine)


class TestBacktestRun(unittest.TestCase):
    """Engine run produces result; empty input safe."""

    def test_empty_bars_returns_result(self) -> None:
        engine = BacktestEngine()
        result = engine.run(bars=[], strategy=hold_strategy)
        self.assertIsInstance(result, BacktestResult)
        self.assertEqual(result.total_trades, 0)
        self.assertEqual(len(result.trades), 0)

    def test_none_bars_safe(self) -> None:
        engine = BacktestEngine()
        result = engine.run(bars=None, strategy=hold_strategy)
        self.assertEqual(result.total_trades, 0)

    def test_no_strategy_returns_empty_trades(self) -> None:
        engine = BacktestEngine()
        bars = [make_bar(1000.0, 100.0), make_bar(2000.0, 101.0)]
        result = engine.run(bars=bars, strategy=None)
        self.assertEqual(result.total_trades, 0)


class TestDeterminism(unittest.TestCase):
    """Same inputs produce same result."""

    def test_same_bars_same_result(self) -> None:
        engine = BacktestEngine()
        bars = [make_bar(1000.0, 100.0), make_bar(2000.0, 101.0), make_bar(3000.0, 99.0)]
        r1 = engine.run(bars=bars, strategy=long_strategy)
        r2 = engine.run(bars=bars, strategy=long_strategy)
        self.assertEqual(r1.total_trades, r2.total_trades)
        self.assertEqual(r1.net_pnl, r2.net_pnl)

    def test_result_has_expected_fields(self) -> None:
        engine = BacktestEngine()
        result = engine.run(bars=[make_bar(1, 100)], strategy=hold_strategy)
        self.assertIsNotNone(result.config)
        self.assertIsInstance(result.win_rate, float)
        self.assertIsInstance(result.max_drawdown, float)
        self.assertIsInstance(result.equity_curve, list)
