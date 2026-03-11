# NEBULA-QUANT v1 | nq_alpha_discovery tests

from __future__ import annotations

import unittest
from typing import Any

from nq_alpha_discovery import (
    AlphaDiscoveryEngine,
    AlphaDiscoveryError,
    AlphaHypothesisPriority,
    rank_hypotheses,
)
from nq_alpha_discovery.extractors import (
    extract_from_audit,
    extract_from_experiment,
    extract_from_learning,
    extract_from_trade_review,
    normalize_direct_observations,
)


def make_clock(now: float = 100.0):
    def clock() -> float:
        return now
    return clock


def make_learning_report(
    patterns: list[dict] | None = None,
    lessons: list[dict] | None = None,
    improvement_candidates: list[dict] | None = None,
) -> dict[str, Any]:
    return {
        "patterns": patterns or [],
        "lessons": lessons or [],
        "improvement_candidates": improvement_candidates or [],
    }


def make_experiment_report(findings: list[dict] | None = None) -> dict[str, Any]:
    return {"findings": findings or []}


def make_audit_report(findings: list[dict] | None = None, recommendations: list[str] | None = None) -> dict[str, Any]:
    return {"findings": findings or [], "recommendations": recommendations or []}


def make_trade_review_report(findings: list[dict] | None = None, recommendations: list[str] | None = None) -> dict[str, Any]:
    return {"findings": findings or [], "recommendations": recommendations or []}


class TestObservationExtractionFromLearning(unittest.TestCase):
    def test_extract_from_learning_report(self) -> None:
        report = make_learning_report(
            patterns=[
                {"pattern_id": "p1", "category": "repeated_blocked", "count": 3, "related_strategy_id": "s1"},
            ],
            lessons=[
                {"lesson_id": "l1", "title": "Review entries", "description": "Poor entry quality", "priority": "high", "related_strategy_id": "s1"},
            ],
            improvement_candidates=[
                {"candidate_id": "c1", "title": "Revise entry rules", "description": "For strategy s1", "priority": "medium"},
            ],
        )
        obs, ev = extract_from_learning(report)
        self.assertEqual(len(obs), 3)
        self.assertEqual(len(ev), 3)
        self.assertEqual(obs[0].category, "repeated_blocked")
        self.assertEqual(obs[0].strategy_id, "s1")
        self.assertEqual(obs[1].title, "Review entries")
        self.assertEqual(obs[2].category, "improvement_candidate")


class TestObservationExtractionFromExperiment(unittest.TestCase):
    def test_extract_from_experiment_report(self) -> None:
        report = make_experiment_report(findings=[
            {"finding_id": "f1", "category": "weak_result", "severity": "warning", "title": "Low expectancy", "strategy_id": "s1"},
        ])
        obs, ev = extract_from_experiment(report)
        self.assertEqual(len(obs), 1)
        self.assertEqual(obs[0].category, "weak_result")
        self.assertEqual(obs[0].severity, "warning")
        self.assertEqual(obs[0].strategy_id, "s1")


class TestObservationExtractionFromAudit(unittest.TestCase):
    def test_extract_from_audit_report(self) -> None:
        report = make_audit_report(
            findings=[
                {"finding_id": "a1", "category": "execution_quality", "severity": "critical", "title": "Slippage", "related_strategy_id": "s1"},
            ],
            recommendations=["Review execution costs"],
        )
        obs, ev = extract_from_audit(report)
        self.assertGreaterEqual(len(obs), 1)
        self.assertEqual(obs[0].category, "execution_quality")
        rec_obs = [o for o in obs if o.category == "recommendation"]
        self.assertEqual(len(rec_obs), 1)
        self.assertIn("Review execution", rec_obs[0].title)


class TestObservationExtractionFromTradeReview(unittest.TestCase):
    def test_extract_from_trade_review_reports(self) -> None:
        reports = [
            make_trade_review_report(
                findings=[{"finding_id": "t1", "category": "poor_entry_quality", "severity": "warning", "title": "Entry", "strategy_id": "s1"}],
                recommendations=["Improve entry timing"],
            ),
        ]
        obs, ev = extract_from_trade_review(reports)
        self.assertGreaterEqual(len(obs), 1)
        self.assertEqual(obs[0].category, "poor_entry_quality")
        recs = [o for o in obs if o.category == "recommendation"]
        self.assertGreaterEqual(len(recs), 1)


