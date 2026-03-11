# NEBULA-QUANT v1 | nq_config defaults

from __future__ import annotations

from pathlib import Path

from nq_config.models import (
    AppConfig,
    CacheModuleConfig,
    DatabaseModuleConfig,
    EventStoreConfig,
    MetricsModuleConfig,
    PortfolioModuleConfig,
    RiskModuleConfig,
    SystemConfig,
)


def build_default_config() -> AppConfig:
    """
    Build AppConfig from explicit, deterministic defaults.
    No env vars; no file loading. Documented defaults only.
    """
    return AppConfig(
        system=SystemConfig(
            environment="development",
            app_name="NEBULA-QUANT v1",
            timezone=None,
            metadata={},
        ),
        db=DatabaseModuleConfig(db_path="nq_db.sqlite3"),
        event_store=EventStoreConfig(db_path=None, use_shared_db=True),
        cache=CacheModuleConfig(
            default_ttl_seconds=None,
            max_entries=None,
            allow_none_values=False,
        ),
        risk=RiskModuleConfig(
            max_risk_per_trade_pct=0.02,
            max_daily_strategy_risk_pct=None,
            max_daily_account_risk_pct=None,
            require_stop_loss=False,
            max_stop_distance_pct=None,
            warning_risk_per_trade_pct=0.015,
        ),
        portfolio=PortfolioModuleConfig(
            max_portfolio_capital_usage_pct=0.95,
            max_strategy_capital_usage_pct=0.25,
            max_open_positions_total=50,
            max_open_positions_per_strategy=10,
            max_daily_drawdown_pct=0.05,
            max_strategy_drawdown_pct=0.10,
            warning_capital_usage_pct=0.80,
            warning_open_positions_pct=0.85,
            warning_drawdown_pct=0.03,
        ),
        metrics=MetricsModuleConfig(
            enable_observability=True,
            default_report_namespace=None,
        ),
    )
