from __future__ import annotations

from typing import Iterable, Tuple

from nq_portfolio.models import PortfolioPosition
from nq_portfolio.config import (
    DEFAULT_MAX_GROSS_EXPOSURE,
    DEFAULT_MAX_NET_EXPOSURE,
    DEFAULT_MAX_POSITIONS,
    DEFAULT_MAX_STRATEGY_WEIGHT,
    DEFAULT_MAX_SYMBOL_WEIGHT,
)


# NEBULA-QUANT v1 | nq_portfolio — constraint checks (skeleton)


def check_max_strategy_weight(
    current_weight: float,
    max_weight: float = DEFAULT_MAX_STRATEGY_WEIGHT,
) -> Tuple[bool, str]:
    """
    Check that a strategy's portfolio weight does not exceed the maximum.

    Returns (allowed, reason).
    """
    if current_weight <= max_weight:
        return True, "strategy weight within limit"
    return False, "strategy weight exceeds max limit"


def check_max_symbol_weight(
    current_weight: float,
    max_weight: float = DEFAULT_MAX_SYMBOL_WEIGHT,
) -> Tuple[bool, str]:
    """Check that a symbol's weight is within configured bounds."""
    if current_weight <= max_weight:
        return True, "symbol weight within limit"
    return False, "symbol weight exceeds max limit"


def check_max_gross_exposure(
    gross_exposure: float,
    equity: float,
    max_ratio: float = DEFAULT_MAX_GROSS_EXPOSURE,
) -> Tuple[bool, str]:
    """Check gross exposure as a fraction of equity."""
    if equity <= 0.0:
        # Fail-closed: no exposure allowed without positive equity baseline.
        if gross_exposure == 0.0:
            return True, "no exposure with non-positive equity"
        return False, "non-positive equity with non-zero gross exposure"

    ratio = gross_exposure / equity
    if ratio <= max_ratio:
        return True, "gross exposure within limit"
    return False, "gross exposure exceeds max limit"


def check_max_net_exposure(
    net_exposure: float,
    equity: float,
    max_ratio: float = DEFAULT_MAX_NET_EXPOSURE,
) -> Tuple[bool, str]:
    """Check absolute net exposure as a fraction of equity."""
    if equity <= 0.0:
        if net_exposure == 0.0:
            return True, "no net exposure with non-positive equity"
        return False, "non-positive equity with non-zero net exposure"

    ratio = abs(net_exposure) / equity
    if ratio <= max_ratio:
        return True, "net exposure within limit"
    return False, "net exposure exceeds max limit"


def check_max_positions(
    positions: Iterable[PortfolioPosition],
    max_positions: int = DEFAULT_MAX_POSITIONS,
) -> Tuple[bool, str]:
    """Check that the number of open positions does not exceed the maximum."""
    count = len(list(positions))
    if count <= max_positions:
        return True, "position count within limit"
    return False, "position count exceeds max limit"

