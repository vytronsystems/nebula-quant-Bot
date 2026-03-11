from __future__ import annotations

# NEBULA-QUANT v1 | nq_orchestrator context

from typing import Any

from nq_orchestrator.models import OrchestrationContext


def create_context(
    workflow_id: str,
    run_id: str,
    initial_values: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> OrchestrationContext:
    """Create an orchestration context for a workflow run."""
    return OrchestrationContext(
        workflow_id=workflow_id,
        run_id=run_id,
        values=dict(initial_values) if initial_values else {},
        metadata=dict(metadata) if metadata else None,
    )
