# NEBULA-QUANT v1 | nq_sre tests

from __future__ import annotations

import unittest
from typing import Any

from nq_sre import (
    CATEGORY_COMPONENT_DEGRADED,
    CATEGORY_COMPONENT_UNAVAILABLE,
    CATEGORY_EXCESSIVE_ERRORS,
    CATEGORY_MISSING_HEARTBEAT,
    CATEGORY_QUEUE_BACKLOG,
    CATEGORY_RELEASE_HEALTH_RISK,
    CATEGORY_REPEATED_FAILURES,
    CATEGORY_STALE_DATA,
    CATEGORY_STALE_SIGNAL,
    SREEngine,
    SREError,
    SREIncident,
    derive_overall_status,
    evaluate_single_input,
)


def fixed_clock(ts: float = 1000.0):
    def clock() -> float:
        return ts
    return clock


def comp(component_name: str, **kwargs: Any) -> dict[str, Any]:
    d: dict[str, Any] = {"component_name": component_name, **kwargs}
    return d


# --- 1. Healthy component evaluation ---
class TestHealthyComponent(unittest.TestCase):
    def test_healthy_component_no_incidents(self) -> None:
        inp = comp("api", healthy=True, status="healthy")
        incidents, evidence = evaluate_single_input(inp, "inc-0", "ev-0")
        self.assertEqual(len(incidents), 0)
        self.assertGreaterEqual(len(evidence), 1)
        self.assertEqual(evidence[0].category, "component")

    def test_engine_healthy_single_input(self) -> None:
        engine = SREEngine(clock=fixed_clock())
        report = engine.evaluate_reliability([comp("svc")])
        self.assertEqual(report.overall_status, "healthy")
        self.assertEqual(len(report.incidents), 0)
        self.assertEqual(report.summary.healthy_components, 1)
        self.assertEqual(report.summary.degraded_components, 0)
        self.assertEqual(report.summary.unavailable_components, 0)


# --- 2. Degraded component evaluation ---
class TestDegradedComponent(unittest.TestCase):
    def test_degraded_flag_produces_incident(self) -> None:
        inp = comp("worker", degraded=True)
        incidents, _ = evaluate_single_input(inp, "i", "e")
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].category, CATEGORY_COMPONENT_DEGRADED)
        self.assertEqual(incidents[0].severity, "warning")

    def test_degraded_status_produces_incident(self) -> None:
        inp = comp("db", status="degraded")
        incidents, _ = evaluate_single_input(inp, "i", "e")
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].category, CATEGORY_COMPONENT_DEGRADED)


# --- 3. Unavailable component evaluation ---
class TestUnavailableComponent(unittest.TestCase):
    def test_unavailable_flag_produces_critical_incident(self) -> None:
        inp = comp("cache", unavailable=True)
        incidents, _ = evaluate_single_input(inp, "i", "e")
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].category, CATEGORY_COMPONENT_UNAVAILABLE)
        self.assertEqual(incidents[0].severity, "critical")

    def test_status_down_produces_unavailable(self) -> None:
        inp = comp("broker", status="down")
        incidents, _ = evaluate_single_input(inp, "i", "e")
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].category, CATEGORY_COMPONENT_UNAVAILABLE)


# --- 4. Stale signal detection ---
class TestStaleSignal(unittest.TestCase):
    def test_stale_true_produces_incident(self) -> None:
        inp = comp("feeder", stale=True)
        incidents, _ = evaluate_single_input(inp, "i", "e")
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].category, CATEGORY_STALE_SIGNAL)
        self.assertEqual(incidents[0].severity, "warning")


# --- 5. Missing heartbeat detection ---
class TestMissingHeartbeat(unittest.TestCase):
    def test_missing_heartbeat_produces_critical(self) -> None:
        inp = comp("agent", missing_heartbeat=True)
        incidents, _ = evaluate_single_input(inp, "i", "e")
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].category, CATEGORY_MISSING_HEARTBEAT)
        self.assertEqual(incidents[0].severity, "critical")


