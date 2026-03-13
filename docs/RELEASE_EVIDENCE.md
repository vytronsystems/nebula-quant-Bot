# Release Evidence Integration

Per Phase 70: release evidence integration.

## Evidence backbone

- **DB**: `phase_execution_log`, `artifact_registry`, `audit_run`, `test_run`, `promotion_review` (003_evidence_backbone).
- **Filesystem**: `artifacts/phases/`, `artifacts/tests/`, `artifacts/audits/` with phase_XX_result.md, phase_XX_test_report.html, phase_XX_audit_report.html, phase_XX_artifact_manifest.json.
- **Phase log**: `artifacts/phase_execution_log.jsonl` (append per phase).
- **Helpers**: `nq_evidence` (register_phase_start/end, register_artifact, write_manifest, write_html_report).

## Release checklist

- Run `scripts/check_secrets.py` (no hardcoded secrets).
- Run tests from repo root: `python3 -m unittest discover -s tests`; `PYTHONPATH=services/bot python3 -m pytest services/bot` when pytest available.
- Control plane: `mvn compile` / `mvn spring-boot:run` when Java/Maven available.
- Frontend: `cd apps/web && npm run build` when Node available.
- Docker: `docker compose up` (Postgres, Redis, Grafana, Prometheus, Alertmanager, bot) from `docker/`.
