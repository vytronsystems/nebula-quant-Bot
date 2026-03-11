# NEBULA-QUANT v1 | nq_edge_decay tests

from __future__ import annotations

import unittest
from typing import Any

from nq_edge_decay import EdgeDecayEngine, EdgeDecayError
from nq_edge_decay.analyzers import analyze_single_input
from nq_edge_decay.models import (
    CATEGORY_EXECUTION_QUALITY_DECAY,
    CATEGORY_EXPERIMENT_QUALITY_DECAY,
    CATEGORY_EXPECTANCY_DECAY,
    CATEGORY_MIXED_EDGE_DECAY,
    CATEGORY_PNL_DECAY,
    CATEGORY_SLIPPAGE_DECAY,
    CATEGORY_WIN_RATE_DECAY,
    CATEGORY_INSUFFICIENT_BASELINE,
)


def make_clock(now: float = 100.0):
    def clock() -> float:
        return now
    return clock


def make_input(
    strategy_id: str | None = "s1",
    recent_pnl: float | None = None,
    baseline_pnl: float | None = None,
    recent_win_rate: float | None = None,
    baseline_win_rate: float | None = None,
    recent_expectancy: float | None = None,
    baseline_expectancy: float | None = None,
    recent_slippage: float | None = None,
    baseline_slippage: float | None = None,
    recent_failed_experiments: int | None = None,
    baseline_failed_experiments: int | None = None,
    recent_degraded_experiments: int | None = None,
    baseline_degraded_experiments: int | None = None,
    repeated_trade_review_findings: int | None = None,
    repeated_audit_findings: int | None = None,
) -> dict[str, Any]:
    return {
        "strategy_id": strategy_id,
        "recent_pnl": recent_pnl,
        "baseline_pnl": baseline_pnl,
        "recent_win_rate": recent_win_rate,
        "baseline_win_rate": baseline_win_rate,
        "recent_expectancy": recent_expectancy,
        "baseline_expectancy": baseline_expectancy,
        "recent_slippage": recent_slippage,
        "baseline_slippage": baseline_slippage,
        "recent_failed_experiments": recent_failed_experiments,
        "baseline_failed_experiments": baseline_failed_experiments,
        "recent_degraded_experiments": recent_degraded_experiments,
        "baseline_degraded_experiments": baseline_degraded_experiments,
        "repeated_trade_review_findings": repeated_trade_review_findings,
        "repeated_audit_findings": repeated_audit_findings,
    }


