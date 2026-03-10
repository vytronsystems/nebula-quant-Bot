from __future__ import annotations

from typing import Any, Dict, List

from nq_portfolio.models import (
    PortfolioAllocation,
    PortfolioPosition,
    PortfolioSnapshot,
)


# NEBULA-QUANT v1 | nq_portfolio — reporting helpers (skeleton)


def _position_to_dict(position: PortfolioPosition) -> Dict[str, Any]:
    return {
        "position_id": position.position_id,
        "symbol": position.symbol,
        "strategy_id": position.strategy_id,
        "side": position.side,
        "qty": position.qty,
        "avg_price": position.avg_price,
        "market_value": position.market_value,
        "weight": position.weight,
        "unrealized_pnl": position.unrealized_pnl,
        "realized_pnl": position.realized_pnl,
        "opened_ts": position.opened_ts.isoformat()
        if position.opened_ts
        else None,
        "updated_ts": position.updated_ts.isoformat()
        if position.updated_ts
        else None,
        "metadata": dict(position.metadata),
    }


def _allocation_to_dict(allocation: PortfolioAllocation) -> Dict[str, Any]:
    return {
        "strategy_id": allocation.strategy_id,
        "target_weight": allocation.target_weight,
        "allocated_capital": allocation.allocated_capital,
        "used_capital": allocation.used_capital,
        "available_capital": allocation.available_capital,
        "metadata": dict(allocation.metadata),
    }


def build_portfolio_report(snapshot: PortfolioSnapshot) -> Dict[str, Any]:
    """
    Build a dictionary representation of the portfolio snapshot suitable
    for dashboards, monitoring and governance review.
    """
    positions: List[Dict[str, Any]] = [
        _position_to_dict(p) for p in snapshot.positions
    ]
    allocations: List[Dict[str, Any]] = [
        _allocation_to_dict(a) for a in snapshot.allocations
    ]

    report: Dict[str, Any] = {
        "cash": snapshot.cash,
        "equity": snapshot.equity,
        "gross_exposure": snapshot.gross_exposure,
        "net_exposure": snapshot.net_exposure,
        "long_exposure": snapshot.long_exposure,
        "short_exposure": snapshot.short_exposure,
        "positions": positions,
        "allocations": allocations,
        "updated_ts": snapshot.updated_ts.isoformat()
        if snapshot.updated_ts
        else None,
        "metadata": dict(snapshot.metadata),
    }
    return report

