# nq_orchestrator

Deterministic orchestration layer for NEBULA-QUANT v1. Coordinates ordered execution of module steps, enforces workflow sequencing, and provides explicit run context and results. **Infrastructure and control flow only** — no trading logic.

## Purpose

- Define workflow step order and validate workflow definitions.
- Execute steps **sequentially** in declared order.
- Carry deterministic execution context between steps.
- Collect ordered execution results and expose run status.
- **Fail closed** on invalid workflows, missing/disabled workflow on run, or step definition errors.

## Workflow model

- A **workflow** is a named, ordered list of **steps**.
- Steps run one after another in declaration order (no DAG, no concurrency).
- Each step receives an **OrchestrationContext**; it may mutate `context.values` and optionally return a value (stored as step output).
- Workflows and steps can be **enabled** or **disabled**. Disabled workflows cannot be run (fail-closed). Disabled steps are skipped (marked SKIPPED).

## Step contract

Step callbacks must have the signature:

```python
def step_callback(context: OrchestrationContext) -> object | None:
    ...
```

- **context**: Shared mutable context for the run. Steps may read/write `context.values`.
- **Return value**: Stored as the step’s output in `StepExecutionResult`; not automatically merged into context (steps update `context.values` explicitly if needed).

Invalid or non-callable callbacks are rejected at registration/validation (fail-closed).

## Context model

- **OrchestrationContext**: `workflow_id`, `run_id`, `values` (dict), optional `metadata`.
- Created at the start of each run with optional `initial_values`.
- Passed by reference to each step; steps may mutate `context.values`.

## Fail-closed behavior

The orchestrator raises **OrchestratorError** and does **not** silently coerce when:

- workflow_id or name is empty
- steps list is empty
- duplicate workflow_id on registration
- duplicate step_id within a workflow
- invalid or non-callable step callback
- run requested for missing workflow
- run requested for disabled workflow

On step callback exception:

- Step is recorded as FAILED with error message.
- Workflow stops if the step has `stop_on_failure=True` (default); remaining steps are marked SKIPPED.
- If `stop_on_failure=False`, workflow continues; failure is still recorded.

## Disabled step / workflow behavior

- **Disabled workflow**: `run_workflow(workflow_id)` raises `OrchestratorError`.
- **Disabled step**: Step is not executed; result is appended with status SKIPPED; workflow continues.

## Deterministic run ID and timing

- **Run ID**: By default, the engine uses an internal counter and produces run ids like `{workflow_id}-run-{counter}`. Optional `run_id` can be passed into `run_workflow` for tests or caller-controlled ids.
- **Timing**: An optional **injectable clock** (and optional `current_time` on `run_workflow`) allows deterministic timestamps in tests. Same workflow, same context, same clock progression → same ordered results.

## Intended future integration

- **nq_scheduler**: Scheduler may trigger `run_workflow(workflow_id)` for audit, reporting, observability, or experiment review workflows.
- No scheduler/orchestrator wiring in this phase; the API is designed so that integration is straightforward later.

## Simple usage example

```python
from nq_orchestrator import (
    OrchestratorEngine,
    WorkflowDefinition,
    WorkflowStep,
    OrchestrationContext,
)

def step_a(context: OrchestrationContext):
    context.values["a"] = 1
    return "done_a"

def step_b(context: OrchestrationContext):
    assert context.values.get("a") == 1
    return "done_b"

engine = OrchestratorEngine()
workflow = WorkflowDefinition(
    workflow_id="example",
    name="Example workflow",
    steps=[
        WorkflowStep(step_id="a", name="Step A", callback=step_a),
        WorkflowStep(step_id="b", name="Step B", callback=step_b),
    ],
)
engine.register_workflow(workflow)
result = engine.run_workflow("example", initial_values={})
assert result.success
assert result.final_context.values["a"] == 1
assert [r.status for r in result.step_results] == ["success", "success"]
```
