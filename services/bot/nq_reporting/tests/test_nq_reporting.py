# NEBULA-QUANT v1 | nq_reporting tests

from __future__ import annotations

import json
import unittest
from typing import Any

from nq_reporting import (
    ReportEngine,
    ReportError,
    build_audit_summary,
    build_experiment_summary,
    build_improvement_summary,
    build_learning_summary,
    build_observability_summary,
    build_trade_review_summary,
    report_to_dict,
    report_to_json,
)


def make_audit_report(
    total_findings: int = 5,
    info_count: int = 1,
    warning_count: int = 2,
    critical_count: int = 2,
    strategies: list[str] | None = None,
    modules: list[str] | None = None,
    recommendations: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "summary": {
            "total_findings": total_findings,
            "info_count": info_count,
            "warning_count": warning_count,
            "critical_count": critical_count,
            "strategies_reviewed": strategies or ["s1"],
            "modules_reviewed": modules or ["nq_risk"],
        },
        "recommendations": recommendations or ["Review s1"],
    }


def make_trade_review_report(outcome: str = "win", findings_count: int = 0) -> dict[str, Any]:
    return {
        "summary": {
            "outcome": outcome,
            "total_findings": findings_count,
            "info_count": 0,
            "warning_count": findings_count,
            "critical_count": 0,
        },
        "findings": [{"category": "poor_entry_quality"}] * findings_count if findings_count else [],
    }


def make_learning_report(
    total_patterns: int = 3,
    total_lessons: int = 2,
    total_improvement_candidates: int = 2,
    high_priority_count: int = 1,
    critical_priority_count: int = 0,
    categories_seen: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "summary": {
            "total_patterns": total_patterns,
            "total_lessons": total_lessons,
            "total_improvement_candidates": total_improvement_candidates,
            "high_priority_count": high_priority_count,
            "critical_priority_count": critical_priority_count,
            "categories_seen": categories_seen or ["repeated_blocked_decisions"],
        },
    }


def make_observability_report(
    system_health_score: float | None = 0.95,
    degraded: list[str] | None = None,
    inactive: list[str] | None = None,
    anomalies: list[str] | None = None,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "system_health_score": system_health_score,
        "degraded_strategies": degraded or [],
        "inactive_strategies": inactive or [],
        "event_anomalies": anomalies or [],
        "metrics_summary": metrics or {},
    }


def make_improvement_plan(
    total_actions: int = 3,
    low_count: int = 1,
    medium_count: int = 1,
    high_count: int = 1,
    critical_count: int = 0,
    affected_strategies: list[str] | None = None,
    affected_modules: list[str] | None = None,
    categories_seen: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "summary": {
            "total_actions": total_actions,
            "low_count": low_count,
            "medium_count": medium_count,
            "high_count": high_count,
            "critical_count": critical_count,
            "affected_strategies": affected_strategies or ["s1"],
            "affected_modules": affected_modules or ["nq_risk"],
            "categories_seen": categories_seen or ["strategy_review"],
        },
    }


def make_experiment_report(
    total_experiments: int = 5,
    successful_experiments: int = 3,
    failed_experiments: int = 1,
    degraded_experiments: int = 1,
    invalid_experiments: int = 0,
    strategies_seen: list[str] | None = None,
    categories_seen: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "summary": {
            "total_experiments": total_experiments,
            "successful_experiments": successful_experiments,
            "failed_experiments": failed_experiments,
            "degraded_experiments": degraded_experiments,
            "invalid_experiments": invalid_experiments,
            "strategies_seen": strategies_seen or ["strat_a", "strat_b"],
            "categories_seen": categories_seen or ["experiment_failed", "weak_result"],
        },
    }


class TestAuditReportSummarization(unittest.TestCase):
    def test_audit_report_summarization(self) -> None:
        audit = make_audit_report(total_findings=10, strategies=["s1", "s2"], recommendations=["R1", "R2"])
        summary = build_audit_summary(audit)
        self.assertEqual(summary.total_findings, 10)
        self.assertEqual(summary.severity_distribution["info"], 1)
        self.assertEqual(summary.severity_distribution["warning"], 2)
        self.assertEqual(summary.severity_distribution["critical"], 2)
        self.assertEqual(sorted(summary.affected_strategies), ["s1", "s2"])
        self.assertEqual(summary.recommendations, ["R1", "R2"])


