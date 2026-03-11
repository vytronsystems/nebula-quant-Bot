# NEBULA-QUANT v1 | nq_metrics engine

from __future__ import annotations

from typing import Any

from nq_metrics.models import (
    MetricsResult,
    ObservabilityInput,
    SystemObservabilityReport,
    TradePerformance,
)
from nq_metrics.observability import generate_observability_report
from nq_metrics.calculations import (
    calculate_win_rate,
    calculate_profit_factor,
    calculate_expectancy,
    calculate_average_win,
    calculate_average_loss,
    calculate_sharpe_ratio,
)
from nq_metrics.equity import build_equity_curve, compute_drawdown
from nq_metrics.distribution import build_trade_distribution, compute_trade_statistics


class MetricsEngine:
    """
    Performance analytics layer. Computes trading performance statistics.
    Does not execute trades or connect to brokers. Analyzes performance data only.
    """

    def __init__(self) -> None:
        pass

    def compute_metrics(
        self,
        trades: list[TradePerformance] | None = None,
        initial_equity: float = 0.0,
    ) -> MetricsResult:
        """
        Compute full metrics from trade list. Returns safe defaults for empty input.
        """
        trades = trades or []
        if not trades:
            return MetricsResult(
                win_rate=0.0,
                profit_factor=0.0,
                expectancy=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                total_trades=0,
                equity_curve=[initial_equity] if initial_equity else [0.0],
                metadata={"empty": True},
            )
        return self._compute_from_trades(trades, initial_equity)

    def compute_trade_metrics(
        self,
        trades: list[TradePerformance] | None = None,
    ) -> dict[str, Any]:
        """Compute trade-level metrics (win rate, profit factor, etc.). Safe for empty."""
        trades = trades or []
        if not trades:
            return {"total_trades": 0, "win_rate": 0.0, "profit_factor": 0.0}
        wins = sum(1 for t in trades if t.pnl > 0)
        win_rate = calculate_win_rate(wins, len(trades))
        gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
        gross_loss = sum(t.pnl for t in trades if t.pnl < 0)
        profit_factor = calculate_profit_factor(gross_profit, gross_loss)
        return {
            "total_trades": len(trades),
            "win_rate": win_rate,
            "profit_factor": profit_factor,
        }

    def compute_equity_metrics(
        self,
        trades: list[TradePerformance] | None = None,
        initial_equity: float = 0.0,
    ) -> dict[str, Any]:
        """Compute equity curve and drawdown. Safe for empty."""
        trades = trades or []
        curve = build_equity_curve(trades, initial_equity)
        max_dd = compute_drawdown(curve)
        return {"equity_curve": curve, "max_drawdown": max_dd}

    def compute_distribution_metrics(
        self,
        trades: list[TradePerformance] | None = None,
    ) -> dict[str, Any]:
        """Compute trade distribution and statistics. Safe for empty."""
        trades = trades or []
        dist = build_trade_distribution(trades)
        stats = compute_trade_statistics(trades)
        return {"distribution": dist, "statistics": stats}

    def _compute_from_trades(
        self,
        trades: list[TradePerformance],
        initial_equity: float,
    ) -> MetricsResult:
        """Internal: full metrics from non-empty trade list."""
        wins = sum(1 for t in trades if t.pnl > 0)
        win_rate = calculate_win_rate(wins, len(trades))
        winning_pnls = [t.pnl for t in trades if t.pnl > 0]
        losing_pnls = [t.pnl for t in trades if t.pnl < 0]
        avg_win = calculate_average_win(winning_pnls)
        avg_loss = calculate_average_loss(losing_pnls)
        expectancy = calculate_expectancy(avg_win, avg_loss, win_rate)
        gross_profit = sum(winning_pnls)
        gross_loss = sum(losing_pnls)
        profit_factor = calculate_profit_factor(gross_profit, gross_loss)
        curve = build_equity_curve(trades, initial_equity)
        max_drawdown = compute_drawdown(curve)
        returns = [t.pnl_pct for t in trades] if trades else []
        sharpe_ratio = calculate_sharpe_ratio(returns)
        return MetricsResult(
            win_rate=win_rate,
            profit_factor=profit_factor,
            expectancy=expectancy,
            avg_win=avg_win,
            avg_loss=avg_loss,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            total_trades=len(trades),
            equity_curve=curve,
            metadata={"skeleton": True},
        )

    def generate_observability_report(
        self,
        inp: ObservabilityInput | None,
        generated_key: str = "",
    ) -> SystemObservabilityReport:
        """
        Generate deterministic system observability report from supplied inputs.
        Side-effect free; does not execute trades or change decisions.
        """
        return generate_observability_report(inp, generated_key)
