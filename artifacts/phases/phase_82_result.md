# Phase 82 — Instrument Management UI — Result

## Summary

Allow enabling/disabling trading instruments; add instrument; activate/deactivate; assign strategies (via deployments).

## Implementation

- **Control Plane**: InstrumentRegistryController — POST /api/instruments (venue, symbol, assetType, active), PATCH /api/instruments/{id} (active, meta). InstrumentRecordDto now includes id.
- **UI**: operator/instruments — Add instrument form (venue, symbol), Activate/Deactivate button per row (PATCH by id). Strategies assignable via deployments filtered by instrument.

## Modules Affected

- services/control-plane api/InstrumentRegistryController.java, dto/InstrumentRecordDto.java
- apps/web/src/app/operator/instruments/page.tsx