class TestTradeReviewSummarization(unittest.TestCase):
    def test_trade_review_summarization(self) -> None:
        reports = [
            make_trade_review_report("win"),
            make_trade_review_report("loss"),
            make_trade_review_report("win"),
            make_trade_review_report("breakeven"),
        ]
        summary = build_trade_review_summary(reports)
        self.assertEqual(summary.total_trades_reviewed, 4)
        self.assertAlmostEqual(summary.win_rate, 0.5)
        self.assertAlmostEqual(summary.loss_rate, 0.25)
        self.assertAlmostEqual(summary.breakeven_rate, 0.25)

    def test_trade_review_empty_list(self) -> None:
        summary = build_trade_review_summary([])
        self.assertEqual(summary.total_trades_reviewed, 0)
        self.assertEqual(summary.win_rate, 0.0)


class TestLearningSummaryGeneration(unittest.TestCase):
    def test_learning_summary_generation(self) -> None:
        learning = make_learning_report(total_patterns=5, total_lessons=3, categories_seen=["a", "b"])
        summary = build_learning_summary(learning)
        self.assertEqual(summary.total_patterns, 5)
        self.assertEqual(summary.total_lessons, 3)
        self.assertEqual(summary.high_priority_items, 1)
        self.assertEqual(sorted(summary.categories_seen), ["a", "b"])

    def test_learning_summary_none_returns_empty(self) -> None:
        summary = build_learning_summary(None)
        self.assertEqual(summary.total_patterns, 0)
        self.assertEqual(summary.total_lessons, 0)


class TestObservabilitySummaryGeneration(unittest.TestCase):
    def test_observability_summary_generation(self) -> None:
        obs = make_observability_report(
            system_health_score=0.8,
            degraded=["s1"],
            inactive=["s2"],
            anomalies=["event_anomaly_1"],
            metrics={"latency_p99": 100},
        )
        summary = build_observability_summary(obs)
        self.assertEqual(summary.system_health_score, 0.8)
        self.assertEqual(summary.degraded_strategies, ["s1"])
        self.assertEqual(summary.inactive_strategies, ["s2"])
        self.assertEqual(summary.event_anomalies, ["event_anomaly_1"])
        self.assertEqual(summary.metrics_summary, {"latency_p99": 100})

    def test_observability_none_returns_empty(self) -> None:
        summary = build_observability_summary(None)
        self.assertIsNone(summary.system_health_score)
        self.assertEqual(summary.degraded_strategies, [])
        self.assertEqual(summary.event_anomalies, [])


class TestImprovementSummaryGeneration(unittest.TestCase):
    def test_improvement_summary_generation(self) -> None:
        plan = make_improvement_plan(
            total_actions=4,
            high_count=2,
            critical_count=1,
            affected_strategies=["s1", "s2"],
            categories_seen=["a", "b"],
        )
        summary = build_improvement_summary(plan)
        self.assertEqual(summary.total_actions, 4)
        self.assertEqual(summary.priority_distribution["high"], 2)
        self.assertEqual(summary.priority_distribution["critical"], 1)
        self.assertEqual(sorted(summary.affected_strategies), ["s1", "s2"])
        self.assertEqual(sorted(summary.categories_seen), ["a", "b"])

    def test_improvement_summary_none_returns_empty(self) -> None:
        summary = build_improvement_summary(None)
        self.assertEqual(summary.total_actions, 0)
        self.assertEqual(summary.priority_distribution["low"], 0)
        self.assertEqual(summary.affected_strategies, [])


