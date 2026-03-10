# NEBULA-QUANT v1 | nq_promotion — allowed lifecycle transitions

from __future__ import annotations

# Allowed (from_status -> to_status). All other transitions are blocked by default.
ALLOWED_TRANSITIONS: set[tuple[str, str]] = {
    ("idea", "research"),
    ("research", "backtest"),
    ("backtest", "walkforward"),
    ("walkforward", "paper"),
    ("paper", "live"),
    ("idea", "disabled"),
    ("research", "disabled"),
    ("backtest", "disabled"),
    ("walkforward", "disabled"),
    ("paper", "disabled"),
    ("live", "disabled"),
    ("live", "retired"),
    ("disabled", "research"),  # re-enable path
    ("disabled", "backtest"),
    ("disabled", "walkforward"),
    ("disabled", "paper"),
    ("disabled", "live"),
}


def is_transition_allowed(from_status: str, to_status: str) -> bool:
    """Return True only if (from_status, to_status) is in the allowed set. Normalize to lowercase."""
    if not from_status or not to_status:
        return False
    key = (from_status.strip().lower(), to_status.strip().lower())
    return key in ALLOWED_TRANSITIONS
