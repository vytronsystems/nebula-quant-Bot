# NEBULA-QUANT v1 | nq_config loader (defaults + env, no file loading)

from __future__ import annotations

import os
from pathlib import Path

from nq_config.defaults import build_default_config
from nq_config.env import get_env, parse_bool, parse_float, parse_float_optional, parse_int, parse_int_optional
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
from nq_config.validation import validate_app_config


def _default_db_path() -> str:
    root = Path(os.getenv("NQ_DB_ROOT", Path.cwd()))
    return str(root / "nq_db.sqlite3")


def load_config_from_env(base: AppConfig | None = None) -> AppConfig:
    """
    Build config from defaults, then apply explicit env overrides.
    Validates and returns. No file loading.
    """
    config = base or build_default_config()

    # System
    env_val = get_env("NQ_ENVIRONMENT")
    if env_val is not None and env_val.strip():
        config = _replace(config, system=SystemConfig(
            environment=env_val.strip(),
            app_name=config.system.app_name,
            timezone=config.system.timezone,
            metadata=config.system.metadata or {},
        ))
    app_val = get_env("NQ_APP_NAME")
    if app_val is not None and app_val.strip():
        config = _replace(config, system=SystemConfig(
            environment=config.system.environment,
            app_name=app_val.strip(),
            timezone=config.system.timezone,
            metadata=config.system.metadata or {},
        ))

    # DB
    db_val = get_env("NQ_DB_PATH")
    if db_val is not None and db_val.strip():
        config = _replace(config, db=DatabaseModuleConfig(db_path=db_val.strip()))
    else:
        config = _replace(config, db=DatabaseModuleConfig(db_path=_default_db_path()))

    # Event store (shared DB by default: same path as db)
    es_path = get_env("NQ_EVENT_STORE_PATH")
    if es_path is not None and es_path.strip():
        config = _replace(config, event_store=EventStoreConfig(db_path=es_path.strip(), use_shared_db=False))
    else:
        config = _replace(config, event_store=EventStoreConfig(db_path=config.db.db_path, use_shared_db=True))

    # Cache
    ttl = parse_float_optional(get_env("NQ_CACHE_DEFAULT_TTL"))
    max_ent = parse_int_optional(get_env("NQ_CACHE_MAX_ENTRIES"))
    allow_none = get_env("NQ_CACHE_ALLOW_NONE")
    allow_none_bool = config.cache.allow_none_values
    if allow_none is not None:
        allow_none_bool = parse_bool(allow_none, default=config.cache.allow_none_values)
    config = _replace(config, cache=CacheModuleConfig(
        default_ttl_seconds=ttl if ttl is not None else config.cache.default_ttl_seconds,
        max_entries=max_ent if max_ent is not None else config.cache.max_entries,
        allow_none_values=allow_none_bool,
    ))

    # Risk
    r = config.risk
    r_max = parse_float(get_env("NQ_RISK_MAX_RISK_PER_TRADE_PCT"), default=r.max_risk_per_trade_pct, min_val=1e-9)
    r_ds = parse_float_optional(get_env("NQ_RISK_MAX_DAILY_STRATEGY_RISK_PCT")) or r.max_daily_strategy_risk_pct
    r_da = parse_float_optional(get_env("NQ_RISK_MAX_DAILY_ACCOUNT_RISK_PCT")) or r.max_daily_account_risk_pct
    r_sl = get_env("NQ_RISK_REQUIRE_STOP_LOSS")
    r_sl_bool = parse_bool(r_sl, default=r.require_stop_loss) if r_sl is not None else r.require_stop_loss
    r_stop = parse_float_optional(get_env("NQ_RISK_MAX_STOP_DISTANCE_PCT")) or r.max_stop_distance_pct
    r_warn = parse_float_optional(get_env("NQ_RISK_WARNING_RISK_PER_TRADE_PCT")) or r.warning_risk_per_trade_pct
    config = _replace(config, risk=RiskModuleConfig(
        max_risk_per_trade_pct=r_max,
        max_daily_strategy_risk_pct=r_ds,
        max_daily_account_risk_pct=r_da,
        require_stop_loss=r_sl_bool,
        max_stop_distance_pct=r_stop,
        warning_risk_per_trade_pct=r_warn,
    ))

    # Portfolio
    p = config.portfolio
    p_cap = parse_float(get_env("NQ_PORTFOLIO_MAX_PORTFOLIO_CAPITAL_USAGE_PCT"), default=p.max_portfolio_capital_usage_pct, min_val=1e-9, max_val=1.0)
    p_strat = parse_float(get_env("NQ_PORTFOLIO_MAX_STRATEGY_CAPITAL_USAGE_PCT"), default=p.max_strategy_capital_usage_pct, min_val=1e-9, max_val=1.0)
    p_pos = parse_int(get_env("NQ_PORTFOLIO_MAX_OPEN_POSITIONS_TOTAL"), default=p.max_open_positions_total, min_val=1)
    p_pos_strat = parse_int(get_env("NQ_PORTFOLIO_MAX_OPEN_POSITIONS_PER_STRATEGY"), default=p.max_open_positions_per_strategy, min_val=1)
    p_dd = parse_float(get_env("NQ_PORTFOLIO_MAX_DAILY_DRAWDOWN_PCT"), default=p.max_daily_drawdown_pct, min_val=1e-9, max_val=1.0)
    p_sdd = parse_float(get_env("NQ_PORTFOLIO_MAX_STRATEGY_DRAWDOWN_PCT"), default=p.max_strategy_drawdown_pct, min_val=1e-9, max_val=1.0)
    p_wcap = parse_float(get_env("NQ_PORTFOLIO_WARNING_CAPITAL_USAGE_PCT"), default=p.warning_capital_usage_pct, min_val=1e-9, max_val=1.0)
    p_wpos = parse_float(get_env("NQ_PORTFOLIO_WARNING_OPEN_POSITIONS_PCT"), default=p.warning_open_positions_pct, min_val=1e-9, max_val=1.0)
    p_wdd = parse_float(get_env("NQ_PORTFOLIO_WARNING_DRAWDOWN_PCT"), default=p.warning_drawdown_pct, min_val=1e-9, max_val=1.0)
    config = _replace(config, portfolio=PortfolioModuleConfig(
        max_portfolio_capital_usage_pct=p_cap,
        max_strategy_capital_usage_pct=p_strat,
        max_open_positions_total=p_pos,
        max_open_positions_per_strategy=p_pos_strat,
        max_daily_drawdown_pct=p_dd,
        max_strategy_drawdown_pct=p_sdd,
        warning_capital_usage_pct=p_wcap,
        warning_open_positions_pct=p_wpos,
        warning_drawdown_pct=p_wdd,
    ))

    # Metrics
    m_obs = get_env("NQ_METRICS_ENABLE_OBSERVABILITY")
    m_obs_bool = parse_bool(m_obs, default=config.metrics.enable_observability) if m_obs is not None else config.metrics.enable_observability
    m_ns = get_env("NQ_METRICS_DEFAULT_REPORT_NAMESPACE")
    m_ns_val = m_ns.strip() if m_ns and m_ns.strip() else config.metrics.default_report_namespace
    config = _replace(config, metrics=MetricsModuleConfig(enable_observability=m_obs_bool, default_report_namespace=m_ns_val))

    validate_app_config(config)
    return config


def _replace(
    config: AppConfig,
    system: SystemConfig | None = None,
    db: DatabaseModuleConfig | None = None,
    event_store: EventStoreConfig | None = None,
    cache: CacheModuleConfig | None = None,
    risk: RiskModuleConfig | None = None,
    portfolio: PortfolioModuleConfig | None = None,
    metrics: MetricsModuleConfig | None = None,
) -> AppConfig:
    return AppConfig(
        system=system or config.system,
        db=db or config.db,
        event_store=event_store or config.event_store,
        cache=cache or config.cache,
        risk=risk or config.risk,
        portfolio=portfolio or config.portfolio,
        metrics=metrics or config.metrics,
    )


def load_config() -> AppConfig:
    """Load config from defaults + environment. Deterministic. No file loading."""
    return load_config_from_env()
