# NEBULA-QUANT v1 | nq_promotion rules — deterministic promotion checks

from __future__ import annotations

from typing import Any

from nq_promotion.config import (
    ALLOW_LIVE_ONLY_IF_GUARDRAILS_CLEAR,
    MAX_BACKTEST_DRAWDOWN,
    MAX_PAPER_DRAWDOWN,
    MIN_BACKTEST_PROFIT_FACTOR,
    MIN_BACKTEST_TRADES,
    MIN_BACKTEST_WIN_RATE,
    MIN_PAPER_TRADES,
    MIN_PAPER_WIN_RATE,
    MIN_WALKFORWARD_PASS_RATE,
)
from nq_promotion.status_map import is_transition_allowed


def _get(data: dict[str, Any] | None, key: str, default: Any = None) -> Any:
    if data is None:
        return default
    return data.get(key, default)


def check_transition_allowed(
    current_status: str,
    target_status: str,
) -> tuple[bool, list[str], list[str]]:
    """Returns (allowed, blocking_issues, warnings)."""
    blocking: list[str] = []
    warnings: list[str] = []
    if not current_status or not target_status:
        blocking.append("missing current_status or target_status")
        return False, blocking, warnings
    allowed = is_transition_allowed(current_status, target_status)
    if not allowed:
        blocking.append(f"transition {current_status} -> {target_status} not allowed")
    return allowed, blocking, warnings


def check_backtest_requirements(
    backtest_summary: dict[str, Any] | None,
    config: Any = None,
) -> tuple[list[str], list[str]]:
    """Returns (blocking_issues, warnings). Fail-closed: missing summary = blocking."""
    blocking: list[str] = []
    warnings: list[str] = []
    if not backtest_summary:
        blocking.append("backtest_summary missing")
        return blocking, warnings
    min_trades = getattr(config, "MIN_BACKTEST_TRADES", None) or MIN_BACKTEST_TRADES
    min_wr = getattr(config, "MIN_BACKTEST_WIN_RATE", None) or MIN_BACKTEST_WIN_RATE
    min_pf = getattr(config, "MIN_BACKTEST_PROFIT_FACTOR", None) or MIN_BACKTEST_PROFIT_FACTOR
    max_dd = getattr(config, "MAX_BACKTEST_DRAWDOWN", None) or MAX_BACKTEST_DRAWDOWN

    total_trades = _get(backtest_summary, "total_trades")
    if total_trades is not None:
        try:
            if int(total_trades) < min_trades:
                blocking.append(f"backtest total_trades {total_trades} < {min_trades}")
        except (TypeError, ValueError):
            blocking.append("backtest total_trades invalid")
    else:
        blocking.append("backtest total_trades missing")

    win_rate = _get(backtest_summary, "win_rate")
    if win_rate is not None:
        try:
            if float(win_rate) < min_wr:
                blocking.append(f"backtest win_rate {win_rate} < {min_wr}")
        except (TypeError, ValueError):
            blocking.append("backtest win_rate invalid")
    else:
        blocking.append("backtest win_rate missing")

    pf = _get(backtest_summary, "profit_factor")
    if pf is not None:
        try:
            if float(pf) < min_pf:
                blocking.append(f"backtest profit_factor {pf} < {min_pf}")
        except (TypeError, ValueError):
            pass  # optional
    else:
        warnings.append("backtest profit_factor missing")

    max_drawdown = _get(backtest_summary, "max_drawdown")
    if max_drawdown is not None:
        try:
            dd = float(max_drawdown)
            if dd > max_dd:
                blocking.append(f"backtest max_drawdown {dd} > {max_dd}")
        except (TypeError, ValueError):
            blocking.append("backtest max_drawdown invalid")
    else:
        blocking.append("backtest max_drawdown missing")

    return blocking, warnings


def check_walkforward_requirements(
    walkforward_summary: dict[str, Any] | None,
    config: Any = None,
) -> tuple[list[str], list[str]]:
    """Returns (blocking_issues, warnings). Fail-closed: missing summary = blocking."""
    blocking: list[str] = []
    warnings: list[str] = []
    if not walkforward_summary:
        blocking.append("walkforward_summary missing")
        return blocking, warnings
    min_pass = getattr(config, "MIN_WALKFORWARD_PASS_RATE", None) or MIN_WALKFORWARD_PASS_RATE
    pass_rate = _get(walkforward_summary, "pass_rate")
    if pass_rate is not None:
        try:
            if float(pass_rate) < min_pass:
                blocking.append(f"walkforward pass_rate {pass_rate} < {min_pass}")
        except (TypeError, ValueError):
            blocking.append("walkforward pass_rate invalid")
    else:
        blocking.append("walkforward pass_rate missing")
    return blocking, warnings


def check_paper_requirements(
    paper_summary: dict[str, Any] | None,
    config: Any = None,
) -> tuple[list[str], list[str]]:
    """Returns (blocking_issues, warnings). Fail-closed: missing summary = blocking."""
    blocking: list[str] = []
    warnings: list[str] = []
    if not paper_summary:
        blocking.append("paper_summary missing")
        return blocking, warnings
    min_trades = getattr(config, "MIN_PAPER_TRADES", None) or MIN_PAPER_TRADES
    min_wr = getattr(config, "MIN_PAPER_WIN_RATE", None) or MIN_PAPER_WIN_RATE
    max_dd = getattr(config, "MAX_PAPER_DRAWDOWN", None) or MAX_PAPER_DRAWDOWN

    total_trades = _get(paper_summary, "total_trades") or _get(paper_summary, "closed_trades")
    if total_trades is not None:
        try:
            if int(total_trades) < min_trades:
                blocking.append(f"paper total_trades {total_trades} < {min_trades}")
        except (TypeError, ValueError):
            blocking.append("paper total_trades invalid")
    else:
        blocking.append("paper total_trades missing")

    win_rate = _get(paper_summary, "win_rate")
    if win_rate is not None:
        try:
            if float(win_rate) < min_wr:
                blocking.append(f"paper win_rate {win_rate} < {min_wr}")
        except (TypeError, ValueError):
            blocking.append("paper win_rate invalid")
    else:
        blocking.append("paper win_rate missing")

    max_drawdown = _get(paper_summary, "max_drawdown")
    if max_drawdown is not None:
        try:
            dd = float(max_drawdown)
            if dd > max_dd:
                blocking.append(f"paper max_drawdown {dd} > {max_dd}")
        except (TypeError, ValueError):
            blocking.append("paper max_drawdown invalid")
    else:
        blocking.append("paper max_drawdown missing")

    return blocking, warnings


def check_guardrail_requirements(
    guardrail_summary: dict[str, Any] | None,
    config: Any = None,
) -> tuple[list[str], list[str]]:
    """Returns (blocking_issues, warnings). For live, guardrails must be clear if config requires."""
    blocking: list[str] = []
    warnings: list[str] = []
    require_clear = getattr(config, "ALLOW_LIVE_ONLY_IF_GUARDRAILS_CLEAR", None)
    if require_clear is False:
        return blocking, warnings
    if require_clear is None:
        require_clear = ALLOW_LIVE_ONLY_IF_GUARDRAILS_CLEAR
    if not require_clear:
        return blocking, warnings
    if not guardrail_summary:
        blocking.append("guardrail_summary missing (required for live)")
        return blocking, warnings
    allowed = _get(guardrail_summary, "allowed", True)
    if allowed is False:
        blocking.append("guardrails not clear (allowed=False)")
    return blocking, warnings