class TestDirectObservationsSupported(unittest.TestCase):
    def test_direct_observations_normalized(self) -> None:
        items = [
            {"category": "slippage", "title": "Slippage in FX", "strategy_id": "s1"},
            {"category": "liquidity", "description": "Thin book"},
        ]
        obs, ev = normalize_direct_observations(items)
        self.assertEqual(len(obs), 2)
        self.assertEqual(obs[0].category, "slippage")
        self.assertEqual(obs[1].category, "liquidity")

    def test_direct_observation_missing_category_and_title_fails(self) -> None:
        with self.assertRaises(AlphaDiscoveryError):
            normalize_direct_observations([{}])


class TestRepeatedRelatedObservationsGenerateHypotheses(unittest.TestCase):
    def test_repeated_observations_generate_hypothesis(self) -> None:
        engine = AlphaDiscoveryEngine(clock=make_clock())
        learning = make_learning_report(
            patterns=[
                {"pattern_id": "p1", "category": "poor_entry", "count": 2, "related_strategy_id": "s1"},
                {"pattern_id": "p2", "category": "poor_entry", "count": 2, "related_strategy_id": "s1"},
            ],
        )
        report = engine.generate_hypotheses(learning_report=learning)
        self.assertGreaterEqual(len(report.hypotheses), 1)
        hyp = [h for h in report.hypotheses if h.category == "poor_entry" and h.related_strategy_id == "s1"]
        self.assertGreaterEqual(len(hyp), 1)
        self.assertIn("poor_entry", hyp[0].title)
        self.assertIn("s1", hyp[0].title)


class TestHypothesesIncludeRationaleAndEvidenceLinkage(unittest.TestCase):
    def test_hypotheses_have_rationale_and_evidence_ids(self) -> None:
        engine = AlphaDiscoveryEngine(clock=make_clock())
        report = engine.generate_hypotheses(
            experiment_report=make_experiment_report(findings=[
                {"finding_id": "f1", "category": "weak_result", "severity": "warning", "title": "Weak", "strategy_id": "s1"},
            ]),
        )
        self.assertGreaterEqual(len(report.hypotheses), 1)
        h = report.hypotheses[0]
        self.assertTrue(h.rationale.startswith("Based on"))
        self.assertIn("observation", h.rationale.lower())
        self.assertGreaterEqual(len(h.evidence_ids), 1)


class TestRankingPriorityDeterministic(unittest.TestCase):
    def test_ranking_priority_assignment_deterministic(self) -> None:
        engine = AlphaDiscoveryEngine(clock=make_clock())
        learning = make_learning_report(
            patterns=[
                {"pattern_id": "p1", "category": "cat_critical", "count": 3, "severity_distribution": {"critical": 1}},
                {"pattern_id": "p2", "category": "cat_low", "count": 1},
            ],
        )
        report = engine.generate_hypotheses(learning_report=learning)
        priorities = [h.priority for h in report.hypotheses]
        if AlphaHypothesisPriority.CRITICAL.value in priorities and AlphaHypothesisPriority.LOW.value in priorities:
            crit_idx = report.hypotheses[0].priority
            self.assertIn(crit_idx, (AlphaHypothesisPriority.CRITICAL.value, AlphaHypothesisPriority.HIGH.value))
        sorted_h = rank_hypotheses(report.hypotheses)
        self.assertEqual(len(sorted_h), len(report.hypotheses))
        pri_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        for i in range(len(sorted_h) - 1):
            self.assertGreaterEqual(pri_rank.get(sorted_h[i].priority, 0), pri_rank.get(sorted_h[i + 1].priority, 0))


class TestMalformedCriticalInputFailsClosed(unittest.TestCase):
    def test_trade_review_reports_not_list_fails(self) -> None:
        with self.assertRaises(AlphaDiscoveryError):
            extract_from_trade_review("not-a-list")

    def test_direct_observation_empty_category_title_fails(self) -> None:
        with self.assertRaises(AlphaDiscoveryError):
            normalize_direct_observations([{"description": "only desc"}])


class TestMissingOptionalSectionsHandledSafely(unittest.TestCase):
    def test_all_optional_none_returns_empty_report(self) -> None:
        engine = AlphaDiscoveryEngine(clock=make_clock())
        report = engine.generate_hypotheses()
        self.assertEqual(report.summary.total_observations, 0)
        self.assertEqual(report.summary.total_hypotheses, 0)
        self.assertEqual(len(report.hypotheses), 0)

    def test_partial_sources_ok(self) -> None:
        engine = AlphaDiscoveryEngine(clock=make_clock())
        report = engine.generate_hypotheses(learning_report=make_learning_report(patterns=[]))
        self.assertEqual(report.summary.total_observations, 0)


