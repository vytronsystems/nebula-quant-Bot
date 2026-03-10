# NEBULA-QUANT v1 | nq_risk engine

from typing import Any

from nq_risk.decision import RiskDecision
from nq_risk.policy import RiskPolicy
from nq_risk.exceptions import RiskEngineError


class RiskEngine:
    """
    Receives signal and basic context; evaluates via policy and returns risk decision.
    No broker integration. Does not modify bot main loop.
    """

    def __init__(self, policy: RiskPolicy) -> None:
        self._policy = policy

    def evaluate(self, signal: Any, context: dict[str, Any]) -> RiskDecision:
        """Run policy evaluation on signal and context; return APPROVE, REJECT, or ADJUST."""
        try:
            return self._policy.evaluate(signal, context)
        except Exception as e:
            raise RiskEngineError(f"Risk evaluation failed: {e}") from e
