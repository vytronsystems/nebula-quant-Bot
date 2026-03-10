# NEBULA-QUANT v1 | nq_experiments storage (in-memory placeholder, no DB)

from nq_experiments.models import ExperimentRecord

_registry: dict[str, ExperimentRecord] = {}


def add_experiment(record: ExperimentRecord) -> None:
    """Store experiment by experiment_id. In-memory only."""
    _registry[record.experiment_id] = record


def update_experiment(record: ExperimentRecord) -> None:
    """Overwrite existing experiment by experiment_id. In-memory only."""
    _registry[record.experiment_id] = record


def get_experiment_by_id(experiment_id: str) -> ExperimentRecord | None:
    """Return experiment by id or None if not found."""
    return _registry.get(experiment_id)


def list_all_experiments() -> list[ExperimentRecord]:
    """Return all stored experiments."""
    return list(_registry.values())