class TestEmptyInputReturnsValidEmptyReport(unittest.TestCase):
    def test_empty_input_returns_valid_empty_report(self) -> None:
        engine = AlphaDiscoveryEngine(clock=make_clock())
        report = engine.generate_hypotheses(
            learning_report=make_learning_report(),
            experiment_report=make_experiment_report(),
            audit_report=make_audit_report(),
        )
        self.assertEqual(report.summary.total_observations, 0)
        self.assertEqual(report.summary.total_hypotheses, 0)
        self.assertEqual(report.hypotheses, [])
        self.assertEqual(report.summary.low_count, 0)
        self.assertEqual(report.summary.categories_seen, [])


class TestSameInputSameReportOutput(unittest.TestCase):
    def test_same_input_same_report_output(self) -> None:
        engine = AlphaDiscoveryEngine(clock=make_clock(50.0))
        learning = make_learning_report(patterns=[{"pattern_id": "p1", "category": "x", "count": 1}])
        r1 = engine.generate_hypotheses(learning_report=learning, generated_at=50.0)
        r2 = engine.generate_hypotheses(learning_report=learning, generated_at=50.0)
        self.assertEqual(len(r1.hypotheses), len(r2.hypotheses))
        self.assertEqual(r1.summary.total_observations, r2.summary.total_observations)
        for h1, h2 in zip(r1.hypotheses, r2.hypotheses):
            self.assertEqual(h1.category, h2.category)
            self.assertEqual(h1.priority, h2.priority)
            self.assertEqual(h1.confidence_score, h2.confidence_score)


class TestDeterministicReportIds(unittest.TestCase):
    def test_deterministic_report_ids(self) -> None:
        engine = AlphaDiscoveryEngine(clock=make_clock())
        r1 = engine.generate_hypotheses(report_id="custom-1")
        r2 = engine.generate_hypotheses()
        r3 = engine.generate_hypotheses()
        self.assertEqual(r1.report_id, "custom-1")
        self.assertEqual(r2.report_id, "alpha-discovery-report-2")
        self.assertEqual(r3.report_id, "alpha-discovery-report-3")


class TestDeterministicHypothesisIds(unittest.TestCase):
    def test_deterministic_hypothesis_ids(self) -> None:
        engine = AlphaDiscoveryEngine(clock=make_clock())
        report = engine.generate_hypotheses(
            learning_report=make_learning_report(patterns=[
                {"pattern_id": "p1", "category": "a", "count": 1},
                {"pattern_id": "p2", "category": "b", "count": 1},
            ]),
        )
        ids = [h.hypothesis_id for h in report.hypotheses]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(id.startswith("hyp-") for id in ids))


class TestSummaryCountsCorrect(unittest.TestCase):
    def test_summary_counts_correct(self) -> None:
        engine = AlphaDiscoveryEngine(clock=make_clock())
        report = engine.generate_hypotheses(
            learning_report=make_learning_report(
                patterns=[
                    {"pattern_id": "p1", "category": "c1", "count": 2, "severity_distribution": {"critical": 1}},
                    {"pattern_id": "p2", "category": "c2", "count": 1},
                ],
            ),
        )
        self.assertEqual(report.summary.total_observations, 2)
        self.assertEqual(report.summary.total_hypotheses, 2)
        total_pri = report.summary.low_count + report.summary.medium_count + report.summary.high_count + report.summary.critical_count
        self.assertEqual(total_pri, report.summary.total_hypotheses)
        self.assertIn("c1", report.summary.categories_seen)
        self.assertIn("c2", report.summary.categories_seen)


class TestNoHiddenDependencies(unittest.TestCase):
    def test_no_hidden_dependencies_on_external_services(self) -> None:
        from nq_alpha_discovery import AlphaDiscoveryEngine
        from nq_alpha_discovery.models import AlphaDiscoveryReport
        engine = AlphaDiscoveryEngine()
        report = engine.generate_hypotheses()
        self.assertIsInstance(report, AlphaDiscoveryReport)
        self.assertEqual(report.summary.total_hypotheses, 0)
