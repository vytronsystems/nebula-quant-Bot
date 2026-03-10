# nq_strategy_registry

**NEBULA-QUANT v1** — Strategy lifecycle control layer (skeleton).

## Purpose

`nq_strategy_registry` is the **strategy lifecycle control layer**. It registers and tracks strategies across the institutional pipeline. It does **not** execute strategies, run backtests, or connect to external systems; it only manages strategy definitions and lifecycle state (identity, versioning, status, market/timeframe metadata, hypothesis, activation/deactivation rules, ownership).

## Institutional strategy lifecycle

Strategies move through stages defined in `docs/12_STRATEGY_REGISTRY_STANDARD.md`: **idea → research → backtest → paper → live**, with terminal/control states **disabled**, **retired**, **rejected**. The registry records status so that governance (research → backtest → paper → live) can be enforced and audited.

## Why skeleton-only

This module provides the API and in-memory storage placeholders so that the rest of the platform can depend on a stable registry interface. Database integration, version history, and persistence will be added in a later iteration without changing the public API.

## How this supports research → backtest → paper → live governance

- **Research / backtest:** Strategies are registered with status `idea` or `research`; promotion to `backtest` after hypothesis and config are in place.
- **Paper / live:** Only strategies that reach `paper` or `live` (after walk-forward, audit, and approval) are considered active; the registry exposes `active_strategies` and `disabled_strategies` for dashboards and runbooks.
- **Auditability:** Every strategy has `strategy_id`, `version`, `status`, `created_at`, `updated_at` for traceability.
