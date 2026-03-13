# ROOT INSTRUCTION — ONE COMMAND ENTRYPOINT FOR CURSOR

Read every file in this folder tree in the exact order below and execute the work accordingly.
Do not improvise architecture outside these files.
Do not skip steps.
Do not mark work complete without artifacts and tests.

## Read order
1. `governance/01_NON_NEGOTIABLES.md`
2. `governance/02_DEFINITION_OF_DONE.md`
3. `governance/03_FORBIDDEN_SHORTCUTS.md`
4. `specs/01_CURRENT_REPO_AUDIT_CONTEXT.md`
5. `specs/02_TARGET_ARCHITECTURE.md`
6. `specs/03_GAP_REMEDIATION_PLAN.md`
7. `specs/04_STACK_DECISIONS.md`
8. `specs/05_DATA_AUDIT_EVIDENCE_STANDARD.md`
9. `specs/06_SECURITY_AND_SECRETS_STANDARD.md`
10. `specs/07_FRONTEND_FUTURISTIC_PRODUCT_SPEC.md`
11. `specs/08_CONTROL_PLANE_SPEC.md`
12. `specs/09_VENUE_AND_RECONCILIATION_SPEC.md`
13. `specs/10_EXECUTION_ORDER.md`
14. every file in `phases/` in numeric order

## Mandatory behavior
- Before each phase, append a DB/file artifact entry.
- After each phase, create:
  - `artifacts/phases/phase_XX_result.md`
  - `artifacts/tests/phase_XX_test_report.html`
  - `artifacts/audits/phase_XX_audit_report.html`
  - `artifacts/phases/phase_XX_artifact_manifest.json`
- If blocked, create an explicit blocked result and stop.
- If a phase changes schema/contracts, update docs in the same phase.
- Preserve current Python core unless the phase explicitly authorizes refactor.
