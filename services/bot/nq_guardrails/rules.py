# NEBULA-QUANT v1 | nq_guardrails rules — deterministic safety checks

from __future__ import annotations

import time
from typing import Any

from nq_guardrails.config import (
    DAILY_LOSS_LIMIT,
    EXTREME_VOLATILITY_THRESHOLD,
    MAX_DRAWDOWN_LIMIT,
    MAX_OPEN_POSITIONS,
    VOLATILITY_THRESHOLD,
)
from nq_guardrails.models import GuardrailResult, GuardrailSignal

SEVERITY_INFO = "INFO"
SEVERITY_WARN = "WARN"
SEVERITY_BLOCK = "BLOCK"


def _get(data: dict[str, Any] | None, key: str, default: Any = None) -> Any:
    """Safe get from dict or dict-like."""
    if data is None:
        return default
    return data.get(key, default)


def check_max_drawdown(
    account: dict[str, Any] | None,
    context: dict[str, Any] | None,
) -> GuardrailResult:
    """
    BLOCK if account drawdown exceeds limit.
    Expects account drawdown as fraction (0–1) or absolute; limit from config or context.
    """
    account = account or {}
    context = context or {}
    drawdown = _get(account, "drawdown")
    if drawdown is None:
        return GuardrailResult(allowed=True, signals=[], reason="ok", metadata={})
    try:
        drawdown = float(drawdown)
    except (TypeError, ValueError):
        return GuardrailResult(allowed=True, signals=[], reason="ok", metadata={})
    limit = float(context.get("max_drawdown_limit", MAX_DRAWDOWN_LIMIT))
    if drawdown >= limit:
        sig = GuardrailSignal(
            signal_type="max_drawdown",
            severity=SEVERITY_BLOCK,
            message=f"drawdown {drawdown:.4f} >= limit {limit}",
            timestamp=time.time(),
            metadata={"drawdown": drawdown, "limit": limit},
        )
        return GuardrailResult(
            allowed=False,
            signals=[sig],
            reason=sig.message,
            metadata={},
        )
    return GuardrailResult(allowed=True, signals=[], reason="ok", metadata={})


def check_daily_loss(
    account: dict[str, Any] | None,
    context: dict[str, Any] | None,
) -> GuardrailResult:
    """
    BLOCK if daily PnL loss exceeds limit.
    Expects account daily_pnl; limit as fraction of equity or absolute from context.
    """
    account = account or {}
    context = context or {}
    daily_pnl = _get(account, "daily_pnl")
    if daily_pnl is None:
        return GuardrailResult(allowed=True, signals=[], reason="ok", metadata={})
    try:
        daily_pnl = float(daily_pnl)
    except (TypeError, ValueError):
        return GuardrailResult(allowed=True, signals=[], reason="ok", metadata={})
    if daily_pnl >= 0:
        return GuardrailResult(allowed=True, signals=[], reason="ok", metadata={})
    limit = float(context.get("daily_loss_limit", DAILY_LOSS_LIMIT))
    equity = _get(account, "equity")
    try:
        equity = float(equity) if equity is not None else 1.0
    except (TypeError, ValueError):
        equity = 1.0
    loss_pct = abs(daily_pnl) / equity if equity > 0 else 0.0
    if loss_pct >= limit:
        sig = GuardrailSignal(
            signal_type="daily_loss",
            severity=SEVERITY_BLOCK,
            message=f"daily loss {loss_pct:.4f} >= limit {limit}",
            timestamp=time.time(),
            metadata={"daily_pnl": daily_pnl, "limit": limit},
        )
        return GuardrailResult(
            allowed=False,
            signals=[sig],
            reason=sig.message,
            metadata={},
        )
    return GuardrailResult(allowed=True, signals=[], reason="ok", metadata={})


def check_volatility_spike(
    market: dict[str, Any] | None,
    context: dict[str, Any] | None,
) -> GuardrailResult:
    """
    BLOCK if volatility >= EXTREME threshold; WARN if >= VOLATILITY_THRESHOLD.
    Expects market volatility (e.g. VIX or realized vol).
    """
    market = market or {}
    context = context or {}
    vol = _get(market, "volatility")
    if vol is None:
        return GuardrailResult(allowed=True, signals=[], reason="ok", metadata={})
    try:
        vol = float(vol)
    except (TypeError, ValueError):
        return GuardrailResult(allowed=True, signals=[], reason="ok", metadata={})
    warn_thresh = float(context.get("volatility_threshold", VOLATILITY_THRESHOLD))
    extreme_thresh = float(context.get("extreme_volatility_threshold", EXTREME_VOLATILITY_THRESHOLD))
    signals: list[GuardrailSignal] = []
    if vol >= extreme_thresh:
        sig = GuardrailSignal(
            signal_type="volatility_spike",
            severity=SEVERITY_BLOCK,
            message=f"volatility {vol} >= extreme threshold {extreme_thresh}",
            timestamp=time.time(),
            metadata={"volatility": vol, "threshold": extreme_thresh},
        )
        signals.append(sig)
        return GuardrailResult(allowed=False, signals=signals, reason=sig.message, metadata={})
    if vol >= warn_thresh:
        sig = GuardrailSignal(
            signal_type="volatility_spike",
            severity=SEVERITY_WARN,
            message=f"volatility {vol} >= warn threshold {warn_thresh}",
            timestamp=time.time(),
            metadata={"volatility": vol, "threshold": warn_thresh},
        )
        signals.append(sig)
    return GuardrailResult(
        allowed=True,
        signals=signals,
        reason="ok" if not signals else signals[0].message,
        metadata={},
    )


def check_strategy_disable(
    strategy_health: dict[str, Any] | None,
    context: dict[str, Any] | None,
) -> GuardrailResult:
    """
    BLOCK if strategy is explicitly disabled (strategy_enabled is False).
    """
    strategy_health = strategy_health or {}
    _ = context
    enabled = _get(strategy_health, "strategy_enabled", True)
    if enabled is False or (isinstance(enabled, str) and enabled.lower() in ("false", "0", "no")):
        sig = GuardrailSignal(
            signal_type="strategy_disable",
            severity=SEVERITY_BLOCK,
            message="strategy explicitly disabled",
            timestamp=time.time(),
            metadata={},
        )
        return GuardrailResult(allowed=False, signals=[sig], reason=sig.message, metadata={})
    return GuardrailResult(allowed=True, signals=[], reason="ok", metadata={})


def check_execution_pause(
    execution_state: dict[str, Any] | None,
    context: dict[str, Any] | None,
) -> GuardrailResult:
    """
    BLOCK if execution is explicitly paused (execution_enabled is False).
    """
    execution_state = execution_state or {}
    _ = context
    enabled = _get(execution_state, "execution_enabled", True)
    if enabled is False or (isinstance(enabled, str) and enabled.lower() in ("false", "0", "no")):
        sig = GuardrailSignal(
            signal_type="execution_pause",
            severity=SEVERITY_BLOCK,
            message="execution explicitly paused",
            timestamp=time.time(),
            metadata={},
        )
        return GuardrailResult(allowed=False, signals=[sig], reason=sig.message, metadata={})
    return GuardrailResult(allowed=True, signals=[], reason="ok", metadata={})
