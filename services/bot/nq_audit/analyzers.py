# NEBULA-QUANT v1 | nq_audit deterministic analyzers

from __future__ import annotations

from collections import defaultdict
from typing import Any

from nq_audit.findings import (
    CATEGORY_DEGRADED_STRATEGY,
    CATEGORY_EVENT_CONCENTRATION,
    CATEGORY_EXCESSIVE_THROTTLING,
    CATEGORY_EXECUTION_FAILURE,
    CATEGORY_INACTIVE_STRATEGY,
    CATEGORY_LIFECYCLE_INCONSISTENCY,
    CATEGORY_PROMOTION_REJECTIONS,
    CATEGORY_REPEATED_BLOCKED,
    make_finding,
    severity_for_repeated_count,
)
from nq_audit.models import AuditError, AuditFinding, AuditInput, AuditFindingSeverity

# Thresholds (deterministic, documented).
THRESHOLD_BLOCKED_WARNING = 2
THRESHOLD_BLOCKED_CRITICAL = 5
THRESHOLD_THROTTLE_WARNING = 2
THRESHOLD_THROTTLE_CRITICAL = 5
THRESHOLD_PROMOTION_REJECT_WARNING = 2
THRESHOLD_PROMOTION_REJECT_CRITICAL = 5
THRESHOLD_EXECUTION_FAILURE_WARNING = 2
THRESHOLD_EXECUTION_FAILURE_CRITICAL = 10


def _ensure_list(value: Any, name: str) -> list[Any]:
    """Fail closed if critical input is not a list."""
    if not isinstance(value, list):
        raise AuditError(f"audit input {name} must be a list, got {type(value).__name__}")
    return value


def _safe_strategy_id(rec: dict[str, Any]) -> str | None:
    return rec.get("strategy_id") if isinstance(rec.get("strategy_id"), str) else None


def _safe_module(rec: dict[str, Any]) -> str | None:
    return rec.get("module") if isinstance(rec.get("module"), str) else None


def analyze_decision_concentration(input_data: AuditInput) -> list[AuditFinding]:
    """Repeated blocked, throttled, and promotion rejections by strategy/module."""
    findings: list[AuditFinding] = []
    decisions = _ensure_list(input_data.decision_records, "decision_records")

    blocked_counts: dict[str, int] = defaultdict(int)
    throttle_counts: dict[str, int] = defaultdict(int)
    promotion_reject_by: dict[str, int] = defaultdict(int)

    for rec in decisions:
        if not isinstance(rec, dict):
            continue
        mod = _safe_module(rec) or "unknown"
        sid = _safe_strategy_id(rec)
        key = sid or mod

        action = rec.get("action") if isinstance(rec.get("action"), str) else None
        outcome = rec.get("outcome") if isinstance(rec.get("outcome"), str) else None
        blocked = rec.get("blocked") is True or (isinstance(outcome, str) and outcome.lower() == "blocked")
        throttled = rec.get("throttled") is True or (isinstance(action, str) and "throttle" in action.lower())
        promotion_reject = (
            rec.get("promotion_rejected") is True
            or (isinstance(outcome, str) and "reject" in outcome.lower() and "promotion" in str(rec.get("category", "")).lower())
        )

        if blocked:
            blocked_counts[key] += 1
        if throttled:
            throttle_counts[key] += 1
        if promotion_reject and sid:
            promotion_reject_by[sid] += 1

    for key, count in blocked_counts.items():
        if count < THRESHOLD_BLOCKED_WARNING:
            continue
        severity = severity_for_repeated_count(count, THRESHOLD_BLOCKED_WARNING, THRESHOLD_BLOCKED_CRITICAL)
        findings.append(
            make_finding(
                f"blocked-{key}-{count}",
                CATEGORY_REPEATED_BLOCKED,
                severity,
                "Repeated blocked decisions",
                f"Blocked decisions count: {count} for {key}.",
                related_strategy_id=key if key not in ("unknown",) else None,
                related_module=key if key == "unknown" else None,
            )
        )

    for key, count in throttle_counts.items():
        if count < THRESHOLD_THROTTLE_WARNING:
            continue
        severity = severity_for_repeated_count(count, THRESHOLD_THROTTLE_WARNING, THRESHOLD_THROTTLE_CRITICAL)
        findings.append(
            make_finding(
                f"throttle-{key}-{count}",
                CATEGORY_EXCESSIVE_THROTTLING,
                severity,
                "Excessive throttling",
                f"Throttle count: {count} for {key}.",
                related_strategy_id=key if key != "unknown" else None,
                related_module=key if key == "unknown" else None,
            )
        )

    for sid, count in promotion_reject_by.items():
        if count < THRESHOLD_PROMOTION_REJECT_WARNING:
            continue
        severity = severity_for_repeated_count(
            count, THRESHOLD_PROMOTION_REJECT_WARNING, THRESHOLD_PROMOTION_REJECT_CRITICAL
        )
        findings.append(
            make_finding(
                f"promo-reject-{sid}-{count}",
                CATEGORY_PROMOTION_REJECTIONS,
                severity,
                "Repeated promotion rejections",
                f"Promotion rejections: {count} for strategy {sid}.",
                related_strategy_id=sid,
                related_module="nq_promotion",
            )
        )

    return findings


