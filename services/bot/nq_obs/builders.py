# NEBULA-QUANT v1 | nq_obs — build nq_metrics-compatible ObservabilityInput

from __future__ import annotations

from nq_metrics.models import ObservabilityInput, StrategyHealthInput
from nq_obs.models import StrategyObservabilitySeed, SystemObservabilityBuilderInput


def seed_to_health_input(seed: StrategyObservabilitySeed) -> StrategyHealthInput:
    """Convert StrategyObservabilitySeed to nq_metrics StrategyHealthInput. No fabrication."""
    return StrategyHealthInput(
        strategy_id=seed.strategy_id,
        lifecycle_state=seed.lifecycle_state or "",
        enabled=seed.enabled if seed.enabled is not None else True,
        signals_processed=0,
        executions_attempted=seed.executions_attempted,
        executions_approved=seed.executions_approved,
        executions_blocked=seed.executions_blocked,
        executions_throttled=seed.executions_throttled,
        realized_pnl=seed.realized_pnl,
        unrealized_pnl=seed.unrealized_pnl,
        daily_pnl=seed.daily_pnl,
        slippage_avg=(sum(seed.slippage_values) / len(seed.slippage_values)) if seed.slippage_values else None,
        metadata=seed.metadata or {},
    )


def build_observability_input(builder_input: SystemObservabilityBuilderInput | None) -> ObservabilityInput:
    """
    Convert SystemObservabilityBuilderInput to nq_metrics ObservabilityInput.
    Deterministic; missing data remains omitted (0, None, empty).
    """
    if builder_input is None:
        return ObservabilityInput(metadata={"omission": "no_builder_input"})

    strategy_health_inputs = [seed_to_health_input(s) for s in (builder_input.strategy_seeds or [])]
    return ObservabilityInput(
        strategy_health_inputs=strategy_health_inputs,
        execution_attempted=builder_input.execution_attempted,
        execution_approved=builder_input.execution_approved,
        execution_blocked=builder_input.execution_blocked,
        execution_throttled=builder_input.execution_throttled,
        execution_reject_count=builder_input.execution_reject_count,
        execution_fill_count=builder_input.execution_fill_count,
        avg_requested_notional=builder_input.avg_requested_notional,
        avg_effective_notional=builder_input.avg_effective_notional,
        avg_slippage=builder_input.avg_slippage,
        guardrail_allow_count=builder_input.guardrail_allow_count,
        guardrail_block_count=builder_input.guardrail_block_count,
        portfolio_allow_count=builder_input.portfolio_allow_count,
        portfolio_block_count=builder_input.portfolio_block_count,
        portfolio_throttle_count=builder_input.portfolio_throttle_count,
        promotion_allow_count=builder_input.promotion_allow_count,
        promotion_reject_count=builder_input.promotion_reject_count,
        invalid_lifecycle_count=builder_input.invalid_lifecycle_count,
        experiment_summary_source=builder_input.experiment_summary if builder_input.experiment_summary else None,
        metadata=builder_input.metadata or {},
    )
