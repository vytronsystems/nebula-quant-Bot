# NEBULA-QUANT v1 | nq_promotion — strategy lifecycle governance
# Does not execute, backtest, or place orders. Evaluates promotion eligibility only.

from nq_promotion.engine import PromotionEngine
from nq_promotion.integration import (
    check_execution_eligibility,
    resolve_lifecycle_from_registry,
    validate_transition_with_registry,
)
from nq_promotion.models import (
    ExecutionEligibilityResult,
    PromotionDecision,
    PromotionInput,
    PromotionResult,
    PromotionTransitionDecision,
    PromotionTransitionRequest,
)

__all__ = [
    "check_execution_eligibility",
    "ExecutionEligibilityResult",
    "PromotionDecision",
    "PromotionEngine",
    "PromotionInput",
    "PromotionResult",
    "PromotionTransitionDecision",
    "PromotionTransitionRequest",
    "resolve_lifecycle_from_registry",
    "validate_transition_with_registry",
]
