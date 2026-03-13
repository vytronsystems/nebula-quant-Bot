# Phase 60 — Evidence Backbone — Result

## Objective
Implement DB-first and filesystem-second evidence tracking.

## Completed tasks

1. **Add DB schema/tables for phase/test/audit/artifact tracking**
   - Added `docker/db/migrations/003_evidence_backbone.sql` with tables: `phase_execution_log`, `artifact_registry`, `audit_run`, `test_run`, `promotion_review`, `paper_trading_daily_snapshot`, `venue_account_snapshot`, `instrument_registry`, `instrument_activation_log` (per Data/Audit Evidence Standard).
   - Migration applied via `docker compose exec ... psql ... -f 003_evidence_backbone.sql`.

2. **Create `artifacts/` structure**
   - Structure already present from Phase 59; `nq_evidence.ensure_artifacts_structure()` creates/ensures: `phases/`, `tests/`, `audits/`, `backtests/`, `walkforward/`, `paper-trading/`, `frontend-review/`, `releases/`.

3. **Add helpers to write manifests and HTML reports**
   - New package `services/bot/nq_evidence` with `backend.py`:
     - `register_phase_start(phase)` → log id
     - `register_phase_end(log_id, status, details)`
     - `register_artifact(phase, artifact_path, artifact_kind)`
     - `write_manifest(phase, manifest)` → path to `artifacts/phases/phase_XX_artifact_manifest.json`
     - `write_html_report(phase, report_type, html)` → path for test or audit report
     - `ensure_artifacts_structure()` → artifacts root
   - Uses `PG_DSN` from env; artifacts root from `NQ_REPO_ROOT` or derived from `__file__`.

4. **Ensure each future phase can register itself in DB and filesystem**
   - Phases can call `nq_evidence.register_phase_start("60")`, then at end `register_phase_end(...)`, `register_artifact(...)`, `write_manifest(...)`, `write_html_report(...)`.
   - Phase execution log (file) continues to be appended in `artifacts/phase_execution_log.jsonl` as before.

## Required outputs

- DB schema: applied.
- Artifacts structure: present and ensured by helper.
- Helpers: implemented in `nq_evidence`.
- Phase 60 artifacts: this result, test report, audit report, manifest.
