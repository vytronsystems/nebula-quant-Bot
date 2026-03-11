# NEBULA-QUANT v1 | nq_obs — integration layer tests

from __future__ import annotations

import unittest
from typing import Any

from nq_strategy_registry.engine import StrategyRegistryEngine
from nq_obs.adapters import (
    build_strategy_seeds_from_registry,
    normalize_execution_outcomes,
    normalize_experiment_summary,
    normalize_guardrail_decisions,
    normalize_portfolio_decisions,
    normalize_promotion_decisions,
)
from nq_obs.builders import build_observability_input, seed_to_health_input
from nq_obs.engine import ObservabilityEngine
from nq_obs.models import StrategyObservabilitySeed, SystemObservabilityBuilderInput


class TestNqObs(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ObservabilityEngine()
        self.registry = StrategyRegistryEngine()

    # 1. registry truth overrides caller lifecycle when available
    def test_registry_truth_overrides_caller_lifecycle(self) -> None:
        self.registry.register_strategy("s1", "S1", status="paper")
        seeds, codes = build_strategy_seeds_from_registry(self.registry, ["s1"])
        self.assertEqual(len(seeds), 1)
        self.assertEqual(seeds[0].lifecycle_state, "paper")
        self.assertTrue(seeds[0].enabled)

    # 2. malformed registry data fails closed
    def test_malformed_registry_fails_closed(self) -> None:
        seeds, codes = build_strategy_seeds_from_registry(self.registry, ["nonexistent"])
        self.assertEqual(len(seeds), 0)
        self.assertGreater(len(codes), 0)

    # 3. duplicate / ambiguous registry state
    def test_duplicate_strategy_id_fails_closed(self) -> None:
        self.registry.register_strategy("dup", "D", status="live")
        seeds, codes = build_strategy_seeds_from_registry(self.registry, ["dup", "dup"])
        self.assertEqual(len(seeds), 1)
        self.assertIn("duplicate_strategy_id", codes)

    # 4. execution outcomes normalize correctly
    def test_execution_outcomes_normalize(self) -> None:
        class FakeResult:
            def __init__(self, status: str, fills: list, order: Any = None):
                self.status = status
                self.fills = fills
                self.order = order
        events = [
            FakeResult("filled", [1], type("Order", (), {"qty": 10.0, "limit_price": 100.0})()),
            FakeResult("rejected", []),
        ]
        a, app, b, t, rej, f, avg_req, _, _ = normalize_execution_outcomes(events)
        self.assertEqual(a, 2)
        self.assertEqual(app, 1)
        self.assertEqual(rej, 1)
        self.assertEqual(f, 1)

    # 5. guardrail decisions normalize correctly
    def test_guardrail_normalize(self) -> None:
        class FGR:
            allowed = False
            signals = []
        allow, block = normalize_guardrail_decisions([FGR(), FGR()])
        self.assertEqual(block, 2)

    # 6. portfolio decisions normalize correctly
    def test_portfolio_decisions_normalize(self) -> None:
        from nq_portfolio.models import PortfolioDecision, PortfolioDecisionType
        decisions = [
            PortfolioDecision(PortfolioDecisionType.ALLOW, [], "ok", None),
            PortfolioDecision(PortfolioDecisionType.BLOCK, [], "no", None),
            PortfolioDecision(PortfolioDecisionType.THROTTLE, [], "throttle", 0.5),
        ]
        a, b, t = normalize_portfolio_decisions(decisions)
        self.assertEqual(a, 1)
        self.assertEqual(b, 1)
        self.assertEqual(t, 1)

    # 7. promotion decisions normalize correctly
    def test_promotion_decisions_normalize(self) -> None:
        from nq_promotion.models import PromotionTransitionDecision
        decisions = [
            PromotionTransitionDecision(allowed=True, reason_codes=[], message="ok"),
            PromotionTransitionDecision(allowed=False, reason_codes=["lifecycle_not_executable"], message="no"),
        ]
        allow, reject, invalid = normalize_promotion_decisions(decisions)
        self.assertEqual(allow, 1)
        self.assertEqual(reject, 1)
        self.assertGreaterEqual(invalid, 1)

    # 8. experiment inputs normalize deterministically
    def test_experiment_normalize(self) -> None:
        summary = normalize_experiment_summary({"runs": 5, "success": 3})
        self.assertEqual(summary.get("runs"), 5)
        self.assertEqual(summary.get("success"), 3)
        empty = normalize_experiment_summary(None)
        self.assertEqual(empty, {})

    # 9. missing optional sources produce empty outputs
    def test_missing_optional_empty_not_fabricated(self) -> None:
        builder = self.engine.gather(registry_engine=None, strategy_ids=[])
        self.assertEqual(len(builder.strategy_seeds), 0)
        self.assertEqual(builder.execution_attempted, 0)
        self.assertEqual(builder.guardrail_block_count, 0)
        obs_in = build_observability_input(builder)
        self.assertEqual(obs_in.execution_attempted, 0)
        self.assertIsNone(obs_in.avg_slippage)

    # 10. builder produces nq_metrics-compatible input
    def test_builder_produces_compatible_input(self) -> None:
        builder = SystemObservabilityBuilderInput(
            strategy_seeds=[StrategyObservabilitySeed(strategy_id="x", lifecycle_state="paper")],
            execution_attempted=2,
            portfolio_block_count=1,
        )
        obs_in = build_observability_input(builder)
        self.assertEqual(len(obs_in.strategy_health_inputs), 1)
        self.assertEqual(obs_in.strategy_health_inputs[0].strategy_id, "x")
        self.assertEqual(obs_in.strategy_health_inputs[0].lifecycle_state, "paper")
        self.assertEqual(obs_in.execution_attempted, 2)
        self.assertEqual(obs_in.portfolio_block_count, 1)

    # 11. report generation bridge returns SystemObservabilityReport
    def test_report_bridge_returns_report(self) -> None:
        self.registry.register_strategy("r1", "R1", status="live")
        report = self.engine.generate_report(
            registry_engine=self.registry,
            strategy_ids=["r1"],
            generated_key="test",
        )
        self.assertIsNotNone(report)
        self.assertEqual(report.generated_key, "test")
        self.assertEqual(len(report.strategies), 1)
        self.assertEqual(report.strategies[0].strategy_id, "r1")
        self.assertEqual(report.strategies[0].lifecycle_state, "live")

    # 12. repeated same input same result
    def test_repeated_input_deterministic(self) -> None:
        builder1 = self.engine.gather(registry_engine=self.registry, strategy_ids=[])
        builder2 = self.engine.gather(registry_engine=self.registry, strategy_ids=[])
        self.assertEqual(builder1.execution_attempted, builder2.execution_attempted)
        self.assertEqual(len(builder1.strategy_seeds), len(builder2.strategy_seeds))
        o1 = build_observability_input(builder1)
        o2 = build_observability_input(builder2)
        self.assertEqual(o1.execution_attempted, o2.execution_attempted)

    # 13. seed_to_health_input
    def test_seed_to_health_input(self) -> None:
        seed = StrategyObservabilitySeed(strategy_id="h", lifecycle_state="paper", executions_approved=3)
        health = seed_to_health_input(seed)
        self.assertEqual(health.strategy_id, "h")
        self.assertEqual(health.lifecycle_state, "paper")
        self.assertEqual(health.executions_approved, 3)

    # 14. nq_metrics regression: can still generate report from ObservabilityInput
    def test_nq_metrics_still_works(self) -> None:
        from nq_metrics.observability import generate_observability_report
        from nq_metrics.models import ObservabilityInput
        inp = ObservabilityInput(execution_attempted=1, portfolio_allow_count=1)
        report = generate_observability_report(inp, "direct")
        self.assertEqual(report.execution_quality.attempted_orders, 1)
        self.assertEqual(report.controls.portfolio_allow_count, 1)
