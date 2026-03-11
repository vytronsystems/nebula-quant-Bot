# NEBULA-QUANT v1 | nq_alpha_discovery — observation extraction

from __future__ import annotations

from typing import Any

from nq_alpha_discovery.models import (
    AlphaDiscoveryError,
    AlphaEvidence,
    AlphaEvidenceSource,
    AlphaObservation,
)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Get attribute or dict key; do not mutate."""
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _ensure_list(val: Any, name: str) -> list[Any]:
    if val is None:
        return []
    if not isinstance(val, list):
        raise AlphaDiscoveryError(f"{name} must be a list or None, got {type(val).__name__}")
    return list(val)


def _str_or_empty(val: Any) -> str:
    return str(val).strip() if val is not None else ""


def extract_from_learning(
    learning_report: Any,
    observation_id_prefix: str = "obs-learn",
    evidence_id_prefix: str = "ev-learn",
) -> tuple[list[AlphaObservation], list[AlphaEvidence]]:
    """
    Extract AlphaObservation and AlphaEvidence from LearningReport (patterns, lessons, improvement_candidates).
    Does not mutate input. Returns ([observations], [evidence]). Empty if report is None.
    """
    observations: list[AlphaObservation] = []
    evidence: list[AlphaEvidence] = []
    if learning_report is None:
        return observations, evidence

    source = AlphaEvidenceSource.LEARNING.value
    idx = 0
    for item in _ensure_list(_get(learning_report, "patterns"), "patterns"):
        oid = f"{observation_id_prefix}-{idx}"
        idx += 1
        cat = _str_or_empty(_get(item, "category")) or "pattern"
        count = int(_get(item, "count", 0) or 0)
        title = _str_or_empty(_get(item, "title")) or f"Pattern: {cat}"
        desc = _str_or_empty(_get(item, "description")) or f"Recurring pattern {cat}, count={count}"
        sev = _str_or_empty(_get(item, "severity")).lower()
        if not sev:
            dist = _get(item, "severity_distribution")
            if isinstance(dist, dict) and dist:
                if dist.get("critical", 0):
                    sev = "critical"
                elif dist.get("warning", 0):
                    sev = "warning"
                else:
                    sev = "info"
            else:
                sev = "info"
        if sev not in ("info", "warning", "critical"):
            sev = "info"
        strat = _get(item, "related_strategy_id")
        strat = str(strat).strip() or None if strat is not None else None
        mod = _get(item, "module") or _get(item, "related_module")
        mod = str(mod).strip() or None if mod is not None else None
        src_id = _str_or_empty(_get(item, "pattern_id")) or oid
        observations.append(AlphaObservation(
            observation_id=oid,
            source_type=source,
            category=cat,
            strategy_id=strat,
            module=mod,
            title=title,
            description=desc,
            severity=sev,
            metadata={},
        ))
        evidence.append(AlphaEvidence(
            evidence_id=f"{evidence_id_prefix}-{src_id}",
            source_type=source,
            source_id=src_id,
            category=cat,
            strategy_id=strat,
            module=mod,
            weight=1.0,
            metadata={},
        ))

    for item in _ensure_list(_get(learning_report, "lessons"), "lessons"):
        oid = f"{observation_id_prefix}-{idx}"
        idx += 1
        title = _str_or_empty(_get(item, "title")) or "Lesson"
        desc = _str_or_empty(_get(item, "description")) or ""
        cat = _str_or_empty(_get(item, "category")) or "lesson"
        for rc in _ensure_list(_get(item, "related_categories"), "related_categories"):
            if rc:
                cat = str(rc).strip()
                break
        sev = _str_or_empty(_get(item, "priority")).lower() or "info"
        if sev not in ("info", "warning", "critical", "low", "medium", "high", "critical"):
            sev = "info"
        strat = _get(item, "related_strategy_id")
        strat = str(strat).strip() or None if strat is not None else None
        mod = _get(item, "related_module")
        mod = str(mod).strip() or None if mod is not None else None
        src_id = _str_or_empty(_get(item, "lesson_id")) or oid
        observations.append(AlphaObservation(
            observation_id=oid,
            source_type=source,
            category=cat,
            strategy_id=strat,
            module=mod,
            title=title,
            description=desc,
            severity=sev,
            metadata={},
        ))
        evidence.append(AlphaEvidence(
            evidence_id=f"{evidence_id_prefix}-{src_id}",
            source_type=source,
            source_id=src_id,
            category=cat,
            strategy_id=strat,
            module=mod,
            weight=1.0,
            metadata={},
        ))

    for item in _ensure_list(_get(learning_report, "improvement_candidates"), "improvement_candidates"):
        oid = f"{observation_id_prefix}-{idx}"
        idx += 1
        title = _str_or_empty(_get(item, "title")) or "Improvement candidate"
        desc = _str_or_empty(_get(item, "description")) or ""
        cat = "improvement_candidate"
        sev = _str_or_empty(_get(item, "priority")).lower() or "info"
        strat = _get(item, "related_strategy_id")
        strat = str(strat).strip() or None if strat is not None else None
        mod = _get(item, "related_module")
        mod = str(mod).strip() or None if mod is not None else None
        src_id = _str_or_empty(_get(item, "candidate_id")) or oid
        observations.append(AlphaObservation(
            observation_id=oid,
            source_type=source,
            category=cat,
            strategy_id=strat,
            module=mod,
            title=title,
            description=desc,
            severity=sev,
            metadata={},
        ))
        evidence.append(AlphaEvidence(
            evidence_id=f"{evidence_id_prefix}-{src_id}",
            source_type=source,
            source_id=src_id,
            category=cat,
            strategy_id=strat,
            module=mod,
            weight=1.0,
            metadata={},
        ))

    return observations, evidence


def extract_from_experiment(
    experiment_report: Any,
    observation_id_prefix: str = "obs-exp",
    evidence_id_prefix: str = "ev-exp",
) -> tuple[list[AlphaObservation], list[AlphaEvidence]]:
    """
    Extract from ExperimentReport (findings). Empty if report is None.
    """
    observations = []
    evidence = []
    if experiment_report is None:
        return observations, evidence

    source = AlphaEvidenceSource.EXPERIMENT.value
    for i, item in enumerate(_ensure_list(_get(experiment_report, "findings"), "findings")):
        oid = f"{observation_id_prefix}-{i}"
        cat = _str_or_empty(_get(item, "category")) or "experiment_finding"
        title = _str_or_empty(_get(item, "title")) or cat
        desc = _str_or_empty(_get(item, "description")) or ""
        sev = _str_or_empty(_get(item, "severity")).lower() or "info"
        if sev not in ("info", "warning", "critical"):
            sev = "info"
        strat = _get(item, "strategy_id")
        strat = str(strat).strip() or None if strat is not None else None
        src_id = _str_or_empty(_get(item, "finding_id")) or oid
        observations.append(AlphaObservation(
            observation_id=oid,
            source_type=source,
            category=cat,
            strategy_id=strat,
            module=None,
            title=title,
            description=desc,
            severity=sev,
            metadata={},
        ))
        evidence.append(AlphaEvidence(
            evidence_id=f"{evidence_id_prefix}-{src_id}",
            source_type=source,
            source_id=src_id,
            category=cat,
            strategy_id=strat,
            module=None,
            weight=1.0,
            metadata={},
        ))
    return observations, evidence


def extract_from_audit(
    audit_report: Any,
    observation_id_prefix: str = "obs-audit",
    evidence_id_prefix: str = "ev-audit",
) -> tuple[list[AlphaObservation], list[AlphaEvidence]]:
    """
    Extract from AuditReport (findings and recommendations). Empty if report is None.
    """
    observations = []
    evidence = []
    if audit_report is None:
        return observations, evidence

    source = AlphaEvidenceSource.AUDIT.value
    for i, item in enumerate(_ensure_list(_get(audit_report, "findings"), "findings")):
        oid = f"{observation_id_prefix}-{i}"
        cat = _str_or_empty(_get(item, "category")) or "audit_finding"
        title = _str_or_empty(_get(item, "title")) or cat
        desc = _str_or_empty(_get(item, "description")) or ""
        sev = _str_or_empty(_get(item, "severity")).lower() or "info"
        strat = _get(item, "related_strategy_id")
        strat = str(strat).strip() or None if strat is not None else None
        mod = _get(item, "related_module")
        mod = str(mod).strip() or None if mod is not None else None
        src_id = _str_or_empty(_get(item, "finding_id")) or oid
        observations.append(AlphaObservation(
            observation_id=oid,
            source_type=source,
            category=cat,
            strategy_id=strat,
            module=mod,
            title=title,
            description=desc,
            severity=sev,
            metadata={},
        ))
        evidence.append(AlphaEvidence(
            evidence_id=f"{evidence_id_prefix}-{src_id}",
            source_type=source,
            source_id=src_id,
            category=cat,
            strategy_id=strat,
            module=mod,
            weight=1.0,
            metadata={},
        ))
    for i, rec in enumerate(_ensure_list(_get(audit_report, "recommendations"), "recommendations")):
        oid = f"{observation_id_prefix}-rec-{i}"
        text = _str_or_empty(rec)
        if not text:
            continue
        observations.append(AlphaObservation(
            observation_id=oid,
            source_type=source,
            category="recommendation",
            strategy_id=None,
            module=None,
            title=text[:80] + ("..." if len(text) > 80 else ""),
            description=text,
            severity="info",
            metadata={},
        ))
        evidence.append(AlphaEvidence(
            evidence_id=f"{evidence_id_prefix}-rec-{i}",
            source_type=source,
            source_id=oid,
            category="recommendation",
            strategy_id=None,
            module=None,
            weight=0.5,
            metadata={},
        ))
    return observations, evidence


def extract_from_trade_review(
    trade_review_reports: Any,
    observation_id_prefix: str = "obs-tr",
    evidence_id_prefix: str = "ev-tr",
) -> tuple[list[AlphaObservation], list[AlphaEvidence]]:
    """
    Extract from list of TradeReviewReport (findings and recommendations). Accepts None or single report.
    """
    observations = []
    evidence = []
    reports = _ensure_list(trade_review_reports, "trade_review_reports") if trade_review_reports is not None else []
    if not reports:
        return observations, evidence

    source = AlphaEvidenceSource.TRADE_REVIEW.value
    global_idx = 0
    for r in reports:
        for i, item in enumerate(_ensure_list(_get(r, "findings"), "findings")):
            oid = f"{observation_id_prefix}-{global_idx}"
            global_idx += 1
            cat = _str_or_empty(_get(item, "category")) or "trade_finding"
            title = _str_or_empty(_get(item, "title")) or cat
            desc = _str_or_empty(_get(item, "description")) or ""
            sev = _str_or_empty(_get(item, "severity")).lower() or "info"
            strat = _get(item, "strategy_id")
            strat = str(strat).strip() or None if strat is not None else None
            src_id = _str_or_empty(_get(item, "finding_id")) or oid
            observations.append(AlphaObservation(
                observation_id=oid,
                source_type=source,
                category=cat,
                strategy_id=strat,
                module=None,
                title=title,
                description=desc,
                severity=sev,
                metadata={},
            ))
            evidence.append(AlphaEvidence(
                evidence_id=f"{evidence_id_prefix}-{src_id}",
                source_type=source,
                source_id=src_id,
                category=cat,
                strategy_id=strat,
                module=None,
                weight=1.0,
                metadata={},
            ))
        for i, rec in enumerate(_ensure_list(_get(r, "recommendations"), "recommendations")):
            oid = f"{observation_id_prefix}-rec-{global_idx}"
            global_idx += 1
            text = _str_or_empty(rec)
            if not text:
                continue
            observations.append(AlphaObservation(
                observation_id=oid,
                source_type=source,
                category="recommendation",
                strategy_id=None,
                module=None,
                title=text[:80] + ("..." if len(text) > 80 else ""),
                description=text,
                severity="info",
                metadata={},
            ))
            evidence.append(AlphaEvidence(
                evidence_id=f"{evidence_id_prefix}-rec-{global_idx}",
                source_type=source,
                source_id=oid,
                category="recommendation",
                strategy_id=None,
                module=None,
                weight=0.5,
                metadata={},
            ))
    return observations, evidence


def normalize_direct_observations(
    observations: Any,
    observation_id_prefix: str = "obs-direct",
    evidence_id_prefix: str = "ev-direct",
) -> tuple[list[AlphaObservation], list[AlphaEvidence]]:
    """
    Normalize caller-supplied observation-like dicts into AlphaObservation and AlphaEvidence.
    Each item must have at least category or title; optional strategy_id, module, description, severity.
    """
    out_obs: list[AlphaObservation] = []
    out_ev: list[AlphaEvidence] = []
    items = _ensure_list(observations, "observations") if observations is not None else []
    source = AlphaEvidenceSource.RESEARCH.value
    for i, item in enumerate(items):
        cat = _str_or_empty(_get(item, "category"))
        title = _str_or_empty(_get(item, "title"))
        if not cat and not title:
            raise AlphaDiscoveryError("direct observation must have category or title")
        if not cat:
            cat = "research"
        if not title:
            title = cat
        oid = _str_or_empty(_get(item, "observation_id")) or f"{observation_id_prefix}-{i}"
        desc = _str_or_empty(_get(item, "description")) or ""
        sev = _str_or_empty(_get(item, "severity")).lower() or "info"
        if sev not in ("info", "warning", "critical"):
            sev = "info"
        strat = _get(item, "strategy_id")
        strat = str(strat).strip() or None if strat is not None else None
        mod = _get(item, "module")
        mod = str(mod).strip() or None if mod is not None else None
        out_obs.append(AlphaObservation(
            observation_id=oid,
            source_type=source,
            category=cat,
            strategy_id=strat,
            module=mod,
            title=title,
            description=desc,
            severity=sev,
            metadata={},
        ))
        out_ev.append(AlphaEvidence(
            evidence_id=f"{evidence_id_prefix}-{oid}",
            source_type=source,
            source_id=oid,
            category=cat,
            strategy_id=strat,
            module=mod,
            weight=1.0,
            metadata={},
        ))
    return out_obs, out_ev
