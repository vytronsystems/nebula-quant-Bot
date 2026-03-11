# NEBULA-QUANT v1 | nq_experiments deterministic analyzers

from __future__ import annotations

from typing import Any

from nq_experiments.models import (
    CATEGORY_EXPERIMENT_DEGRADED,
    CATEGORY_EXPERIMENT_FAILED,
    CATEGORY_EXPERIMENT_INVALID,
    CATEGORY_INCONSISTENT_RECORD,
    CATEGORY_MISSING_METRICS,
    CATEGORY_UNSTABLE_RESULT,
    CATEGORY_WEAK_RESULT,
    ExperimentFinding,
    ExperimentFindingSeverity,
    ExperimentError,
    VALID_EXPERIMENT_TYPES,
    VALID_STATUSES,
)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _normalize_status(status: Any) -> str:
    """Normalize status; 'completed' -> 'success' for alignment with ExperimentStatus."""
    if status is None:
        return "invalid"
    s = str(status).strip().lower()
    if s == "completed":
        return "success"
    return s


def validate_experiment_record(record: Any) -> None:
    """Validate record. Raises ExperimentError if critical fields missing or invalid."""
    if record is None:
        raise ExperimentError("experiment record must not be None")
    eid = _get(record, "experiment_id")
    if not eid or not str(eid).strip():
        raise ExperimentError("experiment_id must be non-empty")
    status = _normalize_status(_get(record, "status"))
    if status not in VALID_STATUSES:
        raise ExperimentError(f"status must be one of {sorted(VALID_STATUSES)}, got {_get(record, 'status')!r}")
    etype = _get(record, "experiment_type")
    if etype is not None and str(etype).strip().lower() not in VALID_EXPERIMENT_TYPES:
        raise ExperimentError(f"experiment_type must be one of {sorted(VALID_EXPERIMENT_TYPES)}, got {etype!r}")
    metrics = _get(record, "metrics")
    if metrics is not None and not isinstance(metrics, dict):
        raise ExperimentError("metrics must be a dict or None")


def _findings_failed(record: Any, experiment_id: str, strategy_id: str | None, finding_idx: int) -> ExperimentFinding | None:
    status = _normalize_status(_get(record, "status"))
    if status != "failed":
        return None
    return ExperimentFinding(
        finding_id=f"finding-{experiment_id}-{finding_idx}",
        category=CATEGORY_EXPERIMENT_FAILED,
        severity=ExperimentFindingSeverity.CRITICAL.value,
        title="Experiment failed",
        description=f"Experiment {experiment_id} has status failed.",
        experiment_id=experiment_id,
        strategy_id=strategy_id,
        metadata={},
    )


def _findings_degraded(record: Any, experiment_id: str, strategy_id: str | None, finding_idx: int) -> ExperimentFinding | None:
    status = _normalize_status(_get(record, "status"))
    if status != "degraded":
        return None
    return ExperimentFinding(
        finding_id=f"finding-{experiment_id}-{finding_idx}",
        category=CATEGORY_EXPERIMENT_DEGRADED,
        severity=ExperimentFindingSeverity.WARNING.value,
        title="Experiment degraded",
        description=f"Experiment {experiment_id} is in degraded state.",
        experiment_id=experiment_id,
        strategy_id=strategy_id,
        metadata={},
    )


def _findings_invalid(record: Any, experiment_id: str, strategy_id: str | None, finding_idx: int) -> ExperimentFinding | None:
    status = _normalize_status(_get(record, "status"))
    if status != "invalid":
        return None
    return ExperimentFinding(
        finding_id=f"finding-{experiment_id}-{finding_idx}",
        category=CATEGORY_EXPERIMENT_INVALID,
        severity=ExperimentFindingSeverity.CRITICAL.value,
        title="Experiment invalid",
        description=f"Experiment {experiment_id} has invalid status or data.",
        experiment_id=experiment_id,
        strategy_id=strategy_id,
        metadata={},
    )


def _findings_missing_metrics(record: Any, experiment_id: str, strategy_id: str | None, finding_idx: int) -> ExperimentFinding | None:
    metrics = _get(record, "metrics")
    if metrics is None:
        return ExperimentFinding(
            finding_id=f"finding-{experiment_id}-{finding_idx}",
            category=CATEGORY_MISSING_METRICS,
            severity=ExperimentFindingSeverity.WARNING.value,
            title="Missing metrics",
            description=f"Experiment {experiment_id} has no metrics.",
            experiment_id=experiment_id,
            strategy_id=strategy_id,
            metadata={},
        )
    if not isinstance(metrics, dict) or len(metrics) == 0:
        return ExperimentFinding(
            finding_id=f"finding-{experiment_id}-{finding_idx}",
            category=CATEGORY_MISSING_METRICS,
            severity=ExperimentFindingSeverity.INFO.value,
            title="Missing or empty metrics",
            description=f"Experiment {experiment_id} has no metric values.",
            experiment_id=experiment_id,
            strategy_id=strategy_id,
            metadata={},
        )
    return None


