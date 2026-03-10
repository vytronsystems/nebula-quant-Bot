from __future__ import annotations

from typing import Dict, Iterable, Mapping

from nq_portfolio.models import PortfolioAllocation


# NEBULA-QUANT v1 | nq_portfolio — capital allocation helpers (skeleton)


def allocate_capital_by_strategy(
    total_equity: float, strategies: Iterable[str]
) -> Mapping[str, PortfolioAllocation]:
    """
    Very simple placeholder allocator: split equity equally across strategies.

    Safe behavior:
    - On non-positive equity or empty strategies, returns an empty mapping.
    """
    strategy_list = list(strategies)
    if total_equity <= 0.0 or not strategy_list:
        return {}

    per_strategy = total_equity / float(len(strategy_list))
    allocations: Dict[str, PortfolioAllocation] = {}
    for sid in strategy_list:
        allocations[sid] = PortfolioAllocation(
            strategy_id=sid,
            target_weight=1.0 / float(len(strategy_list)),
            allocated_capital=per_strategy,
            available_capital=per_strategy,
        )
    return allocations


def allocate_capital_by_instrument(
    total_capital: float, symbols: Iterable[str]
) -> Mapping[str, float]:
    """
    Placeholder: evenly distribute a given capital bucket across instruments.

    Returns a mapping symbol -> capital amount.
    """
    symbol_list = list(symbols)
    if total_capital <= 0.0 or not symbol_list:
        return {}

    per_symbol = total_capital / float(len(symbol_list))
    return {symbol: per_symbol for symbol in symbol_list}


def compute_target_weight(
    desired_capital: float, portfolio_equity: float
) -> float:
    """
    Compute a simple target weight from desired capital and current equity.

    Safe behavior:
    - If equity is non-positive, returns 0.0 to avoid division errors.
    """
    if portfolio_equity <= 0.0:
        return 0.0
    return desired_capital / portfolio_equity