class TestExperimentSummaryGeneration(unittest.TestCase):
    def test_experiment_summary_generation(self) -> None:
        exp_report = make_experiment_report(
            total_experiments=10,
            successful_experiments=6,
            failed_experiments=2,
            degraded_experiments=2,
            strategies_seen=["x", "y"],
            categories_seen=["experiment_failed", "weak_result"],
        )
        summary = build_experiment_summary(exp_report)
        self.assertEqual(summary.total_experiments, 10)
        self.assertEqual(summary.successful_experiments, 6)
        self.assertEqual(summary.failed_experiments, 2)
        self.assertEqual(summary.degraded_experiments, 2)
        self.assertEqual(sorted(summary.strategies_seen), ["x", "y"])
        self.assertEqual(sorted(summary.categories_seen), ["experiment_failed", "weak_result"])

    def test_experiment_summary_none_returns_empty(self) -> None:
        summary = build_experiment_summary(None)
        self.assertEqual(summary.total_experiments, 0)
        self.assertEqual(summary.successful_experiments, 0)
        self.assertEqual(summary.strategies_seen, [])


class TestSystemReportAggregation(unittest.TestCase):
    def test_system_report_aggregation(self) -> None:
        engine = ReportEngine()
        audit = make_audit_report()
        trade_reports = [make_trade_review_report("win"), make_trade_review_report("loss")]
        learning = make_learning_report()
        obs = make_observability_report()
        report = engine.generate_system_report(
            audit_report=audit,
            trade_review_reports=trade_reports,
            learning_report=learning,
            observability_report=obs,
        )
        self.assertIsNotNone(report.report_id)
        self.assertIsNotNone(report.audit_report)
        self.assertIsNotNone(report.trade_review_report)
        self.assertIsNotNone(report.learning_report)
        self.assertIsNone(report.improvement_report)
        self.assertIsNone(report.experiment_report)
        self.assertIsNotNone(report.observability_report)
        self.assertEqual(report.audit_report.total_findings, 5)
        self.assertEqual(report.trade_review_report.total_trades_reviewed, 2)
        self.assertEqual(report.learning_report.total_patterns, 3)

    def test_enriched_system_report_aggregation(self) -> None:
        engine = ReportEngine()
        report = engine.generate_system_report(
            audit_report=make_audit_report(),
            trade_review_reports=[make_trade_review_report("win")],
            learning_report=make_learning_report(),
            improvement_plan=make_improvement_plan(total_actions=2),
            experiment_report=make_experiment_report(total_experiments=4),
            observability_report=make_observability_report(),
        )
        self.assertIsNotNone(report.audit_report)
        self.assertIsNotNone(report.trade_review_report)
        self.assertIsNotNone(report.learning_report)
        self.assertIsNotNone(report.improvement_report)
        self.assertIsNotNone(report.experiment_report)
        self.assertIsNotNone(report.observability_report)
        self.assertEqual(report.improvement_report.total_actions, 2)
        self.assertEqual(report.experiment_report.total_experiments, 4)


class TestDeterministicOrdering(unittest.TestCase):
    def test_deterministic_ordering(self) -> None:
        engine = ReportEngine()
        report = engine.generate_system_report(
            audit_report=make_audit_report(),
            trade_review_reports=[],
            learning_report=make_learning_report(),
            observability_report=make_observability_report(),
        )
        keys = list(report_to_dict(report).keys())
        self.assertIn("report_id", keys)
        self.assertIn("audit_report", keys)
        self.assertIn("trade_review_report", keys)
        self.assertIn("learning_report", keys)
        self.assertIn("improvement_report", keys)
        self.assertIn("experiment_report", keys)
        self.assertIn("observability_report", keys)
        # Deterministic section order (as in SystemReport field order)
        idx_audit = keys.index("audit_report")
        idx_trade = keys.index("trade_review_report")
        idx_learning = keys.index("learning_report")
        idx_improvement = keys.index("improvement_report")
        idx_experiment = keys.index("experiment_report")
        idx_obs = keys.index("observability_report")
        self.assertLess(idx_audit, idx_trade)
        self.assertLess(idx_trade, idx_learning)
        self.assertLess(idx_learning, idx_improvement)
        self.assertLess(idx_improvement, idx_experiment)
        self.assertLess(idx_experiment, idx_obs)


