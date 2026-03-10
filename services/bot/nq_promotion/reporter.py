# NEBULA-QUANT v1 | nq_promotion reporter — governance dashboards and audit

from __future__ import annotations

from typing import Any

from nq_promotion.models import PromotionResult


def build_promotion_report(result: PromotionResult) -> dict[str, Any]:
    """Build a dictionary suitable for governance dashboards and weekly audit reviews."""
    d = result.decision
    return {
        "strategy_id": result.strategy_id,
        "allowed": d.allowed,
        "from_status": d.from_status,
        "to_status": d.to_status,
        "reason": d.reason,
        "blocking_issues": list(d.blocking_issues),
        "warnings": list(d.warnings),
        "evaluated_at": result.evaluated_at,
        "metadata": result.metadata,
    }
