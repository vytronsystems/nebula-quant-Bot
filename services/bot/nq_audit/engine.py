# NEBULA-QUANT v1 | nq_audit engine

from __future__ import annotations

from collections.abc import Callable

from nq_audit.analyzers import run_all_analyzers
from nq_audit.findings import recommendations_from_findings
from nq_audit.models import (
    AuditFindingSeverity,
    AuditInput,
    AuditReport,
    AuditSummary,
)


class AuditEngine:
    """
    Deterministic audit analysis engine.

    Consumes AuditInput (events, decision_records, execution_records, strategy_health, etc.),
    runs all analyzers, and produces an AuditReport with findings and recommendations.
    Uses injectable clock and counter-based or caller-supplied audit_id.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time
        self._clock = clock or time.monotonic
        self._audit_counter = 0

    def _now(self) -> float:
        return self._clock()

    def _next_audit_id(self) -> str:
        self._audit_counter += 1
        return f"audit-{self._audit_counter}"

    def run_audit(
        self,
        input_data: AuditInput,
        audit_id: str | None = None,
        generated_at: float | None = None,
    ) -> AuditReport:
        """
        Run full audit on input_data. Returns deterministic AuditReport.
        Fails closed on malformed critical input (raised by analyzers).
        """
        now = generated_at if generated_at is not None else self._now()
        if audit_id is not None:
            aid = audit_id
            self._audit_counter += 1
        else:
            aid = self._next_audit_id()

        findings = run_all_analyzers(input_data)

        info_c = sum(1 for f in findings if f.severity == AuditFindingSeverity.INFO.value)
        warn_c = sum(1 for f in findings if f.severity == AuditFindingSeverity.WARNING.value)
        crit_c = sum(1 for f in findings if f.severity == AuditFindingSeverity.CRITICAL.value)

        modules: set[str] = set()
        strategies: set[str] = set()
        for f in findings:
            if f.related_module:
                modules.add(f.related_module)
            if f.related_strategy_id:
                strategies.add(f.related_strategy_id)

        summary = AuditSummary(
            total_findings=len(findings),
            info_count=info_c,
            warning_count=warn_c,
            critical_count=crit_c,
            modules_reviewed=sorted(modules),
            strategies_reviewed=sorted(strategies),
            metadata={},
        )

        recommendations = recommendations_from_findings(findings)

        return AuditReport(
            audit_id=aid,
            generated_at=now,
            summary=summary,
            findings=findings,
            recommendations=recommendations,
            metadata={},
        )
