# Phase 72 — Strategy Deployment Registry — Result

## Summary

Implemented a persistent registry controlling strategy deployments with full CRUD API.

## Implementation

- **Database**: New table `strategy_deployment` (migration `004_strategy_deployment_registry.sql`) with:
  - `strategy_name`, `strategy_version`, `instrument`, `venue`
  - `environment` (testnet / production)
  - `stage` (backtest, paper, live)
  - `enabled`, `meta`, timestamps
  - Unique constraint on (strategy_name, strategy_version, instrument, venue)
  - Indexes for instrument, venue, stage, environment

- **Control Plane**:
  - **StrategyDeployment** (JPA entity)
  - **StrategyDeploymentRepository** (find by instrument, venue, stage, environment)
  - **StrategyDeploymentDto** (API response/request)
  - **StrategyDeploymentController** at `/api/deployments`:
    - `GET /api/deployments` — list with optional filters: instrument, venue, stage, environment
    - `GET /api/deployments/{id}` — get one
    - `POST /api/deployments` — create (body: strategyName, strategyVersion, instrument, venue, environment?, stage?, enabled?, meta?)
    - `PATCH /api/deployments/{id}` — update stage, environment, enabled, meta

## Modules Affected

- `docker/db/migrations/` — new migration 004
- `services/control-plane/` — domain, repository, dto, controller

## Services Created or Modified

- Control plane: new deployment registry API; no new services.

## UI Changes

- None in this phase (UI integration in Phase 81).

## Infrastructure

- Migration must be applied to Postgres before use (e.g. `psql -f docker/db/migrations/004_strategy_deployment_registry.sql` or run migrations script if present).

## Fail-Closed / Safety

- No order path or credential selection in this phase; registry is metadata only. Phase 76 (Live Routing) will consume stage/environment for routing.
