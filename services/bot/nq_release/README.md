# nq_release

**NEBULA-QUANT v1** — Deterministic release governance: packaging, validation, and release decisions.

## Purpose

`nq_release` represents release candidates, validates release readiness from structured inputs (module records, architecture/QA gates), and produces **release manifests**, **blockers**, **evidence**, and **release decisions**. It does **not** deploy, run CI, or mutate source modules. Outputs are for reporting and human/automation governance.

## Release candidate input model

- **release_name**, **version_label** — Identity; may be draft placeholders.
- **module_records** — List of module entries: module_name, included, implemented, integrated, validation_status.
- **architecture_gate** / **qa_gate** — Optional pass/fail (bool or object with `pass`); if provided and False → REJECTED.
- **branch**, **commit_hash** — Optional; included in manifest when provided.

## Validation / blocker model

- **Module validation**: Included modules must be implemented; validation_status must not be `fail`; otherwise CRITICAL blocker. Optional: included modules must be integrated → WARNING blocker.
- **Gate checks**: If architecture_gate or qa_gate is explicitly False → CRITICAL blocker and REJECTED.
- **Evidence**: Each check produces `ReleaseEvidence` (evidence_id, category, value, description).
- **Blockers**: `ReleaseBlocker` (blocker_id, category, severity WARNING|CRITICAL, title, description, related_module).

## Manifest model

- **ReleaseManifest**: manifest_id, release_name, version_label, branch, commit_hash, included_modules (sorted), module_records (sorted by module_name). Metadata JSON-compatible.

## Decision rules

- **REJECTED** — One or more gate checks (architecture, QA) failed.
- **BLOCKED** — At least one CRITICAL blocker (e.g. module not implemented, validation failed).
- **DRAFT** — Empty module list and no gate/critical blockers.
- **APPROVED** — No blockers.
- **READY** — Only WARNING blockers; no critical blockers.

Every decision includes rationale, blocker_ids, and evidence_ids.

## Deterministic guarantees

- Same inputs produce the same manifest, blockers, evidence, and decision.
- Report, manifest, decision, blocker, and evidence ids are counter-based (`release-report-{n}`, `manifest-{n}`, `decision-{n}`, `blocker-{n}`, `ev-{n}`).
- No random ids.

## Future integration

- **CI/CD**: Call `evaluate_release` with build/CI outputs; consume report for gating.
- **Scheduler / orchestrator / dashboards**: Expose release decision and manifest for governance workflows.

No deep wiring in this phase; API is ready for integration.
