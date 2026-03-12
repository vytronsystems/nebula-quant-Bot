from __future__ import annotations

from collections.abc import Callable
import hashlib
from typing import Any

from nq_strategy_governance.models import (
    StrategyGovernanceDecision,
    StrategyGovernanceError,
    StrategyGovernanceInput,
    StrategyGovernanceReport,
)
from nq_strategy_governance.rules import evaluate_governance


class StrategyGovernanceEngine:
    """
    Deterministic governance engine for final strategy readiness decisions.

    Evaluates aggregated evidence from backtest, walkforward, paper, metrics,
    edge decay, and audit to decide whether a strategy is approved for live,
    remains in paper, returns to research, or is rejected.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time

        self._clock = clock or time.time

    def _now(self) -> float:
        return float(self._clock())

    def _build_report_id(self, governance_input: StrategyGovernanceInput) -> str:
        """Deterministic hash-based report id from governance input."""
        parts: list[str] = [governance_input.strategy_id]
        for key in (
            "backtest_summary",
            "walkforward_summary",
            "paper_summary",
            "metrics_summary",
            "edge_decay_summary",
            "audit_summary",
        ):
            parts.append(key)
            parts.append(str(getattr(governance_input, key)))
        base = "|".join(parts)
        digest = hashlib.sha256(base.encode("utf-8")).hexdigest()[:12]
        return f"strategy-governance-report-{digest}"

    def _validate_input(self, governance_input: Any) -> StrategyGovernanceInput:
        if not isinstance(governance_input, StrategyGovernanceInput):
            raise StrategyGovernanceError("governance_input must be a StrategyGovernanceInput instance")
        sid = governance_input.strategy_id or ""
        if not str(sid).strip():
            raise StrategyGovernanceError("strategy_id must be non-empty")
        return governance_input

    def evaluate_strategy_readiness(
        self,
        governance_input: StrategyGovernanceInput,
        report_id: str | None = None,
        generated_at: float | None = None,
    ) -> StrategyGovernanceReport:
        """
        Evaluate final readiness of a strategy and return StrategyGovernanceReport.

        Empty summaries fail closed via conservative rules, resulting in
        REMAIN_IN_PAPER, RETURN_TO_RESEARCH, or REJECT_STRATEGY outcomes.
        """
        gi = self._validate_input(governance_input)
        decision, findings, rationale = evaluate_governance(gi)
        rid = report_id or self._build_report_id(gi)
        now = generated_at if generated_at is not None else self._now()
        return StrategyGovernanceReport(
            report_id=rid,
            generated_at=now,
            strategy_id=gi.strategy_id,
            decision=decision,
            findings=findings,
            rationale=rationale,
            metadata={},
        )