# --- 6. Excessive errors detection ---
class TestExcessiveErrors(unittest.TestCase):
    def test_error_count_critical_threshold(self) -> None:
        inp = comp("exec", error_count=100)
        incidents, _ = evaluate_single_input(inp, "i", "e")
        critical = [i for i in incidents if i.category == CATEGORY_EXCESSIVE_ERRORS and i.severity == "critical"]
        self.assertGreaterEqual(len(critical), 1)

    def test_error_count_warning_threshold(self) -> None:
        inp = comp("exec", error_count=10)
        incidents, _ = evaluate_single_input(inp, "i", "e")
        warning = [i for i in incidents if i.category == CATEGORY_EXCESSIVE_ERRORS and i.severity == "warning"]
        self.assertGreaterEqual(len(warning), 1)


# --- 7. Repeated failures detection ---
class TestRepeatedFailures(unittest.TestCase):
    def test_failed_jobs_produces_incident(self) -> None:
        inp = comp("scheduler", failed_jobs=2)
        incidents, _ = evaluate_single_input(inp, "i", "e")
        self.assertGreaterEqual(len(incidents), 1)
        self.assertTrue(any(i.category == CATEGORY_REPEATED_FAILURES for i in incidents))

    def test_repeated_failures_threshold(self) -> None:
        inp = comp("job", repeated_failures=3)
        incidents, _ = evaluate_single_input(inp, "i", "e")
        self.assertGreaterEqual(len(incidents), 1)
        self.assertTrue(any(i.category == CATEGORY_REPEATED_FAILURES for i in incidents))


# --- 8. Queue backlog detection ---
class TestQueueBacklog(unittest.TestCase):
    def test_queue_backlog_warning(self) -> None:
        inp = comp("queue", queue_backlog=15)
        incidents, _ = evaluate_single_input(inp, "i", "e")
        self.assertGreaterEqual(len(incidents), 1)
        self.assertTrue(any(i.category == CATEGORY_QUEUE_BACKLOG for i in incidents))

    def test_queue_backlog_critical(self) -> None:
        inp = comp("queue", queue_backlog=100)
        incidents, _ = evaluate_single_input(inp, "i", "e")
        critical = [i for i in incidents if i.category == CATEGORY_QUEUE_BACKLOG and i.severity == "critical"]
        self.assertGreaterEqual(len(critical), 1)


# --- 9. Release-linked health risk ---
class TestReleaseHealthRisk(unittest.TestCase):
    def test_release_blocked_with_degraded_produces_info_incident(self) -> None:
        inp = comp("gate", release_status="blocked", degraded=True)
        incidents, _ = evaluate_single_input(inp, "i", "e")
        info_release = [i for i in incidents if i.category == CATEGORY_RELEASE_HEALTH_RISK and i.severity == "info"]
        self.assertGreaterEqual(len(info_release), 1)


# --- 10. Overall status derivation ---
class TestOverallStatus(unittest.TestCase):
    def test_no_inputs_unknown(self) -> None:
        status = derive_overall_status([], 0)
        self.assertEqual(status, "unknown")

    def test_no_incidents_healthy(self) -> None:
        # One input evaluated, zero incidents → healthy
        status = derive_overall_status([], 1)
        self.assertEqual(status, "healthy")

    def test_critical_unavailable_makes_overall_unavailable(self) -> None:
        inc = SREIncident(
            incident_id="x",
            component_name="y",
            category=CATEGORY_COMPONENT_UNAVAILABLE,
            severity="critical",
            title="t",
            description="d",
            evidence_ids=[],
            rationale="r",
        )
        status = derive_overall_status([inc], 1)
        self.assertEqual(status, "unavailable")

    def test_warning_makes_overall_degraded(self) -> None:
        inc = SREIncident(
            incident_id="x",
            component_name="y",
            category=CATEGORY_COMPONENT_DEGRADED,
            severity="warning",
            title="t",
            description="d",
            evidence_ids=[],
            rationale="r",
        )
        status = derive_overall_status([inc], 1)
        self.assertEqual(status, "degraded")


# --- 11. Malformed critical input fails closed ---
class TestMalformedInputFailsClosed(unittest.TestCase):
    def test_non_list_raises_sre_error(self) -> None:
        engine = SREEngine(clock=fixed_clock())
        with self.assertRaises(SREError):
            engine.evaluate_reliability({"component_name": "x"})

    def test_none_item_in_list_raises_sre_error(self) -> None:
        engine = SREEngine(clock=fixed_clock())
        with self.assertRaises(SREError):
            engine.evaluate_reliability([comp("a"), None, comp("c")])


