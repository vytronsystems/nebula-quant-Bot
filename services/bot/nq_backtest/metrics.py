# NEBULA-QUANT v1 | nq_backtest metrics — placeholder, safe defaults

from nq_backtest.models import TradeRecord, EquityPoint


def compute_win_rate(trades: list[TradeRecord]) -> float:
    """Placeholder: win rate. Returns 0.0 if trades empty."""
    if not trades:
        return 0.0
    wins = sum(1 for t in trades if t.pnl > 0)
    return wins / len(trades)


def compute_net_pnl(trades: list[TradeRecord]) -> float:
    """Placeholder: sum of trade PnL. Returns 0.0 if trades empty."""
    if not trades:
        return 0.0
    return sum(t.pnl for t in trades)


def compute_max_drawdown(equity_curve: list[EquityPoint]) -> float:
    """
    Placeholder: max drawdown from equity curve.
    Returns 0.0 if curve empty or single point.
    """
    if len(equity_curve) < 2:
        return 0.0
    equities = [e.equity for e in equity_curve]
    peak = equities[0]
    max_dd = 0.0
    for eq in equities:
        if eq > peak:
            peak = eq
        dd = peak - eq
        if dd > max_dd:
            max_dd = dd
    return max_dd


def compute_basic_stats(trades: list[TradeRecord]) -> dict[str, float]:
    """
    Placeholder: basic stats dict. Safe defaults when trades empty.
    """
    if not trades:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "gross_pnl": 0.0,
            "net_pnl": 0.0,
        }
    wins = sum(1 for t in trades if t.pnl > 0)
    losses = len(trades) - wins
    gross = sum(t.pnl for t in trades)
    return {
        "total_trades": len(trades),
        "wins": wins,
        "losses": losses,
        "win_rate": wins / len(trades),
        "gross_pnl": gross,
        "net_pnl": gross,
    }
