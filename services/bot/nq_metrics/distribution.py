# NEBULA-QUANT v1 | nq_metrics distribution (placeholder implementations)

from typing import Any, Sequence

from nq_metrics.models import TradePerformance


def build_trade_distribution(
    trades: Sequence[TradePerformance],
) -> dict[str, Any]:
    """Build trade distribution summary. Returns placeholder for empty."""
    if not trades:
        return {
            "count": 0,
            "by_symbol": {},
            "pnl_buckets": [],
            "skeleton": True,
        }
    by_symbol: dict[str, int] = {}
    for t in trades:
        by_symbol[t.symbol] = by_symbol.get(t.symbol, 0) + 1
    return {
        "count": len(trades),
        "by_symbol": by_symbol,
        "pnl_buckets": [],
        "skeleton": True,
    }


def compute_trade_statistics(
    trades: Sequence[TradePerformance],
) -> dict[str, Any]:
    """Compute trade statistics. Returns placeholder for empty."""
    if not trades:
        return {
            "total_trades": 0,
            "total_pnl": 0.0,
            "wins": 0,
            "losses": 0,
            "skeleton": True,
        }
    wins = sum(1 for t in trades if t.pnl > 0)
    total_pnl = sum(t.pnl for t in trades)
    return {
        "total_trades": len(trades),
        "total_pnl": total_pnl,
        "wins": wins,
        "losses": len(trades) - wins,
        "skeleton": True,
    }
