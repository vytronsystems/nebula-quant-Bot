# NEBULA-QUANT v1 | nq_runbooks — runbook recommendation engine

from __future__ import annotations

import hashlib
from typing import Any, Callable

from nq_runbooks.matcher import match_incident_to_runbook
from nq_runbooks.models import (
    RunbookError,
    RunbookRecommendation,
    RunbookReport,
    RunbookSummary,
)
from nq_runbooks.registry import list_runbooks


def _default_clock() -> float:
    import time
    return time.time()


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _validate_incidents(incidents: Any) -> list[Any]:
    """Validate incidents input. Raises RunbookError if invalid. Returns list."""
    if incidents is None:
        return []
    if not isinstance(incidents, list):
        raise RunbookError("incidents must be a list or None")
    for i, item in enumerate(incidents):
        if item is None:
            raise RunbookError(f"incidents[{i}] must not be None")
        cat = _get(item, "category") or _get(item, "incident_category")
        if cat is None:
            raise RunbookError(f"incidents[{i}] must have category or incident_category")
        if not str(cat).strip():
            raise RunbookError(f"incidents[{i}] category must be non-empty")
    return list(incidents)


def _incident_id(incident: Any) -> str:
    """Extract incident_id from incident for recommendation."""
    iid = _get(incident, "incident_id") or _get(incident, "id")
    if iid is not None and str(iid).strip():
        return str(iid).strip()
    return "unknown"


def _deterministic_report_id(incidents: list[Any]) -> str:
    """Generate deterministic report id from incident fingerprint."""
    if not incidents:
        return "runbook-report-empty"
    parts = []
    for inc in incidents:
        cat = _get(inc, "category") or _get(inc, "incident_category")
        iid = _get(inc, "incident_id") or _get(inc, "id")
        parts.append(f"{cat}:{iid}")
    fingerprint = hashlib.sha256("|".join(parts).encode()).hexdigest()[:12]
    return f"runbook-report-{fingerprint}"


def _build_summary(
    total_runbooks: int,
    recommendations: list[RunbookRecommendation],
    unmatched_incidents: list[Any],
    categories_covered: set[str],
    modules_covered: set[str],
) -> RunbookSummary:
    """Build deterministic summary."""
    return RunbookSummary(
        total_runbooks=total_runbooks,
        categories_covered=sorted(categories_covered),
        modules_covered=sorted(modules_covered),
        recommendations_generated=len(recommendations),
        unmatched_incidents=len(unmatched_incidents),
        metadata={},
    )


class RunbookEngine:
    """
    Deterministic runbook recommendation engine.
    Does not execute runbooks; produces recommendations only.
    """

    def __init__(self, clock: Callable[[], float] | None = None):
        self._clock = clock or _default_clock

    def generate_runbook_recommendations(
        self,
        incidents: list[Any] | None,
        report_id: str | None = None,
        generated_at: float | None = None,
    ) -> RunbookReport:
        """
        Generate runbook recommendations for the given incidents.
        Deterministic: same incidents → same recommendations and ordering.
        """
        incidents_list = _validate_incidents(incidents)
        ts = float(generated_at) if generated_at is not None else self._clock()
        rid = report_id if report_id is not None else _deterministic_report_id(incidents_list)
        runbooks = list_runbooks()

        if not incidents_list:
            summary = _build_summary(len(runbooks), [], [], set(), set())
            return RunbookReport(
                report_id=rid,
                generated_at=ts,
                recommendations=[],
                unmatched_incidents=[],
                summary=summary,
                metadata={},
            )

        recommendations: list[RunbookRecommendation] = []
        unmatched_incidents: list[Any] = []
        categories_covered: set[str] = set()
        modules_covered: set[str] = set()

        for idx, incident in enumerate(incidents_list):
            match, runbook = match_incident_to_runbook(incident, idx, runbooks)
            if match is not None and runbook is not None:
                rec_id = f"rec-{idx}-{runbook.runbook_id}"
                recommendations.append(RunbookRecommendation(
                    recommendation_id=rec_id,
                    incident_id=_incident_id(incident),
                    runbook_id=runbook.runbook_id,
                    steps=list(runbook.steps),
                    rationale=match.rationale,
                    metadata={},
                ))
                categories_covered.add(runbook.incident_category)
                modules_covered.update(runbook.applicable_modules)
            else:
                unmatched_incidents.append(incident)

        summary = _build_summary(
            len(runbooks),
            recommendations,
            unmatched_incidents,
            categories_covered,
            modules_covered,
        )
        return RunbookReport(
            report_id=rid,
            generated_at=ts,
            recommendations=recommendations,
            unmatched_incidents=unmatched_incidents,
            summary=summary,
            metadata={},
        )