# NEBULA-QUANT v1 | nq_improvement deterministic planners

from __future__ import annotations

from typing import Any

from nq_improvement.models import (
    ImprovementAction,
    ImprovementError,
    ImprovementType,
)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _ensure_list(val: Any, name: str) -> list[Any]:
    if val is None:
        return []
    if not isinstance(val, list):
        raise ImprovementError(f"{name} must be a list or None, got {type(val).__name__}")
    return list(val)


def _category_to_improvement_type(category: str) -> str:
    """Map finding category to ImprovementType. Deterministic."""
    c = (category or "").lower()
    if "blocked" in c or "risk" in c:
        return ImprovementType.RISK_REVIEW.value
    if "throttl" in c or "portfolio" in c:
        return ImprovementType.PORTFOLIO_REVIEW.value
    if "promotion" in c:
        return ImprovementType.PROMOTION_REVIEW.value
    if "execution" in c or "exec" in c:
        return ImprovementType.EXECUTION_REVIEW.value
    if "entry" in c or "exit" in c or "slippage" in c or "rr_" in c:
        return ImprovementType.EXECUTION_REVIEW.value
    if "degraded" in c or "inactive" in c:
        return ImprovementType.STRATEGY_REVIEW.value
    if "lifecycle" in c:
        return ImprovementType.PROMOTION_REVIEW.value
    if "observability" in c or "event" in c:
        return ImprovementType.OBSERVABILITY_REVIEW.value
    return ImprovementType.MODULE_REVIEW.value


def plan_from_learning(learning_report: Any, action_id_prefix: str = "learn") -> list[ImprovementAction]:
    """
    Generate improvement actions from LearningReport (improvement_candidates, lessons, patterns).
    Does not mutate input. Returns empty list if learning_report is None.
    """
    if learning_report is None:
        return []
    candidates = _ensure_list(_get(learning_report, "improvement_candidates"), "improvement_candidates")
    actions: list[ImprovementAction] = []
    for i, c in enumerate(candidates):
        aid = f"{action_id_prefix}-{i+1}"
        title = _get(c, "title") or "Improvement from learning"
        desc = _get(c, "description") or ""
        priority = _get(c, "priority") or "medium"
        sid = _get(c, "related_strategy_id")
        mod = _get(c, "related_module")
        source_patterns = _ensure_list(_get(c, "source_patterns"), "source_patterns")
        cat = _get(c, "title", "")
        itype = ImprovementType.MODULE_REVIEW.value
        if "entry" in str(title).lower():
            itype = ImprovementType.EXECUTION_REVIEW.value
        elif "exit" in str(title).lower():
            itype = ImprovementType.EXECUTION_REVIEW.value
        elif "slippage" in str(title).lower():
            itype = ImprovementType.EXECUTION_REVIEW.value
        elif "promotion" in str(title).lower():
            itype = ImprovementType.PROMOTION_REVIEW.value
        elif "throttl" in str(title).lower():
            itype = ImprovementType.PORTFOLIO_REVIEW.value
        elif "blocked" in str(title).lower() or "risk" in str(title).lower():
            itype = ImprovementType.RISK_REVIEW.value
        elif "strategy" in str(title).lower():
            itype = ImprovementType.STRATEGY_REVIEW.value
        actions.append(
            ImprovementAction(
                action_id=aid,
                title=str(title),
                description=str(desc),
                priority=str(priority).lower(),
                improvement_type=itype,
                related_strategy_id=str(sid) if sid is not None else None,
                related_module=str(mod) if mod is not None else None,
                source_categories=[],
                source_ids=list(source_patterns),
                rationale="From learning improvement_candidates",
                metadata={},
            )
        )
    return actions


