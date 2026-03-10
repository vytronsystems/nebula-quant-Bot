# NEBULA-QUANT v1 | nq_guardrails rules (placeholder implementations)

from typing import Any

from nq_guardrails.models import GuardrailSignal, GuardrailResult


def check_max_drawdown(
    account: dict[str, Any] | None,
    context: dict[str, Any] | None,
) -> GuardrailResult:
    """Placeholder: max drawdown check. Returns safe result."""
    return GuardrailResult(
        allowed=True,
        signals=[],
        reason="check_max_drawdown: skeleton (no-op)",
        metadata={},
    )


def check_daily_loss(
    account: dict[str, Any] | None,
    context: dict[str, Any] | None,
) -> GuardrailResult:
    """Placeholder: daily loss limit check. Returns safe result."""
    return GuardrailResult(
        allowed=True,
        signals=[],
        reason="check_daily_loss: skeleton (no-op)",
        metadata={},
    )


def check_volatility_spike(
    market: dict[str, Any] | None,
    context: dict[str, Any] | None,
) -> GuardrailResult:
    """Placeholder: volatility spike check. Returns safe result."""
    return GuardrailResult(
        allowed=True,
        signals=[],
        reason="check_volatility_spike: skeleton (no-op)",
        metadata={},
    )


def check_strategy_disable(
    strategy_health: dict[str, Any] | None,
    context: dict[str, Any] | None,
) -> GuardrailResult:
    """Placeholder: strategy disable check. Returns safe result."""
    return GuardrailResult(
        allowed=True,
        signals=[],
        reason="check_strategy_disable: skeleton (no-op)",
        metadata={},
    )


def check_execution_pause(
    execution_state: dict[str, Any] | None,
    context: dict[str, Any] | None,
) -> GuardrailResult:
    """Placeholder: execution pause check. Returns safe result."""
    return GuardrailResult(
        allowed=True,
        signals=[],
        reason="check_execution_pause: skeleton (no-op)",
        metadata={},
    )
