# NEBULA-QUANT v1 | nq_trade_review models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TradeReviewError(Exception):
    """Deterministic exception for invalid trade-review inputs or state."""


class TradeReviewFindingSeverity(str, Enum):
    """Severity of a trade review finding."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


VALID_SIDES = frozenset({"long", "short", "buy", "sell"})


@dataclass(slots=True)
class TradeReviewInput:
    """Typed input for a single trade review."""

    trade_id: str
    symbol: str
    side: str
    strategy_id: str | None = None
    expected_entry_price: float | None = None
    actual_entry_price: float | None = None
    expected_exit_price: float | None = None
    actual_exit_price: float | None = None
    stop_loss_price: float | None = None
    take_profit_price: float | None = None
    quantity: float | None = None
    notional: float | None = None
    expected_rr: float | None = None
    actual_rr: float | None = None
    entry_timestamp: float | str | None = None
    exit_timestamp: float | str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (self.trade_id and self.trade_id.strip()):
            raise TradeReviewError("trade_id must be non-empty")
        if not (self.symbol and self.symbol.strip()):
            raise TradeReviewError("symbol must be non-empty")
        if not (self.side and self.side.strip()):
            raise TradeReviewError("side must be non-empty")
        side_lower = self.side.strip().lower()
        if side_lower not in VALID_SIDES:
            raise TradeReviewError(f"side must be one of {sorted(VALID_SIDES)}, got {self.side!r}")
        for name, val in (
            ("expected_entry_price", self.expected_entry_price),
            ("actual_entry_price", self.actual_entry_price),
            ("expected_exit_price", self.expected_exit_price),
            ("actual_exit_price", self.actual_exit_price),
            ("stop_loss_price", self.stop_loss_price),
            ("take_profit_price", self.take_profit_price),
            ("quantity", self.quantity),
            ("expected_rr", self.expected_rr),
            ("actual_rr", self.actual_rr),
        ):
            if val is not None and isinstance(val, (int, float)) and val < 0 and name != "actual_rr":
                raise TradeReviewError(f"{name} must be non-negative, got {val}")
        if self.quantity is not None and isinstance(self.quantity, (int, float)) and self.quantity <= 0:
            raise TradeReviewError("quantity must be positive when provided")


@dataclass(slots=True)
class TradeReviewFinding:
    """Single structured trade review finding."""

    finding_id: str
    category: str
    severity: str
    title: str
    description: str
    trade_id: str
    strategy_id: str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class TradeReviewSummary:
    """Summary of a trade review run."""

    trade_id: str
    status: str
    total_findings: int
    info_count: int
    warning_count: int
    critical_count: int
    outcome: str | None = None
    exit_reason: str | None = None
    expected_rr: float | None = None
    actual_rr: float | None = None
    slippage: float | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class TradeReviewReport:
    """Full deterministic trade review report."""

    review_id: str
    generated_at: float
    summary: TradeReviewSummary
    findings: list[TradeReviewFinding]
    recommendations: list[str]
    metadata: dict[str, Any] | None = field(default_factory=dict)
