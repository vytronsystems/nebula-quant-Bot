# NEBULA-QUANT v1 | nq_backtest reporter — summary for reports/dashboards

from typing import Any

from nq_backtest.models import BacktestResult


def build_backtest_summary(result: BacktestResult) -> dict[str, Any]:
    """
    Build a dictionary of summary statistics for reports, walk-forward, dashboards.
    """
    return {
        "symbol": result.config.symbol,
        "timeframe": result.config.timeframe,
        "total_trades": result.total_trades,
        "wins": result.wins,
        "losses": result.losses,
        "win_rate": result.win_rate,
        "gross_pnl": result.gross_pnl,
        "net_pnl": result.net_pnl,
        "max_drawdown": result.max_drawdown,
        "sharpe_like": result.sharpe_like,
        "initial_capital": result.config.initial_capital,
        "metadata": result.metadata,
    }
