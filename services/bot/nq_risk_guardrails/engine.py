# NEBULA-QUANT v1 | Phase 86 — Risk Guardrails
# Fail-closed: block if limits exceeded.

from __future__ import annotations

from typing import Any

from nq_risk_guardrails.models import GuardrailCheck, GuardrailLimits


class RiskGuardrailsEngine:
    """Enforce max drawdown, margin usage, exposure per strategy."""

    def __init__(self, limits: GuardrailLimits | None = None) -> None:
        self.limits = limits or GuardrailLimits()

    def check(
        self,
        drawdown_pct: float | None = None,
        margin_usage_pct: float | None = None,
        exposure_per_strategy_pct: float | None = None,
    ) -> list[GuardrailCheck]:
        results: list[GuardrailCheck] = []
        if drawdown_pct is not None:
            passed = drawdown_pct <= self.limits.max_drawdown_pct
            results.append(GuardrailCheck(
                passed=passed,
                limit_name="max_drawdown",
                current_value=drawdown_pct,
                limit_value=self.limits.max_drawdown_pct,
                reason="ok" if passed else "drawdown_exceeded",
            ))
        if margin_usage_pct is not None:
            passed = margin_usage_pct <= self.limits.max_margin_usage_pct
            results.append(GuardrailCheck(
                passed=passed,
                limit_name="margin_usage",
                current_value=margin_usage_pct,
                limit_value=self.limits.max_margin_usage_pct,
                reason="ok" if passed else "margin_exceeded",
            ))
        if exposure_per_strategy_pct is not None:
            passed = exposure_per_strategy_pct <= self.limits.max_exposure_per_strategy_pct
            results.append(GuardrailCheck(
                passed=passed,
                limit_name="exposure_per_strategy",
                current_value=exposure_per_strategy_pct,
                limit_value=self.limits.max_exposure_per_strategy_pct,
                reason="ok" if passed else "exposure_exceeded",
            ))
        return results
