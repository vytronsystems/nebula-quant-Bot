# NEBULA-QUANT v1 | nq_guardrails reporter

from typing import Any

from nq_guardrails.models import GuardrailResult


def build_guardrail_report(result: GuardrailResult) -> dict[str, Any]:
    """
    Build a dictionary report for monitoring and logs.
    Skeleton: no external APIs or persistence.
    """
    return {
        "allowed": result.allowed,
        "reason": result.reason,
        "signal_count": len(result.signals),
        "signals": [
            {
                "signal_type": s.signal_type,
                "severity": s.severity,
                "message": s.message,
                "timestamp": s.timestamp,
            }
            for s in result.signals
        ],
        "metadata": result.metadata,
    }
