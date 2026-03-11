# NEBULA-QUANT v1 | nq_obs — observability integration layer models

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StrategyObservabilitySeed:
    """Normalized per-strategy input for observability. Registry truth overrides caller when available."""

    strategy_id: str
    lifecycle_state: str | None = None
    enabled: bool | None = None
    executions_attempted: int = 0
    executions_approved: int = 0
    executions_blocked: int = 0
    executions_throttled: int = 0
    realized_pnl: float | None = None
    unrealized_pnl: float | None = None
    daily_pnl: float | None = None
    slippage_values: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ObservabilityGatherResult:
    """Deterministic normalized container from module outputs."""

    strategy_inputs: list[StrategyObservabilitySeed] = field(default_factory=list)
    execution_events: list[Any] = field(default_factory=list)
    guardrail_events: list[Any] = field(default_factory=list)
    portfolio_events: list[Any] = field(default_factory=list)
    promotion_events: list[Any] = field(default_factory=list)
    experiment_events: list[Any] = field(default_factory=list)
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


@dataclass
class SystemObservabilityBuilderInput:
    """Normalized structure suitable to convert into nq_metrics ObservabilityInput."""

    strategy_seeds: list[StrategyObservabilitySeed] = field(default_factory=list)
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
    experiment_summary: dict[str, Any] | list[Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
