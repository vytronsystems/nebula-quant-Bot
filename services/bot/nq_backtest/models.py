# NEBULA-QUANT v1 | nq_backtest models

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BacktestConfig:
    """Configuration for a single backtest run."""

    symbol: str
    timeframe: str
    initial_capital: float
    commission_per_trade: float
    slippage_bps: float
    start_ts: float
    end_ts: float
    qty: float = 1.0  # default position size per trade


@dataclass
class TradeRecord:
    """Single closed trade from backtest."""

    entry_ts: float
    exit_ts: float
    side: str
    entry_price: float
    exit_price: float
    qty: float
    pnl: float
    pnl_pct: float
    reason: str


@dataclass
class EquityPoint:
    """One point on the equity curve."""

    ts: float
    equity: float
    drawdown: float


@dataclass
class BacktestResult:
    """Aggregate result of a backtest run."""

    config: BacktestConfig
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    gross_pnl: float
    net_pnl: float
    max_drawdown: float
    sharpe_like: float
    trades: list[TradeRecord]
    equity_curve: list[EquityPoint]
    metadata: dict[str, Any] = field(default_factory=dict)
