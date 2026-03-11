# NEBULA-QUANT v1 | nq_experiments summary builders

from __future__ import annotations

from typing import Any

from nq_experiments.analyzers import _normalize_status
from nq_experiments.models import ExperimentFinding, ExperimentReport, ExperimentSummary


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def build_experiment_summary(
    experiment_records: list[Any],
    findings: list[ExperimentFinding],
) -> ExperimentSummary:
    """Build deterministic ExperimentSummary from records and findings. Does not mutate inputs."""
    total = len(experiment_records)
    success = failed = degraded = invalid = 0
    strategies_seen: set[str] = set()
    for rec in experiment_records:
        sid = _get(rec, "strategy_id")
        if sid is not None and str(sid).strip():
            strategies_seen.add(str(sid).strip())
        status = _normalize_status(_get(rec, "status"))
        if status == "success":
            success += 1
        elif status == "failed":
            failed += 1
        elif status == "degraded":
            degraded += 1
        elif status == "invalid":
            invalid += 1
    categories_seen: set[str] = set(f.category for f in findings)
    return ExperimentSummary(
        total_experiments=total,
        successful_experiments=success,
        failed_experiments=failed,
        degraded_experiments=degraded,
        invalid_experiments=invalid,
        strategies_seen=sorted(strategies_seen),
        categories_seen=sorted(categories_seen),
        metadata={},
    )


def build_experiment_report(
    report_id: str,
    generated_at: float,
    summary: ExperimentSummary,
    findings: list[ExperimentFinding],
    experiment_records: list[Any],
    metadata: dict[str, Any] | None = None,
) -> ExperimentReport:
    """Build ExperimentReport. Does not mutate inputs."""
    return ExperimentReport(
        report_id=report_id,
        generated_at=generated_at,
        summary=summary,
        findings=list(findings),
        experiment_records=list(experiment_records),
        metadata=metadata or {},
    )
