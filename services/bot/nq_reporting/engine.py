# NEBULA-QUANT v1 | nq_reporting engine

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nq_reporting.builders import (
    build_audit_summary,
    build_learning_summary,
    build_observability_summary,
    build_trade_review_summary,
)
from nq_reporting.models import (
    AuditSummaryReport,
    LearningSummaryReport,
    ObservabilitySummaryReport,
    ReportType,
    SystemReport,
    TradeReviewSummaryReport,
)


class ReportEngine:
    """
    Deterministic report engine. Assembles SystemReport from optional audit,
    trade review, learning, and observability inputs. Uses injectable clock
    and counter-based or caller-supplied report_id.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time
        self._clock = clock or time.monotonic
        self._report_counter = 0

    def _now(self) -> float:
        return self._clock()

    def _next_report_id(self) -> str:
        self._report_counter += 1
        return f"system-report-{self._report_counter}"

    def generate_system_report(
        self,
        audit_report: Any = None,
        trade_review_reports: Any = None,
        learning_report: Any = None,
        observability_report: Any = None,
        report_id: str | None = None,
        generated_at: float | None = None,
    ) -> SystemReport:
        """
        Build SystemReport from optional subreports. Deterministic ordering:
        audit, trade_review, learning, observability. Missing sections yield None.
        """
        now = generated_at if generated_at is not None else self._now()
        if report_id is not None:
            rid = report_id
            self._report_counter += 1
        else:
            rid = self._next_report_id()

        audit_sum: AuditSummaryReport | None = None
        if audit_report is not None:
            audit_sum = build_audit_summary(audit_report)

        trade_sum: TradeReviewSummaryReport | None = build_trade_review_summary(trade_review_reports)
        if trade_sum.total_trades_reviewed == 0 and trade_review_reports is None:
            trade_sum = None

        learning_sum: LearningSummaryReport | None = None
        if learning_report is not None:
            learning_sum = build_learning_summary(learning_report)

        obs_sum: ObservabilitySummaryReport | None = build_observability_summary(observability_report)
        if (
            observability_report is None
            and obs_sum.system_health_score is None
            and not obs_sum.degraded_strategies
            and not obs_sum.inactive_strategies
            and not obs_sum.event_anomalies
            and obs_sum.metrics_summary is None
        ):
            obs_sum = None

        return SystemReport(
            report_id=rid,
            generated_at=now,
            audit_report=audit_sum,
            trade_review_report=trade_sum,
            learning_report=learning_sum,
            observability_report=obs_sum,
            metadata={"report_type": ReportType.SYSTEM.value},
        )
