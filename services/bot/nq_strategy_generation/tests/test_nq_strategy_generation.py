from __future__ import annotations

import unittest
from typing import Any

from nq_research_pipeline import ResearchPipelineEngine
from nq_strategy_generation import (
    StrategyCandidate,
    StrategyFamily,
    StrategyGenerationEngine,
    StrategyGenerationError,
    StrategyGenerationReport,
)


def _fixed_clock() -> float:
    return 1111111111.0


class TestStrategyGeneration(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = StrategyGenerationEngine(clock=_fixed_clock)

    def test_breakout_candidate_generation(self) -> None:
        report = self.engine.generate_strategies(
            market_observations={
                "breakout_signal": True,
                "relative_volume": 1.5,
            },
            regime_context="TRENDING_UP",
        )
        families = {c.family for c in report.candidates}
        self.assertIn(StrategyFamily.BREAKOUT.value, families)

    def test_momentum_continuation_generation(self) -> None:
        report = self.engine.generate_strategies(
            market_observations={
                "trend_strength": 0.8,
                "momentum_score": 0.8,
            },
            regime_context="TRENDING_UP",
        )
        families = {c.family for c in report.candidates}
        self.assertIn(StrategyFamily.MOMENTUM_CONTINUATION.value, families)

    def test_mean_reversion_generation(self) -> None:
        report = self.engine.generate_strategies(
            market_observations={
                "mean_reversion_distance": 2.0,
                "volatility_percentile": 0.5,
            },
            regime_context="RANGE_BOUND",
        )
        families = {c.family for c in report.candidates}
        self.assertIn(StrategyFamily.MEAN_REVERSION.value, families)

    def test_regime_constraints_respected(self) -> None:
        # TRENDING_UP should not generate pure mean-reversion-only candidates without range-bound context.
        report = self.engine.generate_strategies(
            market_observations={
                "mean_reversion_distance": 2.0,
                "volatility_percentile": 0.5,
            },
            regime_context="TRENDING_UP",
        )
        families = {c.family for c in report.candidates}
        self.assertNotIn(StrategyFamily.MEAN_REVERSION.value, families)

    def test_parameter_expansion_deterministic(self) -> None:
        obs = {
            "breakout_signal": True,
            "relative_volume": 1.5,
        }
        r1 = self.engine.generate_strategies(obs, regime_context="TRENDING_UP")
        r2 = self.engine.generate_strategies(obs, regime_context="TRENDING_UP")
        ids1 = [c.candidate_id for c in r1.candidates]
        ids2 = [c.candidate_id for c in r2.candidates]
        self.assertEqual(ids1, ids2)

    def test_empty_input_returns_valid_empty_report(self) -> None:
        report = self.engine.generate_strategies(
            market_observations=None,
            regime_context=None,
            learning_feedback=None,
        )
        self.assertIsInstance(report, StrategyGenerationReport)
        self.assertEqual(report.summary.total_candidates, 0)
        self.assertEqual(len(report.candidates), 0)

    def test_malformed_critical_input_fails_closed(self) -> None:
        with self.assertRaises(StrategyGenerationError):
            self.engine.generate_strategies(
                market_observations=["not a dict"],  # type: ignore[arg-type]
                regime_context=None,
                learning_feedback=None,
            )

    def test_same_input_yields_same_candidate_set_and_report_id(self) -> None:
        obs = {
            "breakout_signal": True,
            "relative_volume": 1.5,
        }
        r1 = self.engine.generate_strategies(obs, regime_context="TRENDING_UP")
        r2 = self.engine.generate_strategies(obs, regime_context="TRENDING_UP")
        self.assertEqual(r1.report_id, r2.report_id)
        ids1 = [c.candidate_id for c in r1.candidates]
        ids2 = [c.candidate_id for c in r2.candidates]
        self.assertEqual(ids1, ids2)

    def test_deterministic_candidate_ids(self) -> None:
        obs = {
            "breakout_signal": True,
            "relative_volume": 1.5,
        }
        report = self.engine.generate_strategies(obs, regime_context="TRENDING_UP")
        for c in report.candidates:
            self.assertTrue(c.candidate_id.startswith("cand-"))
            self.assertIsInstance(c.strategy_id, str)

    def test_bounded_candidate_count_respected(self) -> None:
        limited_engine = StrategyGenerationEngine(clock=_fixed_clock, max_candidates=3)
        obs = {
            "breakout_signal": True,
            "relative_volume": 2.0,
            "trend_strength": 0.9,
            "momentum_score": 0.9,
        }
        report = limited_engine.generate_strategies(obs, regime_context="TRENDING_UP")
        self.assertLessEqual(len(report.candidates), 3)


class TestIntegrationWithResearchPipeline(unittest.TestCase):
    def test_research_pipeline_integration_path_preserved(self) -> None:
        """
        Ensure that the existing ResearchPipelineEngine path still works and
        that enabling strategy generation remains deterministic when used.
        """

        def _fixed_clock_rp() -> float:
            return 2222222222.0

        engine = ResearchPipelineEngine(clock=_fixed_clock_rp)

        # Basic pipeline call (without strategy generation) must still work.
        bars = [
            {"ts": 1.0, "close": 100.0},
            {"ts": 2.0, "close": 101.0},
        ]
        report1 = engine.run_research_cycle(bars, regime_context=None)
        report2 = engine.run_research_cycle(bars, regime_context=None)
        self.assertEqual(report1.cycle_id, report2.cycle_id)
        self.assertEqual(report1.candidate_count, report2.candidate_count)
        self.assertEqual(report1.experiment_count, report2.experiment_count)


if __name__ == "__main__":
    unittest.main()

