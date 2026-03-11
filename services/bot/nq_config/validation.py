# NEBULA-QUANT v1 | nq_config validation (fail-closed)

from __future__ import annotations

from nq_config.models import (
    AppConfig,
    CacheModuleConfig,
    ConfigError,
    DatabaseModuleConfig,
    EventStoreConfig,
    MetricsModuleConfig,
    PortfolioModuleConfig,
    RiskModuleConfig,
    SystemConfig,
)


def validate_system(c: SystemConfig) -> None:
    if not (c.environment and c.environment.strip()):
        raise ConfigError("system.environment must be non-empty")
    if not (c.app_name and c.app_name.strip()):
        raise ConfigError("system.app_name must be non-empty")


def validate_db(c: DatabaseModuleConfig) -> None:
    if not (c.db_path and c.db_path.strip()):
        raise ConfigError("db.db_path must be non-empty")


def validate_event_store(c: EventStoreConfig) -> None:
    # db_path can be None when use_shared_db is True
    pass


def validate_cache(c: CacheModuleConfig) -> None:
    if c.default_ttl_seconds is not None and c.default_ttl_seconds < 0:
        raise ConfigError("cache.default_ttl_seconds must be >= 0")
    if c.max_entries is not None and c.max_entries <= 0:
        raise ConfigError("cache.max_entries must be > 0 when set")


def validate_risk(c: RiskModuleConfig) -> None:
    if c.max_risk_per_trade_pct <= 0:
        raise ConfigError("risk.max_risk_per_trade_pct must be > 0")
    if c.max_daily_strategy_risk_pct is not None and c.max_daily_strategy_risk_pct <= 0:
        raise ConfigError("risk.max_daily_strategy_risk_pct must be > 0 when set")
    if c.max_daily_account_risk_pct is not None and c.max_daily_account_risk_pct <= 0:
        raise ConfigError("risk.max_daily_account_risk_pct must be > 0 when set")
    if c.max_stop_distance_pct is not None and c.max_stop_distance_pct <= 0:
        raise ConfigError("risk.max_stop_distance_pct must be > 0 when set")
    if c.warning_risk_per_trade_pct is not None:
        if c.warning_risk_per_trade_pct <= 0:
            raise ConfigError("risk.warning_risk_per_trade_pct must be > 0 when set")
        if c.warning_risk_per_trade_pct > c.max_risk_per_trade_pct:
            raise ConfigError("risk.warning_risk_per_trade_pct must not exceed max_risk_per_trade_pct")


def validate_portfolio(c: PortfolioModuleConfig) -> None:
    if c.max_portfolio_capital_usage_pct <= 0 or c.max_portfolio_capital_usage_pct > 1.0:
        raise ConfigError("portfolio.max_portfolio_capital_usage_pct must be in (0, 1]")
    if c.max_strategy_capital_usage_pct <= 0 or c.max_strategy_capital_usage_pct > 1.0:
        raise ConfigError("portfolio.max_strategy_capital_usage_pct must be in (0, 1]")
    if c.max_open_positions_total <= 0:
        raise ConfigError("portfolio.max_open_positions_total must be > 0")
    if c.max_open_positions_per_strategy <= 0:
        raise ConfigError("portfolio.max_open_positions_per_strategy must be > 0")
    if c.max_daily_drawdown_pct <= 0 or c.max_daily_drawdown_pct > 1.0:
        raise ConfigError("portfolio.max_daily_drawdown_pct must be in (0, 1]")
    if c.max_strategy_drawdown_pct <= 0 or c.max_strategy_drawdown_pct > 1.0:
        raise ConfigError("portfolio.max_strategy_drawdown_pct must be in (0, 1]")
    if c.warning_capital_usage_pct <= 0 or c.warning_capital_usage_pct > 1.0:
        raise ConfigError("portfolio.warning_capital_usage_pct must be in (0, 1]")
    if c.warning_open_positions_pct <= 0 or c.warning_open_positions_pct > 1.0:
        raise ConfigError("portfolio.warning_open_positions_pct must be in (0, 1]")
    if c.warning_drawdown_pct <= 0 or c.warning_drawdown_pct > 1.0:
        raise ConfigError("portfolio.warning_drawdown_pct must be in (0, 1]")
    if c.warning_capital_usage_pct > c.max_portfolio_capital_usage_pct:
        raise ConfigError("portfolio.warning_capital_usage_pct must not exceed max_portfolio_capital_usage_pct")
    if c.warning_drawdown_pct > c.max_daily_drawdown_pct:
        raise ConfigError("portfolio.warning_drawdown_pct must not exceed max_daily_drawdown_pct")


def validate_metrics(c: MetricsModuleConfig) -> None:
    # Light validation; fields are well-typed
    if c.default_report_namespace is not None and not c.default_report_namespace.strip():
        raise ConfigError("metrics.default_report_namespace must be non-empty when set")


def validate_app_config(config: AppConfig) -> None:
    """Validate full AppConfig and all nested configs. Raises ConfigError on first failure."""
    validate_system(config.system)
    validate_db(config.db)
    validate_event_store(config.event_store)
    validate_cache(config.cache)
    validate_risk(config.risk)
    validate_portfolio(config.portfolio)
    validate_metrics(config.metrics)
