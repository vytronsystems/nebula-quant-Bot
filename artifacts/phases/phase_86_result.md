# Phase 86 — Risk Guardrails — Result

## Summary

Enforce trading limits: max drawdown, margin usage, exposure per strategy.

## Implementation

- **Bot**: `nq_risk_guardrails` — RiskGuardrailsEngine with GuardrailLimits (max_drawdown_pct, max_margin_usage_pct, max_exposure_per_strategy_pct). check(drawdown_pct, margin_usage_pct, exposure_per_strategy_pct) returns list of GuardrailCheck (passed, limit_name, current_value, limit_value).

## Modules Affected

- services/bot/nq_risk_guardrails/
