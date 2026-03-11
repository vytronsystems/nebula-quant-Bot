# NEBULA-QUANT v1 | nq_sre — reliability summary builders

from __future__ import annotations

from typing import Any

from nq_sre.models import SREIncident, SREReport, SRESummary


def build_sre_summary(
    total_inputs: int,
    incidents: list[SREIncident],
    overall_status: str,
    healthy_count: int = 0,
    degraded_count: int = 0,
    unavailable_count: int = 0,
) -> SRESummary:
    """
    Build deterministic summary from inputs count, incidents, and overall status.
    Does not mutate inputs. components_seen from incident component_name; categories_seen from incident category.
    """
    total_incidents = len(incidents)
    info_c = sum(1 for i in incidents if i.severity == "info")
    warn_c = sum(1 for i in incidents if i.severity == "warning")
    crit_c = sum(1 for i in incidents if i.severity == "critical")
    components_seen = sorted(set(i.component_name for i in incidents if i.component_name and str(i.component_name).strip()))
    categories_seen = sorted(set(i.category for i in incidents))
    return SRESummary(
        total_inputs=total_inputs,
        healthy_components=healthy_count,
        degraded_components=degraded_count,
        unavailable_components=unavailable_count,
        total_incidents=total_incidents,
        info_count=info_c,
        warning_count=warn_c,
        critical_count=crit_c,
        components_seen=components_seen,
        categories_seen=categories_seen,
        metadata={},
    )


def build_sre_report(
    report_id: str,
    generated_at: float,
    overall_status: str,
    incidents: list[SREIncident],
    summary: SRESummary,
    metadata: dict[str, Any] | None = None,
) -> SREReport:
    """Build SREReport. Does not mutate inputs."""
    return SREReport(
        report_id=report_id,
        generated_at=generated_at,
        overall_status=overall_status,
        incidents=list(incidents),
        summary=summary,
        metadata=metadata or {},
    )
