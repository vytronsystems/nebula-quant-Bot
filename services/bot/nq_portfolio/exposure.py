from __future__ import annotations

from typing import Iterable, Mapping, Dict, Any

from nq_portfolio.models import PortfolioPosition


# NEBULA-QUANT v1 | nq_portfolio — exposure computation helpers (skeleton)


def compute_gross_exposure(positions: Iterable[PortfolioPosition]) -> float:
    """Sum of absolute market values; returns 0.0 on empty input."""
    return sum(abs(p.market_value) for p in positions)


def compute_net_exposure(positions: Iterable[PortfolioPosition]) -> float:
    """Net market value (long minus short)."""
    return sum(p.market_value for p in positions)


def compute_long_exposure(positions: Iterable[PortfolioPosition]) -> float:
    """Sum of positive market values."""
    return sum(max(p.market_value, 0.0) for p in positions)


def compute_short_exposure(positions: Iterable[PortfolioPosition]) -> float:
    """Sum of absolute values of negative market values."""
    return sum(abs(min(p.market_value, 0.0)) for p in positions)


def build_exposure_summary(
    positions: Iterable[PortfolioPosition],
) -> Mapping[str, float]:
    """
    Build a basic exposure summary from a collection of positions.

    Returns a mapping with keys:
    - gross_exposure
    - net_exposure
    - long_exposure
    - short_exposure
    """
    positions_list = list(positions)
    gross = compute_gross_exposure(positions_list)
    net = compute_net_exposure(positions_list)
    long = compute_long_exposure(positions_list)
    short = compute_short_exposure(positions_list)

    summary: Dict[str, float] = {
        "gross_exposure": gross,
        "net_exposure": net,
        "long_exposure": long,
        "short_exposure": short,
    }
    return summary

