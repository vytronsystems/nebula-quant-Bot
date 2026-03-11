# NEBULA-QUANT v1 | nq_metrics config (placeholder constants)

from __future__ import annotations

from typing import Protocol

# Placeholder: risk-free rate for Sharpe calculation (annualized fraction).
RISK_FREE_RATE: float = 0.05  # 5%

# Placeholder: trading days per year for annualization.
TRADING_DAYS_PER_YEAR: int = 252

# Placeholder: lookback period for Sharpe ratio (number of returns).
SHARPE_LOOKBACK_PERIOD: int = 252


class MetricsModuleConfigLike(Protocol):
    """Protocol for config with metrics/observability settings (e.g. nq_config.MetricsModuleConfig)."""

    enable_observability: bool
    default_report_namespace: str | None


def observability_enabled(config: MetricsModuleConfigLike) -> bool:
    """Return whether observability is enabled from config (e.g. AppConfig.metrics from nq_config)."""
    return config.enable_observability


def default_report_namespace(config: MetricsModuleConfigLike) -> str | None:
    """Return default report namespace from config (e.g. AppConfig.metrics from nq_config)."""
    return config.default_report_namespace
