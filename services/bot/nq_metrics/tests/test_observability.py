# NEBULA-QUANT v1 | nq_metrics — observability layer tests

from __future__ import annotations

import unittest

from nq_metrics.models import (
    ObservabilityInput,
    StrategyHealthInput,
)
from nq_metrics.observability import (
    build_control_decision_snapshot,
    build_execution_quality_snapshot,
    build_experiment_summary,
    build_strategy_health_snapshots,
    classify_strategy_health,
    generate_observability_report,
)
from nq_metrics.engine import MetricsEngine


class TestObservability(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MetricsEngine()

    # 1. strategy health snapshot can be generated deterministically
    def test_strategy_health_snapshot_deterministic(self) -> None:
        inp = StrategyHealthInput(
            strategy_id="s1",
            lifecycle_state="paper",
            executions_attempted=10,
            executions_approved=8,
            executions_blocked=0,
            executions_throttled=2,
        )
        snapshots = build_strategy_health_snapshots([inp])
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0].strategy_id, "s1")
        self.assertEqual(snapshots[0].lifecycle_state, "paper")
        self.assertEqual(snapshots[0].executions_attempted, 10)
        self.assertIn(snapshots[0].status, ("healthy", "warning", "degraded", "inactive"))

    # 2. lifecycle state is pulled from input (registry truth supplied by caller)
    def test_lifecycle_state_from_input(self) -> None:
        inp = StrategyHealthInput(strategy_id="s2", lifecycle_state="live", enabled=True)
        snapshots = build_strategy_health_snapshots([inp])
        self.assertEqual(snapshots[0].lifecycle_state, "live")

    # 3. execution quality aggregation for mixed allow/block/throttle
    def test_execution_quality_aggregation(self) -> None:
        inp = ObservabilityInput(
            execution_attempted=100,
            execution_approved=70,
            execution_blocked=20,
            execution_throttled=10,
            execution_fill_count=68,
        )
        snap = build_execution_quality_snapshot(inp)
        self.assertEqual(snap.attempted_orders, 100)
        self.assertEqual(snap.approved_orders, 70)
        self.assertEqual(snap.blocked_orders, 20)
        self.assertEqual(snap.throttled_orders, 10)
        self.assertEqual(snap.fill_count, 68)

    # 4. control metrics aggregate guardrail / portfolio / promotion
    def test_control_metrics_aggregation(self) -> None:
        inp = ObservabilityInput(
            guardrail_allow_count=50,
            guardrail_block_count=5,
            portfolio_allow_count=45,
            portfolio_block_count=3,
            portfolio_throttle_count=2,
            promotion_allow_count=1,
            promotion_reject_count=1,
        )
        snap = build_control_decision_snapshot(inp)
        self.assertEqual(snap.guardrail_allow_count, 50)
        self.assertEqual(snap.guardrail_block_count, 5)
        self.assertEqual(snap.portfolio_allow_count, 45)
        self.assertEqual(snap.portfolio_block_count, 3)
        self.assertEqual(snap.portfolio_throttle_count, 2)
        self.assertEqual(snap.promotion_reject_count, 1)

    # 5. malformed input does not fabricate values
    def test_malformed_input_no_fabrication(self) -> None:
        snapshots = build_strategy_health_snapshots([None, "not_a_StrategyHealthInput"])
        self.assertEqual(len(snapshots), 0)
        snapshots2 = build_strategy_health_snapshots([StrategyHealthInput(strategy_id="")])
        self.assertEqual(len(snapshots2), 0)
        rep = generate_observability_report(None)
        self.assertEqual(len(rep.strategies), 0)
        self.assertIn("omission", rep.execution_quality.metadata)

    # 6. missing optional fields produce deterministic omissions
    def test_missing_optional_fields_deterministic_omissions(self) -> None:
        inp = ObservabilityInput()
        rep = generate_observability_report(inp)
        self.assertEqual(rep.execution_quality.attempted_orders, 0)
        self.assertIsNone(rep.execution_quality.avg_slippage)
        self.assertEqual(rep.controls.guardrail_block_count, 0)
        self.assertEqual(rep.totals.get("total_strategies_observed", -1), 0)

    # 7. repeated same input returns same output
    def test_repeated_input_same_output(self) -> None:
        inp = ObservabilityInput(
            strategy_health_inputs=[
                StrategyHealthInput(strategy_id="r1", lifecycle_state="paper", executions_approved=5),
            ],
            execution_attempted=10,
            guardrail_block_count=1,
        )
        r1 = generate_observability_report(inp, "k1")
        r2 = generate_observability_report(inp, "k1")
        self.assertEqual(r1.generated_key, r2.generated_key)
        self.assertEqual(len(r1.strategies), len(r2.strategies))
        self.assertEqual(r1.execution_quality.attempted_orders, r2.execution_quality.attempted_orders)
        self.assertEqual(r1.controls.guardrail_block_count, r2.controls.guardrail_block_count)

    # 8. inactive / healthy / warning / degraded classifications deterministic
    def test_health_classification_inactive(self) -> None:
        self.assertEqual(classify_strategy_health(StrategyHealthInput(strategy_id="x", lifecycle_state="retired")), "inactive")
        self.assertEqual(classify_strategy_health(StrategyHealthInput(strategy_id="x", enabled=False)), "inactive")

    def test_health_classification_healthy(self) -> None:
        inp = StrategyHealthInput(
            strategy_id="h1",
            lifecycle_state="paper",
            enabled=True,
            executions_attempted=10,
            executions_approved=9,
            executions_blocked=0,
            executions_throttled=1,
        )
        self.assertEqual(classify_strategy_health(inp), "healthy")

    def test_health_classification_degraded(self) -> None:
        inp = StrategyHealthInput(
            strategy_id="d1",
            lifecycle_state="paper",
            executions_attempted=10,
            executions_approved=0,
            executions_blocked=5,
        )
        self.assertEqual(classify_strategy_health(inp), "degraded")

    def test_health_classification_warning(self) -> None:
        inp = StrategyHealthInput(
            strategy_id="w1",
            lifecycle_state="paper",
            executions_attempted=6,
            executions_approved=4,
            executions_blocked=1,
            executions_throttled=1,
            drawdown_pct=0.05,
        )
        self.assertEqual(classify_strategy_health(inp), "warning")

    # 9. experiment summary aggregates from supplied source only
    def test_experiment_summary_from_input(self) -> None:
        inp = ObservabilityInput(experiment_summary_source={"runs": 10, "success": 8})
        rep = generate_observability_report(inp)
        self.assertEqual(rep.experiment_summary.get("runs"), 10)
        self.assertEqual(rep.experiment_summary.get("success"), 8)

    # 10. system report generation with valid mixed inputs
    def test_system_report_valid_mixed_inputs(self) -> None:
        inp = ObservabilityInput(
            strategy_health_inputs=[
                StrategyHealthInput(strategy_id="a", lifecycle_state="paper"),
                StrategyHealthInput(strategy_id="b", lifecycle_state="live"),
            ],
            execution_attempted=20,
            execution_approved=15,
            execution_blocked=3,
            execution_throttled=2,
            guardrail_allow_count=18,
            guardrail_block_count=2,
            portfolio_allow_count=15,
            portfolio_block_count=3,
            portfolio_throttle_count=2,
            promotion_reject_count=0,
        )
        rep = generate_observability_report(inp, "mixed")
        self.assertEqual(len(rep.strategies), 2)
        self.assertEqual(rep.execution_quality.attempted_orders, 20)
        self.assertEqual(rep.controls.guardrail_block_count, 2)
        self.assertEqual(rep.totals["total_executable"], 2)
        self.assertEqual(rep.totals["total_paper"], 1)
        self.assertEqual(rep.totals["total_live"], 1)
        self.assertEqual(rep.generated_key, "mixed")

    # 11. backward compatibility: MetricsEngine.compute_metrics unchanged
    def test_backward_compat_compute_metrics(self) -> None:
        from nq_metrics.models import TradePerformance
        result = self.engine.compute_metrics(trades=[], initial_equity=1000.0)
        self.assertEqual(result.total_trades, 0)
        self.assertEqual(result.win_rate, 0.0)
        self.assertIn("empty", result.metadata)

    # 12. engine.generate_observability_report
    def test_engine_generate_observability_report(self) -> None:
        inp = ObservabilityInput(execution_attempted=5, portfolio_block_count=1)
        rep = self.engine.generate_observability_report(inp, "eng")
        self.assertEqual(rep.execution_quality.attempted_orders, 5)
        self.assertEqual(rep.controls.portfolio_block_count, 1)
        self.assertEqual(rep.generated_key, "eng")
