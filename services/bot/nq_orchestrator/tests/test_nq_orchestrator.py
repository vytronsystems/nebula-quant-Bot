from __future__ import annotations

# NEBULA-QUANT v1 | nq_orchestrator tests

import unittest
from typing import Any, Callable

from nq_orchestrator import (
    OrchestrationContext,
    OrchestratorEngine,
    OrchestratorError,
    StepStatus,
    WorkflowDefinition,
    WorkflowStep,
)


def make_clock(ticks: list[float]) -> tuple[list[float], Callable[[], float]]:
    """Returns (ticks list, clock callable). clock() returns next tick."""
    it = iter(ticks)

    def clock() -> float:
        return next(it)

    return ticks, clock


def noop(context: OrchestrationContext) -> None:
    return None


# --- Registration ------------------------------------------------------------


class TestWorkflowRegistration(unittest.TestCase):
    def test_valid_workflow_registration_works(self) -> None:
        engine = OrchestratorEngine()
        w = WorkflowDefinition(
            workflow_id="w1",
            name="Workflow 1",
            steps=[WorkflowStep(step_id="s1", name="Step 1", callback=noop)],
        )
        engine.register_workflow(w)
        self.assertEqual(engine.get_workflow("w1").workflow_id, "w1")
        self.assertEqual(len(engine.list_workflows()), 1)

    def test_duplicate_workflow_id_fails_closed(self) -> None:
        engine = OrchestratorEngine()
        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[WorkflowStep(step_id="s1", name="S1", callback=noop)],
        )
        engine.register_workflow(w)
        with self.assertRaises(OrchestratorError):
            engine.register_workflow(w)

    def test_empty_workflow_id_fails_closed(self) -> None:
        engine = OrchestratorEngine()
        with self.assertRaises(OrchestratorError):
            WorkflowDefinition(
                workflow_id="",
                name="W",
                steps=[WorkflowStep(step_id="s1", name="S1", callback=noop)],
            )

    def test_empty_workflow_name_fails_closed(self) -> None:
        with self.assertRaises(OrchestratorError):
            WorkflowDefinition(
                workflow_id="w1",
                name="",
                steps=[WorkflowStep(step_id="s1", name="S1", callback=noop)],
            )

    def test_empty_step_list_fails_closed(self) -> None:
        with self.assertRaises(OrchestratorError):
            WorkflowDefinition(workflow_id="w1", name="W1", steps=[])

    def test_duplicate_step_id_within_workflow_fails_closed(self) -> None:
        engine = OrchestratorEngine()
        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[
                WorkflowStep(step_id="s1", name="S1", callback=noop),
                WorkflowStep(step_id="s1", name="S2", callback=noop),
            ],
        )
        with self.assertRaises(OrchestratorError):
            engine.register_workflow(w)

    def test_invalid_callback_fails_closed(self) -> None:
        with self.assertRaises(OrchestratorError):
            WorkflowStep(step_id="s1", name="S1", callback=None)  # type: ignore[arg-type]


# --- Execution order and context ----------------------------------------------


class TestWorkflowExecution(unittest.TestCase):
    def test_execution_runs_steps_in_declared_order(self) -> None:
        order: list[str] = []
        engine = OrchestratorEngine()

        def make_step(sid: str):
            def step(context: OrchestrationContext) -> None:
                order.append(sid)
            return step

        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[
                WorkflowStep(step_id="a", name="A", callback=make_step("a")),
                WorkflowStep(step_id="b", name="B", callback=make_step("b")),
                WorkflowStep(step_id="c", name="C", callback=make_step("c")),
            ],
        )
        engine.register_workflow(w)
        result = engine.run_workflow("w1")
        self.assertTrue(result.success)
        self.assertEqual(order, ["a", "b", "c"])
        self.assertEqual([r.step_id for r in result.step_results], ["a", "b", "c"])

    def test_context_passed_through_steps(self) -> None:
        engine = OrchestratorEngine()

        def step1(context: OrchestrationContext) -> None:
            context.values["x"] = 1

        def step2(context: OrchestrationContext) -> Any:
            return context.values.get("x")

        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[
                WorkflowStep(step_id="s1", name="S1", callback=step1),
                WorkflowStep(step_id="s2", name="S2", callback=step2),
            ],
        )
        engine.register_workflow(w)
        result = engine.run_workflow("w1", initial_values={})
        self.assertTrue(result.success)
        self.assertEqual(result.final_context.values.get("x"), 1)
        self.assertEqual(result.step_results[1].output, 1)

    def test_initial_values_in_context(self) -> None:
        engine = OrchestratorEngine()

        def step(context: OrchestrationContext) -> Any:
            return context.values.get("seed")

        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[WorkflowStep(step_id="s1", name="S1", callback=step)],
        )
        engine.register_workflow(w)
        result = engine.run_workflow("w1", initial_values={"seed": 42})
        self.assertTrue(result.success)
        self.assertEqual(result.final_context.values.get("seed"), 42)
        self.assertEqual(result.step_results[0].output, 42)