# --- 12. Empty input returns valid empty report ---
class TestEmptyInputReturnsValidReport(unittest.TestCase):
    def test_none_input_empty_report(self) -> None:
        engine = SREEngine(clock=fixed_clock())
        report = engine.evaluate_reliability(None)
        self.assertEqual(report.overall_status, "unknown")
        self.assertEqual(len(report.incidents), 0)
        self.assertEqual(report.summary.total_inputs, 0)
        self.assertIn("report", report.report_id.lower())

    def test_empty_list_empty_report(self) -> None:
        engine = SREEngine(clock=fixed_clock())
        report = engine.evaluate_reliability([])
        self.assertEqual(report.overall_status, "unknown")
        self.assertEqual(len(report.incidents), 0)


# --- 13. Same input → same report output ---
class TestDeterminismSameInput(unittest.TestCase):
    def test_same_input_same_incidents_and_order(self) -> None:
        inp = [comp("a", degraded=True), comp("b", stale=True)]
        engine = SREEngine(clock=fixed_clock())
        r1 = engine.evaluate_reliability(inp)
        r2 = engine.evaluate_reliability(inp)
        self.assertEqual(len(r1.incidents), len(r2.incidents))
        for a, b in zip(r1.incidents, r2.incidents):
            self.assertEqual(a.incident_id, b.incident_id)
            self.assertEqual(a.category, b.category)
            self.assertEqual(a.severity, b.severity)
        self.assertEqual(r1.overall_status, r2.overall_status)


# --- 14–16. Deterministic IDs ---
class TestDeterministicIds(unittest.TestCase):
    def test_report_id_deterministic_for_same_inputs(self) -> None:
        inp = [comp("x")]
        engine = SREEngine(clock=fixed_clock())
        r1 = engine.evaluate_reliability(inp)
        r2 = engine.evaluate_reliability(inp)
        self.assertEqual(r1.report_id, r2.report_id)
        self.assertTrue(r1.report_id.startswith("sre-report-"))

    def test_incident_ids_deterministic(self) -> None:
        inp = [comp("c", degraded=True)]
        incidents1, _ = evaluate_single_input(inp[0], "inc-0", "ev-0")
        incidents2, _ = evaluate_single_input(inp[0], "inc-0", "ev-0")
        self.assertEqual([i.incident_id for i in incidents1], [i.incident_id for i in incidents2])

    def test_evidence_ids_deterministic(self) -> None:
        inp = comp("c", degraded=True)
        _, ev1 = evaluate_single_input(inp, "i", "e")
        _, ev2 = evaluate_single_input(inp, "i", "e")
        self.assertEqual([e.evidence_id for e in ev1], [e.evidence_id for e in ev2])


# --- 17. Summary counts correct ---
class TestSummaryCounts(unittest.TestCase):
    def test_summary_counts_match_incidents(self) -> None:
        inp = [comp("a", degraded=True), comp("b", error_count=50)]
        engine = SREEngine(clock=fixed_clock())
        report = engine.evaluate_reliability(inp)
        s = report.summary
        self.assertEqual(s.total_inputs, 2)
        self.assertEqual(s.total_incidents, len(report.incidents))
        self.assertEqual(s.info_count + s.warning_count + s.critical_count, s.total_incidents)
        self.assertEqual(s.healthy_components + s.degraded_components + s.unavailable_components, 2)


# --- 18. No hidden external dependencies ---
class TestNoExternalDependencies(unittest.TestCase):
    def test_evaluate_single_input_pure(self) -> None:
        # No network, no filesystem, no env — just in-memory input
        inp = comp("test")
        incidents, evidence = evaluate_single_input(inp, "i", "e")
        self.assertIsInstance(incidents, list)
        self.assertIsInstance(evidence, list)

    def test_engine_evaluate_reliability_pure(self) -> None:
        engine = SREEngine(clock=fixed_clock())
        report = engine.evaluate_reliability([comp("x")])
        self.assertIsNotNone(report.report_id)
        self.assertIsNotNone(report.summary)
        # No side effects; we only assert we got a valid report
        self.assertIn(report.overall_status, ("healthy", "degraded", "unavailable", "unknown"))


# --- Stale data category ---
class TestStaleData(unittest.TestCase):
    def test_stale_data_true_produces_incident(self) -> None:
        inp = comp("ds", stale_data=True)
        incidents, _ = evaluate_single_input(inp, "i", "e")
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].category, CATEGORY_STALE_DATA)
        self.assertEqual(incidents[0].severity, "warning")
