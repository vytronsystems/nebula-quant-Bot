# NEBULA-QUANT v1 | nq_risk engine

from __future__ import annotations

from typing import Any

from nq_risk.decision import RiskDecision
from nq_risk.models import (
    RiskContext,
    RiskDecisionResult,
    RiskLimits,
    RiskOrderIntent,
)
from nq_risk.policy import RiskPolicy
from nq_risk.exceptions import RiskEngineError
from nq_risk.rules import evaluate_risk
from nq_risk.limits import DEFAULT_RISK_LIMITS


class RiskEngine:
    """
    Risk decision engine: evaluates order intents against risk policy.
    Returns ALLOW, REDUCE, or BLOCK. No broker integration. Fail-closed.
    """

    def __init__(self, policy: RiskPolicy | None = None) -> None:
        self._policy = policy

    def evaluate(self, signal: Any, context: dict[str, Any]) -> RiskDecision:
        """Run policy evaluation on signal and context; return APPROVE, REJECT, or ADJUST (legacy)."""
        if self._policy is None:
            raise RiskEngineError("Policy required for evaluate()")
        try:
            return self._policy.evaluate(signal, context)
        except Exception as e:
            raise RiskEngineError(f"Risk evaluation failed: {e}") from e

    def evaluate_order_intent(
        self,
        intent: RiskOrderIntent | None,
        context: RiskContext | None,
        limits: RiskLimits | None = None,
    ) -> RiskDecisionResult:
        """
        Evaluate order intent against risk policy. Deterministic, fail-closed.
        Returns ALLOW, REDUCE, or BLOCK with reason_codes and optional approved_quantity/approved_notional.
        """
        return evaluate_risk(intent, context, limits if limits is not None else DEFAULT_RISK_LIMITS)
