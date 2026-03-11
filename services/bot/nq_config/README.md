# nq_config

Centralized, deterministic configuration for NEBULA-QUANT v1. Provides typed config models, explicit defaults, environment-variable overrides, and fail-closed validation. No file loading in this phase (env + defaults only).

## Purpose

- **Unify** configuration for system, nq_db, nq_event_store, nq_cache, nq_risk, nq_portfolio, nq_metrics.
- **Load** deterministically from defaults and env vars.
- **Validate** strictly; invalid or missing required values raise `ConfigError`.
- **Avoid** scattered ad-hoc config across modules; ready for incremental adoption.

## Typed config design

All config is represented by dataclasses: `SystemConfig`, `DatabaseModuleConfig`, `EventStoreConfig`, `CacheModuleConfig`, `RiskModuleConfig`, `PortfolioModuleConfig`, `MetricsModuleConfig`, and the top-level `AppConfig` that groups them. Types are explicit; no silent coercion.

## Defaults model

- `build_default_config()` returns an `AppConfig` with documented, in-code defaults only (no env, no files).
- Defaults align with existing module conventions where applicable (e.g. nq_db path `nq_db.sqlite3`, nq_risk 2% per trade, nq_portfolio limits from `PortfolioLimits`).
- Example defaults: `environment="development"`, `app_name="NEBULA-QUANT v1"`, `db_path="nq_db.sqlite3"`, `event_store.use_shared_db=True`, cache/risk/portfolio values as in spec.

## Env override model

Env vars override defaults only when explicitly defined in the loader. Examples:

- `NQ_ENVIRONMENT`, `NQ_APP_NAME`
- `NQ_DB_PATH` (and `NQ_DB_ROOT` for default path when `NQ_DB_PATH` unset)
- `NQ_EVENT_STORE_PATH`
- `NQ_CACHE_DEFAULT_TTL`, `NQ_CACHE_MAX_ENTRIES`, `NQ_CACHE_ALLOW_NONE`
- `NQ_RISK_MAX_RISK_PER_TRADE_PCT`, `NQ_RISK_MAX_DAILY_STRATEGY_RISK_PCT`, etc.
- `NQ_PORTFOLIO_MAX_OPEN_POSITIONS_TOTAL`, etc.
- `NQ_METRICS_ENABLE_OBSERVABILITY`, `NQ_METRICS_DEFAULT_REPORT_NAMESPACE`

Boolean parsing is deterministic (`true`/`false`/`1`/`0`/`yes`/`no`/`on`/`off`, case-insensitive). Numeric parsing validates strictly; invalid values raise `ConfigError`.

## Validation philosophy

- Required string fields (e.g. `environment`, `app_name`, `db_path`) must be non-empty.
- Percentages and counts must be in valid ranges (e.g. risk/portfolio pcts > 0; warning ≤ hard limit where applicable).
- Cache: `default_ttl_seconds >= 0` if set; `max_entries > 0` if set.
- No silent fixes: invalid config raises `ConfigError`; no fabrication of values.

## Fail-closed behavior

- Invalid env value (e.g. non-numeric where numeric required, or out-of-range) → `ConfigError`.
- Empty required string after override → validation fails.
- Nested invalid child config → `validate_app_config` raises; no partial use.

## Intended future integration points

- **nq_db**: read `app_config.db.db_path` (or keep using own config until migrated).
- **nq_event_store**: read `app_config.event_store`.
- **nq_cache**: build `CachePolicy` from `app_config.cache`.
- **nq_risk**: use `app_config.risk` for limits.
- **nq_portfolio**: use `app_config.portfolio` for governance limits.
- **nq_metrics / nq_obs**: use `app_config.metrics` for observability toggles and namespace.

No deep wiring in this phase; modules can adopt incrementally.

## Usage example

```python
from nq_config import load_config, build_default_config, ConfigError

# From defaults + env
config = load_config()
print(config.system.app_name)
print(config.db.db_path)
print(config.risk.max_risk_per_trade_pct)

# Defaults only (e.g. tests)
defaults = build_default_config()
assert defaults.system.environment == "development"
```

## No file loading

This phase does not load YAML, TOML, or JSON. Configuration is **defaults + environment variables** only.
