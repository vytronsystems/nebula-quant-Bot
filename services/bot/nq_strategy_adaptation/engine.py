from __future__ import annotations

from collections.abc import Callable
import hashlib
from typing import Any

from nq_strategy_adaptation.adapters import (
    adapt_audit,
    adapt_edge_decay,
    adapt_experiments,
    adapt_improvement_plan,
    adapt_learning,
    adapt_trade_review,
)
from nq_strategy_adaptation.models import (
    AdaptationDirective,
    StrategyAdaptationError,
    StrategyAdaptationReport,
    StrategyAdaptationSummary,
)
from nq_strategy_adaptation.rules import apply_adaptation_rules


class StrategyAdaptationEngine:
    """
    Deterministic adaptive improvement engine for strategy generation.

    Converts learning, review, audit, edge-decay, and experiment feedback into
    structured AdaptationDirective instances that can be consumed by
    nq_strategy_generation and nq_research_pipeline.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time

        self._clock = clock or time.time

    def _now(self) -> float:
        return float(self._clock())

    def _build_report_id(self, normalized: dict[str, Any]) -> str:
        """Deterministic hash-based report id from normalized feedback."""
        # Sort top-level keys and nested items for stability.
        pieces: list[str] = []
        for key in sorted(normalized.keys()):
            pieces.append(key)
            pieces.append(str(normalized[key]))
        base = "|".join(pieces)
        digest = hashlib.sha256(base.encode("utf-8")).hexdigest()[:12]
        return f"strategy-adaptation-report-{digest}"

    def _validate_inputs(
        self,
        learning_report: Any,
        improvement_plan: Any,
        edge_decay_report: Any,
        trade_review_reports: Any,
        audit_report: Any,
        experiment_report: Any,
    ) -> None:
        # Inputs are duck-typed; only enforce that trade_review_reports, when list-like,
        # are not of an unsupported scalar type.
        if isinstance(trade_review_reports, (int, float, str)):
            raise StrategyAdaptationError("trade_review_reports must be a report or list, not a scalar")

    def generate_adaptation_report(
        self,
        learning_report: Any | None = None,
        improvement_plan: Any | None = None,
        edge_decay_report: Any | None = None,
        trade_review_reports: Any | None = None,
        audit_report: Any | None = None,
        experiment_report: Any | None = None,
        report_id: str | None = None,
        generated_at: float | None = None,
    ) -> StrategyAdaptationReport:
        """
        Build a StrategyAdaptationReport from structured internal feedback.

        Empty inputs yield a valid empty report with no directives.
        """
        self._validate_inputs(
            learning_report,
            improvement_plan,
            edge_decay_report,
            trade_review_reports,
            audit_report,
            experiment_report,
        )

        normalized = {
            "learning": adapt_learning(learning_report),
            "improvement_plan": adapt_improvement_plan(improvement_plan),
            "edge_decay": adapt_edge_decay(edge_decay_report),
            "trade_review": adapt_trade_review(trade_review_reports),
            "audit": adapt_audit(audit_report),
            "experiments": adapt_experiments(experiment_report),
        }

        directives: list[AdaptationDirective] = apply_adaptation_rules(normalized)

        suppressed_families = sorted(
            {
                d.target_family
                for d in directives
                if d.action_type in (AdaptationActionType.SUPPRESS_FAMILY.value, AdaptationActionType.REDUCE_PRIORITY.value)
                and d.target_family
            }
        )
        preferred_families = sorted(
            {
                d.target_family
                for d in directives
                if d.action_type in (AdaptationActionType.PREFER_FAMILY.value, AdaptationActionType.INCREASE_PRIORITY.value)
                and d.target_family
            }
        )
        excluded_regimes = sorted(
            {
                d.target_regime
                for d in directives
                if d.action_type == AdaptationActionType.EXCLUDE_REGIME.value and d.target_regime
            }
        )
        parameter_adjustments = [
            {
                "family": d.target_family,
                "parameter": d.target_parameter,
                "value": d.value,
            }
            for d in directives
            if d.action_type == AdaptationActionType.ADJUST_PARAMETER_RANGE.value
        ]

        summary = StrategyAdaptationSummary(
            total_directives=len(directives),
            suppressed_families=suppressed_families,
            preferred_families=preferred_families,
            excluded_regimes=excluded_regimes,
            parameter_adjustments=parameter_adjustments,
            metadata={},
        )

        rid = report_id or self._build_report_id(normalized)
        now = generated_at if generated_at is not None else self._now()
        return StrategyAdaptationReport(
            report_id=rid,
            generated_at=now,
            directives=directives,
            summary=summary,
            metadata={},
        )


from nq_strategy_adaptation.models import AdaptationActionType  # noqa: E402  (circular type reference for summary)