class TestDeterministicReportIds(unittest.TestCase):
    def test_deterministic_report_ids(self) -> None:
        engine = ReportEngine()
        r1 = engine.generate_system_report(report_id="custom-1")
        r2 = engine.generate_system_report()
        r3 = engine.generate_system_report()
        self.assertEqual(r1.report_id, "custom-1")
        self.assertEqual(r2.report_id, "system-report-2")
        self.assertEqual(r3.report_id, "system-report-3")


class TestSerializationCorrectness(unittest.TestCase):
    def test_report_to_dict(self) -> None:
        engine = ReportEngine()
        report = engine.generate_system_report(audit_report=make_audit_report())
        d = report_to_dict(report)
        self.assertIsInstance(d, dict)
        self.assertIn("report_id", d)
        self.assertIn("generated_at", d)
        self.assertIsInstance(d["audit_report"], dict)
        self.assertEqual(d["audit_report"]["total_findings"], 5)

    def test_report_to_json(self) -> None:
        engine = ReportEngine()
        report = engine.generate_system_report(audit_report=make_audit_report())
        s = report_to_json(report)
        self.assertIsInstance(s, str)
        parsed = json.loads(s)
        self.assertEqual(parsed["audit_report"]["total_findings"], 5)

    def test_serialization_handles_enriched_reports(self) -> None:
        engine = ReportEngine()
        report = engine.generate_system_report(
            audit_report=make_audit_report(),
            improvement_plan=make_improvement_plan(total_actions=2),
            experiment_report=make_experiment_report(total_experiments=3),
        )
        d = report_to_dict(report)
        self.assertIn("improvement_report", d)
        self.assertIn("experiment_report", d)
        self.assertEqual(d["improvement_report"]["total_actions"], 2)
        self.assertEqual(d["experiment_report"]["total_experiments"], 3)
        s = report_to_json(report)
        parsed = json.loads(s)
        self.assertEqual(parsed["improvement_report"]["total_actions"], 2)
        self.assertEqual(parsed["experiment_report"]["total_experiments"], 3)


class TestMalformedInputFailsClosed(unittest.TestCase):
    def test_audit_report_without_summary_fails(self) -> None:
        with self.assertRaises(ReportError):
            build_audit_summary({})

    def test_audit_report_none_fails(self) -> None:
        with self.assertRaises(ReportError):
            build_audit_summary(None)

    def test_learning_report_without_summary_fails(self) -> None:
        with self.assertRaises(ReportError):
            build_learning_summary({"no_summary": True})

    def test_trade_review_reports_not_list_fails(self) -> None:
        with self.assertRaises(ReportError):
            build_trade_review_summary("not-a-list")

    def test_improvement_plan_without_summary_fails(self) -> None:
        with self.assertRaises(ReportError):
            build_improvement_summary({"no_summary": True})

    def test_experiment_report_without_summary_fails(self) -> None:
        with self.assertRaises(ReportError):
            build_experiment_summary({"no_summary": True})


class TestOptionalSectionsHandledSafely(unittest.TestCase):
    def test_all_optional_none(self) -> None:
        engine = ReportEngine()
        report = engine.generate_system_report()
        self.assertIsNone(report.audit_report)
        self.assertIsNone(report.trade_review_report)
        self.assertIsNone(report.learning_report)
        self.assertIsNone(report.improvement_report)
        self.assertIsNone(report.experiment_report)
        self.assertIsNone(report.observability_report)

    def test_partial_reports(self) -> None:
        engine = ReportEngine()
        report = engine.generate_system_report(audit_report=make_audit_report())
        self.assertIsNotNone(report.audit_report)
        self.assertIsNone(report.learning_report)
        self.assertIsNone(report.improvement_report)
        self.assertIsNone(report.experiment_report)


