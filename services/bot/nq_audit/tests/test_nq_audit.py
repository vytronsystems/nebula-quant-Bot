# NEBULA-QUANT v1 | nq_audit tests

from __future__ import annotations

import unittest
from typing import Callable

from nq_audit import AuditEngine, AuditError, AuditInput


def make_clock(ticks: list[float]) -> tuple[list[float], Callable[[], float]]:
    it = iter(ticks)
    def clock() -> float:
        return next(it)
    return ticks, clock


class TestValidInputDeterministicReport(unittest.TestCase):
    def test_valid_audit_input_produces_deterministic_report(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput(decision_records=[], execution_records=[], strategy_health=[])
        report = engine.run_audit(input_data)
        self.assertIsNotNone(report.audit_id)
        self.assertIsInstance(report.generated_at, (int, float))
        self.assertEqual(report.summary.total_findings, 0)
        self.assertEqual(report.summary.info_count, 0)
        self.assertEqual(report.summary.warning_count, 0)
        self.assertEqual(report.summary.critical_count, 0)
        self.assertEqual(len(report.findings), 0)
        self.assertEqual(len(report.recommendations), 0)


class TestRepeatedBlockedDecisions(unittest.TestCase):
    def test_repeated_blocked_decisions_create_expected_findings(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput(
            decision_records=[
                {"module": "nq_risk", "strategy_id": "s1", "blocked": True},
                {"module": "nq_risk", "strategy_id": "s1", "blocked": True},
                {"module": "nq_risk", "strategy_id": "s1", "blocked": True},
            ],
            execution_records=[],
            strategy_health=[],
        )
        report = engine.run_audit(input_data)
        blocked = [f for f in report.findings if f.category == "repeated_blocked_decisions"]
        self.assertGreaterEqual(len(blocked), 1)
        self.assertIn("s1", blocked[0].description or "")
        self.assertEqual(blocked[0].related_strategy_id, "s1")
        self.assertIn(blocked[0].severity, ("warning", "critical"))


class TestRepeatedThrottling(unittest.TestCase):
    def test_repeated_throttling_creates_expected_findings(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput(
            decision_records=[
                {"module": "nq_guardrails", "strategy_id": "s2", "throttled": True},
                {"module": "nq_guardrails", "strategy_id": "s2", "throttled": True},
                {"module": "nq_guardrails", "strategy_id": "s2", "throttled": True},
            ],
            execution_records=[],
            strategy_health=[],
        )
        report = engine.run_audit(input_data)
        throttle = [f for f in report.findings if f.category == "excessive_throttling"]
        self.assertGreaterEqual(len(throttle), 1)
        self.assertEqual(throttle[0].related_strategy_id, "s2")


class TestRepeatedPromotionRejections(unittest.TestCase):
    def test_repeated_promotion_rejections_create_expected_findings(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput(
            decision_records=[
                {"strategy_id": "s3", "promotion_rejected": True, "module": "nq_promotion"},
                {"strategy_id": "s3", "promotion_rejected": True, "module": "nq_promotion"},
                {"strategy_id": "s3", "outcome": "rejected", "category": "promotion", "module": "nq_promotion"},
            ],
            execution_records=[],
            strategy_health=[],
        )
        report = engine.run_audit(input_data)
        promo = [f for f in report.findings if f.category == "repeated_promotion_rejections"]
        self.assertGreaterEqual(len(promo), 1)
        self.assertEqual(promo[0].related_strategy_id, "s3")
        self.assertEqual(promo[0].related_module, "nq_promotion")


class TestDegradedStrategyHealth(unittest.TestCase):
    def test_degraded_strategy_health_creates_expected_findings(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput(
            decision_records=[],
            execution_records=[],
            strategy_health=[
                {"strategy_id": "s4", "health": "degraded", "status": "active"},
            ],
        )
        report = engine.run_audit(input_data)
        degraded = [f for f in report.findings if f.category == "degraded_strategy_detected"]
        self.assertGreaterEqual(len(degraded), 1)
        self.assertEqual(degraded[0].related_strategy_id, "s4")
        self.assertEqual(degraded[0].severity, "warning")


class TestInactiveStrategyHealth(unittest.TestCase):
    def test_inactive_strategy_health_creates_expected_findings(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput(
            decision_records=[],
            execution_records=[],
            strategy_health=[
                {"strategy_id": "s5", "status": "inactive"},
            ],
        )
        report = engine.run_audit(input_data)
        inactive = [f for f in report.findings if f.category == "inactive_strategy_detected"]
        self.assertGreaterEqual(len(inactive), 1)
        self.assertEqual(inactive[0].related_strategy_id, "s5")
        self.assertEqual(inactive[0].severity, "info")


class TestExecutionFailurePatterns(unittest.TestCase):
    def test_execution_failure_patterns_create_expected_findings(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput(
            decision_records=[],
            execution_records=[
                {"strategy_id": "s6", "module": "nq_exec", "success": False},
                {"strategy_id": "s6", "module": "nq_exec", "success": False},
                {"strategy_id": "s6", "module": "nq_exec", "failed": True},
            ],
            strategy_health=[],
        )
        report = engine.run_audit(input_data)
        exec_fail = [f for f in report.findings if f.category == "execution_failure_pattern"]
        self.assertGreaterEqual(len(exec_fail), 1)
        self.assertIn("s6", exec_fail[0].description)


class TestOptionalMissingSections(unittest.TestCase):
    def test_optional_missing_sections_do_not_crash_audit(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput()
        report = engine.run_audit(input_data)
        self.assertEqual(report.summary.total_findings, 0)

    def test_empty_lists_ok(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput(
            events=[],
            decision_records=[],
            execution_records=[],
            strategy_health=[],
            control_summary=None,
            experiment_summary=None,
            registry_records=None,
        )
        report = engine.run_audit(input_data)
        self.assertIsNotNone(report.audit_id)


class TestMalformedCriticalInput(unittest.TestCase):
    def test_malformed_decision_records_fails_closed(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput(
            decision_records="not-a-list",  # type: ignore[arg-type]
            execution_records=[],
            strategy_health=[],
        )
        with self.assertRaises(AuditError):
            engine.run_audit(input_data)

    def test_malformed_registry_records_fails_closed(self) -> None:
        from nq_audit.analyzers import run_all_analyzers
        input_data = AuditInput(
            decision_records=[],
            execution_records=[],
            strategy_health=[],
            registry_records="not-a-list",  # type: ignore[arg-type]
        )
        with self.assertRaises(AuditError):
            run_all_analyzers(input_data)


class TestFindingsSeverityCounts(unittest.TestCase):
    def test_findings_severity_counts_are_correct(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput(
            strategy_health=[
                {"strategy_id": "sx", "health": "degraded"},
                {"strategy_id": "sy", "status": "inactive"},
            ],
            decision_records=[
                {"strategy_id": "s1", "blocked": True},
                {"strategy_id": "s1", "blocked": True},
            ],
            execution_records=[],
        )
        report = engine.run_audit(input_data)
        self.assertEqual(
            report.summary.info_count + report.summary.warning_count + report.summary.critical_count,
            report.summary.total_findings,
        )
        self.assertEqual(len(report.findings), report.summary.total_findings)


class TestRecommendationsDeterministic(unittest.TestCase):
    def test_recommendations_derived_deterministically(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput(
            decision_records=[
                {"strategy_id": "s1", "blocked": True},
                {"strategy_id": "s1", "blocked": True},
            ],
            execution_records=[],
            strategy_health=[],
        )
        report = engine.run_audit(input_data)
        self.assertGreater(len(report.findings), 0)
        for rec in report.recommendations:
            self.assertIn("s1", rec or "")


class TestRepeatedInputsSameStructure(unittest.TestCase):
    def test_repeated_same_inputs_yield_same_report_structure(self) -> None:
        ticks = [100.0, 101.0]
        _, clock = make_clock(ticks)
        engine = AuditEngine(clock=clock)
        input_data = AuditInput(
            decision_records=[
                {"strategy_id": "s1", "blocked": True},
                {"strategy_id": "s1", "blocked": True},
            ],
            execution_records=[],
            strategy_health=[],
        )
        r1 = engine.run_audit(input_data, generated_at=100.0)
        r2 = engine.run_audit(input_data, generated_at=100.0)
        self.assertEqual(len(r1.findings), len(r2.findings))
        self.assertEqual(r1.summary.total_findings, r2.summary.total_findings)
        self.assertEqual([f.category for f in r1.findings], [f.category for f in r2.findings])


class TestAuditIdsDeterministic(unittest.TestCase):
    def test_audit_ids_deterministic(self) -> None:
        engine = AuditEngine()
        r1 = engine.run_audit(AuditInput(), audit_id="custom-1")
        r2 = engine.run_audit(AuditInput())
        r3 = engine.run_audit(AuditInput())
        self.assertEqual(r1.audit_id, "custom-1")
        self.assertEqual(r2.audit_id, "audit-2")
        self.assertEqual(r3.audit_id, "audit-3")


class TestLifecycleConsistency(unittest.TestCase):
    def test_lifecycle_inconsistency_creates_finding(self) -> None:
        engine = AuditEngine()
        input_data = AuditInput(
            decision_records=[],
            execution_records=[],
            strategy_health=[],
            registry_records=[
                {"strategy_id": "s7", "executable": False, "lifecycle_state": "promoted"},
            ],
        )
        report = engine.run_audit(input_data)
        life = [f for f in report.findings if f.category == "lifecycle_inconsistency_detected"]
        self.assertGreaterEqual(len(life), 1)
        self.assertEqual(life[0].related_strategy_id, "s7")


class TestNoHiddenDependencies(unittest.TestCase):
    def test_no_hidden_external_services(self) -> None:
        # Unit test only; no network, no files, no threads
        engine = AuditEngine()
        report = engine.run_audit(AuditInput())
        self.assertIsNotNone(report.audit_id)
        self.assertIsInstance(report.findings, list)
