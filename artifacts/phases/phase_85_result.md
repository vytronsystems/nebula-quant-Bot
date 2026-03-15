# Phase 85 — Dataset Versioning — Result

## Summary

Store and version datasets for research; snapshots, dataset identifiers, reproducibility.

## Implementation

- **DB**: Migration 006 — dataset_version table (dataset_id, version, snapshot_path, meta).
- **Control Plane**: DatasetVersion entity, DatasetVersionRepository, DatasetVersionController — GET /api/datasets (optional datasetId), POST /api/datasets (datasetId, version, snapshotPath).

## Modules Affected

- docker/db/migrations/006_alerts_and_datasets.sql
- services/control-plane domain/DatasetVersion.java, repository, api/DatasetVersionController.java
