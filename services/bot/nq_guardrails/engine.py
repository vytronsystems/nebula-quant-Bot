# NEBULA-QUANT v1 | nq_guardrails engine — real evaluation, fail-closed aggregation

from __future__ import annotations

import time
from typing import Any

from nq_guardrails.models import GuardrailResult, GuardrailSignal
from nq_guardrails.rules import (
    SEVERITY_BLOCK,
    check_daily_loss,
    check_execution_pause,
    check_max_drawdown,
    check_strategy_disable,
    check_volatility_spike,
)
from nq_guardrails.state import GuardrailsState


class GuardrailsEngine:
    """
    System-level safety controller. Evaluates risk conditions and returns
    safety signals. Does not execute trades.
    """

    def __init__(self) -> None:
        self._state = GuardrailsState()

    def evaluate_account_state(
        self,
        account: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> GuardrailResult:
        """Evaluate account-level guardrails (drawdown, daily loss)."""
        account = account or {}
        context = context or {}
        r1 = check_max_drawdown(account, context)
        r2 = check_daily_loss(account, context)
        return self._merge_results([r1, r2])

    def evaluate_market_conditions(
        self,
        market: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> GuardrailResult:
        """Evaluate market-level guardrails (volatility, abnormal conditions)."""
        market = market or {}
        context = context or {}
        return check_volatility_spike(market, context)

    def evaluate_strategy_health(
        self,
        strategy_health: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> GuardrailResult:
        """Evaluate strategy-level guardrails (disable signals)."""
        strategy_health = strategy_health or {}
        context = context or {}
        return check_strategy_disable(strategy_health, context)

    def run_guardrails(
        self,
        account: dict[str, Any] | None = None,
        positions: dict[str, Any] | None = None,
        volatility: dict[str, Any] | None = None,
        strategy_health: dict[str, Any] | None = None,
        execution_state: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> GuardrailResult:
        """
        Run all guardrail checks. Accepts optional context; never crashes on empty inputs.
        Returns GuardrailResult (allowed=True if all pass).
        """
        account = account or {}
        positions = positions or {}
        volatility = volatility or {}
        strategy_health = strategy_health or {}
        execution_state = execution_state or {}
        context = context or {}

        results: list[GuardrailResult] = []
        results.append(self.evaluate_account_state(account, context))
        results.append(self.evaluate_market_conditions(volatility, context))
        results.append(self.evaluate_strategy_health(strategy_health, context))
        results.append(check_execution_pause(execution_state, context))

        out = self._merge_results(results)
        self._state.updated_ts = time.time()
        self._state.trading_enabled = out.allowed
        self._state.last_shutdown_reason = out.reason if not out.allowed else ""
        return out

    def _merge_results(self, results: list[GuardrailResult]) -> GuardrailResult:
        """Merge multiple GuardrailResults; fail-closed: any BLOCK signal → allowed=False."""
        all_signals: list[GuardrailSignal] = []
        for r in results:
            all_signals.extend(r.signals)
        block_signals = [s for s in all_signals if s.severity == SEVERITY_BLOCK]
        allowed = len(block_signals) == 0
        reason = block_signals[0].message if block_signals else "ok"
        self._state.active_signals = [
            {"signal_type": s.signal_type, "severity": s.severity, "message": s.message, "timestamp": s.timestamp}
            for s in all_signals
        ]
        return GuardrailResult(
            allowed=allowed,
            signals=all_signals,
            reason=reason,
            metadata={"merged_count": len(results)},
        )
