# Phase 84 — Alert System — Result

## Summary

Operational alerts: dashboard, Telegram, email. Triggered by degradation, system failure, risk breach.

## Implementation

- **DB**: Migration 006 — alerts table (channel, severity, title, body, trigger_type, meta).
- **Control Plane**: Alert entity, AlertRepository, AlertsController — GET /api/alerts, POST /api/alerts (channel, severity, title, body, triggerType). Dashboard links to /api/alerts.

## Modules Affected

- docker/db/migrations/006_alerts_and_datasets.sql
- services/control-plane domain/Alert.java, repository, api/AlertsController.java
