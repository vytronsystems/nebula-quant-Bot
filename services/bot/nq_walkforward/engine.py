# NEBULA-QUANT v1 | nq_walkforward engine — real walk-forward validation

from __future__ import annotations

from typing import Any, Sequence

from nq_backtest import BacktestConfig, BacktestEngine
from nq_backtest.reporter import build_backtest_summary

from nq_walkforward.config import (
    DEFAULT_MAX_TEST_DRAWDOWN,
    DEFAULT_MAX_TEST_TRAIN_DIVERGENCE,
    DEFAULT_MIN_TEST_NET_PNL,
    DEFAULT_MIN_TEST_TRADES,
    DEFAULT_TEST_WINDOWS,
    DEFAULT_TRAIN_WINDOWS,
)
from nq_walkforward.models import (
    WalkForwardConfig,
    WalkForwardResult,
    WalkForwardWindowResult,
)
from nq_walkforward.splitter import build_windows


def _evaluate_pass_fail(
    train_summary: dict[str, Any],
    test_summary: dict[str, Any],
    min_test_trades: int,
    min_test_net_pnl: float,
    max_test_drawdown: float,
    max_divergence: float,
) -> tuple[bool, str]:
    """Deterministic pass/fail for one window. Returns (passed, notes)."""
    test_trades = test_summary.get("total_trades", 0)
    test_net_pnl = test_summary.get("net_pnl", 0.0)
    test_dd = test_summary.get("max_drawdown", 0.0)
    train_net_pnl = train_summary.get("net_pnl", 0.0)

    if test_trades < min_test_trades:
        return False, f"test total_trades {test_trades} < {min_test_trades}"
    if test_net_pnl < min_test_net_pnl:
        return False, f"test net_pnl {test_net_pnl} below minimum {min_test_net_pnl}"
    if test_dd > max_test_drawdown:
        return False, f"test max_drawdown {test_dd} exceeds {max_test_drawdown}"

    # Catastrophic divergence: train profitable but test loses more than allowed multiple
    if train_net_pnl > 0 and test_net_pnl < -max_divergence * train_net_pnl:
        return False, f"train/test divergence: train_pnl={train_net_pnl} test_pnl={test_net_pnl}"

    return True, "pass"


class WalkForwardEngine:
    """
    Real walk-forward engine: builds train/test windows, runs nq_backtest per window,
    evaluates pass/fail, aggregates WalkForwardResult.
    """

    def __init__(
        self,
        train_size: int | None = None,
        test_size: int | None = None,
        symbol: str = "QQQ",
        timeframe: str = "1d",
        initial_capital: float = 100_000.0,
        min_test_trades: int | None = None,
        min_test_net_pnl: float | None = None,
        max_test_drawdown: float | None = None,
        max_test_train_divergence: float | None = None,
        **kwargs: Any,
    ) -> None:
        self._train_size = train_size if train_size is not None else DEFAULT_TRAIN_WINDOWS
        self._test_size = test_size if test_size is not None else DEFAULT_TEST_WINDOWS
        self._symbol = symbol
        self._timeframe = timeframe
        self._initial_capital = float(initial_capital)
        self._min_test_trades = (
            min_test_trades if min_test_trades is not None else DEFAULT_MIN_TEST_TRADES
        )
        self._min_test_net_pnl = (
            min_test_net_pnl if min_test_net_pnl is not None else DEFAULT_MIN_TEST_NET_PNL
        )
        self._max_test_drawdown = (
            max_test_drawdown
            if max_test_drawdown is not None
            else DEFAULT_MAX_TEST_DRAWDOWN
        )
        self._max_divergence = (
            max_test_train_divergence
            if max_test_train_divergence is not None
            else DEFAULT_MAX_TEST_TRAIN_DIVERGENCE
        )
        self._kwargs = kwargs
        self._window_results: list[WalkForwardWindowResult] = []

    def run(
        self,
        bars: Sequence[Any] | None = None,
        strategy: Any = None,
    ) -> WalkForwardResult:
        """
        Run walk-forward validation: build windows, run backtest on each train/test pair,
        evaluate pass/fail, return aggregated result. Empty or too-small bars returns safe empty result.
        """
        self._validate_inputs(bars, strategy)
        self._window_results = []
        bar_list = list(bars or [])
        if not bar_list or strategy is None:
            return self._build_result()

        windows = build_windows(
            bar_list,
            train_size=self._train_size,
            test_size=self._test_size,
            symbol=self._symbol,
            timeframe=self._timeframe,
        )
        for wf_config, train_bars, test_bars in windows:
            wr = self._run_window(wf_config, train_bars, test_bars, strategy)
            self._window_results.append(wr)
        return self._build_result()

    def _validate_inputs(
        self,
        bars: Sequence[Any] | None,
        strategy: Any,
    ) -> None:
        """No-op; empty/small input handled in run() without raising."""
        pass

    def _run_window(
        self,
        wf_config: WalkForwardConfig,
        train_bars: list[Any],
        test_bars: list[Any],
        strategy: Any,
    ) -> WalkForwardWindowResult:
        """Run backtest on train and test bars; evaluate pass/fail."""
        # Use start_ts=0, end_ts=0 so backtest uses all bars in the slice (no time filter)
        bc = BacktestConfig(
            symbol=self._symbol,
            timeframe=self._timeframe,
            initial_capital=self._initial_capital,
            commission_per_trade=0.0,
            slippage_bps=0.0,
            start_ts=0.0,
            end_ts=0.0,
            qty=1.0,
        )
        engine = BacktestEngine(config=bc)
        train_result = engine.run(bars=train_bars, strategy=strategy)
        test_result = engine.run(bars=test_bars, strategy=strategy)
        train_summary = build_backtest_summary(train_result)
        test_summary = build_backtest_summary(test_result)

        passed, notes = _evaluate_pass_fail(
            train_summary,
            test_summary,
            min_test_trades=self._min_test_trades,
            min_test_net_pnl=self._min_test_net_pnl,
            max_test_drawdown=self._max_test_drawdown,
            max_divergence=self._max_divergence,
        )
        return WalkForwardWindowResult(
            config=wf_config,
            train_summary=train_summary,
            test_summary=test_summary,
            passed=passed,
            notes=notes,
        )

    def _build_result(self) -> WalkForwardResult:
        """Aggregate window results into WalkForwardResult."""
        results = getattr(self, "_window_results", [])
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        pass_rate = (passed / total) if total else 0.0
        return WalkForwardResult(
            windows=results,
            total_windows=total,
            passed_windows=passed,
            failed_windows=failed,
            pass_rate=pass_rate,
            metadata={"engine": "nq_walkforward", "version": "real"},
        )
