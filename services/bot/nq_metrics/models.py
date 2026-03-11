# NEBULA-QUANT v1 | nq_metrics models

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# --- Observability layer (Phase 17) ---


@dataclass
class MetricRecord:
    """Normalized deterministic metric entry."""

    metric_name: str
    scope: str
    subject_id: str | None
    value: int | float | str | bool
    timestamp_key: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class StrategyHealthSnapshot:
    """Per-strategy health view for observability."""

    strategy_id: str
    lifecycle_state: str = ""
    status: str = "inactive"  # inactive | healthy | warning | degraded
    signals_processed: int = 0
    executions_attempted: int = 0
    executions_approved: int = 0
    executions_blocked: int = 0
    executions_throttled: int = 0
    realized_pnl: float | None = None
    unrealized_pnl: float | None = None
    daily_pnl: float | None = None
    slippage_avg: float | None = None
    drawdown_pct: float | None = None
    win_count: int | None = None
    loss_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionQualitySnapshot:
    """Aggregate execution quality for observability."""

    attempted_orders: int = 0
    approved_orders: int = 0
    blocked_orders: int = 0
    throttled_orders: int = 0
    reject_count: int = 0
    fill_count: int = 0
    avg_requested_notional: float | None = None
    avg_effective_notional: float | None = None
    avg_slippage: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ControlDecisionSnapshot:
    """Aggregate control layer decisions for observability."""

    guardrail_allow_count: int = 0
    guardrail_block_count: int = 0
    portfolio_allow_count: int = 0
    portfolio_block_count: int = 0
    portfolio_throttle_count: int = 0
    promotion_allow_count: int = 0
    promotion_reject_count: int = 0
    invalid_lifecycle_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemObservabilityReport:
    """Deterministic system observability report."""

    strategies: list[StrategyHealthSnapshot] = field(default_factory=list)
    execution_quality: ExecutionQualitySnapshot = field(default_factory=ExecutionQualitySnapshot)
    controls: ControlDecisionSnapshot = field(default_factory=ControlDecisionSnapshot)
    experiment_summary: dict[str, Any] | list[Any] = field(default_factory=dict)
    totals: dict[str, int | float | str] = field(default_factory=dict)
    generated_key: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# --- Input types for report generation (caller supplies from modules) ---


@dataclass
class StrategyHealthInput:
    """Per-strategy input for health snapshot. All optional except strategy_id."""

    strategy_id: str
    lifecycle_state: str = ""
    enabled: bool = True
    signals_processed: int = 0
    executions_attempted: int = 0
    executions_approved: int = 0
    executions_blocked: int = 0
    executions_throttled: int = 0
    realized_pnl: float | None = None
    unrealized_pnl: float | None = None
    daily_pnl: float | None = None
    slippage_avg: float | None = None
    drawdown_pct: float | None = None
    win_count: int | None = None
    loss_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ObservabilityInput:
    """Bundled input for generating SystemObservabilityReport. All optional lists/counts."""

    strategy_health_inputs: list[StrategyHealthInput] = field(default_factory=list)
    execution_attempted: int = 0
    execution_approved: int = 0
    execution_blocked: int = 0
    execution_throttled: int = 0
    execution_reject_count: int = 0
    execution_fill_count: int = 0
    avg_requested_notional: float | None = None
    avg_effective_notional: float | None = None
    avg_slippage: float | None = None
    guardrail_allow_count: int = 0
    guardrail_block_count: int = 0
    portfolio_allow_count: int = 0
    portfolio_block_count: int = 0
    portfolio_throttle_count: int = 0
    promotion_allow_count: int = 0
    promotion_reject_count: int = 0
    invalid_lifecycle_count: int = 0
    experiment_summary_source: dict[str, Any] | list[Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# --- Performance (existing) ---


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
