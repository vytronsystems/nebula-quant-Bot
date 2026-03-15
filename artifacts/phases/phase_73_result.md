# Phase 73 — Promotion Queue UI — Result

## Summary

Created the Promotion Queue UI where operators approve promotion of strategies, with audit trail logging.

## Implementation

- **UI**: New route `/operator/promotion-queue`:
  - Table columns: Strategy (name@version), Instrument, Venue, Stage, WinRate, PnL, Trades, Days, Actions
  - WinRate / PnL / Trades / Days read from deployment `meta` (metrics API in Phase 74 will populate these)
  - Buttons: **Promote to Live**, **Move to Paper**, **Move to Backtest**
  - On action: PATCH `/api/deployments/{id}` to set new stage; POST `/api/promotion-review` with fromStage, toStage, decision (approved), strategyId

- **Backend**: Control plane:
  - **PromotionReview** JPA entity and **PromotionReviewRepository**
  - **PromotionReviewController**: GET `/api/promotion-review`, POST `/api/promotion-review` (body: strategyId, fromStage, toStage, decision, evidencePath?, meta?)
  - Persists to existing `promotion_review` table (audit trail)

- **Operator Cockpit**: Added "Promotion Queue" card linking to `/operator/promotion-queue`.

## Modules Affected

- `apps/web/src/app/operator/` — new promotion-queue page, operator hub link
- `services/control-plane/` — PromotionReview entity, repository, controller

## Services Created or Modified

- Control plane: new promotion-review API; no new containers.

## UI Changes

- Promotion Queue screen with table and action buttons; approvals logged to audit trail.

## Infrastructure

- None beyond existing control plane and DB (`promotion_review` table from migration 003).
