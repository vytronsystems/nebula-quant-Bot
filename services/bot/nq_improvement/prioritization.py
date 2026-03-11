# NEBULA-QUANT v1 | nq_improvement prioritization rules

from __future__ import annotations

from nq_improvement.models import ImprovementAction, ImprovementPriority


_PRIORITY_ORDER = {
    ImprovementPriority.CRITICAL.value: 4,
    ImprovementPriority.HIGH.value: 3,
    ImprovementPriority.MEDIUM.value: 2,
    ImprovementPriority.LOW.value: 1,
}


def normalize_priority(priority: str) -> str:
    """Normalize priority string to low/medium/high/critical. Default medium."""
    if not priority or not isinstance(priority, str):
        return ImprovementPriority.MEDIUM.value
    p = priority.strip().lower()
    if p in _PRIORITY_ORDER:
        return p
    if p in ("info", "informational"):
        return ImprovementPriority.LOW.value
    if p in ("warn", "warning"):
        return ImprovementPriority.HIGH.value
    if p in ("crit", "critical"):
        return ImprovementPriority.CRITICAL.value
    return ImprovementPriority.MEDIUM.value


def priority_rank(p: str) -> int:
    """Higher rank = higher priority. For sorting."""
    return _PRIORITY_ORDER.get(normalize_priority(p), 0)


def assign_priority(action: ImprovementAction) -> str:
    """
    Ensure action has a valid normalized priority. Returns same or normalized.
    Does not mutate; callers can replace action.priority with return value.
    """
    return normalize_priority(action.priority)


def merge_priority(a: str, b: str) -> str:
    """Return the higher of two priorities (deterministic)."""
    if priority_rank(b) > priority_rank(a):
        return normalize_priority(b)
    return normalize_priority(a)
