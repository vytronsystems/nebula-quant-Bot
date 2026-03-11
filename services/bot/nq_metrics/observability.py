# NEBULA-QUANT v1 | nq_metrics — observability and system metrics layer
# Deterministic, side-effect free. Does not execute trades or change decisions.

from __future__ import annotations

from nq_metrics.models import (
    ControlDecisionSnapshot,
    ExecutionQualitySnapshot,
    ObservabilityInput,
    StrategyHealthInput,
    StrategyHealthSnapshot,
    SystemObservabilityReport,
)


# Execution-compatible lifecycle states (paper, live only)
_EXECUTABLE_STATES = frozenset({"paper", "live"})
_INACTIVE_STATES = frozenset({"disabled", "retired", "rejected", ""})


def classify_strategy_health(inp: StrategyHealthInput) -> str:
    """
    Deterministic strategy health classification: inactive | healthy | warning | degraded.
    Rule-based and reproducible. Does not invent values.
    """
    if not inp.strategy_id or not str(inp.strategy_id).strip():
        return "inactive"
    state = (inp.lifecycle_state or "").strip().lower()
    if state in _INACTIVE_STATES or not inp.enabled:
        return "inactive"
    if state not in _EXECUTABLE_STATES and inp.signals_processed == 0 and inp.executions_attempted == 0:
        return "inactive"

    blocked = inp.executions_blocked or 0
    throttled = inp.executions_throttled or 0
    attempted = inp.executions_attempted or 0
    approved = inp.executions_approved or 0
    drawdown = inp.drawdown_pct if inp.drawdown_pct is not None else 0.0
    daily_pnl = inp.daily_pnl if inp.daily_pnl is not None else 0.0

    # degraded: repeated blocks, or high drawdown, or strong deterioration
    if attempted > 0 and blocked >= max(3, attempted // 2):
        return "degraded"
    if drawdown >= 0.10:  # 10%+ drawdown
        return "degraded"
    if attempted >= 5 and approved == 0:
        return "degraded"

    # warning: elevated blocks/throttles or mild degradation
    if attempted > 0 and (throttled >= max(2, attempted // 3) or blocked >= 1):
        return "warning"
    if drawdown >= 0.03 and drawdown < 0.10:
        return "warning"
    if daily_pnl < 0 and attempted >= 3:
        return "warning"

    return "healthy"


def _safe_int(x: int | None) -> int:
    return x if x is not None else 0


def _safe_float(x: float | None) -> float | None:
    return x


def build_strategy_health_snapshots(
    inputs: list[StrategyHealthInput] | None,
) -> list[StrategyHealthSnapshot]:
    """Build strategy health snapshots from inputs. Malformed entries skipped with omission in metadata."""
    if inputs is None:
        return []
    snapshots: list[StrategyHealthSnapshot] = []
    for inp in inputs:
        if not isinstance(inp, StrategyHealthInput):
            continue
        sid = getattr(inp, "strategy_id", None)
        if not sid or not str(sid).strip():
            continue
        status = classify_strategy_health(inp)
        snapshots.append(
            StrategyHealthSnapshot(
                strategy_id=str(sid).strip(),
                lifecycle_state=(getattr(inp, "lifecycle_state", None) or "").strip().lower(),
                status=status,
                signals_processed=_safe_int(getattr(inp, "signals_processed", None)),
                executions_attempted=_safe_int(getattr(inp, "executions_attempted", None)),
                executions_approved=_safe_int(getattr(inp, "executions_approved", None)),
                executions_blocked=_safe_int(getattr(inp, "executions_blocked", None)),
                executions_throttled=_safe_int(getattr(inp, "executions_throttled", None)),
                realized_pnl=_safe_float(getattr(inp, "realized_pnl", None)),
                unrealized_pnl=_safe_float(getattr(inp, "unrealized_pnl", None)),
                daily_pnl=_safe_float(getattr(inp, "daily_pnl", None)),
                slippage_avg=_safe_float(getattr(inp, "slippage_avg", None)),
                drawdown_pct=_safe_float(getattr(inp, "drawdown_pct", None)),
                win_count=getattr(inp, "win_count", None),
                loss_count=getattr(inp, "loss_count", None),
                metadata=getattr(inp, "metadata", None) or {},
            )
        )
    return snapshots


def build_execution_quality_snapshot(inp: ObservabilityInput | None) -> ExecutionQualitySnapshot:
    """Aggregate execution quality from ObservabilityInput. Missing values left as 0 or None."""
    if inp is None:
        return ExecutionQualitySnapshot(metadata={"omission": "no_input"})
    return ExecutionQualitySnapshot(
        attempted_orders=getattr(inp, "execution_attempted", 0) or 0,
        approved_orders=getattr(inp, "execution_approved", 0) or 0,
        blocked_orders=getattr(inp, "execution_blocked", 0) or 0,
        throttled_orders=getattr(inp, "execution_throttled", 0) or 0,
        reject_count=getattr(inp, "execution_reject_count", 0) or 0,
        fill_count=getattr(inp, "execution_fill_count", 0) or 0,
        avg_requested_notional=_safe_float(getattr(inp, "avg_requested_notional", None)),
        avg_effective_notional=_safe_float(getattr(inp, "avg_effective_notional", None)),
        avg_slippage=_safe_float(getattr(inp, "avg_slippage", None)),
        metadata=getattr(inp, "metadata", None) or {},
    )


def build_control_decision_snapshot(inp: ObservabilityInput | None) -> ControlDecisionSnapshot:
    """Aggregate control layer counts from ObservabilityInput."""
    if inp is None:
        return ControlDecisionSnapshot(metadata={"omission": "no_input"})
    return ControlDecisionSnapshot(
        guardrail_allow_count=getattr(inp, "guardrail_allow_count", 0) or 0,
        guardrail_block_count=getattr(inp, "guardrail_block_count", 0) or 0,
        portfolio_allow_count=getattr(inp, "portfolio_allow_count", 0) or 0,
        portfolio_block_count=getattr(inp, "portfolio_block_count", 0) or 0,
        portfolio_throttle_count=getattr(inp, "portfolio_throttle_count", 0) or 0,
        promotion_allow_count=getattr(inp, "promotion_allow_count", 0) or 0,
        promotion_reject_count=getattr(inp, "promotion_reject_count", 0) or 0,
        invalid_lifecycle_count=getattr(inp, "invalid_lifecycle_count", 0) or 0,
        metadata=getattr(inp, "metadata", None) or {},
    )


def build_experiment_summary(
    inp: ObservabilityInput | None,
) -> dict[str, object] | list[object]:
    """Build experiment summary from input. No fabrication; return empty or supplied data only."""
    if inp is None:
        return {}
    src = getattr(inp, "experiment_summary_source", None)
    if src is None:
        return {}
    if isinstance(src, dict):
        return dict(src)
    if isinstance(src, list):
        return list(src)
    return {}


def generate_observability_report(
    inp: ObservabilityInput | None,
    generated_key: str = "",
) -> SystemObservabilityReport:
    """
    Generate a deterministic SystemObservabilityReport from supplied inputs.
    Does not fabricate values; missing data produces deterministic omissions (0, None, empty).
    """
    if inp is None:
        return SystemObservabilityReport(
            strategies=[],
            execution_quality=ExecutionQualitySnapshot(metadata={"omission": "no_input"}),
            controls=ControlDecisionSnapshot(metadata={"omission": "no_input"}),
            experiment_summary={},
            totals={
                "total_strategies_observed": 0,
                "total_executable": 0,
                "total_live": 0,
                "total_paper": 0,
                "total_blocked": 0,
                "total_throttled": 0,
                "total_rejected_promotions": 0,
            },
            generated_key=generated_key or "no_input",
            metadata={"omission": "no_input"},
        )

    strategies = build_strategy_health_snapshots(
        getattr(inp, "strategy_health_inputs", None) or [],
    )
    execution = build_execution_quality_snapshot(inp)
    controls = build_control_decision_snapshot(inp)
    experiment_summary = build_experiment_summary(inp)

    total_strategies = len(strategies)
    executable = sum(1 for s in strategies if s.lifecycle_state in _EXECUTABLE_STATES)
    paper = sum(1 for s in strategies if s.lifecycle_state == "paper")
    live = sum(1 for s in strategies if s.lifecycle_state == "live")

    totals = {
        "total_strategies_observed": total_strategies,
        "total_executable": executable,
        "total_paper": paper,
        "total_live": live,
        "total_blocked": controls.portfolio_block_count + execution.blocked_orders,
        "total_throttled": controls.portfolio_throttle_count + execution.throttled_orders,
        "total_rejected_promotions": controls.promotion_reject_count,
    }

    key = generated_key or f"report_n{total_strategies}_e{execution.attempted_orders}"

    return SystemObservabilityReport(
        strategies=strategies,
        execution_quality=execution,
        controls=controls,
        experiment_summary=experiment_summary,
        totals=totals,
        generated_key=key,
        metadata=getattr(inp, "metadata", None) or {},
    )
