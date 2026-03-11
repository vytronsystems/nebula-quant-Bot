from __future__ import annotations

# NEBULA-QUANT v1 | nq_orchestrator workflow validation

from nq_orchestrator.models import OrchestratorError, WorkflowDefinition, WorkflowStep


def validate_workflow(workflow: WorkflowDefinition) -> None:
    """
    Validate workflow definition. Raises OrchestratorError on invalid input.
    - Non-empty workflow_id and name (enforced in WorkflowDefinition.__post_init__)
    - Non-empty steps (enforced in WorkflowDefinition.__post_init__)
    - No duplicate step_id within workflow
    """
    step_ids: set[str] = set()
    for step in workflow.steps:
        if step.step_id in step_ids:
            raise OrchestratorError(
                f"workflow {workflow.workflow_id!r}: duplicate step_id {step.step_id!r}"
            )
        step_ids.add(step.step_id)
