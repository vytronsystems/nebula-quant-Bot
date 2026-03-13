"""TradeStation adapter models: account, positions, contracts, option selection."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass
class TSAccountSummary:
    """TradeStation account summary (normalized)."""
    account_id: str
    equity: float
    buying_power: float
    cash_balance: float
    meta: dict[str, Any] | None = None


@dataclass
class TSPosition:
    """Single position (option or equity)."""
    symbol: str
    asset_type: str  # Option, Equity, etc.
    quantity: float
    average_price: float
    market_value: float
    meta: dict[str, Any] | None = None


@dataclass
class TSOptionContract:
    """Option contract (strike, expiry, right)."""
    symbol: str
    underlying: str
    expiry: date
    strike: float
    right: str  # Call | Put
    multiplier: int = 100
    meta: dict[str, Any] | None = None

    def dte(self, as_of: date | None = None) -> int:
        """Days to expiry (0 = expiry day)."""
        ref = as_of or date.today()
        return (self.expiry - ref).days


@dataclass
class TSOptionSelectionRequest:
    """Inputs for option selection (long call / long put only)."""
    underlying: str
    direction: str  # call | put
    dte_policy_min: int = 0
    dte_policy_max: int | None = None
    liquidity_min: float | None = None
    max_spread_bps: float | None = None
    max_risk_per_contract: float | None = None
    capital_allocated: float | None = None
    momentum_filter: str | None = None  # e.g. "otm" | "itm" | "atm"
    meta: dict[str, Any] | None = None


@dataclass
class TSOptionSelectionResult:
    """Selected contract(s) and reason."""
    underlying: str
    direction: str
    selected: list[TSOptionContract]
    dte_used: int
    filter_used: dict[str, Any]
    meta: dict[str, Any] | None = None
