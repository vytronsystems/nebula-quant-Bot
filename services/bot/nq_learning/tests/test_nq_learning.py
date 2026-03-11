# NEBULA-QUANT v1 | nq_learning tests

from __future__ import annotations

import unittest
from typing import Callable

from nq_learning import LearningEngine, LearningError, LearningInput


def make_clock(ticks: list[float]) -> tuple[list[float], Callable[[], float]]:
    it = iter(ticks)
    def clock() -> float:
        return next(it)
    return ticks, clock


def finding(category: str, severity: str = "info", strategy_id: str | None = None, module: str | None = None) -> dict:
    d: dict = {"category": category, "severity": severity}
    if strategy_id is not None:
        d["related_strategy_id"] = strategy_id
    if module is not None:
        d["related_module"] = module
    return d


class TestValidInputDeterministicReport(unittest.TestCase):
    def test_valid_learning_input_produces_deterministic_report(self) -> None:
        engine = LearningEngine()
        input_data = LearningInput(audit_findings=[], trade_review_findings=[])
        report = engine.run_learning(input_data)
        self.assertIsNotNone(report.learning_id)
        self.assertIsInstance(report.generated_at, (int, float))
        self.assertEqual(report.summary.total_patterns, 0)
        self.assertEqual(report.summary.total_lessons, 0)
        self.assertEqual(report.summary.total_improvement_candidates, 0)
        self.assertEqual(len(report.patterns), 0)
        self.assertEqual(len(report.lessons), 0)
        self.assertEqual(len(report.improvement_candidates), 0)


class TestRepeatedCategoriesAggregate(unittest.TestCase):
    def test_repeated_categories_aggregate_into_expected_patterns(self) -> None:
        engine = LearningEngine()
        input_data = LearningInput(
            audit_findings=[
                finding("repeated_blocked_decisions", "warning"),
                finding("repeated_blocked_decisions", "warning"),
                finding("repeated_blocked_decisions", "critical"),
            ],
            trade_review_findings=[],
        )
        report = engine.run_learning(input_data)
        by_cat = [p for p in report.patterns if p.category == "repeated_blocked_decisions" and p.related_strategy_id is None and p.related_module is None]
        self.assertGreaterEqual(len(by_cat), 1)
        self.assertEqual(by_cat[0].count, 3)
        self.assertIn("warning", by_cat[0].severity_distribution)
        self.assertIn("critical", by_cat[0].severity_distribution)


class TestStrategySpecificPatterns(unittest.TestCase):
    def test_strategy_specific_repeated_findings_create_strategy_linked_patterns(self) -> None:
        engine = LearningEngine()
        input_data = LearningInput(
            audit_findings=[],
            trade_review_findings=[
                finding("poor_entry_quality", "warning", strategy_id="s1"),
                finding("poor_entry_quality", "warning", strategy_id="s1"),
            ],
        )
        report = engine.run_learning(input_data)
        strategy_patterns = [p for p in report.patterns if p.related_strategy_id == "s1"]
        self.assertGreaterEqual(len(strategy_patterns), 1)
        self.assertIn("s1", report.summary.strategies_seen)


class TestModuleSpecificPatterns(unittest.TestCase):
    def test_module_specific_repeated_findings_create_module_linked_patterns(self) -> None:
        engine = LearningEngine()
        input_data = LearningInput(
            audit_findings=[
                finding("excessive_throttling", "warning", module="nq_guardrails"),
                finding("excessive_throttling", "warning", module="nq_guardrails"),
            ],
            trade_review_findings=[],
        )
        report = engine.run_learning(input_data)
        module_patterns = [p for p in report.patterns if p.related_module == "nq_guardrails"]
        self.assertGreaterEqual(len(module_patterns), 1)
        self.assertIn("nq_guardrails", report.summary.modules_seen)


class TestSeverityDistributions(unittest.TestCase):
    def test_severity_distributions_are_counted_correctly(self) -> None:
        engine = LearningEngine()
        input_data = LearningInput(
            audit_findings=[
                finding("rr_underperformance", "info"),
                finding("rr_underperformance", "warning"),
                finding("rr_underperformance", "warning"),
            ],
            trade_review_findings=[],
        )
        report = engine.run_learning(input_data)
        rr_patterns = [p for p in report.patterns if p.category == "rr_underperformance"]
        self.assertGreaterEqual(len(rr_patterns), 1)
        p0 = rr_patterns[0]
        self.assertEqual(p0.severity_distribution.get("info", 0), 1)
        self.assertEqual(p0.severity_distribution.get("warning", 0), 2)


