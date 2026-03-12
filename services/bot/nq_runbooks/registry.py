# NEBULA-QUANT v1 | nq_runbooks — runbook registry

from __future__ import annotations

from typing import Any

from nq_runbooks.models import Runbook, RunbookError, RunbookStep


def _validate_step(step: Any, index: int) -> None:
    """Validate a single step. Raises RunbookError if invalid."""
    if step is None:
        raise RunbookError(f"Runbook step at index {index} must not be None")
    step_id = _get(step, "step_id")
    description = _get(step, "description")
    action_type = _get(step, "action_type")
    if not step_id or not str(step_id).strip():
        raise RunbookError(f"Runbook step at index {index} must have non-empty step_id")
    if description is None:
        raise RunbookError(f"Runbook step at index {index} must have description")
    if not action_type or not str(action_type).strip():
        raise RunbookError(f"Runbook step at index {index} must have non-empty action_type")


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _runbook_to_internal(runbook: Any) -> Runbook:
    """Convert dict or Runbook to Runbook with validated steps."""
    runbook_id = _get(runbook, "runbook_id")
    title = _get(runbook, "title", "")
    description = _get(runbook, "description", "")
    incident_category = _get(runbook, "incident_category")
    applicable_modules = _get(runbook, "applicable_modules")
    severity = _get(runbook, "severity", "info")
    steps_raw = _get(runbook, "steps")
    version = _get(runbook, "version", "1.0")
    metadata = _get(runbook, "metadata") or {}

    if not runbook_id or not str(runbook_id).strip():
        raise RunbookError("Runbook must have non-empty runbook_id")
    if not incident_category or not str(incident_category).strip():
        raise RunbookError("Runbook must have non-empty incident_category")
    if not isinstance(steps_raw, list):
        raise RunbookError("Runbook steps must be a list")

    steps: list[RunbookStep] = []
    for i, s in enumerate(steps_raw):
        _validate_step(s, i)
        steps.append(RunbookStep(
            step_id=str(_get(s, "step_id")).strip(),
            description=str(_get(s, "description")),
            action_type=str(_get(s, "action_type")).strip(),
            expected_outcome=_get(s, "expected_outcome"),
            metadata=_get(s, "metadata") or {},
        ))

    if not isinstance(applicable_modules, list):
        applicable_modules = []
    else:
        applicable_modules = [str(m).strip() for m in applicable_modules if m is not None and str(m).strip()]

    return Runbook(
        runbook_id=str(runbook_id).strip(),
        title=str(title) if title else "",
        description=str(description) if description else "",
        incident_category=str(incident_category).strip(),
        applicable_modules=applicable_modules,
        severity=str(severity).strip().lower() if severity else "info",
        steps=steps,
        version=str(version) if version else "1.0",
        metadata=metadata,
    )


# Module-level registry: deterministic order by registration order.
_runbooks: list[Runbook] = []
_runbooks_by_id: dict[str, Runbook] = {}


def register_runbook(runbook: Any) -> None:
    """
    Register a runbook. Validates structure. Same runbook_id re-registration replaces previous.
    Order is deterministic (registration order).
    """
    r = _runbook_to_internal(runbook)
    if r.runbook_id in _runbooks_by_id:
        # Replace: remove old from list, then append new
        _runbooks[:] = [x for x in _runbooks if x.runbook_id != r.runbook_id]
    _runbooks_by_id[r.runbook_id] = r
    _runbooks.append(r)


def list_runbooks() -> list[Runbook]:
    """Return all runbooks in deterministic (registration) order."""
    return list(_runbooks)


def get_runbooks_by_category(category: str) -> list[Runbook]:
    """Return runbooks whose incident_category matches. Order is deterministic (registry order)."""
    if not category or not str(category).strip():
        return []
    cat = str(category).strip()
    return [r for r in _runbooks if r.incident_category == cat]


def clear_registry() -> None:
    """Clear the registry. For tests only."""
    global _runbooks, _runbooks_by_id
    _runbooks = []
    _runbooks_by_id = {}
