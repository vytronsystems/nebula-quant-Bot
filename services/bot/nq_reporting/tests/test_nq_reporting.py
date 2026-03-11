# NEBULA-QUANT v1 | nq_reporting tests

from __future__ import annotations

import json
import unittest
from typing import Any

from nq_reporting import (
    ReportEngine,
    ReportError,
    build_audit_summary,
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
        self.assertIsNotNone(report.observability_report)
        self.assertEqual(report.audit_report.total_findings, 5)
        self.assertEqual(report.trade_review_report.total_trades_reviewed, 2)
        self.assertEqual(report.learning_report.total_patterns, 3)


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
        self.assertIn("observability_report", keys)


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


class TestOptionalSectionsHandledSafely(unittest.TestCase):
    def test_all_optional_none(self) -> None:
        engine = ReportEngine()
        report = engine.generate_system_report()
        self.assertIsNone(report.audit_report)
        self.assertIsNone(report.trade_review_report)
        self.assertIsNone(report.learning_report)
        self.assertIsNone(report.observability_report)

    def test_partial_reports(self) -> None:
        engine = ReportEngine()
        report = engine.generate_system_report(audit_report=make_audit_report())
        self.assertIsNotNone(report.audit_report)
        self.assertIsNone(report.learning_report)


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


class TestSummaryCountsCorrect(unittest.TestCase):
    def test_summary_counts_correct(self) -> None:
        audit = make_audit_report(total_findings=7, info_count=2, warning_count=3, critical_count=2)
        summary = build_audit_summary(audit)
        self.assertEqual(
            summary.severity_distribution["info"] + summary.severity_distribution["warning"] + summary.severity_distribution["critical"],
            summary.total_findings,
        )