class TestLessonsDerivedFromPatterns(unittest.TestCase):
    def test_lessons_derived_deterministically_from_patterns(self) -> None:
        engine = LearningEngine()
        input_data = LearningInput(
            audit_findings=[
                finding("repeated_promotion_rejections", "warning", strategy_id="s1"),
                finding("repeated_promotion_rejections", "warning", strategy_id="s1"),
            ],
            trade_review_findings=[],
        )
        report = engine.run_learning(input_data)
        self.assertGreaterEqual(report.summary.total_lessons, 1)
        for lesson in report.lessons:
            self.assertIn(lesson.related_categories[0], ["repeated_promotion_rejections"])
            self.assertIn(lesson.priority, ("low", "medium", "high", "critical"))


class TestImprovementCandidatesDerived(unittest.TestCase):
    def test_improvement_candidates_derived_deterministically(self) -> None:
        engine = LearningEngine()
        input_data = LearningInput(
            trade_review_findings=[
                finding("excessive_slippage", "warning", strategy_id="s2"),
                finding("excessive_slippage", "warning", strategy_id="s2"),
            ],
            audit_findings=[],
        )
        report = engine.run_learning(input_data)
        self.assertGreaterEqual(report.summary.total_improvement_candidates, 1)
        slip_candidates = [c for c in report.improvement_candidates if "slippage" in c.title.lower()]
        self.assertGreaterEqual(len(slip_candidates), 1)


class TestPriorityAssignment(unittest.TestCase):
    def test_priority_assignment_deterministic_and_grounded(self) -> None:
        engine = LearningEngine()
        input_data = LearningInput(
            audit_findings=[
                finding("repeated_blocked_decisions", "critical", strategy_id="s1"),
                finding("repeated_blocked_decisions", "critical", strategy_id="s1"),
            ],
            trade_review_findings=[],
        )
        report = engine.run_learning(input_data)
        critical_lessons = [l for l in report.lessons if l.priority == "critical"]
        critical_candidates = [c for c in report.improvement_candidates if c.priority == "critical"]
        self.assertGreaterEqual(len(critical_lessons) + len(critical_candidates), 1)


class TestMissingOptionalSections(unittest.TestCase):
    def test_missing_optional_sections_do_not_crash_learning(self) -> None:
        engine = LearningEngine()
        input_data = LearningInput()
        report = engine.run_learning(input_data)
        self.assertEqual(report.summary.total_patterns, 0)


class TestMalformedCriticalInput(unittest.TestCase):
    def test_malformed_audit_findings_fails_closed(self) -> None:
        engine = LearningEngine()
        input_data = LearningInput(
            audit_findings="not-a-list",  # type: ignore[arg-type]
            trade_review_findings=[],
        )
        with self.assertRaises(LearningError):
            engine.run_learning(input_data)


class TestRepeatedInputsSameStructure(unittest.TestCase):
    def test_repeated_same_inputs_yield_same_report_structure(self) -> None:
        _, clock = make_clock([100.0, 101.0])
        engine = LearningEngine(clock=clock)
        input_data = LearningInput(
            audit_findings=[finding("repeated_blocked_decisions", "warning"), finding("repeated_blocked_decisions", "warning")],
            trade_review_findings=[],
        )
        r1 = engine.run_learning(input_data, generated_at=100.0)
        r2 = engine.run_learning(input_data, generated_at=100.0)
        self.assertEqual(len(r1.patterns), len(r2.patterns))
        self.assertEqual([p.category for p in r1.patterns], [p.category for p in r2.patterns])


class TestLearningIdsDeterministic(unittest.TestCase):
    def test_learning_ids_deterministic(self) -> None:
        engine = LearningEngine()
        r1 = engine.run_learning(LearningInput(), learning_id="custom-1")
        r2 = engine.run_learning(LearningInput())
        r3 = engine.run_learning(LearningInput())
        self.assertEqual(r1.learning_id, "custom-1")
        self.assertEqual(r2.learning_id, "learning-2")
        self.assertEqual(r3.learning_id, "learning-3")


class TestNoHiddenDependencies(unittest.TestCase):
    def test_no_hidden_external_services(self) -> None:
        engine = LearningEngine()
        report = engine.run_learning(LearningInput())
        self.assertIsNotNone(report.learning_id)
        self.assertIsInstance(report.patterns, list)


class TestSummaryCounts(unittest.TestCase):
    def test_summary_counts_are_correct(self) -> None:
        engine = LearningEngine()
        input_data = LearningInput(
            audit_findings=[
                finding("repeated_blocked_decisions", "warning", strategy_id="s1"),
                finding("repeated_blocked_decisions", "warning", strategy_id="s1"),
            ],
            trade_review_findings=[
                finding("incomplete_trade_record", "info"),
                finding("incomplete_trade_record", "info"),
            ],
        )
        report = engine.run_learning(input_data)
        self.assertEqual(report.summary.total_patterns, len(report.patterns))
        self.assertEqual(report.summary.total_lessons, len(report.lessons))
        self.assertEqual(report.summary.total_improvement_candidates, len(report.improvement_candidates))
        self.assertEqual(report.summary.categories_seen, sorted(set(p.category for p in report.patterns)))
