# NEBULA-QUANT v1 | nq_risk limits (stubs and default policy)

from __future__ import annotations

from typing import Protocol

from nq_risk.models import RiskLimits


class RiskModuleConfigLike(Protocol):
    """Protocol for config with risk settings (e.g. nq_config.RiskModuleConfig)."""

    max_risk_per_trade_pct: float
    max_daily_strategy_risk_pct: float | None
    max_daily_account_risk_pct: float | None
    require_stop_loss: bool
    max_stop_distance_pct: float | None
    warning_risk_per_trade_pct: float | None


# Stub: max risk per trade (e.g. fraction of equity or absolute).
MAX_RISK_PER_TRADE: float = 0.02  # 2% placeholder

# Stub: max daily drawdown (fraction) before halting new risk.
MAX_DAILY_DRAWDOWN: float = 0.05  # 5% placeholder

# Stub: max concurrent open positions.
MAX_CONCURRENT_POSITIONS: int = 5  # placeholder

# Default risk limits for the decision engine (aligned with nq_config defaults).
DEFAULT_RISK_LIMITS: RiskLimits = RiskLimits(
    max_risk_per_trade_pct=0.02,
    max_daily_strategy_risk_pct=None,
    max_daily_account_risk_pct=None,
    require_stop_loss=False,
    max_stop_distance_pct=None,
    warning_risk_per_trade_pct=0.015,
)


def risk_limits_from_config(config: RiskModuleConfigLike) -> RiskLimits:
    """Build RiskLimits from a config (e.g. AppConfig.risk from nq_config)."""
    return RiskLimits(
        max_risk_per_trade_pct=config.max_risk_per_trade_pct,
        max_daily_strategy_risk_pct=config.max_daily_strategy_risk_pct,
        max_daily_account_risk_pct=config.max_daily_account_risk_pct,
        require_stop_loss=config.require_stop_loss,
        max_stop_distance_pct=config.max_stop_distance_pct,
        warning_risk_per_trade_pct=config.warning_risk_per_trade_pct,
    )
