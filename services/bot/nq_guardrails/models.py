# NEBULA-QUANT v1 | nq_guardrails models

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GuardrailSignal:
    """Single guardrail evaluation signal."""

    signal_type: str
    severity: str  # INFO, WARN, BLOCK
    message: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardrailResult:
    """Aggregate result of guardrails evaluation; allowed=False if any BLOCK."""

    allowed: bool
    signals: list[GuardrailSignal]
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)
