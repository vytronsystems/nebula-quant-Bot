# NEBULA-QUANT v1 | nq_sre — reliability evaluation engine

from __future__ import annotations

import hashlib
from typing import Any, Callable

from nq_sre.evaluators import derive_overall_status, evaluate_single_input
from nq_sre.models import (
    CATEGORY_COMPONENT_UNAVAILABLE,
    CATEGORY_MISSING_HEARTBEAT,
    SREError,
    SREIncident,
    SREReport,
    SRESummary,
)
from nq_sre.summaries import build_sre_report, build_sre_summary


def _default_clock() -> float:
    """Default clock: Unix timestamp. Override via SREEngine(clock=...)."""
    import time
    return time.time()


def _normalize_input(inp: Any) -> Any:
    """Return input as-is; validation happens in evaluator. Dict or SREInput-like."""
    return inp


def _validate_inputs(sre_inputs: Any) -> list[Any]:
    """
    Validate sre_inputs. Raises SREError if malformed.
    Returns list (empty if None or empty list). Missing optional fields (e.g. component_name) allowed.
    """
    if sre_inputs is None:
        return []
    if not isinstance(sre_inputs, list):
        raise SREError("sre_inputs must be a list or None")
    for i, item in enumerate(sre_inputs):
        if item is None:
            raise SREError(f"sre_inputs[{i}] must not be None")
    return list(sre_inputs)


def _component_state_for_incidents(incidents: list[SREIncident]) -> str:
    """Return 'unavailable' | 'degraded' | 'healthy' for this input's incidents."""
    if not incidents:
        return "healthy"
    critical_unav = [
        i for i in incidents
        if i.severity == "critical" and i.category in (CATEGORY_COMPONENT_UNAVAILABLE, CATEGORY_MISSING_HEARTBEAT)
    ]
    if critical_unav:
        return "unavailable"
    return "degraded"


def _deterministic_report_id(sre_inputs: list[Any]) -> str:
    """Generate deterministic report id from input fingerprint. Same inputs → same id."""
    if not sre_inputs:
        return "sre-report-empty"
    parts = []
    for inp in sre_inputs:
        name = None
        if hasattr(inp, "component_name"):
            name = getattr(inp, "component_name", None)
        elif hasattr(inp, "component"):
            name = getattr(inp, "component", None)
        elif isinstance(inp, dict):
            name = inp.get("component_name") or inp.get("component")
        parts.append(str(name) if name is not None else "")
    fingerprint = hashlib.sha256("|".join(parts).encode()).hexdigest()[:12]
    return f"sre-report-{fingerprint}"


class SREEngine:
    """
    Deterministic reliability evaluation engine.
    Clock is injectable for tests; default is time.time().
    """

    def __init__(self, clock: Callable[[], float] | None = None):
        self._clock = clock or _default_clock

    def evaluate_reliability(
        self,
        sre_inputs: list[Any] | None,
        report_id: str | None = None,
        generated_at: float | None = None,
    ) -> SREReport:
        """
        Evaluate reliability for the given inputs. Deterministic for same inputs.
        Empty/None inputs return a valid empty report.
        """
        inputs_list = _validate_inputs(sre_inputs)
        ts = float(generated_at) if generated_at is not None else self._clock()
        rid = report_id if report_id is not None else _deterministic_report_id(inputs_list)

        if not inputs_list:
            overall = "unknown"
            summary = build_sre_summary(0, [], overall, 0, 0, 0)
            return build_sre_report(rid, ts, overall, [], summary, {})

        all_incidents: list[SREIncident] = []
        healthy_count = 0
        degraded_count = 0
        unavailable_count = 0

        for idx, inp in enumerate(inputs_list):
            inp_norm = _normalize_input(inp)
            inc_prefix = f"incident-{idx}"
            ev_prefix = f"ev-{idx}"
            incidents, _evidence = evaluate_single_input(inp_norm, inc_prefix, ev_prefix)
            state = _component_state_for_incidents(incidents)
            if state == "unavailable":
                unavailable_count += 1
            elif state == "degraded":
                degraded_count += 1
            else:
                healthy_count += 1
            all_incidents.extend(incidents)

        overall = derive_overall_status(all_incidents, len(inputs_list))
        summary = build_sre_summary(
            len(inputs_list),
            all_incidents,
            overall,
            healthy_count=healthy_count,
            degraded_count=degraded_count,
            unavailable_count=unavailable_count,
        )
        return build_sre_report(rid, ts, overall, all_incidents, summary, {})
