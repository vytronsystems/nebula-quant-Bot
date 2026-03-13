# Final Security and Audit (Phase 70)

## Security checks

- **Secrets**: No hardcoded secrets in committed files. Run `python3 scripts/check_secrets.py` from repo root; must exit 0. CI should run this.
- **Env**: All sensitive config (Postgres, Grafana, Telegram) via environment variables; `.env.example` at root and `docker/.env.example` document required vars.
- **Control plane**: Auth foundation in place; MFA support points for sensitive actions. No quant logic in Java.

## Audit trail

- Phase execution: `artifacts/phase_execution_log.jsonl` and DB table `phase_execution_log`.
- Per-phase artifacts: result.md, test_report.html, audit_report.html, artifact_manifest.json under `artifacts/phases/`, `artifacts/tests/`, `artifacts/audits/`.
- Instrument activation: `instrument_activation_log`. Venue snapshots: `venue_account_snapshot`. Reconciliation: nq_reconciliation modules with typed summaries.

## Docker wiring (new services)

- **Control plane**: Java 21 / Maven. To run in Docker: add Dockerfile in `services/control-plane` (e.g. multi-stage Maven build) and a service in compose pointing at it; port 8081.
- **Web**: Next.js. To run in Docker: add Dockerfile in `apps/web` (node build + start) and a service in compose; port 3000 for app (Grafana already uses 3000 — use 3001 for web app or change Grafana port).
- Example override: see `docker/README_NEW_SERVICES.md` for how to add control-plane and web to the stack when Dockerfiles are ready.
