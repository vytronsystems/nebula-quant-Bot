# NEBULA-QUANT v1 | nq_runbooks — incident-to-runbook matching

from __future__ import annotations

from typing import Any

from nq_runbooks.registry import get_runbooks_by_category, list_runbooks
from nq_runbooks.models import Runbook, RunbookMatch, RunbookStep


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _incident_category(incident: Any) -> str | None:
    """Extract category from incident (category or equivalent)."""
    cat = _get(incident, "category") or _get(incident, "incident_category")
    if cat is None:
        return None
    s = str(cat).strip()
    return s if s else None


def _incident_module(incident: Any) -> str | None:
    """Extract module/component from incident for secondary matching."""
    mod = _get(incident, "module") or _get(incident, "component_name") or _get(incident, "component")
    if mod is None:
        return None
    s = str(mod).strip()
    return s if s else None


def match_incident_to_runbook(
    incident: Any,
    incident_index: int,
    runbooks: list[Runbook] | None = None,
) -> tuple[RunbookMatch | None, Runbook | None]:
    """
    Match a single incident to a runbook. Deterministic.
    Returns (RunbookMatch, Runbook) if matched, else (None, None).
    Uses primary match: incident.category == runbook.incident_category.
    Secondary: incident.module/component_name in runbook.applicable_modules (same category).
    """
    category = _incident_category(incident)
    if not category:
        return None, None

    if runbooks is None:
        candidates = get_runbooks_by_category(category)
    else:
        candidates = [r for r in runbooks if r.incident_category == category]

    if not candidates:
        return None, None

    # Primary match: first runbook with matching category (deterministic order).
    runbook = candidates[0]
    module = _incident_module(incident)
    if module and runbook.applicable_modules and module in runbook.applicable_modules:
        rationale = f"Incident category '{category}' matches runbook; component/module '{module}' in applicable_modules."
        confidence = "high"
    else:
        rationale = f"Incident category '{category}' matches runbook incident_category."
        confidence = "high" if not runbook.applicable_modules else "medium"

    match_id = f"match-{incident_index}-{runbook.runbook_id}"
    match = RunbookMatch(
        match_id=match_id,
        incident_category=category,
        matched_runbook_id=runbook.runbook_id,
        confidence=confidence,
        rationale=rationale,
        metadata={},
    )
    return match, runbook


def match_incidents(
    incidents: list[Any],
    runbooks: list[Runbook] | None = None,
) -> tuple[list[tuple[RunbookMatch, Runbook]], list[tuple[int, Any]]]:
    """
    Match a list of incidents to runbooks. Returns:
    - matched: list of (RunbookMatch, Runbook) in incident order
    - unmatched: list of (incident_index, incident) for incidents with no match
    Deterministic ordering.
    """
    if runbooks is None:
        runbooks = list_runbooks()
    matched: list[tuple[RunbookMatch, Runbook]] = []
    unmatched: list[tuple[int, Any]] = []
    for idx, inc in enumerate(incidents):
        m, r = match_incident_to_runbook(inc, idx, runbooks)
        if m is not None and r is not None:
            matched.append((m, r))
        else:
            unmatched.append((idx, inc))
    return matched, unmatched
