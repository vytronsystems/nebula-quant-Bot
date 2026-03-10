# NEBULA-QUANT v1 | nq_guardrails reporter — summary for monitoring and logs

from __future__ import annotations

from typing import Any

from nq_guardrails.models import GuardrailResult


def build_guardrail_report(result: GuardrailResult) -> dict[str, Any]:
    """
    Build a dictionary report for monitoring and logs.
    issue_count = number of signals with severity WARN or BLOCK.
    """
    issue_count = sum(1 for s in result.signals if s.severity in ("WARN", "BLOCK"))
    return {
        "allowed": result.allowed,
        "reason": result.reason,
        "issue_count": issue_count,
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