def _findings_weak_result(record: Any, experiment_id: str, strategy_id: str | None, finding_idx: int) -> ExperimentFinding | None:
    metrics = _get(record, "metrics")
    if not isinstance(metrics, dict):
        return None
    pnl = metrics.get("pnl") if isinstance(metrics.get("pnl"), (int, float)) else metrics.get("total_pnl")
    win_rate = metrics.get("win_rate") if isinstance(metrics.get("win_rate"), (int, float)) else metrics.get("win_rate_pct")
    expectancy = metrics.get("expectancy")
    if pnl is not None and isinstance(pnl, (int, float)) and float(pnl) < 0:
        return ExperimentFinding(
            finding_id=f"finding-{experiment_id}-{finding_idx}",
            category=CATEGORY_WEAK_RESULT,
            severity=ExperimentFindingSeverity.WARNING.value,
            title="Weak result: negative PnL",
            description=f"Experiment {experiment_id} has negative PnL.",
            experiment_id=experiment_id,
            strategy_id=strategy_id,
            metadata={"pnl": float(pnl)},
        )
    if win_rate is not None and isinstance(win_rate, (int, float)) and float(win_rate) < 0.3:
        return ExperimentFinding(
            finding_id=f"finding-{experiment_id}-{finding_idx}",
            category=CATEGORY_WEAK_RESULT,
            severity=ExperimentFindingSeverity.INFO.value,
            title="Weak result: low win rate",
            description=f"Experiment {experiment_id} has win rate below 0.3.",
            experiment_id=experiment_id,
            strategy_id=strategy_id,
            metadata={"win_rate": float(win_rate)},
        )
    if expectancy is not None and isinstance(expectancy, (int, float)) and float(expectancy) < 0:
        return ExperimentFinding(
            finding_id=f"finding-{experiment_id}-{finding_idx}",
            category=CATEGORY_WEAK_RESULT,
            severity=ExperimentFindingSeverity.WARNING.value,
            title="Weak result: negative expectancy",
            description=f"Experiment {experiment_id} has negative expectancy.",
            experiment_id=experiment_id,
            strategy_id=strategy_id,
            metadata={"expectancy": float(expectancy)},
        )
    return None


def _findings_inconsistent(record: Any, experiment_id: str, strategy_id: str | None, finding_idx: int) -> ExperimentFinding | None:
    started = _get(record, "started_at")
    finished = _get(record, "finished_at")
    created = _get(record, "created_at")
    updated = _get(record, "updated_at")
    if started is not None and finished is not None and isinstance(started, (int, float)) and isinstance(finished, (int, float)):
        if float(finished) < float(started):
            return ExperimentFinding(
                finding_id=f"finding-{experiment_id}-{finding_idx}",
                category=CATEGORY_INCONSISTENT_RECORD,
                severity=ExperimentFindingSeverity.CRITICAL.value,
                title="Inconsistent experiment record",
                description=f"Experiment {experiment_id}: finished_at < started_at.",
                experiment_id=experiment_id,
                strategy_id=strategy_id,
                metadata={},
            )
    if created is not None and updated is not None and isinstance(created, (int, float)) and isinstance(updated, (int, float)):
        if float(updated) < float(created):
            return ExperimentFinding(
                finding_id=f"finding-{experiment_id}-{finding_idx}",
                category=CATEGORY_INCONSISTENT_RECORD,
                severity=ExperimentFindingSeverity.WARNING.value,
                title="Inconsistent experiment record",
                description=f"Experiment {experiment_id}: updated_at < created_at.",
                experiment_id=experiment_id,
                strategy_id=strategy_id,
                metadata={},
            )
    return None


def analyze_experiment_records(records: list[Any]) -> list[ExperimentFinding]:
    """Produce deterministic findings from experiment records. Validates each record; invalid raises ExperimentError."""
    findings: list[ExperimentFinding] = []
    for i, rec in enumerate(records):
        validate_experiment_record(rec)
        eid = str(_get(rec, "experiment_id") or "").strip()
        sid = _get(rec, "strategy_id")
        if sid is not None:
            sid = str(sid).strip() or None
        finding_idx = 1
        for fn in (
            _findings_failed,
            _findings_degraded,
            _findings_invalid,
            _findings_missing_metrics,
            _findings_weak_result,
            _findings_inconsistent,
        ):
            f = fn(rec, eid, sid, finding_idx)
            if f is not None:
                findings.append(f)
                finding_idx += 1
    return findings
