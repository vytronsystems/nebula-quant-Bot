# NEBULA-QUANT v1 | nq_metrics calculations (placeholder implementations)

from typing import Sequence


def calculate_win_rate(wins: int, total: int) -> float:
    """Placeholder: win rate. Returns safe default for empty/zero total."""
    if total <= 0:
        return 0.0
    return wins / total


def calculate_profit_factor(gross_profit: float, gross_loss: float) -> float:
    """Placeholder: profit factor. Returns safe default."""
    if gross_loss == 0:
        return 1.0 if gross_profit >= 0 else 0.0
    return gross_profit / abs(gross_loss)


def calculate_expectancy(avg_win: float, avg_loss: float, win_rate: float) -> float:
    """Placeholder: expectancy. Returns safe default."""
    return win_rate * avg_win + (1.0 - win_rate) * avg_loss


def calculate_average_win(winning_pnls: Sequence[float]) -> float:
    """Placeholder: average win. Returns 0.0 for empty."""
    if not winning_pnls:
        return 0.0
    return sum(winning_pnls) / len(winning_pnls)


def calculate_average_loss(losing_pnls: Sequence[float]) -> float:
    """Placeholder: average loss. Returns 0.0 for empty."""
    if not losing_pnls:
        return 0.0
    return sum(losing_pnls) / len(losing_pnls)


def calculate_sharpe_ratio(
    returns: Sequence[float],
    risk_free_rate: float = 0.05,
    annualize: bool = True,
) -> float:
    """Placeholder: Sharpe ratio. Returns 0.0 for empty or insufficient data."""
    if not returns or len(returns) < 2:
        return 0.0
    mean_ret = sum(returns) / len(returns)
    variance = sum((r - mean_ret) ** 2 for r in returns) / (len(returns) - 1)
    if variance <= 0:
        return 0.0
    std = variance**0.5
    sharpe = (mean_ret - risk_free_rate / 252) / std if std else 0.0
    if annualize and sharpe != 0:
        sharpe = sharpe * (252**0.5)
    return sharpe
