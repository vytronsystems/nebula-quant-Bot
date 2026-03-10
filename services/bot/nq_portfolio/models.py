from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# NEBULA-QUANT v1 | nq_portfolio — portfolio state and governance models


class PortfolioDecisionType(str, Enum):
    """Final portfolio gate decision before nq_exec."""

    ALLOW = "allow"
    THROTTLE = "throttle"
    BLOCK = "block"


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
    """Result of the portfolio approval gate (final gate before nq_exec)."""

    decision: PortfolioDecisionType
    reason_codes: List[str]
    message: str
    throttle_ratio: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})

    @property
    def allowed(self) -> bool:
        """True only when decision is ALLOW (backward compat)."""
        return self.decision == PortfolioDecisionType.ALLOW

    @property
    def reason(self) -> str:
        """Alias for message (backward compat)."""
        return self.message


# --- Governance models (portfolio risk engine) ---


@dataclass(slots=True)
class PortfolioLimits:
    """Portfolio and strategy limits for the approval gate."""

    max_portfolio_capital_usage_pct: float = 0.95
    max_strategy_capital_usage_pct: float = 0.25
    max_open_positions_total: int = 50
    max_open_positions_per_strategy: int = 10
    max_daily_drawdown_pct: float = 0.05
    max_strategy_drawdown_pct: float = 0.10
    warning_capital_usage_pct: float = 0.80
    warning_open_positions_pct: float = 0.85
    warning_drawdown_pct: float = 0.03


@dataclass(slots=True)
class StrategyAllocation:
    """Per-strategy allocation and execution eligibility."""

    strategy_id: str
    allocated_capital: float = 0.0
    used_capital: float = 0.0
    max_positions: int = 10
    strategy_enabled: bool = True
    strategy_lifecycle_state: str = "paper"  # paper | live only for execution


@dataclass(slots=True)
class PositionSnapshot:
    """Snapshot of a single open position for governance."""

    position_id: str
    strategy_id: str
    symbol: str
    notional_value: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0


@dataclass(slots=True)
class PortfolioState:
    """Current portfolio state for the approval gate."""

    portfolio_equity: float = 0.0
    cash_available: float = 0.0
    open_positions: List[PositionSnapshot] = field(default_factory=list)
    strategy_allocations: List[StrategyAllocation] = field(default_factory=list)
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    daily_pnl: float = 0.0
    strategy_daily_pnl: Dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class OrderIntent:
    """Order intent to be evaluated by the portfolio gate."""

    strategy_id: str
    symbol: str
    requested_notional: float = 0.0
    requested_quantity: float = 0.0
    side: str = ""
    timestamp: float = 0.0

