# NEBULA-QUANT v1 | nq_sre — deterministic reliability evaluation rules

from __future__ import annotations

from typing import Any

from nq_sre.models import (
    CATEGORY_COMPONENT_DEGRADED,
    CATEGORY_COMPONENT_UNAVAILABLE,
    CATEGORY_EXCESSIVE_ERRORS,
    CATEGORY_MISSING_HEARTBEAT,
    CATEGORY_QUEUE_BACKLOG,
    CATEGORY_RELEASE_HEALTH_RISK,
    CATEGORY_REPEATED_FAILURES,
    CATEGORY_STALE_DATA,
    CATEGORY_STALE_SIGNAL,
    SREEvidence,
    SREIncident,
)

# Documented thresholds.
ERROR_COUNT_CRITICAL = 100
ERROR_COUNT_WARNING = 10
FAILED_JOBS_CRITICAL = 5
FAILED_JOBS_WARNING = 1
QUEUE_BACKLOG_CRITICAL = 100
QUEUE_BACKLOG_WARNING = 10
REPEATED_FAILURES_THRESHOLD = 3


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _int_or_none(val: Any) -> int | None:
    if val is None:
        return None
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    return None


def _bool_or_none(val: Any) -> bool | None:
    if val is None:
        return None
    return bool(val)


