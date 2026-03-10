# NEBULA-QUANT v1 | nq_metrics models

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TradePerformance:
    """Single trade performance record (skeleton)."""

    trade_id: str
    symbol: str
    entry_price: float
    exit_price: float
    qty: float
    pnl: float
    pnl_pct: float
    holding_time: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricsResult:
    """Aggregate performance metrics (skeleton)."""

    win_rate: float
    profit_factor: float
    expectancy: float
    avg_win: float
    avg_loss: float
    max_drawdown: float
    sharpe_ratio: float
    total_trades: int
    equity_curve: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)
