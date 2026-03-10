from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


# NEBULA-QUANT v1 | nq_portfolio — portfolio state models (skeleton)


@dataclass(slots=True)
class PortfolioPosition:
    """Represents a single open position in the portfolio."""

    position_id: str
    symbol: str
    strategy_id: str
    side: str  # LONG / SHORT / FLAT, left as free-form for now
    qty: float
    avg_price: float
    market_value: float = 0.0
    weight: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    opened_ts: Optional[datetime] = None
    updated_ts: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PortfolioAllocation:
    """Capital allocation state per strategy."""

    strategy_id: str
    target_weight: float = 0.0
    allocated_capital: float = 0.0
    used_capital: float = 0.0
    available_capital: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PortfolioSnapshot:
    """Point-in-time view of the full portfolio state."""

    cash: float = 0.0
    equity: float = 0.0
    gross_exposure: float = 0.0
    net_exposure: float = 0.0
    long_exposure: float = 0.0
    short_exposure: float = 0.0
    positions: List[PortfolioPosition] = field(default_factory=list)
    allocations: List[PortfolioAllocation] = field(default_factory=list)
    updated_ts: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PortfolioDecision:
    """Result of a portfolio-level decision for a requested position change."""

    allowed: bool
    reason: str
    adjusted_qty: float = 0.0
    adjusted_weight: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

