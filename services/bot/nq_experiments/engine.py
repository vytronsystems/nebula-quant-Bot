# NEBULA-QUANT v1 | nq_experiments engine

import time
from dataclasses import replace
from typing import Any

from nq_experiments.models import ExperimentRecord, ExperimentsRegistryResult
from nq_experiments.storage import (
    add_experiment,
    update_experiment,
    get_experiment_by_id,
    list_all_experiments,
)
from nq_experiments.config import (
    DEFAULT_EXPERIMENT_OWNER,
    DEFAULT_EXPERIMENT_STATUS,
    DEFAULT_EXPERIMENT_TYPE,
)


class ExperimentsEngine:
    """
    Experiment tracking and research comparison layer. Records and compares
    backtest/walk-forward runs, parameters, metrics. Does not execute strategies
    or connect to brokers/APIs. In-memory only (skeleton).
    """

    def __init__(self) -> None:
        pass

    def register_experiment(
        self,
        experiment_id: str,
        strategy_id: str,
        strategy_version: str = "1.0.0",
        experiment_type: str | None = None,
        status: str | None = None,
        parameters: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
        notes: str = "",
        owner: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExperimentRecord:
        """Register an experiment. Safe defaults; no crash on empty inputs."""
        now = time.time()
        record = ExperimentRecord(
            experiment_id=experiment_id or "",
            strategy_id=strategy_id or "",
            strategy_version=strategy_version or "1.0.0",
            experiment_type=experiment_type or DEFAULT_EXPERIMENT_TYPE,
            status=status or DEFAULT_EXPERIMENT_STATUS,
            parameters=parameters or {},
            metrics=metrics or {},
            notes=notes or "",
            created_at=now,
            updated_at=now,
            owner=owner or DEFAULT_EXPERIMENT_OWNER,
            metadata=metadata or {},
        )
        add_experiment(record)
        return record

    def update_experiment_status(self, experiment_id: str, new_status: str) -> ExperimentRecord | None:
        """Update status of an experiment. Returns updated record or None if not found."""
        existing = get_experiment_by_id(experiment_id)
        if existing is None:
            return None
        updated = replace(existing, status=new_status, updated_at=time.time())
        update_experiment(updated)
        return updated

    def update_experiment_metrics(
        self,
        experiment_id: str,
        metrics: dict[str, Any],
    ) -> ExperimentRecord | None:
        """Update metrics of an experiment. Returns updated record or None if not found."""
        existing = get_experiment_by_id(experiment_id)
        if existing is None:
            return None
        updated = replace(
            existing,
            metrics={**existing.metrics, **metrics},
            updated_at=time.time(),
        )
        update_experiment(updated)
        return updated

    def get_experiment(self, experiment_id: str) -> ExperimentRecord | None:
        """Return experiment by id or None."""
        return get_experiment_by_id(experiment_id or "")

    def list_experiments(
        self,
        status_filter: str | None = None,
        experiment_type: str | None = None,
    ) -> list[ExperimentRecord]:
        """List experiments; optional filter by status and/or type."""
        all_e = list_all_experiments()
        if status_filter:
            all_e = [e for e in all_e if e.status == status_filter]
        if experiment_type:
            all_e = [e for e in all_e if e.experiment_type == experiment_type]
        return all_e

    def build_registry_result(
        self,
        experiments: list[ExperimentRecord] | None = None,
    ) -> ExperimentsRegistryResult:
        """Build ExperimentsRegistryResult. Safe for empty."""
        experiments = experiments if experiments is not None else list_all_experiments()
        active = sum(1 for e in experiments if e.status in ("pending", "running"))
        completed = sum(1 for e in experiments if e.status == "completed")
        failed = sum(1 for e in experiments if e.status == "failed")
        return ExperimentsRegistryResult(
            experiments=list(experiments),
            total_experiments=len(experiments),
            active_experiments=active,
            completed_experiments=completed,
            failed_experiments=failed,
            metadata={"skeleton": True},
        )
