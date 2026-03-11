# NEBULA-QUANT v1 | nq_audit findings and recommendations

from __future__ import annotations

from nq_audit.models import AuditFinding, AuditFindingSeverity


# Category identifiers (deterministic, documented).
CATEGORY_REPEATED_BLOCKED = "repeated_blocked_decisions"
CATEGORY_EXCESSIVE_THROTTLING = "excessive_throttling"
CATEGORY_PROMOTION_REJECTIONS = "repeated_promotion_rejections"
CATEGORY_DEGRADED_STRATEGY = "degraded_strategy_detected"
CATEGORY_INACTIVE_STRATEGY = "inactive_strategy_detected"
CATEGORY_EXECUTION_FAILURE = "execution_failure_pattern"
CATEGORY_LIFECYCLE_INCONSISTENCY = "lifecycle_inconsistency_detected"
CATEGORY_EVENT_CONCENTRATION = "event_concentration"


def make_finding(
    finding_id: str,
    category: str,
    severity: AuditFindingSeverity,
    title: str,
    description: str,
    related_strategy_id: str | None = None,
    related_module: str | None = None,
    metadata: dict | None = None,
) -> AuditFinding:
    """Build an AuditFinding with string severity."""
    return AuditFinding(
        finding_id=finding_id,
        category=category,
        severity=severity.value,
        title=title,
        description=description,
        related_strategy_id=related_strategy_id,
        related_module=related_module,
        metadata=metadata or {},
    )


def severity_for_repeated_count(count: int, threshold_warning: int, threshold_critical: int) -> AuditFindingSeverity:
    """Deterministic severity: INFO below warning, WARNING in [warning, critical), CRITICAL at or above critical."""
    if count >= threshold_critical:
        return AuditFindingSeverity.CRITICAL
    if count >= threshold_warning:
        return AuditFindingSeverity.WARNING
    return AuditFindingSeverity.INFO


def recommendations_from_findings(findings: list[AuditFinding]) -> list[str]:
    """
    Derive deterministic recommendations from findings. One recommendation per relevant finding;
    no speculation beyond available finding fields.
    """
    out: list[str] = []
    for f in findings:
        if f.severity == AuditFindingSeverity.CRITICAL.value or f.severity == AuditFindingSeverity.WARNING.value:
            if f.related_strategy_id and "blocked" in f.category:
                out.append(f"Review strategy {f.related_strategy_id} due to repeated blocked decisions.")
            elif f.related_strategy_id and "promotion" in f.category:
                out.append(
                    f"Pause further promotion attempts for strategy {f.related_strategy_id} until lifecycle inconsistency is resolved."
                )
            elif f.related_module and "execution" in f.category:
                out.append(f"Investigate module {f.related_module} due to repeated execution failures.")
            elif f.related_strategy_id and "degraded" in f.category:
                out.append(f"Review degraded strategy {f.related_strategy_id}.")
            elif f.related_strategy_id and "inactive" in f.category:
                out.append(f"Review inactive strategy {f.related_strategy_id}.")
            elif f.related_module and "throttl" in f.category.lower():
                out.append(f"Review throttling patterns for module {f.related_module}.")
            elif "lifecycle" in f.category and f.related_strategy_id:
                out.append(
                    f"Resolve lifecycle inconsistency for strategy {f.related_strategy_id} before further promotion."
                )
    return out
