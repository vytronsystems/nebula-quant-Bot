# Release Evidence Integration

## Evidence backbone

- **DB**: `phase_execution_log`, `artifact_registry`, `audit_run`, `test_run`, `promotion_review` (see migration 003 and spec 05).
- **Filesystem**: `artifacts/phases/`, `artifacts/tests/`, `artifacts/audits/`, `artifacts/releases/`. Naming: `phase_XX_result.md`, `phase_XX_test_report.html`, `phase_XX_audit_report.html`, `phase_XX_artifact_manifest.json`.

## Release gate

- Release checklist can consume: phase results, test reports, audit reports, and `scripts/release_check.py` (nq_release). Control plane can expose `GET /api/artifacts?phase=...` for UI. Final security: run `scripts/check_secrets.py` before release.
