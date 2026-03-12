from __future__ import annotations

import unittest

from nq_research_pipeline import ResearchPipelineEngine
from nq_strategy_governance import (
    StrategyGovernanceDecision,
    StrategyGovernanceEngine,
    StrategyGovernanceError,
    StrategyGovernanceInput,
)


def _fixed_clock() -> float:
    return 4444444444.0


class TestStrategyGovernance(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = StrategyGovernanceEngine(clock=_fixed_clock)

    def _base_input(self) -> StrategyGovernanceInput:
        return StrategyGovernanceInput(
            strategy_id="strategy_1",
            backtest_summary={"profit_factor": 1.5, "win_rate": 0.6, "max_drawdown": 0.2},
            walkforward_summary={"pass_rate": 0.7},
            paper_summary={"total_trades": 40, "win_rate": 0.6, "max_drawdown": 0.15},
            metrics_summary={"win_rate": 0.6, "expectancy": 0.01, "max_drawdown": 0.15},
            edge_decay_summary={"significant": False},
            audit_summary={"blocking_issues": [], "structural_invalid": False},
        )

    def test_strategy_approved_for_live(self) -> None:
        gi = self._base_input()
        report = self.engine.evaluate_strategy_readiness(gi)
        self.assertEqual(report.decision, StrategyGovernanceDecision.APPROVED_FOR_LIVE)

    def test_strategy_remains_in_paper(self) -> None:
        gi = self._base_input()
        gi.paper_summary = {"total_trades": 10, "win_rate": 0.55, "max_drawdown": 0.15}
        report = self.engine.evaluate_strategy_readiness(gi)
        self.assertEqual(report.decision, StrategyGovernanceDecision.REMAIN_IN_PAPER)

    def test_strategy_returns_to_research(self) -> None:
        gi = self._base_input()
        gi.backtest_summary = {"profit_factor": 1.0, "win_rate": 0.45, "max_drawdown": 0.3}
        report = self.engine.evaluate_strategy_readiness(gi)
        self.assertEqual(report.decision, StrategyGovernanceDecision.RETURN_TO_RESEARCH)

    def test_strategy_rejected_outright(self) -> None:
        gi = self._base_input()
        gi.audit_summary = {"blocking_issues": ["structural_failure"], "structural_invalid": True}
        report = self.engine.evaluate_strategy_readiness(gi)
        self.assertEqual(report.decision, StrategyGovernanceDecision.REJECT_STRATEGY)

    def test_edge_decay_blocks_live_approval(self) -> None:
        gi = self._base_input()
        gi.edge_decay_summary = {"significant": True}
        report = self.engine.evaluate_strategy_readiness(gi)
        self.assertEqual(report.decision, StrategyGovernanceDecision.REJECT_STRATEGY)

    def test_blocking_audit_issue_blocks_live_approval(self) -> None:
        gi = self._base_input()
        gi.audit_summary = {"blocking_issues": ["risk_control_failure"], "structural_invalid": False}
        report = self.engine.evaluate_strategy_readiness(gi)
        self.assertNotEqual(report.decision, StrategyGovernanceDecision.APPROVED_FOR_LIVE)

    def test_empty_or_malformed_input_fails_closed(self) -> None:
        with self.assertRaises(StrategyGovernanceError):
            self.engine.evaluate_strategy_readiness(  # type: ignore[arg-type]
                governance_input={"strategy_id": "x"},
            )
        with self.assertRaises(StrategyGovernanceError):
            self.engine.evaluate_strategy_readiness(
                StrategyGovernanceInput(strategy_id=""),
            )

    def test_same_input_yields_same_decision_and_report_id(self) -> None:
        gi = self._base_input()
        r1 = self.engine.evaluate_strategy_readiness(gi)
        r2 = self.engine.evaluate_strategy_readiness(gi)
        self.assertEqual(r1.decision, r2.decision)
        self.assertEqual(r1.report_id, r2.report_id)

    def test_deterministic_report_ids(self) -> None:
        gi = self._base_input()
        report = self.engine.evaluate_strategy_readiness(gi)
        self.assertTrue(report.report_id.startswith("strategy-governance-report-"))


class TestGovernanceIntegrationWithResearchPipeline(unittest.TestCase):
    def test_pipeline_backward_compatible_without_governance(self) -> None:
        def _clock() -> float:
            return 5555555555.0

        engine = ResearchPipelineEngine(clock=_clock)
        bars = [{"ts": 1.0, "close": 100.0}, {"ts": 2.0, "close": 101.0}]
        r1 = engine.run_research_cycle(bars, regime_context=None)
        r2 = engine.run_research_cycle(bars, regime_context=None)
        self.assertEqual(r1.cycle_id, r2.cycle_id)
        self.assertEqual(r1.candidate_count, r2.candidate_count)
        self.assertEqual(r1.approved_strategies, r2.approved_strategies)
        self.assertEqual(r1.rejected_strategies, r2.rejected_strategies)

    def test_governance_enabled_pipeline_changes_disposition_deterministically(self) -> None:
        def _clock() -> float:
            return 6666666666.0

        engine = ResearchPipelineEngine(clock=_clock)
        gov_engine = StrategyGovernanceEngine(clock=_clock)
        bars = [{"ts": 1.0, "close": 100.0}, {"ts": 2.0, "close": 101.0}]

        report = engine.run_research_cycle(
            bars,
            regime_context=None,
            governance_engine=gov_engine,
            enable_governance=True,
        )
        report2 = engine.run_research_cycle(
            bars,
            regime_context=None,
            governance_engine=gov_engine,
            enable_governance=True,
        )
        # Determinism under governance.
        self.assertEqual(report.approved_strategies, report2.approved_strategies)
        self.assertEqual(report.rejected_strategies, report2.rejected_strategies)


if __name__ == "__main__":
    unittest.main()