def analyze_execution_anomalies(input_data: AuditInput) -> list[AuditFinding]:
    """Repeated execution failures/rejections by strategy or module."""
    findings: list[AuditFinding] = []
    records = _ensure_list(input_data.execution_records, "execution_records")

    failure_by_key: dict[str, int] = defaultdict(int)
    for rec in records:
        if not isinstance(rec, dict):
            continue
        failed = rec.get("success") is False or rec.get("failed") is True or (isinstance(rec.get("outcome"), str) and "fail" in rec.get("outcome", "").lower())
        if not failed:
            continue
        sid = _safe_strategy_id(rec)
        mod = _safe_module(rec) or "nq_exec"
        key = sid or mod
        failure_by_key[key] += 1

    for key, count in failure_by_key.items():
        if count < THRESHOLD_EXECUTION_FAILURE_WARNING:
            continue
        severity = severity_for_repeated_count(
            count, THRESHOLD_EXECUTION_FAILURE_WARNING, THRESHOLD_EXECUTION_FAILURE_CRITICAL
        )
        findings.append(
            make_finding(
                f"exec-fail-{key}-{count}",
                CATEGORY_EXECUTION_FAILURE,
                severity,
                "Execution failure pattern",
                f"Execution failures: {count} for {key}.",
                related_strategy_id=key if key != "nq_exec" else None,
                related_module=key if key == "nq_exec" else None,
            )
        )
    return findings


def analyze_strategy_health(input_data: AuditInput) -> list[AuditFinding]:
    """Degraded or inactive strategy health."""
    findings: list[AuditFinding] = []
    health_list = _ensure_list(input_data.strategy_health, "strategy_health")

    for rec in health_list:
        if not isinstance(rec, dict):
            continue
        sid = _safe_strategy_id(rec)
        if not sid:
            continue
        status = rec.get("status") if isinstance(rec.get("status"), str) else None
        health = rec.get("health") if isinstance(rec.get("health"), str) else None
        state = (health or status or "").lower()
        if "degraded" in state or rec.get("degraded") is True:
            findings.append(
                make_finding(
                    f"degraded-{sid}",
                    CATEGORY_DEGRADED_STRATEGY,
                    AuditFindingSeverity.WARNING,
                    "Degraded strategy detected",
                    f"Strategy {sid} is in degraded state.",
                    related_strategy_id=sid,
                    metadata={"status": status, "health": health},
                )
            )
        if "inactive" in state or rec.get("inactive") is True or (status and "inactive" in status.lower()):
            findings.append(
                make_finding(
                    f"inactive-{sid}",
                    CATEGORY_INACTIVE_STRATEGY,
                    AuditFindingSeverity.INFO,
                    "Inactive strategy detected",
                    f"Strategy {sid} is inactive.",
                    related_strategy_id=sid,
                    metadata={"status": status, "health": health},
                )
            )
    return findings


def analyze_lifecycle_consistency(input_data: AuditInput) -> list[AuditFinding]:
    """Non-executable or inconsistent lifecycle from registry/control summary."""
    findings: list[AuditFinding] = []
    registry = input_data.registry_records
    if registry is not None and not isinstance(registry, list):
        raise AuditError("audit input registry_records must be a list or None")
    control = input_data.control_summary

    if registry:
        for rec in registry:
            if not isinstance(rec, dict):
                continue
            sid = _safe_strategy_id(rec)
            if not sid:
                continue
            executable = rec.get("executable")
            state = rec.get("lifecycle_state") or rec.get("state")
            if executable is False and state:
                findings.append(
                    make_finding(
                        f"lifecycle-{sid}",
                        CATEGORY_LIFECYCLE_INCONSISTENCY,
                        AuditFindingSeverity.WARNING,
                        "Lifecycle inconsistency detected",
                        f"Strategy {sid} is non-executable (state: {state}).",
                        related_strategy_id=sid,
                        related_module="nq_strategy_registry",
                    )
                )

    if isinstance(control, dict):
        inconsistent = control.get("inconsistent_strategies") or control.get("lifecycle_issues") or []
        if isinstance(inconsistent, list):
            for sid in inconsistent:
                if isinstance(sid, str):
                    findings.append(
                        make_finding(
                            f"lifecycle-ctrl-{sid}",
                            CATEGORY_LIFECYCLE_INCONSISTENCY,
                            AuditFindingSeverity.WARNING,
                            "Lifecycle inconsistency detected",
                            f"Strategy {sid} has lifecycle inconsistency (control summary).",
                            related_strategy_id=sid,
                        )
                    )
    return findings


def analyze_event_stream(input_data: AuditInput) -> list[AuditFinding]:
    """Summarize event types/counts and concentrations by module/category."""
    findings: list[AuditFinding] = []
    events = _ensure_list(input_data.events, "events")

    type_counts: dict[str, int] = defaultdict(int)
    module_counts: dict[str, int] = defaultdict(int)
    for ev in events:
        if not isinstance(ev, dict):
            continue
        et = ev.get("event_type") or ev.get("type") or "unknown"
        if isinstance(et, str):
            type_counts[et] += 1
        mod = ev.get("aggregate_type") or ev.get("module") or ev.get("source")
        if isinstance(mod, str):
            module_counts[mod] += 1

    total = sum(type_counts.values())
    if total > 0:
        for et, count in sorted(type_counts.items()):
            if count >= max(10, total // 2):
                findings.append(
                    make_finding(
                        f"event-concentration-{et}-{count}",
                        CATEGORY_EVENT_CONCENTRATION,
                        AuditFindingSeverity.INFO,
                        "Event concentration",
                        f"Event type {et} has {count} events (total {total}).",
                        related_module=et,
                        metadata={"count": count, "total": total},
                    )
                )
    return findings


def run_all_analyzers(input_data: AuditInput) -> list[AuditFinding]:
    """Run all analyzers and return combined findings. Fails closed on malformed critical input."""
    combined: list[AuditFinding] = []
    combined.extend(analyze_decision_concentration(input_data))
    combined.extend(analyze_execution_anomalies(input_data))
    combined.extend(analyze_strategy_health(input_data))
    combined.extend(analyze_lifecycle_consistency(input_data))
    combined.extend(analyze_event_stream(input_data))
    return combined
