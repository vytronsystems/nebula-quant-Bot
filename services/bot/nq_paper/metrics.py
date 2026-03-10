# NEBULA-QUANT v1 | nq_paper metrics — real calculations, safe on empty input

from __future__ import annotations

from nq_paper.models import PaperTrade


def compute_paper_win_rate(trades: list[PaperTrade]) -> float:
    """Win rate from closed paper trades. Returns 0.0 if trades empty."""
    if not trades:
        return 0.0
    wins = sum(1 for t in trades if t.pnl > 0)
    return wins / len(trades)


def compute_paper_net_pnl(trades: list[PaperTrade]) -> float:
    """Sum of trade PnL. Returns 0.0 if trades empty."""
    if not trades:
        return 0.0
    return sum(t.pnl for t in trades)


def compute_paper_drawdown(equity_curve: list[tuple[float, float]]) -> float:
    """
    Max drawdown from (ts, equity) pairs.
    Returns 0.0 if curve empty or single point.
    """
    if len(equity_curve) < 2:
        return 0.0
    equities = [e[1] for e in equity_curve]
    peak = equities[0]
    max_dd = 0.0
    for eq in equities:
        if eq > peak:
            peak = eq
        dd = peak - eq
        if dd > max_dd:
            max_dd = dd
    return max_dd


def compute_paper_basic_stats(trades: list[PaperTrade]) -> dict[str, float]:
    """Basic stats from closed paper trades. Safe defaults when trades empty."""
    if not trades:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "net_pnl": 0.0,
        }
    wins = sum(1 for t in trades if t.pnl > 0)
    losses = len(trades) - wins
    return {
        "total_trades": len(trades),
        "wins": wins,
        "losses": losses,
        "win_rate": wins / len(trades),
        "net_pnl": sum(t.pnl for t in trades),
    }
