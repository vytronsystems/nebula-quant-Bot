# NEBULA-QUANT v1 | nq_obs — observability integration engine

from __future__ import annotations

from typing import Any

from nq_metrics.models import SystemObservabilityReport
from nq_metrics.observability import generate_observability_report
from nq_obs.adapters import (
    build_strategy_seeds_from_registry,
    normalize_execution_outcomes,
    normalize_experiment_summary,
    normalize_guardrail_decisions,
    normalize_portfolio_decisions,
    normalize_promotion_decisions,
)
from nq_obs.builders import build_observability_input
from nq_obs.models import SystemObservabilityBuilderInput


class ObservabilityEngine:
    """
    Thin integration layer: gathers module outputs, normalizes into observability-ready input,
    and bridges to nq_metrics reporting. Does not compute metrics or replace nq_metrics.
    """

    def gather(
        self,
        registry_engine: Any = None,
        strategy_ids: list[str] | None = None,
        execution_events: Any = None,
        guardrail_results: Any = None,
        portfolio_decisions: Any = None,
        promotion_decisions: Any = None,
        experiment_result: Any = None,
    ) -> SystemObservabilityBuilderInput:
        """
        Gather and normalize module outputs into a single builder input.
        Registry truth is used for strategy seeds when registry_engine and strategy_ids are provided.
        Missing or malformed data is omitted; no fabrication.
        """
        strategy_seeds, _ = build_strategy_seeds_from_registry(registry_engine, strategy_ids or [])

        (
            exec_attempted,
            exec_approved,
            exec_blocked,
            exec_throttled,
            exec_reject,
            exec_fill,
            avg_req,
            avg_eff,
            avg_slip,
        ) = normalize_execution_outcomes(execution_events)
        guard_allow, guard_block = normalize_guardrail_decisions(guardrail_results)
        port_allow, port_block, port_throttle = normalize_portfolio_decisions(portfolio_decisions)
        prom_allow, prom_reject, invalid_lifecycle = normalize_promotion_decisions(promotion_decisions)
        experiment_summary = normalize_experiment_summary(experiment_result)

        return SystemObservabilityBuilderInput(
            strategy_seeds=strategy_seeds,
            execution_attempted=exec_attempted,
            execution_approved=exec_approved,
            execution_blocked=exec_blocked,
            execution_throttled=exec_throttled,
            execution_reject_count=exec_reject,
            execution_fill_count=exec_fill,
            avg_requested_notional=avg_req,
            avg_effective_notional=avg_eff,
            avg_slippage=avg_slip,
            guardrail_allow_count=guard_allow,
            guardrail_block_count=guard_block,
            portfolio_allow_count=port_allow,
            portfolio_block_count=port_block,
            portfolio_throttle_count=port_throttle,
            promotion_allow_count=prom_allow,
            promotion_reject_count=prom_reject,
            invalid_lifecycle_count=invalid_lifecycle,
            experiment_summary=experiment_summary,
            metadata={"source": "nq_obs"},
        )

    def build_observability_input(self, builder_input: SystemObservabilityBuilderInput | None) -> Any:
        """Build nq_metrics ObservabilityInput from normalized builder input."""
        return build_observability_input(builder_input)

    def generate_report(
        self,
        registry_engine: Any = None,
        strategy_ids: list[str] | None = None,
        execution_events: Any = None,
        guardrail_results: Any = None,
        portfolio_decisions: Any = None,
        promotion_decisions: Any = None,
        experiment_result: Any = None,
        generated_key: str = "",
    ) -> SystemObservabilityReport:
        """
        Gather, normalize, build ObservabilityInput, and call nq_metrics.generate_observability_report.
        Returns SystemObservabilityReport. nq_metrics remains the reporting engine.
        """
        builder_input = self.gather(
            registry_engine=registry_engine,
            strategy_ids=strategy_ids,
            execution_events=execution_events,
            guardrail_results=guardrail_results,
            portfolio_decisions=portfolio_decisions,
            promotion_decisions=promotion_decisions,
            experiment_result=experiment_result,
        )
        observability_input = build_observability_input(builder_input)
        return generate_observability_report(observability_input, generated_key)