class TestSameInputSameOutput(unittest.TestCase):
    def test_same_input_same_report_output(self) -> None:
        engine = ReportEngine()
        audit = make_audit_report()
        r1 = engine.generate_system_report(audit_report=audit, generated_at=100.0)
        r2 = engine.generate_system_report(audit_report=audit, generated_at=100.0)
        self.assertEqual(r1.audit_report.total_findings, r2.audit_report.total_findings)
        self.assertEqual(r1.audit_report.affected_strategies, r2.audit_report.affected_strategies)
        d1 = report_to_dict(r1)
        d2 = report_to_dict(r2)
        d1["report_id"] = d2["report_id"]
        d1["generated_at"] = d2["generated_at"]
        self.assertEqual(d1, d2)

    def test_same_input_same_system_report_with_all_sections(self) -> None:
        engine = ReportEngine()
        audit = make_audit_report()
        improvement = make_improvement_plan(total_actions=2)
        experiment = make_experiment_report(total_experiments=3)
        r1 = engine.generate_system_report(
            audit_report=audit,
            improvement_plan=improvement,
            experiment_report=experiment,
            report_id="sys-1",
            generated_at=200.0,
        )
        r2 = engine.generate_system_report(
            audit_report=audit,
            improvement_plan=improvement,
            experiment_report=experiment,
            report_id="sys-1",
            generated_at=200.0,
        )
        self.assertEqual(r1.improvement_report.total_actions, r2.improvement_report.total_actions)
        self.assertEqual(r1.experiment_report.total_experiments, r2.experiment_report.total_experiments)
        d1 = report_to_dict(r1)
        d2 = report_to_dict(r2)
        self.assertEqual(d1["improvement_report"], d2["improvement_report"])
        self.assertEqual(d1["experiment_report"], d2["experiment_report"])


class TestSummaryCountsCorrect(unittest.TestCase):
    def test_summary_counts_correct(self) -> None:
        audit = make_audit_report(total_findings=7, info_count=2, warning_count=3, critical_count=2)
        summary = build_audit_summary(audit)
        self.assertEqual(
            summary.severity_distribution["info"] + summary.severity_distribution["warning"] + summary.severity_distribution["critical"],
            summary.total_findings,
        )

    def test_improvement_summary_counts_correct(self) -> None:
        plan = make_improvement_plan(
            total_actions=10,
            low_count=2,
            medium_count=3,
            high_count=4,
            critical_count=1,
        )
        summary = build_improvement_summary(plan)
        self.assertEqual(summary.total_actions, 10)
        self.assertEqual(
            summary.priority_distribution["low"] + summary.priority_distribution["medium"]
            + summary.priority_distribution["high"] + summary.priority_distribution["critical"],
            10,
        )

    def test_experiment_summary_counts_correct(self) -> None:
        exp = make_experiment_report(
            total_experiments=8,
            successful_experiments=4,
            failed_experiments=2,
            degraded_experiments=1,
            invalid_experiments=1,
        )
        summary = build_experiment_summary(exp)
        self.assertEqual(summary.total_experiments, 8)
        self.assertEqual(
            summary.successful_experiments + summary.failed_experiments
            + summary.degraded_experiments + summary.invalid_experiments,
            8,
        )


class TestBackwardCompatibility(unittest.TestCase):
    """Prior supported report flows must keep working."""

    def test_audit_only_flow_unchanged(self) -> None:
        engine = ReportEngine()
        report = engine.generate_system_report(audit_report=make_audit_report())
        self.assertIsNotNone(report.audit_report)
        self.assertEqual(report.audit_report.total_findings, 5)
        self.assertIsNone(report.trade_review_report)
        self.assertIsNone(report.learning_report)
        self.assertIsNone(report.improvement_report)
        self.assertIsNone(report.experiment_report)

    def test_audit_trade_learning_observability_flow_unchanged(self) -> None:
        engine = ReportEngine()
        report = engine.generate_system_report(
            audit_report=make_audit_report(),
            trade_review_reports=[make_trade_review_report("win")],
            learning_report=make_learning_report(),
            observability_report=make_observability_report(),
        )
        self.assertIsNotNone(report.audit_report)
        self.assertIsNotNone(report.trade_review_report)
        self.assertIsNotNone(report.learning_report)
        self.assertIsNotNone(report.observability_report)
        self.assertIsNone(report.improvement_report)
        self.assertIsNone(report.experiment_report)
        self.assertEqual(report.trade_review_report.total_trades_reviewed, 1)
        self.assertEqual(report.learning_report.total_patterns, 3)
