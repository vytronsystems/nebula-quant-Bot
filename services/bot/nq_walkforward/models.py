# NEBULA-QUANT v1 | nq_walkforward models

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class WalkForwardConfig:
    """Configuration for a single walk-forward window (train + test)."""

    train_start_ts: float
    train_end_ts: float
    test_start_ts: float
    test_end_ts: float
    symbol: str
    timeframe: str
    window_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WalkForwardWindowResult:
    """Result of one walk-forward window (train + test)."""

    config: WalkForwardConfig
    train_summary: dict[str, Any]
    test_summary: dict[str, Any]
    passed: bool
    notes: str


@dataclass
class WalkForwardResult:
    """Aggregate result of a full walk-forward run."""

    windows: list[WalkForwardWindowResult]
    total_windows: int
    passed_windows: int
    failed_windows: int
    pass_rate: float
    metadata: dict[str, Any] = field(default_factory=dict)
