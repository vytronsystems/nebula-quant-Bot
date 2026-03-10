# NEBULA-QUANT v1 | nq_metrics equity (placeholder implementations)

from typing import Sequence

from nq_metrics.models import TradePerformance


def build_equity_curve(
    trades: Sequence[TradePerformance],
    initial_equity: float = 0.0,
) -> list[float]:
    """Build cumulative equity curve from trades. Returns [initial_equity] for empty."""
    if not trades:
        return [initial_equity] if initial_equity != 0 else [0.0]
    curve: list[float] = [initial_equity]
    cum = initial_equity
    for t in trades:
        cum += t.pnl
        curve.append(cum)
    return curve


def compute_drawdown(equity_curve: Sequence[float]) -> float:
    """Compute max drawdown from equity curve (peak-to-trough). Returns 0.0 for empty."""
    if not equity_curve or len(equity_curve) < 2:
        return 0.0
    peak = equity_curve[0]
    max_dd = 0.0
    for eq in equity_curve:
        if eq > peak:
            peak = eq
        dd = peak - eq
        if dd > max_dd:
            max_dd = dd
    return max_dd
