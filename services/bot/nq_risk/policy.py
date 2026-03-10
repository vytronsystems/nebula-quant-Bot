# NEBULA-QUANT v1 | nq_risk policy base

from abc import ABC, abstractmethod
from typing import Any

from nq_risk.decision import RiskDecision


class RiskPolicy(ABC):
    """Base for risk policies. Subclasses define limits and evaluation logic."""

    @abstractmethod
    def evaluate(self, signal: Any, context: dict[str, Any]) -> RiskDecision:
        """Evaluate signal and context; return APPROVE, REJECT, or ADJUST."""
        ...
