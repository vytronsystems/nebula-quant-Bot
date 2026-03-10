# NEBULA-QUANT v1 | nq_promotion engine — lifecycle governance, fail-closed

from __future__ import annotations

import time
from typing import Any

from nq_promotion.models import PromotionDecision, PromotionInput, PromotionResult
from nq_promotion.rules import (
    check_backtest_requirements,
    check_guardrail_requirements,
    check_paper_requirements,
    check_transition_allowed,
    check_walkforward_requirements,
)


class PromotionEngine:
    """
    Evaluates whether a strategy may be promoted to a target lifecycle status.
    Fail-closed: missing required evidence or failed checks → allowed=False.
    """

    def __init__(self, config: Any = None) -> None:
        self._config = config

    def evaluate_promotion(
        self,
        promotion_input: PromotionInput | None = None,
        target_status: str | None = None,
        **kwargs: Any,
    ) -> PromotionResult:
        """
        Evaluate promotion to target_status. Uses promotion_input or kwargs.
        Returns PromotionResult with allowed=True only when transition is allowed and all required evidence passes.
        """
        inp = promotion_input or self._input_from_kwargs(kwargs)
        target = target_status or kwargs.get("target_status", "")
        self._validate_input(inp, target)
        decision = self._apply_rules(inp, target)
        return self._build_result(inp.strategy_id, inp.current_status, target, decision)

    def _input_from_kwargs(self, kwargs: Any) -> PromotionInput:
        return PromotionInput(
            strategy_id=kwargs.get("strategy_id", ""),
            current_status=kwargs.get("current_status", ""),
            backtest_summary=kwargs.get("backtest_summary") or {},
            walkforward_summary=kwargs.get("walkforward_summary") or {},
            paper_summary=kwargs.get("paper_summary") or {},
            guardrail_summary=kwargs.get("guardrail_summary") or {},
            metrics_summary=kwargs.get("metrics_summary") or {},
            experiment_summary=kwargs.get("experiment_summary") or {},
            metadata=kwargs.get("metadata") or {},
        )

    def _validate_input(self, inp: PromotionInput, target_status: str) -> None:
        """No raise; missing fields produce fail-closed in _apply_rules."""
        pass

    def _apply_rules(self, inp: PromotionInput, target_status: str) -> PromotionDecision:
        """Apply transition check and stage-specific evidence rules. Fail-closed."""
        from_status = (inp.current_status or "").strip().lower()
        to_status = (target_status or "").strip().lower()
        all_blocking: list[str] = []
        all_warnings: list[str] = []

        allowed, block, warn = check_transition_allowed(from_status, to_status)
        all_blocking.extend(block)
        all_warnings.extend(warn)
        if not allowed:
            return PromotionDecision(
                allowed=False,
                from_status=inp.current_status,
                to_status=target_status,
                reason=all_blocking[0] if all_blocking else "transition not allowed",
                blocking_issues=all_blocking,
                warnings=all_warnings,
                metadata={},
            )

        # Stage-specific evidence requirements (fail-closed when required and missing)
        if to_status == "walkforward":
            block, warn = check_backtest_requirements(inp.backtest_summary, self._config)
            all_blocking.extend(block)
            all_warnings.extend(warn)
        elif to_status == "paper":
            block, warn = check_backtest_requirements(inp.backtest_summary, self._config)
            all_blocking.extend(block)
            all_warnings.extend(warn)
            block, warn = check_walkforward_requirements(inp.walkforward_summary, self._config)
            all_blocking.extend(block)
            all_warnings.extend(warn)
        elif to_status == "live":
            block, warn = check_paper_requirements(inp.paper_summary, self._config)
            all_blocking.extend(block)
            all_warnings.extend(warn)
            block, warn = check_guardrail_requirements(inp.guardrail_summary, self._config)
            all_blocking.extend(block)
            all_warnings.extend(warn)
        # idea->research, research->backtest, any->disabled, live->retired: no extra evidence

        allowed = len(all_blocking) == 0
        reason = all_blocking[0] if all_blocking else "ok"
        return PromotionDecision(
            allowed=allowed,
            from_status=inp.current_status,
            to_status=target_status,
            reason=reason,
            blocking_issues=all_blocking,
            warnings=all_warnings,
            metadata={},
        )

    def _build_result(
        self,
        strategy_id: str,
        from_status: str,
        to_status: str,
        decision: PromotionDecision,
    ) -> PromotionResult:
        return PromotionResult(
            strategy_id=strategy_id,
            decision=decision,
            evaluated_at=time.time(),
            metadata={"engine": "nq_promotion", "version": "1"},
        )