class TestPnlDecayDetection(unittest.TestCase):
    def test_pnl_decay_detection(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        inp = make_input(baseline_pnl=100.0, recent_pnl=85.0)  # 15% drop
        report = engine.analyze_edge_decay([inp])
        self.assertGreaterEqual(len(report.findings), 1)
        pnl_findings = [f for f in report.findings if f.category == CATEGORY_PNL_DECAY]
        self.assertEqual(len(pnl_findings), 1)
        self.assertIn("deteriorat", pnl_findings[0].rationale.lower())


class TestWinRateDecayDetection(unittest.TestCase):
    def test_win_rate_decay_detection(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        inp = make_input(baseline_win_rate=0.55, recent_win_rate=0.48)  # 7 pp drop
        report = engine.analyze_edge_decay([inp])
        wr_findings = [f for f in report.findings if f.category == CATEGORY_WIN_RATE_DECAY]
        self.assertEqual(len(wr_findings), 1)
        self.assertIn("drop", wr_findings[0].rationale.lower())


class TestExpectancyDecayDetection(unittest.TestCase):
    def test_expectancy_decay_detection(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        inp = make_input(baseline_expectancy=0.5, recent_expectancy=0.35)  # 0.15 drop
        report = engine.analyze_edge_decay([inp])
        exp_findings = [f for f in report.findings if f.category == CATEGORY_EXPECTANCY_DECAY]
        self.assertEqual(len(exp_findings), 1)


class TestSlippageDecayDetection(unittest.TestCase):
    def test_slippage_decay_detection(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        inp = make_input(baseline_slippage=0.001, recent_slippage=0.0015)  # 50% increase
        report = engine.analyze_edge_decay([inp])
        slip_findings = [f for f in report.findings if f.category == CATEGORY_SLIPPAGE_DECAY]
        self.assertEqual(len(slip_findings), 1)


class TestExperimentQualityDecayDetection(unittest.TestCase):
    def test_experiment_quality_decay_detection(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        inp = make_input(
            baseline_failed_experiments=0,
            baseline_degraded_experiments=1,
            recent_failed_experiments=1,
            recent_degraded_experiments=2,
        )
        report = engine.analyze_edge_decay([inp])
        exp_findings = [f for f in report.findings if f.category == CATEGORY_EXPERIMENT_QUALITY_DECAY]
        self.assertEqual(len(exp_findings), 1)


class TestExecutionQualityDecayDetection(unittest.TestCase):
    def test_execution_quality_decay_from_repeated_findings(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        inp = make_input(repeated_trade_review_findings=3, repeated_audit_findings=2)
        report = engine.analyze_edge_decay([inp])
        exec_findings = [f for f in report.findings if f.category == CATEGORY_EXECUTION_QUALITY_DECAY]
        self.assertEqual(len(exec_findings), 1)


class TestMixedEdgeDecayGeneration(unittest.TestCase):
    def test_mixed_edge_decay_when_multiple_categories_trigger(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        inp = make_input(
            baseline_pnl=100.0,
            recent_pnl=80.0,
            baseline_win_rate=0.55,
            recent_win_rate=0.48,
        )
        report = engine.analyze_edge_decay([inp])
        mixed = [f for f in report.findings if f.category == CATEGORY_MIXED_EDGE_DECAY]
        self.assertEqual(len(mixed), 1)
        self.assertEqual(mixed[0].severity, "critical")
        self.assertIn("Multiple", mixed[0].title)


class TestInsufficientBaselineHandling(unittest.TestCase):
    def test_insufficient_baseline_handling(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        inp = make_input(strategy_id="s1", recent_pnl=50.0, baseline_pnl=None)
        report = engine.analyze_edge_decay([inp])
        insuf = [f for f in report.findings if f.category == CATEGORY_INSUFFICIENT_BASELINE]
        self.assertGreaterEqual(len(insuf), 1)
        self.assertIn("baseline", insuf[0].title.lower())


class TestMalformedCriticalInputFailsClosed(unittest.TestCase):
    def test_edge_inputs_not_list_raises(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        with self.assertRaises(EdgeDecayError):
            engine.analyze_edge_decay("not-a-list")

    def test_edge_inputs_contains_none_raises(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        with self.assertRaises(EdgeDecayError):
            engine.analyze_edge_decay([make_input(), None])


class TestEmptyInputReturnsValidEmptyReport(unittest.TestCase):
    def test_empty_input_returns_valid_empty_report(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        report = engine.analyze_edge_decay([])
        self.assertEqual(report.summary.total_findings, 0)
        self.assertEqual(report.findings, [])
        self.assertEqual(report.summary.strategies_seen, [])

    def test_none_input_returns_empty_report(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        report = engine.analyze_edge_decay(None)
        self.assertEqual(report.summary.total_findings, 0)


class TestSameInputSameReportOutput(unittest.TestCase):
    def test_same_input_same_report_output(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock(50.0))
        inp = make_input(baseline_win_rate=0.5, recent_win_rate=0.42)
        r1 = engine.analyze_edge_decay([inp], generated_at=50.0)
        r2 = engine.analyze_edge_decay([inp], generated_at=50.0)
        self.assertEqual(len(r1.findings), len(r2.findings))
        self.assertEqual(r1.summary.total_findings, r2.summary.total_findings)
        for f1, f2 in zip(r1.findings, r2.findings):
            self.assertEqual(f1.category, f2.category)
            self.assertEqual(f1.rationale, f2.rationale)


class TestDeterministicReportIds(unittest.TestCase):
    def test_deterministic_report_ids(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        r1 = engine.analyze_edge_decay([make_input()], report_id="custom-1")
        r2 = engine.analyze_edge_decay([make_input()])
        r3 = engine.analyze_edge_decay([make_input()])
        self.assertEqual(r1.report_id, "custom-1")
        self.assertEqual(r2.report_id, "edge-decay-report-2")
        self.assertEqual(r3.report_id, "edge-decay-report-3")


class TestDeterministicFindingIds(unittest.TestCase):
    def test_deterministic_finding_ids(self) -> None:
        findings, _ = analyze_single_input(
            make_input(baseline_pnl=100, recent_pnl=80),
            "find-0",
            "ev-0",
        )
        self.assertGreaterEqual(len(findings), 1)
        self.assertTrue(findings[0].finding_id.startswith("find-0-"))


class TestDeterministicEvidenceIds(unittest.TestCase):
    def test_deterministic_evidence_ids(self) -> None:
        _, evidence = analyze_single_input(
            make_input(baseline_pnl=100, recent_pnl=80),
            "find-0",
            "ev-0",
        )
        self.assertGreaterEqual(len(evidence), 1)
        self.assertTrue(evidence[0].evidence_id.startswith("ev-0-"))


class TestSummaryCountsCorrect(unittest.TestCase):
    def test_summary_counts_correct(self) -> None:
        engine = EdgeDecayEngine(clock=make_clock())
        report = engine.analyze_edge_decay([
            make_input(baseline_pnl=100, recent_pnl=85, strategy_id="s1"),
            make_input(repeated_trade_review_findings=3, strategy_id="s2"),
        ])
        self.assertGreaterEqual(report.summary.total_findings, 1)
        total_sev = report.summary.info_count + report.summary.warning_count + report.summary.critical_count
        self.assertEqual(total_sev, report.summary.total_findings)
        self.assertIn("s1", report.summary.strategies_seen or [])
        self.assertIn("s2", report.summary.strategies_seen or [])


class TestNoHiddenDependencies(unittest.TestCase):
    def test_no_hidden_dependencies_on_external_services(self) -> None:
        from nq_edge_decay import EdgeDecayEngine
        from nq_edge_decay.models import EdgeDecayReport
        engine = EdgeDecayEngine()
        report = engine.analyze_edge_decay([])
        self.assertIsInstance(report, EdgeDecayReport)
        self.assertEqual(report.summary.total_findings, 0)
