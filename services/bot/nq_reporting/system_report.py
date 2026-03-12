# NEBULA-QUANT v1 | nq_reporting — operational system report integration

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nq_release import ReleaseEngine, ReleaseError, ReleaseReport
from nq_reporting.engine import ReportEngine
from nq_reporting.models import ReportError, SystemReport
from nq_runbooks import RunbookEngine, RunbookError, RunbookReport
from nq_sre import SREEngine, SREError, SREReport


def _ensure_list(val: Any, name: str) -> list[Any]:
    if val is None:
        return []
    if not isinstance(val, list):
        raise ReportError(f"{name} must be a list or None")
    return list(val)


def _count_critical_incidents(sre_report: SREReport | None) -> int:
    if sre_report is None:
        return 0
    return sum(1 for inc in sre_report.incidents if getattr(inc, "severity", "").lower() == "critical")


def _recommended_runbook_ids(runbook_report: RunbookReport | None) -> list[str]:
    if runbook_report is None:
        return []
    ids = {rec.runbook_id for rec in (runbook_report.recommendations or [])}
    return sorted(ids)


def generate_system_report(
    sre_inputs: list[Any] | None,
    incidents: list[Any] | None,
    module_records: list[Any] | None,
    architecture_gate: Any = True,
    qa_gate: Any = True,
    *,
    clock: Callable[[], float] | None = None,
) -> SystemReport:
    """
    Generate a unified operational SystemReport by wiring:
    nq_sre → nq_runbooks → nq_release → nq_reporting.

    - sre_inputs: list of SREInput-like objects or dicts for SREEngine.
    - incidents: optional pre-normalized incidents; when None, incidents from SREReport are used.
    - module_records: list of release module records for ReleaseEngine.evaluate_release.
    - architecture_gate / qa_gate: gate flags passed to ReleaseEngine.

    Deterministic and fail-closed for invalid critical inputs.
    """
    # Validate top-level inputs in a fail-closed, non-mutating way.
    if sre_inputs is not None and not isinstance(sre_inputs, list):
        raise ReportError("sre_inputs must be a list or None")
    if module_records is not None and not isinstance(module_records, list):
        raise ReportError("module_records must be a list or None")

    sre_engine = SREEngine(clock=clock)
    runbook_engine = RunbookEngine(clock=clock)
    release_engine = ReleaseEngine(clock=clock)
    report_engine = ReportEngine(clock=clock)

    # Step 1 — Reliability evaluation (nq_sre)
    try:
        sre_report: SREReport = sre_engine.evaluate_reliability(sre_inputs or [])
    except SREError as exc:  # fail-closed
        raise ReportError(f"sre_evaluation_failed: {exc}") from exc

    # Step 2 — Runbook recommendations (nq_runbooks)
    incident_list = incidents if incidents is not None else list(sre_report.incidents or [])
    try:
        runbook_report: RunbookReport = runbook_engine.generate_runbook_recommendations(incident_list)
    except RunbookError as exc:
        raise ReportError(f"runbook_recommendation_failed: {exc}") from exc

    # Step 3 — Release governance (nq_release)
    try:
        release_report: ReleaseReport = release_engine.evaluate_release(
            release_name="operational",
            version_label="v1",
            module_records=module_records or [],
            architecture_gate=architecture_gate,
            qa_gate=qa_gate,
        )
    except ReleaseError as exc:
        raise ReportError(f"release_evaluation_failed: {exc}") from exc

    # Step 4 — Reporting (nq_reporting)
    # Base SystemReport from ReportEngine (no analytical subreports by default here).
    base_report = report_engine.generate_system_report()

    # Compute high-level summary for operational view.
    system_status = getattr(sre_report, "overall_status", "unknown")
    critical_incidents = _count_critical_incidents(sre_report)
    recommended_runbooks = _recommended_runbook_ids(runbook_report)
    release_status = getattr(release_report.decision, "status", "unknown")

    summary = {
        "system_status": system_status,
        "critical_incidents": critical_incidents,
        "recommended_runbooks": recommended_runbooks,
        "release_status": release_status,
    }

    # Enrich SystemReport with operational subreports and summary.
    base_report.sre_report = sre_report
    base_report.runbook_report = runbook_report
    base_report.release_report = release_report
    base_report.summary = summary

    if base_report.metadata is None:
        base_report.metadata = {}
    base_report.metadata.setdefault("report_type", "system")
    base_report.metadata["operational_pipeline"] = "nq_sre → nq_runbooks → nq_release → nq_reporting"

    return base_report

