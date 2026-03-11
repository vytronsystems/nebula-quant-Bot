from __future__ import annotations

# NEBULA-QUANT v1 | nq_orchestrator registry

from nq_orchestrator.models import OrchestratorError, WorkflowDefinition
from nq_orchestrator.workflow import validate_workflow


class WorkflowRegistry:
    """Registry of workflow definitions. Fail-closed on invalid or duplicate registration."""

    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowDefinition] = {}

    def register(self, workflow: WorkflowDefinition) -> None:
        """Register a workflow. Raises OrchestratorError on duplicate workflow_id or invalid definition."""
        if not (workflow.workflow_id and workflow.workflow_id.strip()):
            raise OrchestratorError("workflow_id must be non-empty")
        if not (workflow.name and workflow.name.strip()):
            raise OrchestratorError("workflow name must be non-empty")
        if not workflow.steps:
            raise OrchestratorError("workflow must have at least one step")
        validate_workflow(workflow)
        if workflow.workflow_id in self._workflows:
            raise OrchestratorError(f"duplicate workflow_id: {workflow.workflow_id!r}")
        self._workflows[workflow.workflow_id] = workflow

    def get(self, workflow_id: str) -> WorkflowDefinition:
        """Return workflow by id. Raises OrchestratorError if not found."""
        if workflow_id not in self._workflows:
            raise OrchestratorError(f"workflow not found: {workflow_id!r}")
        return self._workflows[workflow_id]

    def list_workflows(self) -> list[WorkflowDefinition]:
        """Return all registered workflows in deterministic (registration) order."""
        return list(self._workflows.values())

    def __contains__(self, workflow_id: str) -> bool:
        return workflow_id in self._workflows
