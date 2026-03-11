from __future__ import annotations

# NEBULA-QUANT v1 | nq_portfolio — configuration defaults (skeleton)

from typing import Protocol

# Safe, conservative defaults for portfolio constraints.
# These values are placeholders and can be tightened/relaxed in later iterations.

DEFAULT_PORTFOLIO_CASH: float = 0.0

# Maximum weight per strategy (fraction of portfolio equity, e.g. 0.2 = 20%).
DEFAULT_MAX_STRATEGY_WEIGHT: float = 0.2

# Maximum weight per individual symbol (fraction of portfolio equity).
DEFAULT_MAX_SYMBOL_WEIGHT: float = 0.05

# Maximum gross exposure relative to equity (e.g. 1.0 = 100%).
DEFAULT_MAX_GROSS_EXPOSURE: float = 1.0

# Maximum absolute net exposure relative to equity (e.g. 0.5 = 50%).
DEFAULT_MAX_NET_EXPOSURE: float = 0.5

# Maximum number of open positions in the portfolio.
DEFAULT_MAX_POSITIONS: int = 50

# --- Portfolio risk engine (governance) defaults ---

from nq_portfolio.models import PortfolioLimits


class PortfolioModuleConfigLike(Protocol):
    """Protocol for config with portfolio limits (e.g. nq_config.PortfolioModuleConfig)."""

    max_portfolio_capital_usage_pct: float
    max_strategy_capital_usage_pct: float
    max_open_positions_total: int
    max_open_positions_per_strategy: int
    max_daily_drawdown_pct: float
    max_strategy_drawdown_pct: float
    warning_capital_usage_pct: float
    warning_open_positions_pct: float
    warning_drawdown_pct: float


DEFAULT_PORTFOLIO_LIMITS: PortfolioLimits = PortfolioLimits(
    max_portfolio_capital_usage_pct=0.95,
    max_strategy_capital_usage_pct=0.25,
    max_open_positions_total=50,
    max_open_positions_per_strategy=10,
    max_daily_drawdown_pct=0.05,
    max_strategy_drawdown_pct=0.10,
    warning_capital_usage_pct=0.80,
    warning_open_positions_pct=0.85,
    warning_drawdown_pct=0.03,
)


def portfolio_limits_from_config(config: PortfolioModuleConfigLike) -> PortfolioLimits:
    """Build PortfolioLimits from a config (e.g. AppConfig.portfolio from nq_config)."""
    return PortfolioLimits(
        max_portfolio_capital_usage_pct=config.max_portfolio_capital_usage_pct,
        max_strategy_capital_usage_pct=config.max_strategy_capital_usage_pct,
        max_open_positions_total=config.max_open_positions_total,
        max_open_positions_per_strategy=config.max_open_positions_per_strategy,
        max_daily_drawdown_pct=config.max_daily_drawdown_pct,
        max_strategy_drawdown_pct=config.max_strategy_drawdown_pct,
        warning_capital_usage_pct=config.warning_capital_usage_pct,
        warning_open_positions_pct=config.warning_open_positions_pct,
        warning_drawdown_pct=config.warning_drawdown_pct,
    )

