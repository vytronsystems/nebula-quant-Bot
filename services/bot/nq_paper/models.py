# NEBULA-QUANT v1 | nq_paper models

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PaperTrade:
    """Single paper trade (open or closed)."""

    trade_id: str
    symbol: str
    side: str
    qty: float
    entry_ts: float
    entry_price: float
    exit_ts: float
    exit_price: float
    status: str
    pnl: float
    pnl_pct: float
    reason: str
    strategy_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PaperPosition:
    """Open paper position."""

    symbol: str
    side: str
    qty: float
    avg_price: float
    opened_ts: float
    unrealized_pnl: float
    realized_pnl: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PaperAccountState:
    """Paper account snapshot."""

    cash: float
    equity: float
    used_buying_power: float
    available_buying_power: float
    open_positions: list[PaperPosition]
    closed_trades: list[PaperTrade]
    updated_ts: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PaperSessionResult:
    """Result of a paper trading session."""

    session_id: str
    started_ts: float
    ended_ts: float
    trades: list[PaperTrade]
    positions: list[PaperPosition]
    account_state: PaperAccountState
    summary: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
