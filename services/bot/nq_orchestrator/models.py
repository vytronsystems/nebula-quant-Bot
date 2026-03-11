from __future__ import annotations

# NEBULA-QUANT v1 | nq_orchestrator models

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OrchestratorError(Exception):
    """Deterministic exception for invalid orchestration state or definitions."""


class StepStatus(str, Enum):
    """Status of a workflow step."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(slots=True)
class WorkflowStep:
    """Single step in a workflow."""

    step_id: str
    name: str
    callback: Callable[..., Any]
    enabled: bool = True
    stop_on_failure: bool = True
    metadata: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (self.step_id and self.step_id.strip()):
            raise OrchestratorError("step_id must be non-empty")
        if not (self.name and self.name.strip()):
            raise OrchestratorError("step name must be non-empty")
        if not callable(self.callback):
            raise OrchestratorError("step callback must be callable")


@dataclass(slots=True)
class WorkflowDefinition:
    """Named ordered list of steps."""

    workflow_id: str
    name: str
    steps: list[WorkflowStep]
    enabled: bool = True
    metadata: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (self.workflow_id and self.workflow_id.strip()):
            raise OrchestratorError("workflow_id must be non-empty")
        if not (self.name and self.name.strip()):
            raise OrchestratorError("workflow name must be non-empty")
        if not self.steps:
            raise OrchestratorError("workflow must have at least one step")


@dataclass(slots=True)
class OrchestrationContext:
    """Deterministic execution context passed through workflow steps."""

    workflow_id: str
    run_id: str
    values: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class StepExecutionResult:
    """Result of a single step execution."""

    step_id: str
    started_at: float | None
    finished_at: float | None
    status: str
    output: Any = None
    error: str | None = None


@dataclass(slots=True)
class WorkflowExecutionResult:
    """Result of a full workflow run."""

    workflow_id: str
    run_id: str
    started_at: float
    finished_at: float | None
    success: bool
    step_results: list[StepExecutionResult]
    final_context: OrchestrationContext
    error: str | None = None


@dataclass(slots=True)
class OrchestratorStats:
    """Counters for orchestrator inspection."""

    registered_workflows: int = 0
    enabled_workflows: int = 0
    disabled_workflows: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    step_failures: int = 0
