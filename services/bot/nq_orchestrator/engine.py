from __future__ import annotations

# NEBULA-QUANT v1 | nq_orchestrator engine

from collections.abc import Callable
from typing import Any

from nq_orchestrator.context import create_context
from nq_orchestrator.models import (
    OrchestrationContext,
    OrchestratorError,
    OrchestratorStats,
    StepExecutionResult,
    StepStatus,
    WorkflowDefinition,
    WorkflowExecutionResult,
    WorkflowStep,
)
from nq_orchestrator.registry import WorkflowRegistry
from nq_orchestrator.workflow import validate_workflow


class OrchestratorEngine:
    """
    Deterministic orchestration engine for ordered workflow execution.

    - Sequential step execution in declared order.
    - Injectable clock for timestamps; deterministic run_id via internal counter.
    - Fail-closed on invalid workflow, disabled workflow, or missing workflow.
    - Step callback contract: (context: OrchestrationContext) -> object | None.
    - Callback may mutate context.values; return value is stored as step output.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time
        self._clock = clock or time.monotonic
        self._registry = WorkflowRegistry()
        self._stats = OrchestratorStats()
        self._run_counter = 0

    def _now(self) -> float:
        return self._clock()

    def _next_run_id(self, workflow_id: str) -> str:
        self._run_counter += 1
        return f"{workflow_id}-run-{self._run_counter}"

    def _recompute_stats_counts(self) -> None:
        workflows = self._registry.list_workflows()
        self._stats.registered_workflows = len(workflows)
        self._stats.enabled_workflows = sum(1 for w in workflows if w.enabled)
        self._stats.disabled_workflows = sum(1 for w in workflows if not w.enabled)

    # Registration / inspection -------------------------------------------------

    def register_workflow(self, workflow: WorkflowDefinition) -> None:
        """Register a workflow. Raises OrchestratorError on invalid or duplicate definition."""
        self._registry.register(workflow)
        self._recompute_stats_counts()

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition:
        """Return workflow by id. Raises OrchestratorError if not found."""
        return self._registry.get(workflow_id)

    def list_workflows(self) -> list[WorkflowDefinition]:
        """Return all registered workflows."""
        return self._registry.list_workflows()

    def validate_workflow(self, workflow: WorkflowDefinition) -> None:
        """Validate workflow definition. Raises OrchestratorError if invalid."""
        validate_workflow(workflow)

    def stats(self) -> OrchestratorStats:
        """Return current orchestrator stats (copy of internal counters)."""
        return OrchestratorStats(
            registered_workflows=self._stats.registered_workflows,
            enabled_workflows=self._stats.enabled_workflows,
            disabled_workflows=self._stats.disabled_workflows,
            successful_runs=self._stats.successful_runs,
            failed_runs=self._stats.failed_runs,
            step_failures=self._stats.step_failures,
        )

    # Execution -----------------------------------------------------------------

    def run_workflow(
        self,
        workflow_id: str,
        initial_values: dict[str, Any] | None = None,
        current_time: float | None = None,
        run_id: str | None = None,
    ) -> WorkflowExecutionResult:
        """
        Run workflow by id. Steps execute sequentially in declared order.
        Fail-closed if workflow not found or disabled.
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow.enabled:
            raise OrchestratorError(f"workflow {workflow_id!r} is disabled and cannot be run")

        now = current_time if current_time is not None else self._now()
        if run_id is not None:
            rid = run_id
            self._run_counter += 1  # keep counter in sync for deterministic next run_id
        else:
            rid = self._next_run_id(workflow_id)
        context = create_context(
            workflow_id=workflow_id,
            run_id=rid,
            initial_values=initial_values,
        )

        step_results: list[StepExecutionResult] = []
        workflow_error: str | None = None
        finished_at: float | None = None
        success = True

        for step in workflow.steps:
            if not step.enabled:
                step_results.append(
                    StepExecutionResult(
                        step_id=step.step_id,
                        started_at=None,
                        finished_at=None,
                        status=StepStatus.SKIPPED.value,
                        output=None,
                        error=None,
                    )
                )
                continue

            started_at = self._now() if current_time is None else current_time
            try:
                output = step.callback(context)
            except Exception as e:  # noqa: BLE001
                self._stats.step_failures += 1
                err_msg = f"{type(e).__name__}: {e}"
                step_finished = self._now() if current_time is None else current_time
                step_results.append(
                    StepExecutionResult(
                        step_id=step.step_id,
                        started_at=started_at,
                        finished_at=step_finished,
                        status=StepStatus.FAILED.value,
                        output=None,
                        error=err_msg,
                    )
                )
                workflow_error = err_msg
                success = False
                finished_at = step_finished
                if step.stop_on_failure:
                    for rest in workflow.steps[workflow.steps.index(step) + 1 :]:
                        step_results.append(
                            StepExecutionResult(
                                step_id=rest.step_id,
                                started_at=None,
                                finished_at=None,
                                status=StepStatus.SKIPPED.value,
                                output=None,
                                error=None,
                            )
                        )
                    break
                continue

            finished_step = self._now() if current_time is None else (current_time or self._now())
            step_results.append(
                StepExecutionResult(
                    step_id=step.step_id,
                    started_at=started_at,
                    finished_at=finished_step,
                    status=StepStatus.SUCCESS.value,
                    output=output,
                    error=None,
                )
            )
            if current_time is not None:
                current_time = finished_step

        if finished_at is None and step_results:
            finished_at = self._now() if current_time is None else (current_time or self._now())

        if success:
            self._stats.successful_runs += 1
        else:
            self._stats.failed_runs += 1

        return WorkflowExecutionResult(
            workflow_id=workflow_id,
            run_id=rid,
            started_at=now,
            finished_at=finished_at,
            success=success,
            step_results=step_results,
            final_context=context,
            error=workflow_error,
        )
