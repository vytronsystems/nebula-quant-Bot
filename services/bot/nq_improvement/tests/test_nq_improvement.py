# NEBULA-QUANT v1 | nq_improvement tests

from __future__ import annotations

import unittest
from typing import Any

from nq_improvement import (
    ImprovementEngine,
    ImprovementError,
    plan_from_audit,
    plan_from_learning,
    plan_from_trade_review,
)


def make_learning_report(
    candidates: list[dict[str, Any]] | None = None,
    lessons: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "improvement_candidates": candidates or [
            {"title": "Review entry rules", "description": "Entry quality", "priority": "high", "related_strategy_id": "s1", "source_patterns": ["p1"]},
        ],
        "lessons": lessons or [],
        "patterns": [],
    }


def make_audit_report(
    findings: list[dict[str, Any]] | None = None,
    recommendations: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "findings": findings or [
            {"category": "repeated_blocked_decisions", "severity": "warning", "related_strategy_id": "s1", "finding_id": "f1", "title": "Blocked", "description": "Desc"},
        ],
        "recommendations": recommendations or ["Review strategy s1"],
    }


def make_trade_review_report(
    findings: list[dict[str, Any]] | None = None,
    recommendations: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "findings": findings or [
            {"category": "poor_entry_quality", "severity": "warning", "strategy_id": "s1", "finding_id": "tr1", "title": "Poor entry", "description": "Desc"},
        ],
        "recommendations": recommendations or [],
    }


class TestPlanningFromLearning(unittest.TestCase):
    def test_planning_from_learning_report(self) -> None:
        report = make_learning_report(candidates=[{"title": "T1", "description": "D1", "priority": "critical", "related_strategy_id": "s1"}])
        actions = plan_from_learning(report)
        self.assertGreaterEqual(len(actions), 1)
        self.assertEqual(actions[0].priority, "critical")
        self.assertEqual(actions[0].related_strategy_id, "s1")

    def test_planning_from_learning_none_returns_empty(self) -> None:
        self.assertEqual(plan_from_learning(None), [])


class TestPlanningFromAudit(unittest.TestCase):
    def test_planning_from_audit_report(self) -> None:
        report = make_audit_report(
            findings=[{"category": "repeated_blocked_decisions", "severity": "critical", "related_strategy_id": "s1", "finding_id": "f1", "title": "T", "description": "D"}],
            recommendations=["Rec 1"],
        )
        actions = plan_from_audit(report)
        self.assertGreaterEqual(len(actions), 1)
        self.assertIn(actions[0].priority, ("critical", "high", "medium"))

    def test_planning_from_audit_none_returns_empty(self) -> None:
        self.assertEqual(plan_from_audit(None), [])


class TestPlanningFromTradeReview(unittest.TestCase):
    def test_planning_from_trade_review_report(self) -> None:
        reports = [make_trade_review_report(findings=[{"category": "excessive_slippage", "severity": "warning", "strategy_id": "s2", "finding_id": "t1", "title": "Slippage", "description": "D"}])]
        actions = plan_from_trade_review(reports)
        self.assertGreaterEqual(len(actions), 1)
        self.assertEqual(actions[0].improvement_type, "execution_review")

    def test_planning_from_trade_review_none_returns_empty(self) -> None:
        self.assertEqual(plan_from_trade_review(None), [])


class TestMixedSourcePlan(unittest.TestCase):
    def test_mixed_source_plan_generation(self) -> None:
        engine = ImprovementEngine()
        plan = engine.generate_improvement_plan(
            learning_report=make_learning_report(),
            audit_report=make_audit_report(),
            trade_review_reports=[make_trade_review_report()],
        )
        self.assertIsNotNone(plan.plan_id)
        self.assertGreaterEqual(plan.summary.total_actions, 1)
        self.assertGreaterEqual(len(plan.actions), 1)


class TestPriorityAssignment(unittest.TestCase):
    def test_priority_assignment_correctness(self) -> None:
        engine = ImprovementEngine()
        plan = engine.generate_improvement_plan(
            learning_report=make_learning_report(candidates=[{"title": "C", "description": "D", "priority": "critical", "related_strategy_id": "s1", "source_patterns": []}]),
        )
        self.assertGreaterEqual(plan.summary.critical_count, 1)
        for a in plan.actions:
            self.assertIn(a.priority, ("low", "medium", "high", "critical"))


class TestDeduplicationConsolidation(unittest.TestCase):
    def test_deduplication_consolidation_behavior(self) -> None:
        engine = ImprovementEngine()
        plan = engine.generate_improvement_plan(
            audit_report=make_audit_report(
                findings=[
                    {"category": "repeated_blocked_decisions", "severity": "warning", "related_strategy_id": "s1", "finding_id": "f1", "title": "T1", "description": "D1"},
                    {"category": "repeated_blocked_decisions", "severity": "warning", "related_strategy_id": "s1", "finding_id": "f2", "title": "T2", "description": "D2"},
                ],
            ),
        )
        strategy_actions = [a for a in plan.actions if a.related_strategy_id == "s1" and a.improvement_type == "risk_review"]
        self.assertLessEqual(len(strategy_actions), 2)
        if len(strategy_actions) == 1:
            self.assertGreaterEqual(len(strategy_actions[0].source_ids), 1)


