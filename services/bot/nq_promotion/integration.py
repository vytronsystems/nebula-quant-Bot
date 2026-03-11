# NEBULA-QUANT v1 | nq_promotion — registry integration: lifecycle truth and transition validation

from __future__ import annotations

from nq_promotion.models import ExecutionEligibilityResult, PromotionTransitionDecision
from nq_promotion.status_map import (
    EXECUTION_COMPATIBLE_STATES,
    OFFICIAL_LIFECYCLE_STATES,
    is_transition_allowed,
)
from nq_strategy_registry.engine import StrategyRegistryEngine


def resolve_lifecycle_from_registry(
    registry_engine: StrategyRegistryEngine,
    strategy_id: str,
) -> tuple[str | None, list[str], str]:
    """
    Resolve lifecycle state from nq_strategy_registry (source of truth).
    Returns (lifecycle_state or None, reason_codes, message).
    Fail-closed: missing strategy or state → (None, reason_codes, message).
    """
    result = registry_engine.get_registration_record(strategy_id or "")
    if not result.ok or result.record is None:
        return (
            None,
            result.reason_codes,
            result.message,
        )
    return (
        result.record.lifecycle_state,
        [],
        "ok",
    )


def validate_transition_with_registry(
    registry_engine: StrategyRegistryEngine,
    strategy_id: str,
    target_state: str,
) -> PromotionTransitionDecision:
    """
    Validate a lifecycle transition. Current state is resolved from registry (not caller).
    nq_promotion is the authorized transition engine; registry is source of truth for current state.
    Fail-closed: not registered, missing state, unknown state, disallowed transition → allowed=False.
    """
    lookup = registry_engine.get_registration_record(strategy_id or "")
    if not lookup.ok or lookup.record is None:
        return PromotionTransitionDecision(
            allowed=False,
            reason_codes=lookup.reason_codes,
            message=lookup.message,
        )

    current_state = lookup.record.lifecycle_state
    target = (target_state or "").strip().lower()
    if not target:
        return PromotionTransitionDecision(
            allowed=False,
            reason_codes=["missing_target_state"],
            message="promotion: target_state missing",
        )
    if target not in OFFICIAL_LIFECYCLE_STATES:
        return PromotionTransitionDecision(
            allowed=False,
            reason_codes=["unknown_target_state"],
            message=f"promotion: unknown target_state {target!r}",
        )

    current = (current_state or "").strip().lower()
    if current not in OFFICIAL_LIFECYCLE_STATES:
        return PromotionTransitionDecision(
            allowed=False,
            reason_codes=["unknown_current_state"],
            message=f"promotion: current lifecycle state {current!r} not in official states",
        )

    # Retired → any active state is never allowed (no (retired, *) in ALLOWED_TRANSITIONS)
    if current == "retired" and target != "retired":
        return PromotionTransitionDecision(
            allowed=False,
            reason_codes=["retired_not_reactivatable"],
            message="promotion: transition from retired to active not allowed",
        )

    allowed = is_transition_allowed(current, target)
    if not allowed:
        return PromotionTransitionDecision(
            allowed=False,
            reason_codes=["transition_not_allowed"],
            message=f"promotion: transition {current} -> {target} not allowed",
        )

    return PromotionTransitionDecision(
        allowed=True,
        reason_codes=[],
        message="ok",
    )


def check_execution_eligibility(
    registry_engine: StrategyRegistryEngine,
    strategy_id: str,
) -> ExecutionEligibilityResult:
    """
    Determine if a strategy is executable (registered and lifecycle in {paper, live}).
    Lifecycle state is resolved from nq_strategy_registry only.
    Fail-closed: not registered, missing state, or not paper/live → executable=False.
    """
    lookup = registry_engine.get_registration_record(strategy_id or "")
    if not lookup.ok or lookup.record is None:
        return ExecutionEligibilityResult(
            executable=False,
            lifecycle_state=None,
            reason_codes=lookup.reason_codes,
            message=lookup.message,
        )

    state = lookup.record.lifecycle_state
    if not state or state not in EXECUTION_COMPATIBLE_STATES:
        return ExecutionEligibilityResult(
            executable=False,
            lifecycle_state=state,
            reason_codes=["lifecycle_not_executable"],
            message=f"strategy lifecycle {state!r} not in {{paper, live}}",
        )

    return ExecutionEligibilityResult(
        executable=True,
        lifecycle_state=state,
        reason_codes=[],
        message="ok",
    )
