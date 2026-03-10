# NEBULA-QUANT v1 | nq_guardrails state — in-memory runtime state, no persistence

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GuardrailsState:
    """Runtime state for guardrails; updated by engine after each run_guardrails()."""

    trading_enabled: bool = True
    last_shutdown_reason: str = ""
    active_signals: list[dict[str, Any]] = field(default_factory=list)
    updated_ts: float = 0.0