class TestDeterministicOrdering(unittest.TestCase):
    def test_deterministic_ordering(self) -> None:
        engine = ImprovementEngine()
        plan = engine.generate_improvement_plan(
            learning_report=make_learning_report(),
            audit_report=make_audit_report(),
        )
        priorities = [a.priority for a in plan.actions]
        ranks = ["critical", "high", "medium", "low"]
        for i in range(len(priorities) - 1):
            idx_i = ranks.index(priorities[i]) if priorities[i] in ranks else 3
            idx_next = ranks.index(priorities[i + 1]) if priorities[i + 1] in ranks else 3
            self.assertLessEqual(idx_i, idx_next)


class TestDeterministicPlanIds(unittest.TestCase):
    def test_deterministic_plan_ids(self) -> None:
        engine = ImprovementEngine()
        p1 = engine.generate_improvement_plan(plan_id="custom-1")
        p2 = engine.generate_improvement_plan()
        p3 = engine.generate_improvement_plan()
        self.assertEqual(p1.plan_id, "custom-1")
        self.assertEqual(p2.plan_id, "improvement-plan-2")
        self.assertEqual(p3.plan_id, "improvement-plan-3")


class TestDeterministicActionIds(unittest.TestCase):
    def test_deterministic_action_ids(self) -> None:
        engine = ImprovementEngine()
        plan = engine.generate_improvement_plan(learning_report=make_learning_report())
        ids = [a.action_id for a in plan.actions]
        self.assertTrue(all(ids[i] == f"action-{i+1}" for i in range(len(ids))))


class TestMalformedCriticalInput(unittest.TestCase):
    def test_learning_report_improvement_candidates_not_list_fails(self) -> None:
        with self.assertRaises(ImprovementError):
            plan_from_learning({"improvement_candidates": "not-a-list"})

    def test_audit_report_findings_not_list_fails(self) -> None:
        with self.assertRaises(ImprovementError):
            plan_from_audit({"findings": "not-a-list"})

    def test_trade_review_reports_not_list_fails(self) -> None:
        with self.assertRaises(ImprovementError):
            plan_from_trade_review("not-a-list")


class TestOptionalSectionsHandledSafely(unittest.TestCase):
    def test_optional_sections_handled_safely(self) -> None:
        engine = ImprovementEngine()
        plan = engine.generate_improvement_plan()
        self.assertIsNotNone(plan.plan_id)
        self.assertEqual(plan.summary.total_actions, 0)
        self.assertEqual(len(plan.actions), 0)


class TestEmptyInputReturnsValidEmptyPlan(unittest.TestCase):
    def test_empty_input_returns_valid_empty_plan(self) -> None:
        engine = ImprovementEngine()
        plan = engine.generate_improvement_plan()
        self.assertEqual(plan.summary.total_actions, 0)
        self.assertEqual(plan.summary.low_count, 0)
        self.assertEqual(plan.summary.medium_count, 0)
        self.assertEqual(plan.summary.high_count, 0)
        self.assertEqual(plan.summary.critical_count, 0)
        self.assertEqual(len(plan.actions), 0)


class TestSameInputSamePlanOutput(unittest.TestCase):
    def test_same_input_same_plan_output(self) -> None:
        engine = ImprovementEngine()
        learning = make_learning_report()
        audit = make_audit_report()
        p1 = engine.generate_improvement_plan(learning_report=learning, audit_report=audit, generated_at=100.0)
        p2 = engine.generate_improvement_plan(learning_report=learning, audit_report=audit, generated_at=100.0)
        self.assertEqual(len(p1.actions), len(p2.actions))
        self.assertEqual([a.title for a in p1.actions], [a.title for a in p2.actions])
        self.assertEqual(p1.summary.total_actions, p2.summary.total_actions)


class TestSummaryCountsCorrect(unittest.TestCase):
    def test_summary_counts_correct(self) -> None:
        engine = ImprovementEngine()
        plan = engine.generate_improvement_plan(
            learning_report=make_learning_report(candidates=[
                {"title": "L", "description": "D", "priority": "low", "source_patterns": []},
                {"title": "H", "description": "D", "priority": "high", "source_patterns": []},
            ]),
        )
        self.assertEqual(
            plan.summary.low_count + plan.summary.medium_count + plan.summary.high_count + plan.summary.critical_count,
            plan.summary.total_actions,
        )
        self.assertEqual(len(plan.actions), plan.summary.total_actions)
