# NEBULA-QUANT v1 | nq_guardrails models

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GuardrailSignal:
    """Single guardrail evaluation signal (skeleton)."""

    signal_type: str
    severity: str
    message: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardrailResult:
    """Aggregate result of guardrails evaluation (skeleton)."""

    allowed: bool
    signals: list[GuardrailSignal]
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)
