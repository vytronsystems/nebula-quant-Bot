# NEBULA-QUANT v1 | nq_experiments comparison (skeleton)

from typing import Any

from nq_experiments.models import ExperimentComparisonResult


def build_metric_deltas(
    baseline_metrics: dict[str, Any] | None,
    candidate_metrics: dict[str, Any] | None,
) -> dict[str, float]:
    """Build deltas between two metric dicts. Skeleton: returns empty or safe placeholder."""
    baseline_metrics = baseline_metrics or {}
    candidate_metrics = candidate_metrics or {}
    deltas: dict[str, float] = {}
    all_keys = set(baseline_metrics) | set(candidate_metrics)
    for k in all_keys:
        b = baseline_metrics.get(k)
        c = candidate_metrics.get(k)
        if isinstance(b, (int, float)) and isinstance(c, (int, float)):
            deltas[k] = float(c) - float(b)
    return deltas


def compare_experiments(
    baseline_id: str,
    candidate_id: str,
    baseline_metrics: dict[str, Any] | None = None,
    candidate_metrics: dict[str, Any] | None = None,
) -> ExperimentComparisonResult:
    """Compare two experiments by metrics. Skeleton: safe defaults, no crash on empty."""
    baseline_metrics = baseline_metrics or {}
    candidate_metrics = candidate_metrics or {}
    deltas = build_metric_deltas(baseline_metrics, candidate_metrics)
    return ExperimentComparisonResult(
        baseline_experiment_id=baseline_id or "",
        candidate_experiment_id=candidate_id or "",
        metric_deltas=deltas,
        winner="",
        summary="skeleton comparison (no winner logic)",
        metadata={"skeleton": True},
    )
