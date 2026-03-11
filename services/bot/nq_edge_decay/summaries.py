# NEBULA-QUANT v1 | nq_edge_decay — edge decay summary builders

from __future__ import annotations

from typing import Any

from nq_edge_decay.models import EdgeDecayFinding, EdgeDecayReport, EdgeDecaySummary


def build_edge_decay_summary(findings: list[EdgeDecayFinding]) -> EdgeDecaySummary:
    """
    Build deterministic summary from findings. Does not mutate input.
    Counts by severity; strategies_seen and categories_seen in stable order.
    """
    total = len(findings)
    info_c = sum(1 for f in findings if f.severity == "info")
    warn_c = sum(1 for f in findings if f.severity == "warning")
    crit_c = sum(1 for f in findings if f.severity == "critical")
    strategies_seen = sorted(set(f.strategy_id for f in findings if f.strategy_id and str(f.strategy_id).strip()))
    categories_seen = sorted(set(f.category for f in findings))
    return EdgeDecaySummary(
        total_findings=total,
        info_count=info_c,
        warning_count=warn_c,
        critical_count=crit_c,
        strategies_seen=strategies_seen,
        categories_seen=categories_seen,
        metadata={},
    )


def build_edge_decay_report(
    report_id: str,
    generated_at: float,
    findings: list[EdgeDecayFinding],
    summary: EdgeDecaySummary | None = None,
    metadata: dict[str, Any] | None = None,
) -> EdgeDecayReport:
    """Build EdgeDecayReport. Does not mutate inputs."""
    if summary is None:
        summary = build_edge_decay_summary(findings)
    return EdgeDecayReport(
        report_id=report_id,
        generated_at=generated_at,
        findings=list(findings),
        summary=summary,
        metadata=metadata or {},
    )
