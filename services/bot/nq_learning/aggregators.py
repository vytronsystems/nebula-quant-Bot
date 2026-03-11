# NEBULA-QUANT v1 | nq_learning deterministic aggregators

from __future__ import annotations

from collections import defaultdict
from typing import Any

from nq_learning.models import LearningError, LearningPattern


def _normalize_finding(f: Any) -> dict[str, Any] | None:
    """Extract category, severity, strategy_id, module from a finding (dict or object). Return None if invalid."""
    if hasattr(f, "get"):
        d = f
    elif hasattr(f, "__dict__"):
        d = vars(f)
    else:
        return None
    category = d.get("category")
    if not category or not isinstance(category, str) or not category.strip():
        return None
    severity = d.get("severity")
    if severity is not None and not isinstance(severity, str):
        severity = str(severity) if severity is not None else "unknown"
    else:
        severity = severity or "unknown"
    strategy_id = d.get("related_strategy_id") or d.get("strategy_id")
    if strategy_id is not None and not isinstance(strategy_id, str):
        strategy_id = None
    module = d.get("related_module")
    if module is not None and not isinstance(module, str):
        module = None
    return {"category": category.strip(), "severity": severity, "strategy_id": strategy_id, "module": module}


def _ensure_finding_list(val: Any, name: str) -> list[Any]:
    if not isinstance(val, list):
        raise LearningError(f"learning input {name} must be a list, got {type(val).__name__}")
    return val


def aggregate_patterns(
    audit_findings: list[Any],
    trade_review_findings: list[Any],
) -> list[LearningPattern]:
    """
    Group findings by (category), (category, strategy_id), (category, module).
    Each group becomes a LearningPattern with count and severity_distribution.
    Deterministic; fails closed on malformed critical input (non-list).
    """
    audit_findings = _ensure_finding_list(audit_findings, "audit_findings")
    trade_review_findings = _ensure_finding_list(trade_review_findings, "trade_review_findings")

    # key -> (count, severity_distribution)
    by_key: dict[tuple[str, str | None, str | None], tuple[int, dict[str, int]]] = defaultdict(
        lambda: (0, defaultdict(int))
    )

    for f in audit_findings + trade_review_findings:
        n = _normalize_finding(f)
        if n is None:
            continue
        cat, sev, sid, mod = n["category"], n["severity"], n["strategy_id"], n["module"]
        # Global by category
        k0 = (cat, None, None)
        c0, s0 = by_key[k0]
        by_key[k0] = (c0 + 1, {**s0, sev: s0.get(sev, 0) + 1})
        # By category + strategy
        if sid:
            k1 = (cat, sid, None)
            c1, s1 = by_key[k1]
            by_key[k1] = (c1 + 1, {**s1, sev: s1.get(sev, 0) + 1})
        # By category + module
        if mod:
            k2 = (cat, None, mod)
            c2, s2 = by_key[k2]
            by_key[k2] = (c2 + 1, {**s2, sev: s2.get(sev, 0) + 1})

    patterns: list[LearningPattern] = []
    for (category, strategy_id, module), (count, sev_dist) in by_key.items():
        if count == 0:
            continue
        parts = [category]
        if strategy_id:
            parts.append(strategy_id)
        if module:
            parts.append(module)
        pattern_id = "-".join(parts) + f"-{count}"
        patterns.append(
            LearningPattern(
                pattern_id=pattern_id,
                category=category,
                count=count,
                related_strategy_id=strategy_id,
                related_module=module,
                severity_distribution=dict(sev_dist),
                metadata={},
            )
        )
    return patterns