# --- Disabled step ------------------------------------------------------------


class TestDisabledStep(unittest.TestCase):
    def test_disabled_step_skipped_deterministically(self) -> None:
        ran: list[str] = []
        engine = OrchestratorEngine()

        def make_step(sid: str):
            def step(context: OrchestrationContext) -> None:
                ran.append(sid)
            return step

        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[
                WorkflowStep(step_id="a", name="A", callback=make_step("a")),
                WorkflowStep(step_id="b", name="B", callback=make_step("b"), enabled=False),
                WorkflowStep(step_id="c", name="C", callback=make_step("c")),
            ],
        )
        engine.register_workflow(w)
        result = engine.run_workflow("w1")
        self.assertTrue(result.success)
        self.assertEqual(ran, ["a", "c"])
        self.assertEqual(result.step_results[0].status, StepStatus.SUCCESS.value)
        self.assertEqual(result.step_results[1].status, StepStatus.SKIPPED.value)
        self.assertEqual(result.step_results[2].status, StepStatus.SUCCESS.value)


# --- Step failure and stop-on-failure -----------------------------------------


class TestStepFailure(unittest.TestCase):
    def test_step_failure_recorded_and_workflow_stops(self) -> None:
        engine = OrchestratorEngine()

        def fail_step(context: OrchestrationContext) -> None:
            raise ValueError("step failed")

        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[
                WorkflowStep(step_id="a", name="A", callback=noop),
                WorkflowStep(step_id="b", name="B", callback=fail_step),
                WorkflowStep(step_id="c", name="C", callback=noop),
            ],
        )
        engine.register_workflow(w)
        result = engine.run_workflow("w1")
        self.assertFalse(result.success)
        self.assertEqual(result.step_results[0].status, StepStatus.SUCCESS.value)
        self.assertEqual(result.step_results[1].status, StepStatus.FAILED.value)
        self.assertIn("step failed", result.step_results[1].error or "")
        self.assertIsNotNone(result.error)

    def test_remaining_steps_skipped_after_stop_on_failure(self) -> None:
        ran: list[str] = []
        engine = OrchestratorEngine()

        def make_step(sid: str):
            def step(context: OrchestrationContext) -> None:
                ran.append(sid)
            return step

        def fail(context: OrchestrationContext) -> None:
            raise RuntimeError("fail")

        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[
                WorkflowStep(step_id="a", name="A", callback=make_step("a")),
                WorkflowStep(step_id="b", name="B", callback=fail, stop_on_failure=True),
                WorkflowStep(step_id="c", name="C", callback=make_step("c")),
            ],
        )
        engine.register_workflow(w)
        result = engine.run_workflow("w1")
        self.assertFalse(result.success)
        self.assertEqual(ran, ["a"])
        self.assertEqual(len(result.step_results), 3)
        self.assertEqual(result.step_results[2].status, StepStatus.SKIPPED.value)


# --- Disabled / missing workflow ----------------------------------------------


class TestRunFailClosed(unittest.TestCase):
    def test_disabled_workflow_run_fails_closed(self) -> None:
        engine = OrchestratorEngine()
        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[WorkflowStep(step_id="s1", name="S1", callback=noop)],
            enabled=False,
        )
        engine.register_workflow(w)
        with self.assertRaises(OrchestratorError):
            engine.run_workflow("w1")

    def test_missing_workflow_run_fails_closed(self) -> None:
        engine = OrchestratorEngine()
        with self.assertRaises(OrchestratorError):
            engine.run_workflow("nonexistent")


