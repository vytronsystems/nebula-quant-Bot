from __future__ import annotations

import unittest
from typing import Any

from nq_strategy_adaptation import (
    AdaptationActionType,
    StrategyAdaptationEngine,
    StrategyAdaptationError,
)
from nq_strategy_generation import StrategyFamily, StrategyGenerationEngine


def _fixed_clock() -> float:
    return 3333333333.0


class TestStrategyAdaptation(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = StrategyAdaptationEngine(clock=_fixed_clock)

    def test_slippage_driven_family_suppression(self) -> None:
        trade_review = {
            "report_id": "tr-1",
            "findings": [
                {"category": "slippage_issue"},
                {"category": "poor_entry_quality"},
            ],
        }
        report = self.engine.generate_adaptation_report(trade_review_reports=[trade_review])
        actions = {(d.action_type, d.target_family) for d in report.directives}
        self.assertIn((AdaptationActionType.SUPPRESS_FAMILY.value, "breakout"), actions)
        self.assertIn((AdaptationActionType.SUPPRESS_FAMILY.value, "opening_range_breakout"), actions)

    def test_edge_decay_driven_family_suppression(self) -> None:
        edge_decay = {
            "report_id": "ed-1",
            "decayed_families": ["breakout"],
        }
        report = self.engine.generate_adaptation_report(edge_decay_report=edge_decay)
        actions = {(d.action_type, d.target_family) for d in report.directives}
        self.assertIn((AdaptationActionType.REDUCE_PRIORITY.value, "breakout"), actions)

    def test_successful_experiment_family_preference(self) -> None:
        experiment_report = {
            "report_id": "exp-1",
            "findings": [
                {"category": "positive_result", "strategy_id": "momentum_continuation"},
            ],
        }
        report = self.engine.generate_adaptation_report(experiment_report=experiment_report)
        actions = {(d.action_type, d.target_family) for d in report.directives}
        self.assertIn((AdaptationActionType.PREFER_FAMILY.value, "momentum_continuation"), actions)

    def test_regime_specialization_directives(self) -> None:
        audit_report = {
            "report_id": "audit-1",
            "findings": [
                {"strategy_family": "breakout", "regime": "HIGH_VOLATILITY", "outcome": "strong_positive"},
                {"strategy_family": "breakout", "regime": "LOW_VOLATILITY", "outcome": "fail_negative"},
            ],
        }
        report = self.engine.generate_adaptation_report(audit_report=audit_report)
        actions = {(d.action_type, d.target_family, d.target_regime) for d in report.directives}
        self.assertIn(
            (AdaptationActionType.REQUIRE_REGIME.value, "breakout", "HIGH_VOLATILITY"),
            actions,
        )
        self.assertIn(
            (AdaptationActionType.EXCLUDE_REGIME.value, "breakout", "LOW_VOLATILITY"),
            actions,
        )

    def test_parameter_adjustment_directives(self) -> None:
        trade_review = {
            "report_id": "tr-2",
            "findings": [
                {"category": "poor_entry_quality"},
                {"category": "poor_entry_quality"},
                {"category": "poor_entry_quality"},
            ],
        }
        report = self.engine.generate_adaptation_report(trade_review_reports=[trade_review])
        adjustments = [
            (d.target_family, d.target_parameter)
            for d in report.directives
            if d.action_type == AdaptationActionType.ADJUST_PARAMETER_RANGE.value
        ]
        self.assertIn(("breakout", "lookback_bars"), adjustments)

    def test_empty_input_returns_valid_empty_report(self) -> None:
        report = self.engine.generate_adaptation_report()
        self.assertEqual(report.summary.total_directives, 0)
        self.assertEqual(len(report.directives), 0)

    def test_malformed_critical_input_fails_closed(self) -> None:
        with self.assertRaises(StrategyAdaptationError):
            self.engine.generate_adaptation_report(trade_review_reports="not-a-list")  # type: ignore[arg-type]

    def test_same_input_yields_same_directives_and_report_id(self) -> None:
        audit_report = {
            "report_id": "audit-2",
            "findings": [
                {"strategy_family": "breakout", "regime": "HIGH_VOLATILITY", "outcome": "strong_positive"},
            ],
        }
        r1 = self.engine.generate_adaptation_report(audit_report=audit_report)
        r2 = self.engine.generate_adaptation_report(audit_report=audit_report)
        self.assertEqual(r1.report_id, r2.report_id)
        ids1 = [d.directive_id for d in r1.directives]
        ids2 = [d.directive_id for d in r2.directives]
        self.assertEqual(ids1, ids2)

    def test_deterministic_directive_ids(self) -> None:
        edge_decay = {
            "report_id": "ed-2",
            "decayed_families": ["breakout"],
        }
        report = self.engine.generate_adaptation_report(edge_decay_report=edge_decay)
        for d in report.directives:
            self.assertTrue(d.directive_id.startswith("dir-"))


class TestIntegrationWithStrategyGeneration(unittest.TestCase):
    def test_integration_backward_compatible_without_adaptation(self) -> None:
        """Existing StrategyGenerationEngine usage without adaptation_report must still work."""
        engine = StrategyGenerationEngine(clock=_fixed_clock)
        obs = {"breakout_signal": True, "relative_volume": 1.5}
        report = engine.generate_strategies(obs, regime_context="TRENDING_UP")
        self.assertGreaterEqual(report.summary.total_candidates, 0)

    def test_adaptation_report_changes_candidate_generation_deterministically(self) -> None:
        """Adaptation report must alter candidate families deterministically."""
        sg_engine = StrategyGenerationEngine(clock=_fixed_clock)
        obs = {"breakout_signal": True, "relative_volume": 2.0}

        # Baseline without adaptation: expect breakout candidates.
        base = sg_engine.generate_strategies(obs, regime_context="TRENDING_UP")
        base_families = {c.family for c in base.candidates}
        self.assertIn(StrategyFamily.BREAKOUT.value, base_families)

        # Build adaptation report that suppresses breakout.
        adaptation_engine = StrategyAdaptationEngine(clock=_fixed_clock)
        trade_review = {
            "report_id": "tr-3",
            "findings": [{"category": "slippage_issue"}],
        }
        adaptation_report = adaptation_engine.generate_adaptation_report(trade_review_reports=[trade_review])

        adapted = sg_engine.generate_strategies(
            obs,
            regime_context="TRENDING_UP",
            learning_feedback=None,
            report_id=None,
            generated_at=None,
            adaptation_report=adaptation_report,
        )
        adapted_families = {c.family for c in adapted.candidates}
        self.assertNotIn(StrategyFamily.BREAKOUT.value, adapted_families)

        # Determinism: repeated call with same adaptation_report yields same families.
        adapted2 = sg_engine.generate_strategies(
            obs,
            regime_context="TRENDING_UP",
            learning_feedback=None,
            report_id=None,
            generated_at=None,
            adaptation_report=adaptation_report,
        )
        self.assertEqual(
            sorted(c.family for c in adapted.candidates),
            sorted(c.family for c in adapted2.candidates),
        )


if __name__ == "__main__":
    unittest.main()

