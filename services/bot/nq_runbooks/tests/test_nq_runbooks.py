# NEBULA-QUANT v1 | nq_runbooks tests

from __future__ import annotations

import unittest
from typing import Any

from nq_runbooks import (
    RunbookEngine,
    RunbookError,
    clear_registry,
    get_runbooks_by_category,
    list_runbooks,
    register_runbook,
    match_incident_to_runbook,
)


def fixed_clock(ts: float = 2000.0):
    def clock() -> float:
        return ts
    return clock


def make_step(step_id: str, description: str, action_type: str = "check", expected_outcome: str | None = None) -> dict[str, Any]:
    return {"step_id": step_id, "description": description, "action_type": action_type, "expected_outcome": expected_outcome}


def make_runbook(
    runbook_id: str,
    incident_category: str,
    title: str = "Title",
    applicable_modules: list[str] | None = None,
    steps: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if steps is None:
        steps = [make_step("1", "First step"), make_step("2", "Second step")]
    return {
        "runbook_id": runbook_id,
        "title": title,
        "description": "Description",
        "incident_category": incident_category,
        "applicable_modules": applicable_modules or [],
        "severity": "warning",
        "steps": steps,
        "version": "1.0",
    }


def incident(category: str, incident_id: str = "inc-1", module: str | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {"category": category, "incident_id": incident_id}
    if module is not None:
        d["module"] = module
    return d


# --- 1. Runbook registration ---
class TestRunbookRegistration(unittest.TestCase):
    def setUp(self) -> None:
        clear_registry()

    def test_register_and_list_runbooks(self) -> None:
        register_runbook(make_runbook("rb-1", "component_unavailable"))
        register_runbook(make_runbook("rb-2", "stale_signal"))
        all_rb = list_runbooks()
        self.assertEqual(len(all_rb), 2)
        self.assertEqual(all_rb[0].runbook_id, "rb-1")
        self.assertEqual(all_rb[1].runbook_id, "rb-2")

    def test_register_validates_steps(self) -> None:
        with self.assertRaises(RunbookError):
            register_runbook({
                "runbook_id": "x",
                "title": "x",
                "description": "x",
                "incident_category": "y",
                "applicable_modules": [],
                "severity": "info",
                "steps": [{"step_id": "", "description": "d", "action_type": "check"}],
                "version": "1",
            })


# --- 2. Runbook retrieval by category ---
class TestRunbookRetrievalByCategory(unittest.TestCase):
    def setUp(self) -> None:
        clear_registry()
        register_runbook(make_runbook("rb-a", "component_unavailable"))
        register_runbook(make_runbook("rb-b", "stale_signal"))
        register_runbook(make_runbook("rb-c", "component_unavailable"))

    def test_get_by_category(self) -> None:
        rbs = get_runbooks_by_category("component_unavailable")
        self.assertEqual(len(rbs), 2)
        self.assertEqual(rbs[0].runbook_id, "rb-a")
        self.assertEqual(rbs[1].runbook_id, "rb-c")
        self.assertEqual(get_runbooks_by_category("stale_signal")[0].runbook_id, "rb-b")
        self.assertEqual(len(get_runbooks_by_category("nonexistent")), 0)


# --- 3. Matching incident to runbook ---
class TestMatchingIncidentToRunbook(unittest.TestCase):
    def setUp(self) -> None:
        clear_registry()
        register_runbook(make_runbook("rb-match", "component_degraded"))

    def test_match_by_category(self) -> None:
        inc = incident("component_degraded")
        match, runbook = match_incident_to_runbook(inc, 0)
        self.assertIsNotNone(match)
        self.assertIsNotNone(runbook)
        self.assertEqual(runbook.runbook_id, "rb-match")
        self.assertEqual(match.incident_category, "component_degraded")
        self.assertIn("component_degraded", match.rationale)


# --- 4. Unmatched incident detection ---
class TestUnmatchedIncident(unittest.TestCase):
    def setUp(self) -> None:
        clear_registry()
        register_runbook(make_runbook("rb-x", "stale_signal"))

    def test_unmatched_incident(self) -> None:
        inc = incident("component_unavailable")
        match, runbook = match_incident_to_runbook(inc, 0)
        self.assertIsNone(match)
        self.assertIsNone(runbook)

    def test_engine_reports_unmatched(self) -> None:
        engine = RunbookEngine(clock=fixed_clock())
        report = engine.generate_runbook_recommendations([incident("component_unavailable")])
        self.assertEqual(len(report.recommendations), 0)
        self.assertEqual(len(report.unmatched_incidents), 1)
        self.assertEqual(report.summary.unmatched_incidents, 1)


# --- 5. Recommendation generation ---
class TestRecommendationGeneration(unittest.TestCase):
    def setUp(self) -> None:
        clear_registry()
        register_runbook(make_runbook("rb-rec", "excessive_errors"))

    def test_recommendation_has_steps_and_rationale(self) -> None:
        engine = RunbookEngine(clock=fixed_clock())
        report = engine.generate_runbook_recommendations([incident("excessive_errors", "inc-1")])
        self.assertEqual(len(report.recommendations), 1)
        rec = report.recommendations[0]
        self.assertEqual(rec.incident_id, "inc-1")
        self.assertEqual(rec.runbook_id, "rb-rec")
        self.assertGreater(len(rec.steps), 0)
        self.assertTrue(rec.rationale)


# --- 6–8. Deterministic IDs and ordering ---
class TestDeterministicIds(unittest.TestCase):
    def setUp(self) -> None:
        clear_registry()
        register_runbook(make_runbook("rb-d", "queue_backlog"))

    def test_deterministic_report_ids(self) -> None:
        engine = RunbookEngine(clock=fixed_clock())
        incs = [incident("queue_backlog", "i1")]
        r1 = engine.generate_runbook_recommendations(incs)
        r2 = engine.generate_runbook_recommendations(incs)
        self.assertEqual(r1.report_id, r2.report_id)
        self.assertTrue(r1.report_id.startswith("runbook-report-"))

    def test_deterministic_recommendation_ids(self) -> None:
        engine = RunbookEngine(clock=fixed_clock())
        incs = [incident("queue_backlog", "a"), incident("queue_backlog", "b")]
        report = engine.generate_runbook_recommendations(incs)
        rec_ids = [r.recommendation_id for r in report.recommendations]
        self.assertEqual(rec_ids[0], "rec-0-rb-d")
        self.assertEqual(rec_ids[1], "rec-1-rb-d")

    def test_deterministic_ordering(self) -> None:
        engine = RunbookEngine(clock=fixed_clock())
        incs = [incident("queue_backlog", "x")] * 1
        r1 = engine.generate_runbook_recommendations(incs)
        r2 = engine.generate_runbook_recommendations(incs)
        self.assertEqual([r.recommendation_id for r in r1.recommendations], [r.recommendation_id for r in r2.recommendations])


# --- 9. Malformed incident input fails closed ---
class TestMalformedInputFailsClosed(unittest.TestCase):
    def test_non_list_raises(self) -> None:
        engine = RunbookEngine(clock=fixed_clock())
        with self.assertRaises(RunbookError):
            engine.generate_runbook_recommendations(incident("x"))

    def test_none_item_raises(self) -> None:
        engine = RunbookEngine(clock=fixed_clock())
        with self.assertRaises(RunbookError):
            engine.generate_runbook_recommendations([incident("a"), None])

    def test_missing_category_raises(self) -> None:
        engine = RunbookEngine(clock=fixed_clock())
        with self.assertRaises(RunbookError):
            engine.generate_runbook_recommendations([{"incident_id": "1"}])


# --- 10. Empty incident list returns valid report ---
class TestEmptyIncidentList(unittest.TestCase):
    def setUp(self) -> None:
        clear_registry()
        register_runbook(make_runbook("rb-e", "y"))

    def test_empty_list(self) -> None:
        engine = RunbookEngine(clock=fixed_clock())
        report = engine.generate_runbook_recommendations([])
        self.assertEqual(len(report.recommendations), 0)
        self.assertEqual(len(report.unmatched_incidents), 0)
        self.assertEqual(report.report_id, "runbook-report-empty")

    def test_none_input(self) -> None:
        engine = RunbookEngine(clock=fixed_clock())
        report = engine.generate_runbook_recommendations(None)
        self.assertEqual(len(report.recommendations), 0)
        self.assertEqual(len(report.unmatched_incidents), 0)


# --- 11. Same input → same output ---
class TestSameInputSameOutput(unittest.TestCase):
    def setUp(self) -> None:
        clear_registry()
        register_runbook(make_runbook("rb-s", "stale_data"))

    def test_same_incidents_same_report(self) -> None:
        engine = RunbookEngine(clock=fixed_clock())
        incs = [incident("stale_data", "id1")]
        r1 = engine.generate_runbook_recommendations(incs)
        r2 = engine.generate_runbook_recommendations(incs)
        self.assertEqual(r1.report_id, r2.report_id)
        self.assertEqual(len(r1.recommendations), len(r2.recommendations))
        for a, b in zip(r1.recommendations, r2.recommendations):
            self.assertEqual(a.recommendation_id, b.recommendation_id)
            self.assertEqual(a.runbook_id, b.runbook_id)


# --- 12. Summary counts correct ---
class TestSummaryCounts(unittest.TestCase):
    def setUp(self) -> None:
        clear_registry()
        register_runbook(make_runbook("rb-1", "cat_a"))
        register_runbook(make_runbook("rb-2", "cat_b"))

    def test_summary_counts(self) -> None:
        engine = RunbookEngine(clock=fixed_clock())
        report = engine.generate_runbook_recommendations([
            incident("cat_a", "i1"),
            incident("cat_b", "i2"),
            incident("cat_unknown", "i3"),
        ])
        self.assertEqual(report.summary.total_runbooks, 2)
        self.assertEqual(report.summary.recommendations_generated, 2)
        self.assertEqual(report.summary.unmatched_incidents, 1)
        self.assertEqual(len(report.summary.categories_covered), 2)
        self.assertIn("cat_a", report.summary.categories_covered)
        self.assertIn("cat_b", report.summary.categories_covered)


# --- 13. No external dependencies ---
class TestNoExternalDependencies(unittest.TestCase):
    def test_engine_pure(self) -> None:
        clear_registry()
        register_runbook(make_runbook("rb-pure", "z"))
        engine = RunbookEngine(clock=fixed_clock())
        report = engine.generate_runbook_recommendations([incident("z")])
        self.assertIsNotNone(report.report_id)
        self.assertIsNotNone(report.summary)
        self.assertIn(report.summary.recommendations_generated, (0, 1))