# --- Stats --------------------------------------------------------------------


class TestStats(unittest.TestCase):
    def test_stats_update_correctly(self) -> None:
        engine = OrchestratorEngine()
        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[
                WorkflowStep(step_id="s1", name="S1", callback=noop),
            ],
        )
        engine.register_workflow(w)
        s = engine.stats()
        self.assertEqual(s.registered_workflows, 1)
        self.assertEqual(s.enabled_workflows, 1)
        self.assertEqual(s.disabled_workflows, 0)

        engine.run_workflow("w1")
        s = engine.stats()
        self.assertEqual(s.successful_runs, 1)
        self.assertEqual(s.failed_runs, 0)

        w2 = WorkflowDefinition(
            workflow_id="w2",
            name="W2",
            steps=[WorkflowStep(step_id="s1", name="S1", callback=lambda c: (_ for _ in ()).throw(ValueError("x")))],
        )
        engine.register_workflow(w2)
        engine.run_workflow("w2")
        s = engine.stats()
        self.assertEqual(s.registered_workflows, 2)
        self.assertEqual(s.failed_runs, 1)
        self.assertEqual(s.step_failures, 1)


# --- Determinism --------------------------------------------------------------


class TestDeterminism(unittest.TestCase):
    def test_repeated_same_workflow_and_context_yield_consistent_results(self) -> None:
        ticks = [100.0, 101.0, 102.0, 103.0]
        _, clock = make_clock(ticks)
        engine = OrchestratorEngine(clock=clock)
        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[
                WorkflowStep(step_id="a", name="A", callback=noop),
                WorkflowStep(step_id="b", name="B", callback=noop),
            ],
        )
        engine.register_workflow(w)
        r1 = engine.run_workflow("w1", current_time=100.0)
        # Second run: need fresh clock with same ticks for determinism
        ticks2 = [200.0, 201.0, 202.0, 203.0]
        _, clock2 = make_clock(ticks2)
        engine2 = OrchestratorEngine(clock=clock2)
        engine2.register_workflow(w)
        r2 = engine2.run_workflow("w1", current_time=200.0)
        self.assertEqual([x.status for x in r1.step_results], [x.status for x in r2.step_results])
        self.assertEqual(len(r1.step_results), len(r2.step_results))

    def test_deterministic_run_ids(self) -> None:
        engine = OrchestratorEngine()
        w = WorkflowDefinition(
            workflow_id="wf",
            name="W",
            steps=[WorkflowStep(step_id="s1", name="S1", callback=noop)],
        )
        engine.register_workflow(w)
        r1 = engine.run_workflow("wf", run_id="custom-1")
        r2 = engine.run_workflow("wf")
        r3 = engine.run_workflow("wf")
        self.assertEqual(r1.run_id, "custom-1")
        self.assertEqual(r2.run_id, "wf-run-2")  # counter incremented for r1 and r2
        self.assertEqual(r3.run_id, "wf-run-3")

    def test_no_hidden_concurrency(self) -> None:
        """Steps run sequentially; no threads/async."""
        order: list[int] = []
        engine = OrchestratorEngine()

        def make_step(i: int):
            def step(context: OrchestrationContext) -> None:
                order.append(i)
            return step

        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[
                WorkflowStep(step_id="a", name="A", callback=make_step(1)),
                WorkflowStep(step_id="b", name="B", callback=make_step(2)),
                WorkflowStep(step_id="c", name="C", callback=make_step(3)),
            ],
        )
        engine.register_workflow(w)
        engine.run_workflow("w1")
        self.assertEqual(order, [1, 2, 3])


# --- validate_workflow --------------------------------------------------------


class TestValidateWorkflow(unittest.TestCase):
    def test_validate_workflow_duplicate_step_raises(self) -> None:
        engine = OrchestratorEngine()
        w = WorkflowDefinition(
            workflow_id="w1",
            name="W1",
            steps=[
                WorkflowStep(step_id="x", name="X", callback=noop),
                WorkflowStep(step_id="x", name="Y", callback=noop),
            ],
        )
        with self.assertRaises(OrchestratorError):
            engine.validate_workflow(w)
