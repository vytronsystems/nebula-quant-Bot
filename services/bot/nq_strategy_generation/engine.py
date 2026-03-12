from __future__ import annotations

from collections.abc import Callable
import hashlib
from typing import Any

from nq_strategy_generation.generator import generate_candidates_for_templates
from nq_strategy_generation.models import (
    StrategyCandidate,
    StrategyGenerationError,
    StrategyGenerationReport,
    StrategyGenerationSummary,
    StrategyParameterSet,
    StrategyTemplate,
)
from nq_strategy_generation.parameter_expansion import expand_parameters_for_template
from nq_strategy_generation.templates import build_all_templates


class StrategyGenerationEngine:
    """
    Deterministic strategy generation orchestrator.

    Transforms structured feature observations, regime context, and internal
    learning feedback into StrategyTemplate, StrategyParameterSet, and
    StrategyCandidate outputs bundled in a StrategyGenerationReport.
    """

    def __init__(self, clock: Callable[[], float] | None = None, max_candidates: int | None = None) -> None:
        import time

        self._clock = clock or time.time
        self._max_candidates = max_candidates

    def _now(self) -> float:
        return float(self._clock())

    def _build_report_id(
        self,
        market_observations: dict[str, Any] | None,
        regime_context: Any | None,
        learning_feedback: dict[str, Any] | None,
    ) -> str:
        """Deterministic hash-based report id derived from normalized inputs."""
        parts = [
            str(sorted((market_observations or {}).items())),
            str(regime_context),
            str(sorted((learning_feedback or {}).items())),
        ]
        base = "|".join(parts)
        digest = hashlib.sha256(base.encode("utf-8")).hexdigest()[:12]
        return f"strategy-generation-report-{digest}"

    def _validate_inputs(
        self,
        market_observations: Any,
        regime_context: Any,
        learning_feedback: Any,
    ) -> None:
        if market_observations is not None and not isinstance(market_observations, dict):
            raise StrategyGenerationError("market_observations must be a dict or None")
        # regime_context is intentionally free-form (e.g. Enum, str); no strict validation.
        if learning_feedback is not None and not isinstance(learning_feedback, dict):
            raise StrategyGenerationError("learning_feedback must be a dict or None")

    def generate_strategies(
        self,
        market_observations: dict[str, Any] | None,
        regime_context: Any | None = None,
        learning_feedback: dict[str, Any] | None = None,
        report_id: str | None = None,
        generated_at: float | None = None,
    ) -> StrategyGenerationReport:
        """
        Main entry point for deterministic strategy generation.

        Returns a StrategyGenerationReport; empty inputs yield a valid empty
        report with no candidates.
        """
        self._validate_inputs(market_observations, regime_context, learning_feedback)

        templates: list[StrategyTemplate] = build_all_templates()
        parameter_sets: list[StrategyParameterSet] = []
        for tpl in templates:
            expanded = expand_parameters_for_template(tpl)
            parameter_sets.extend(expanded)

        candidates: list[StrategyCandidate] = generate_candidates_for_templates(
            templates=templates,
            parameter_sets=parameter_sets,
            market_observations=market_observations,
            regime_context=regime_context,
            learning_feedback=learning_feedback,
        )

        if self._max_candidates is not None:
            candidates = candidates[: max(0, int(self._max_candidates))]

        fams_seen = sorted({c.family for c in candidates})
        regimes_seen = sorted({c.regime for c in candidates if c.regime})
        summary = StrategyGenerationSummary(
            total_templates=len(templates),
            total_parameter_sets=len(parameter_sets),
            total_candidates=len(candidates),
            families_seen=fams_seen,
            regimes_seen=regimes_seen,
            metadata={},
        )

        rid = report_id or self._build_report_id(market_observations, regime_context, learning_feedback)
        now = generated_at if generated_at is not None else self._now()
        return StrategyGenerationReport(
            report_id=rid,
            generated_at=now,
            templates=templates,
            parameter_sets=parameter_sets,
            candidates=candidates,
            summary=summary,
            metadata={},
        )

