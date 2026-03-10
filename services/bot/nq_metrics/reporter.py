# NEBULA-QUANT v1 | nq_metrics reporter

from typing import Any

from nq_metrics.models import MetricsResult


def build_metrics_report(result: MetricsResult) -> dict[str, Any]:
    """
    Build dictionary report for dashboards and monitoring.
    Skeleton: no external APIs or persistence.
    """
    return {
        "win_rate": result.win_rate,
        "profit_factor": result.profit_factor,
        "expectancy": result.expectancy,
        "avg_win": result.avg_win,
        "avg_loss": result.avg_loss,
        "max_drawdown": result.max_drawdown,
        "sharpe_ratio": result.sharpe_ratio,
        "total_trades": result.total_trades,
        "equity_curve_length": len(result.equity_curve),
        "metadata": result.metadata,
    }
