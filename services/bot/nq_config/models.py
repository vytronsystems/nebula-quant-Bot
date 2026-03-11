# NEBULA-QUANT v1 | nq_config models

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ConfigError(Exception):
    """Deterministic configuration exception. Raised on invalid or missing required config."""


@dataclass(slots=True)
class SystemConfig:
    """System-level settings."""

    environment: str
    app_name: str
    timezone: str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class DatabaseModuleConfig:
    """nq_db persistence settings."""

    db_path: str


@dataclass(slots=True)
class EventStoreConfig:
    """nq_event_store settings."""

    db_path: str | None = None
    use_shared_db: bool = True


@dataclass(slots=True)
class CacheModuleConfig:
    """nq_cache settings."""

    default_ttl_seconds: float | None = None
    max_entries: int | None = None
    allow_none_values: bool = False


@dataclass(slots=True)
class RiskModuleConfig:
    """nq_risk settings."""

    max_risk_per_trade_pct: float
    max_daily_strategy_risk_pct: float | None = None
    max_daily_account_risk_pct: float | None = None
    require_stop_loss: bool = False
    max_stop_distance_pct: float | None = None
    warning_risk_per_trade_pct: float | None = None


@dataclass(slots=True)
class PortfolioModuleConfig:
    """nq_portfolio governance settings."""

    max_portfolio_capital_usage_pct: float
    max_strategy_capital_usage_pct: float
    max_open_positions_total: int
    max_open_positions_per_strategy: int
    max_daily_drawdown_pct: float
    max_strategy_drawdown_pct: float
    warning_capital_usage_pct: float
    warning_open_positions_pct: float
    warning_drawdown_pct: float


@dataclass(slots=True)
class MetricsModuleConfig:
    """nq_metrics / observability settings."""

    enable_observability: bool = True
    default_report_namespace: str | None = None


@dataclass(slots=True)
class AppConfig:
    """Top-level aggregate config grouping all module configs."""

    system: SystemConfig
    db: DatabaseModuleConfig
    event_store: EventStoreConfig
    cache: CacheModuleConfig
    risk: RiskModuleConfig
    portfolio: PortfolioModuleConfig
    metrics: MetricsModuleConfig
