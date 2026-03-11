# NEBULA-QUANT v1 | nq_risk — risk decision engine domain models

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class RiskDecisionType(str, Enum):
    """Risk evaluation outcome: allow, reduce size, or block."""

    ALLOW = "allow"
    REDUCE = "reduce"
    BLOCK = "block"


@dataclass
class RiskDecisionResult:
    """Result of risk evaluation. Deterministic, fail-closed."""

    decision: RiskDecisionType
    reason_codes: list[str]
    message: str
    approved_quantity: float | None = None
    approved_notional: float | None = None
    risk_amount: float | None = None
    risk_pct: float | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


@dataclass
class RiskLimits:
    """Risk policy limits for the decision engine."""

    max_risk_per_trade_pct: float = 0.02
    max_daily_strategy_risk_pct: float | None = None
    max_daily_account_risk_pct: float | None = None
    require_stop_loss: bool = False
    max_stop_distance_pct: float | None = None
    warning_risk_per_trade_pct: float | None = None


@dataclass
class RiskContext:
    """Context for risk evaluation (account, strategy, daily PnL)."""

    account_equity: float
    strategy_id: str
    strategy_daily_realized_pnl: float | None = None
    account_daily_realized_pnl: float | None = None
    strategy_lifecycle_state: str | None = None
    symbol: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


@dataclass
class RiskOrderIntent:
    """Order intent to be evaluated by the risk engine."""

    strategy_id: str
    symbol: str
    side: str
    entry_price: float | None = None
    stop_loss_price: float | None = None
    requested_quantity: float | None = None
    requested_notional: float | None = None
    timestamp: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})