def plan_from_audit(audit_report: Any, action_id_prefix: str = "audit") -> list[ImprovementAction]:
    """
    Generate improvement actions from AuditReport (findings and recommendations).
    Does not mutate input. Returns empty list if audit_report is None.
    """
    if audit_report is None:
        return []
    findings = _ensure_list(_get(audit_report, "findings"), "findings")
    recommendations = _ensure_list(_get(audit_report, "recommendations"), "recommendations")
    actions: list[ImprovementAction] = []
    seen_key: set[tuple[str | None, str | None, str]] = set()
    for i, f in enumerate(findings):
        severity = _get(f, "severity") or "info"
        if str(severity).lower() not in ("warning", "critical"):
            continue
        cat = _get(f, "category") or "unknown"
        sid = _get(f, "related_strategy_id")
        mod = _get(f, "related_module")
        key = (sid, mod, cat)
        if key in seen_key:
            continue
        seen_key.add(key)
        aid = f"{action_id_prefix}-{len(actions)+1}"
        title = _get(f, "title") or f"Address {cat}"
        desc = _get(f, "description") or ""
        itype = _category_to_improvement_type(cat)
        actions.append(
            ImprovementAction(
                action_id=aid,
                title=str(title),
                description=str(desc),
                priority=str(severity).lower(),
                improvement_type=itype,
                related_strategy_id=str(sid) if sid is not None else None,
                related_module=str(mod) if mod is not None else None,
                source_categories=[str(cat)],
                source_ids=[_get(f, "finding_id") or aid],
                rationale="From audit finding",
                metadata={},
            )
        )
    for i, rec in enumerate(recommendations):
        if not isinstance(rec, str) or not rec.strip():
            continue
        aid = f"{action_id_prefix}-rec-{i+1}"
        actions.append(
            ImprovementAction(
                action_id=aid,
                title=rec[:80] + "..." if len(rec) > 80 else rec,
                description=str(rec),
                priority="medium",
                improvement_type=ImprovementType.MODULE_REVIEW.value,
                related_strategy_id=None,
                related_module=None,
                source_categories=[],
                source_ids=[],
                rationale="From audit recommendation",
                metadata={},
            )
        )
    return actions


def plan_from_trade_review(trade_review_reports: Any, action_id_prefix: str = "trade") -> list[ImprovementAction]:
    """
    Generate improvement actions from TradeReviewReport(s) (findings and recommendations).
    Does not mutate input. Returns empty list if reports is None or empty.
    """
    reports = _ensure_list(trade_review_reports, "trade_review_reports") if trade_review_reports is not None else []
    if not reports:
        return []
    actions: list[ImprovementAction] = []
    seen_key: set[tuple[str | None, str | None, str]] = set()
    idx = 0
    for r in reports:
        findings = _ensure_list(_get(r, "findings"), "findings")
        for f in findings:
            cat = _get(f, "category") or "unknown"
            severity = _get(f, "severity") or "info"
            sid = _get(f, "strategy_id") or _get(f, "related_strategy_id")
            key = (sid, None, cat)
            if key in seen_key:
                continue
            seen_key.add(key)
            idx += 1
            aid = f"{action_id_prefix}-{idx}"
            title = _get(f, "title") or f"Address trade {cat}"
            desc = _get(f, "description") or ""
            itype = _category_to_improvement_type(cat)
            actions.append(
                ImprovementAction(
                    action_id=aid,
                    title=str(title),
                    description=str(desc),
                    priority=str(severity).lower(),
                    improvement_type=itype,
                    related_strategy_id=str(sid) if sid is not None else None,
                    related_module=None,
                    source_categories=[str(cat)],
                    source_ids=[_get(f, "finding_id") or aid],
                    rationale="From trade review finding",
                    metadata={},
                )
            )
        recs = _ensure_list(_get(r, "recommendations"), "recommendations")
        for rec in recs:
            if not isinstance(rec, str) or not rec.strip():
                continue
            idx += 1
            actions.append(
                ImprovementAction(
                    action_id=f"{action_id_prefix}-rec-{idx}",
                    title=rec[:80] + "..." if len(rec) > 80 else rec,
                    description=str(rec),
                    priority="medium",
                    improvement_type=ImprovementType.EXECUTION_REVIEW.value,
                    related_strategy_id=None,
                    related_module=None,
                    source_categories=[],
                    source_ids=[],
                    rationale="From trade review recommendation",
                    metadata={},
                )
            )
    return actions
