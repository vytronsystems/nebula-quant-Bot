# NEBULA-QUANT v1 | nq_reporting deterministic builders

from __future__ import annotations

from collections import defaultdict
from typing import Any

from nq_reporting.models import (
    AuditSummaryReport,
    LearningSummaryReport,
    ObservabilitySummaryReport,
    ReportError,
    TradeReviewSummaryReport,
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
        raise ReportError(f"{name} must be a list or None, got {type(val).__name__}")
    return list(val)


def build_audit_summary(audit_report: Any) -> AuditSummaryReport:
    """
    Build AuditSummaryReport from an nq_audit AuditReport.
    Does not mutate input. Fails closed if critical structure is missing.
    """
    if audit_report is None:
        raise ReportError("audit_report must not be None")
    summary = _get(audit_report, "summary")
    if summary is None:
        raise ReportError("audit_report must have a summary")
    total = _get(summary, "total_findings", 0)
    if not isinstance(total, (int, float)):
        total = 0
    total = int(total)
    info_c = int(_get(summary, "info_count", 0) or 0)
    warn_c = int(_get(summary, "warning_count", 0) or 0)
    crit_c = int(_get(summary, "critical_count", 0) or 0)
    severity_distribution: dict[str, int] = {
        "info": info_c,
        "warning": warn_c,
        "critical": crit_c,
    }
    strategies = _ensure_list(_get(summary, "strategies_reviewed"), "strategies_reviewed")
    modules = _ensure_list(_get(summary, "modules_reviewed"), "modules_reviewed")
    recommendations = _ensure_list(_get(audit_report, "recommendations"), "recommendations")
    return AuditSummaryReport(
        total_findings=total,
        severity_distribution=severity_distribution,
        affected_strategies=sorted(str(s) for s in strategies if s is not None),
        affected_modules=sorted(str(m) for m in modules if m is not None),
        recommendations=list(recommendations),
        metadata={},
    )


def build_trade_review_summary(trade_review_reports: Any) -> TradeReviewSummaryReport:
    """
    Build TradeReviewSummaryReport from a list of nq_trade_review TradeReviewReport.
    Does not mutate input. Optional: pass None or empty list for empty summary.
    """
    reports = _ensure_list(trade_review_reports, "trade_review_reports") if trade_review_reports is not None else []
    if not reports:
        return TradeReviewSummaryReport(
            total_trades_reviewed=0,
            win_rate=0.0,
            loss_rate=0.0,
            breakeven_rate=0.0,
            common_issues=[],
            severity_distribution={"info": 0, "warning": 0, "critical": 0},
            metadata={},
        )
    total = len(reports)
    wins = losses = breakevens = 0
    severity_dist: dict[str, int] = defaultdict(int)
    category_counts: dict[str, int] = defaultdict(int)
    for r in reports:
        summary = _get(r, "summary")
        if summary is not None:
            outcome = _get(summary, "outcome")
            if outcome == "win":
                wins += 1
            elif outcome == "loss":
                losses += 1
            elif outcome == "breakeven":
                breakevens += 1
            for key in ("info_count", "warning_count", "critical_count"):
                cnt = _get(summary, key)
                if isinstance(cnt, (int, float)):
                    label = key.replace("_count", "")
                    severity_dist[label] = severity_dist[label] + int(cnt)
        findings = _ensure_list(_get(r, "findings"), "findings")
        for f in findings:
            cat = _get(f, "category")
            if isinstance(cat, str) and cat.strip():
                category_counts[cat.strip()] += 1
    common_issues = sorted(category_counts.keys(), key=lambda k: (-category_counts[k], k))[:20]
    return TradeReviewSummaryReport(
        total_trades_reviewed=total,
        win_rate=wins / total if total else 0.0,
        loss_rate=losses / total if total else 0.0,
        breakeven_rate=breakevens / total if total else 0.0,
        common_issues=common_issues,
        severity_distribution=dict(severity_dist) if severity_dist else {"info": 0, "warning": 0, "critical": 0},
        metadata={},
    )


def build_learning_summary(learning_report: Any) -> LearningSummaryReport:
    """
    Build LearningSummaryReport from an nq_learning LearningReport.
    Does not mutate input. Returns empty summary if learning_report is None.
    Fails closed if report is non-None but missing summary.
    """
    if learning_report is None:
        return LearningSummaryReport(
            total_patterns=0,
            total_lessons=0,
            total_improvement_candidates=0,
            high_priority_items=0,
            critical_priority_items=0,
            categories_seen=[],
            metadata={},
        )
    summary = _get(learning_report, "summary")
    if summary is None:
        raise ReportError("learning_report must have a summary")
    return LearningSummaryReport(
        total_patterns=int(_get(summary, "total_patterns", 0) or 0),
        total_lessons=int(_get(summary, "total_lessons", 0) or 0),
        total_improvement_candidates=int(_get(summary, "total_improvement_candidates", 0) or 0),
        high_priority_items=int(_get(summary, "high_priority_count", 0) or 0),
        critical_priority_items=int(_get(summary, "critical_priority_count", 0) or 0),
        categories_seen=sorted(_ensure_list(_get(summary, "categories_seen"), "categories_seen")),
        metadata={},
    )


def build_observability_summary(observability_report: Any) -> ObservabilitySummaryReport:
    """
    Build ObservabilitySummaryReport from observability input (dict or object).
    Does not mutate input. Accepts None for optional report.
    """
    if observability_report is None:
        return ObservabilitySummaryReport(
            system_health_score=None,
            degraded_strategies=[],
            inactive_strategies=[],
            event_anomalies=[],
            metrics_summary=None,
            metadata={},
        )
    score = _get(observability_report, "system_health_score")
    if score is not None and isinstance(score, (int, float)):
        score = float(score)
    else:
        score = None
    degraded = _ensure_list(_get(observability_report, "degraded_strategies"), "degraded_strategies")
    inactive = _ensure_list(_get(observability_report, "inactive_strategies"), "inactive_strategies")
    anomalies = _ensure_list(_get(observability_report, "event_anomalies"), "event_anomalies")
    metrics = _get(observability_report, "metrics_summary")
    if metrics is not None and not isinstance(metrics, dict):
        metrics = None
    return ObservabilitySummaryReport(
        system_health_score=score,
        degraded_strategies=sorted(str(s) for s in degraded if s is not None),
        inactive_strategies=sorted(str(s) for s in inactive if s is not None),
        event_anomalies=list(anomalies),
        metrics_summary=metrics,
        metadata={},
    )
