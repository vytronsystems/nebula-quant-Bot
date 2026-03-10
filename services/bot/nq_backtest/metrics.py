# NEBULA-QUANT v1 | nq_backtest metrics — real calculations, safe on empty input

from __future__ import annotations

from nq_backtest.models import EquityPoint, TradeRecord


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
    Max drawdown from equity curve.
    Returns 0.0 if curve empty or single point.
    """
    if len(equity_curve) < 2:
        return 0.0
    peak = equity_curve[0].equity
    max_dd = 0.0
    for e in equity_curve:
        if e.equity > peak:
            peak = e.equity
        dd = peak - e.equity
        if dd > max_dd:
            max_dd = dd
    return max_dd


def compute_sharpe_like(
    equity_curve: list[EquityPoint],
    periods_per_year: float = 252.0,
) -> float:
    """
    Sharpe-like ratio from equity curve: annualized return / volatility of returns.
    Uses simple period-to-period returns. Returns 0.0 if insufficient data or zero std.
    """
    if len(equity_curve) < 2:
        return 0.0
    equities = [e.equity for e in equity_curve]
    returns: list[float] = []
    for i in range(1, len(equities)):
        prev = equities[i - 1]
        curr = equities[i]
        if prev <= 0:
            continue
        ret = (curr - prev) / prev
        returns.append(ret)
    if not returns:
        return 0.0
    mean_ret = sum(returns) / len(returns)
    variance = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
    std = variance ** 0.5
    if std <= 0:
        return 0.0
    # Annualize: scale by sqrt(periods_per_year) for volatility
    return (mean_ret / std) * (periods_per_year ** 0.5)


def compute_basic_stats(trades: list[TradeRecord]) -> dict[str, float]:
    """
    Basic stats dict from trade list. Safe defaults when trades empty.
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
    net_pnl = sum(t.pnl for t in trades)
    gross_pnl = 0.0
    for t in trades:
        if t.side == "long":
            gross_pnl += (t.exit_price - t.entry_price) * t.qty
        else:
            gross_pnl += (t.entry_price - t.exit_price) * t.qty
    return {
        "total_trades": len(trades),
        "wins": wins,
        "losses": losses,
        "win_rate": wins / len(trades),
        "gross_pnl": gross_pnl,
        "net_pnl": net_pnl,
    }
