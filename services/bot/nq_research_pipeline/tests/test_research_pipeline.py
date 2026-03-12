from __future__ import annotations

import math
import unittest
from typing import Any

from nq_research_pipeline import ResearchPipelineEngine, ResearchCycleReport


def _fixed_clock() -> float:
    return 1234567890.0


def _build_bars(n: int) -> list[dict[str, Any]]:
    bars: list[dict[str, Any]] = []
    for i in range(n):
        bars.append(
            {
                "ts": float(i + 1),
                "close": 100.0 + float(i),
                "symbol": "TEST",
                "timeframe": "1d",
            }
        )
    return bars


class TestResearchPipeline(unittest.TestCase):
    def test_full_research_cycle_execution(self) -> None:
        engine = ResearchPipelineEngine(clock=_fixed_clock)
        bars = _build_bars(5)

        report = engine.run_research_cycle(bars, regime_context=None)

        self.assertIsInstance(report, ResearchCycleReport)
        self.assertIsInstance(report.cycle_id, str)
        self.assertGreaterEqual(report.candidate_count, 0)
        self.assertGreaterEqual(report.experiment_count, 0)
        self.assertIsInstance(report.approved_strategies, list)
        self.assertIsInstance(report.rejected_strategies, list)
        self.assertIsInstance(report.summary, dict)

    def test_deterministic_results_for_same_inputs(self) -> None:
        engine = ResearchPipelineEngine(clock=_fixed_clock)
        bars = _build_bars(5)

        report1 = engine.run_research_cycle(bars, regime_context=None)
        report2 = engine.run_research_cycle(bars, regime_context=None)

        self.assertEqual(report1.cycle_id, report2.cycle_id)
        self.assertEqual(report1.candidate_count, report2.candidate_count)
        self.assertEqual(report1.experiment_count, report2.experiment_count)
        self.assertEqual(report1.approved_strategies, report2.approved_strategies)
        self.assertEqual(report1.rejected_strategies, report2.rejected_strategies)
        self.assertEqual(report1.summary, report2.summary)

    def test_empty_market_data_produces_empty_candidates(self) -> None:
        engine = ResearchPipelineEngine(clock=_fixed_clock)

        report = engine.run_research_cycle([], regime_context=None)

        self.assertEqual(report.candidate_count, 0)
        self.assertEqual(report.experiment_count, 0)
        self.assertEqual(report.approved_strategies, [])
        self.assertEqual(report.rejected_strategies, [])
        self.assertEqual(
            report.summary.get("candidate_count"),
            0,
        )

    def test_promotion_rejects_failing_strategies(self) -> None:
        engine = ResearchPipelineEngine(clock=_fixed_clock)
        # Very small number of bars → promotion thresholds should fail.
        bars = _build_bars(2)

        report = engine.run_research_cycle(bars, regime_context=None)

        # All discovered candidates should be rejected under conservative defaults.
        self.assertEqual(len(report.approved_strategies), 0)
        self.assertEqual(
            len(report.rejected_strategies),
            report.candidate_count,
        )
        # Sanity: non-negative candidate_count.
        self.assertGreaterEqual(report.candidate_count, 0)
        # generated_at should come from the fixed clock.
        self.assertTrue(math.isclose(report.generated_at, _fixed_clock()))


if __name__ == "__main__":
    unittest.main()

