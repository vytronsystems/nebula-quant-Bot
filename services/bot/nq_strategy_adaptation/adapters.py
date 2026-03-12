from __future__ import annotations

from typing import Any


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _ensure_list(val: Any) -> list[Any]:
    if val is None:
        return []
    if isinstance(val, list):
        return list(val)
    return [val]


def adapt_trade_review(trade_review_reports: Any) -> dict[str, Any]:
    """
    Extract simple slippage/entry/exit quality signals from TradeReviewReport inputs.

    Returns dict with keys like:
    - slippage_issues: bool
    - poor_entry_count: int
    - poor_exit_count: int
    - source_ids: list[str]
    """
    reports = _ensure_list(trade_review_reports) if trade_review_reports is not None else []
    slippage_issues = False
    poor_entry = 0
    poor_exit = 0
    source_ids: list[str] = []
    for r in reports:
        rid = _get(r, "report_id")
        if rid:
            source_ids.append(str(rid))
        findings = _ensure_list(_get(r, "findings"))
        for f in findings:
            cat = str(_get(f, "category", "") or "").lower()
            if "slippage" in cat:
                slippage_issues = True
            if "poor_entry" in cat or "entry_quality" in cat:
                poor_entry += 1
            if "poor_exit" in cat or "exit_quality" in cat:
                poor_exit += 1
    return {
        "slippage_issues": slippage_issues,
        "poor_entry_count": poor_entry,
        "poor_exit_count": poor_exit,
        "source_ids": source_ids,
    }


def adapt_edge_decay(edge_decay_report: Any) -> dict[str, Any]:
    """
    Extract edge decay signals by strategy family from EdgeDecayReport.

    Expected fields (duck-typed):
    - decayed_families: list[str] or in metadata
    """
    if edge_decay_report is None:
        return {"decayed_families": [], "source_ids": []}
    source_id = _get(edge_decay_report, "report_id")
    families = _get(edge_decay_report, "decayed_families") or _get(
        _get(edge_decay_report, "metadata", {}) or {}, "decayed_families"
    )
    out_fams: list[str] = []
    for f in _ensure_list(families):
        out_fams.append(str(f))
    return {"decayed_families": out_fams, "source_ids": [str(source_id)] if source_id else []}


def adapt_experiments(experiment_report: Any) -> dict[str, Any]:
    """
    Extract experiment success/failure by family.

    Uses:
    - findings categories or summary metadata to derive reinforced / weak families.
    """
    if experiment_report is None:
        return {"reinforced_families": [], "weak_families": [], "source_ids": []}
    source_id = _get(experiment_report, "report_id")
    findings = _ensure_list(_get(experiment_report, "findings"))
    reinforced: set[str] = set()
    weak: set[str] = set()
    for f in findings:
        cat = str(_get(f, "category", "") or "")
        fam = str(_get(f, "strategy_id", "") or "")
        # Simple heuristic: categories mentioning "weak" or "unstable" mark weak; others mark reinforced.
        lower_cat = cat.lower()
        if "weak" in lower_cat or "unstable" in lower_cat or "invalid" in lower_cat:
            if fam:
                weak.add(fam)
        else:
            if fam:
                reinforced.add(fam)
    return {
        "reinforced_families": sorted(reinforced),
        "weak_families": sorted(weak),
        "source_ids": [str(source_id)] if source_id else [],
    }


def adapt_learning(learning_report: Any) -> dict[str, Any]:
    """
    Extract high-level improvement signals from LearningReport.
    Example fields:
    - improvement_candidates: list with family hints
    """
    if learning_report is None:
        return {"preferred_families": [], "source_ids": []}
    source_id = _get(learning_report, "report_id")
    candidates = _ensure_list(_get(learning_report, "improvement_candidates"))
    preferred: set[str] = set()
    for c in candidates:
        fam = _get(c, "target_family") or _get(c, "family")
        if fam:
            preferred.add(str(fam))
    return {
        "preferred_families": sorted(preferred),
        "source_ids": [str(source_id)] if source_id else [],
    }


def adapt_improvement_plan(improvement_plan: Any) -> dict[str, Any]:
    """
    Extract explicit improvement directives from ImprovementPlan.
    """
    if improvement_plan is None:
        return {"flagged_families": [], "source_ids": []}
    source_id = _get(improvement_plan, "plan_id") or _get(improvement_plan, "id")
    items = _ensure_list(_get(improvement_plan, "items"))
    flagged: set[str] = set()
    for item in items:
        fam = _get(item, "target_family") or _get(item, "family")
        if fam:
            flagged.add(str(fam))
    return {
        "flagged_families": sorted(flagged),
        "source_ids": [str(source_id)] if source_id else [],
    }


def adapt_audit(audit_report: Any) -> dict[str, Any]:
    """
    Extract regime performance hints from AuditReport findings.

    Example: findings may reference specific regimes and families as strong/weak.
    """
    if audit_report is None:
        return {"regime_failures": [], "regime_successes": [], "source_ids": []}
    source_id = _get(audit_report, "report_id")
    findings = _ensure_list(_get(audit_report, "findings"))
    regime_failures: set[tuple[str, str]] = set()
    regime_successes: set[tuple[str, str]] = set()
    for f in findings:
        fam = str(_get(f, "strategy_family", "") or "")
        regime = str(_get(f, "regime", "") or "").upper()
        outcome = str(_get(f, "outcome", "") or "").lower()
        if not fam or not regime:
            continue
        pair = (fam, regime)
        if "fail" in outcome or "negative" in outcome:
            regime_failures.add(pair)
        if "success" in outcome or "positive" in outcome or "strong" in outcome:
            regime_successes.add(pair)
    return {
        "regime_failures": sorted(regime_failures),
        "regime_successes": sorted(regime_successes),
        "source_ids": [str(source_id)] if source_id else [],
    }

