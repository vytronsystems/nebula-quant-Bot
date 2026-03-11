# NEBULA-QUANT v1 | nq_alpha_discovery — deterministic hypothesis ranking

from __future__ import annotations

from nq_alpha_discovery.models import AlphaHypothesis, AlphaHypothesisPriority


def _severity_rank(severity: str) -> int:
    """Higher = more severe. Used for ordering."""
    s = (severity or "").lower()
    if s == "critical":
        return 3
    if s in ("high", "warning"):
        return 2
    if s in ("medium",):
        return 1
    return 0


def _priority_rank(priority: str) -> int:
    """Higher = higher priority."""
    p = (priority or "").lower()
    if p == AlphaHypothesisPriority.CRITICAL.value:
        return 4
    if p == AlphaHypothesisPriority.HIGH.value:
        return 3
    if p == AlphaHypothesisPriority.MEDIUM.value:
        return 2
    if p == AlphaHypothesisPriority.LOW.value:
        return 1
    return 0


def rank_hypotheses(hypotheses: list[AlphaHypothesis]) -> list[AlphaHypothesis]:
    """
    Sort hypotheses deterministically: by priority (critical > high > medium > low),
    then by confidence_score descending, then by hypothesis_id.
    Does not mutate input; returns new list in sorted order.
    """
    return sorted(
        hypotheses,
        key=lambda h: (
            -_priority_rank(h.priority),
            -h.confidence_score,
            h.hypothesis_id,
        ),
    )