def evaluate_single_input(
    inp: Any,
    incident_id_prefix: str,
    evidence_id_prefix: str,
) -> tuple[list[SREIncident], list[SREEvidence]]:
    """
    Evaluate one SRE input. Returns (incidents, evidence). Deterministic; does not mutate input.
    """
    incidents: list[SREIncident] = []
    evidence: list[SREEvidence] = []
    inc_idx = [0]
    ev_idx = [0]

    def add_ev(category: str, value: Any, description: str) -> str:
        eid = f"{evidence_id_prefix}-{ev_idx[0]}"
        ev_idx[0] += 1
        evidence.append(SREEvidence(evidence_id=eid, category=category, value=value, description=description, metadata={}))
        return eid

    def add_incident(category: str, severity: str, title: str, description: str, rationale: str, ev_ids: list[str]) -> None:
        iid = f"{incident_id_prefix}-{inc_idx[0]}"
        inc_idx[0] += 1
        comp = _get(inp, "component_name") or _get(inp, "component")
        comp = str(comp).strip() if comp else None
        incidents.append(SREIncident(
            incident_id=iid,
            component_name=comp,
            category=category,
            severity=severity,
            title=title,
            description=description,
            evidence_ids=list(ev_ids),
            rationale=rationale,
            metadata={},
        ))

    comp_name = _get(inp, "component_name") or _get(inp, "component")
    comp_name = str(comp_name).strip() if comp_name else "unknown"
    status = _get(inp, "status")
    status = str(status).strip().lower() if status else None
    unavailable = _bool_or_none(_get(inp, "unavailable"))
    degraded = _bool_or_none(_get(inp, "degraded"))
    healthy = _bool_or_none(_get(inp, "healthy"))
    stale = _bool_or_none(_get(inp, "stale"))
    missing_heartbeat = _bool_or_none(_get(inp, "missing_heartbeat"))
    stale_data = _bool_or_none(_get(inp, "stale_data"))
    error_count = _int_or_none(_get(inp, "error_count"))
    failed_jobs = _int_or_none(_get(inp, "failed_jobs"))
    repeated_failures = _int_or_none(_get(inp, "repeated_failures"))
    queue_backlog = _int_or_none(_get(inp, "queue_backlog"))
    release_status = _get(inp, "release_status")
    release_status = str(release_status).strip().lower() if release_status else None

    add_ev("component", comp_name, f"Component {comp_name}")

    # A. Unavailable
    if unavailable is True or (status in ("unavailable", "down", "off")):
        eid = add_ev("unavailable", True, "Component reported unavailable")
        add_incident(
            CATEGORY_COMPONENT_UNAVAILABLE,
            "critical",
            f"Component {comp_name} unavailable",
            "Component reported unavailable state.",
            "Component reported unavailable state.",
            [eid],
        )
        return incidents, evidence

    # B. Degraded
    if degraded is True or (status in ("degraded",)):
        eid = add_ev("degraded", True, "Component reported degraded")
        add_incident(
            CATEGORY_COMPONENT_DEGRADED,
            "warning",
            f"Component {comp_name} degraded",
            "Component reported degraded state.",
            "Component reported degraded state.",
            [eid],
        )

    # C. Stale / stale_data
    if stale is True:
        eid = add_ev("stale", True, "Stale signal")
        add_incident(
            CATEGORY_STALE_SIGNAL,
            "warning",
            f"Stale signal for {comp_name}",
            "Stale signal detected.",
            "Stale signal detected for component.",
            [eid],
        )
    if stale_data is True:
        eid = add_ev("stale_data", True, "Stale data")
        add_incident(
            CATEGORY_STALE_DATA,
            "warning",
            f"Stale data for {comp_name}",
            "Stale data detected.",
            "Stale data detected for component.",
            [eid],
        )

    # D. Missing heartbeat
    if missing_heartbeat is True:
        eid = add_ev("missing_heartbeat", True, "Heartbeat missing")
        add_incident(
            CATEGORY_MISSING_HEARTBEAT,
            "critical",
            f"Missing heartbeat for {comp_name}",
            "Heartbeat missing.",
            "Heartbeat missing; component may be unresponsive.",
            [eid],
        )

    # E. Error count
    if error_count is not None:
        add_ev("error_count", error_count, "Error count")
        if error_count >= ERROR_COUNT_CRITICAL:
            add_incident(
                CATEGORY_EXCESSIVE_ERRORS,
                "critical",
                f"Excessive errors for {comp_name}",
                f"Error count {error_count} >= {ERROR_COUNT_CRITICAL}.",
                f"Error count exceeded critical threshold ({ERROR_COUNT_CRITICAL}).",
                [evidence[-1].evidence_id],
            )
        elif error_count >= ERROR_COUNT_WARNING:
            add_incident(
                CATEGORY_EXCESSIVE_ERRORS,
                "warning",
                f"Elevated errors for {comp_name}",
                f"Error count {error_count} >= {ERROR_COUNT_WARNING}.",
                f"Error count exceeded warning threshold ({ERROR_COUNT_WARNING}).",
                [evidence[-1].evidence_id],
            )

    # F. Failed jobs
    if failed_jobs is not None:
        add_ev("failed_jobs", failed_jobs, "Failed jobs count")
        if failed_jobs >= FAILED_JOBS_CRITICAL:
            add_incident(
                CATEGORY_REPEATED_FAILURES,
                "critical",
                f"Excessive failed jobs for {comp_name}",
                f"Failed jobs {failed_jobs} >= {FAILED_JOBS_CRITICAL}.",
                f"Failed jobs exceeded critical threshold ({FAILED_JOBS_CRITICAL}).",
                [evidence[-1].evidence_id],
            )
        elif failed_jobs >= FAILED_JOBS_WARNING:
            add_incident(
                CATEGORY_REPEATED_FAILURES,
                "warning",
                f"Failed jobs for {comp_name}",
                f"Failed jobs {failed_jobs} >= {FAILED_JOBS_WARNING}.",
                f"Failed jobs exceeded warning threshold ({FAILED_JOBS_WARNING}).",
                [evidence[-1].evidence_id],
            )

    # G. Repeated failures
    if repeated_failures is not None and repeated_failures >= REPEATED_FAILURES_THRESHOLD:
        eid = add_ev("repeated_failures", repeated_failures, "Repeated failures count")
        add_incident(
            CATEGORY_REPEATED_FAILURES,
            "warning",
            f"Repeated failures for {comp_name}",
            f"Repeated failures {repeated_failures} >= {REPEATED_FAILURES_THRESHOLD}.",
            f"Repeated failures exceeded threshold ({REPEATED_FAILURES_THRESHOLD}).",
            [eid],
        )

    # H. Queue backlog
    if queue_backlog is not None:
        add_ev("queue_backlog", queue_backlog, "Queue backlog")
        if queue_backlog >= QUEUE_BACKLOG_CRITICAL:
            add_incident(
                CATEGORY_QUEUE_BACKLOG,
                "critical",
                f"Queue backlog critical for {comp_name}",
                f"Queue backlog {queue_backlog} >= {QUEUE_BACKLOG_CRITICAL}.",
                f"Queue backlog exceeded critical threshold ({QUEUE_BACKLOG_CRITICAL}).",
                [evidence[-1].evidence_id],
            )
        elif queue_backlog >= QUEUE_BACKLOG_WARNING:
            add_incident(
                CATEGORY_QUEUE_BACKLOG,
                "warning",
                f"Queue backlog elevated for {comp_name}",
                f"Queue backlog {queue_backlog} >= {QUEUE_BACKLOG_WARNING}.",
                f"Queue backlog exceeded warning threshold ({QUEUE_BACKLOG_WARNING}).",
                [evidence[-1].evidence_id],
            )

    # I. Release health risk (blocked/rejected + unhealthy context)
    if release_status in ("blocked", "rejected") and (degraded is True or unavailable is True or len(incidents) > 0):
        eid = add_ev("release_status", release_status, "Release status")
        add_incident(
            CATEGORY_RELEASE_HEALTH_RISK,
            "info",
            f"Release health risk for {comp_name}",
            f"Release status {release_status} with operational concerns.",
            "Release is blocked/rejected and component has operational concerns.",
            [eid],
        )

    return incidents, evidence


def derive_overall_status(incidents: list[SREIncident], total_inputs: int) -> str:
    """
    Derive overall reliability status. Deterministic.
    UNAVAILABLE if any CRITICAL component_unavailable or missing_heartbeat;
    DEGRADED if any WARNING or other CRITICAL;
    HEALTHY if no incidents;
    UNKNOWN if no inputs.
    """
    from nq_sre.models import ReliabilityStatus

    if total_inputs == 0:
        return ReliabilityStatus.UNKNOWN.value
    if not incidents:
        return ReliabilityStatus.HEALTHY.value
    critical = [i for i in incidents if i.severity == "critical"]
    unavailable_cats = (CATEGORY_COMPONENT_UNAVAILABLE, CATEGORY_MISSING_HEARTBEAT)
    if any(i.category in unavailable_cats for i in critical):
        return ReliabilityStatus.UNAVAILABLE.value
    if critical or any(i.severity == "warning" for i in incidents):
        return ReliabilityStatus.DEGRADED.value
    return ReliabilityStatus.HEALTHY.value
