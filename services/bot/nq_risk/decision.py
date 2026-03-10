# NEBULA-QUANT v1 | nq_risk decision outcome

from enum import Enum


class RiskDecision(str, Enum):
    """Result of risk evaluation: allow, block, or allow with adjustment."""

    APPROVE = "approve"
    REJECT = "reject"
    ADJUST = "adjust"
