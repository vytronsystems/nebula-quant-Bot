# NEBULA-QUANT v1 | nq_experiments reporter

from typing import Any

from nq_experiments.models import (
    ExperimentsRegistryResult,
    ExperimentComparisonResult,
)


def build_experiments_report(result: ExperimentsRegistryResult) -> dict[str, Any]:
    """Build dictionary for dashboards and governance review. Skeleton only."""
    return {
        "total_experiments": result.total_experiments,
        "active_experiments": result.active_experiments,
        "completed_experiments": result.completed_experiments,
        "failed_experiments": result.failed_experiments,
        "experiments": [
            {
                "experiment_id": e.experiment_id,
                "strategy_id": e.strategy_id,
                "strategy_version": e.strategy_version,
                "experiment_type": e.experiment_type,
                "status": e.status,
                "owner": e.owner,
            }
            for e in result.experiments
        ],
        "metadata": result.metadata,
    }


def build_experiment_comparison_report(result: ExperimentComparisonResult) -> dict[str, Any]:
    """Build dictionary for comparison dashboards. Skeleton only."""
    return {
        "baseline_experiment_id": result.baseline_experiment_id,
        "candidate_experiment_id": result.candidate_experiment_id,
        "metric_deltas": result.metric_deltas,
        "winner": result.winner,
        "summary": result.summary,
        "metadata": result.metadata,
    }
