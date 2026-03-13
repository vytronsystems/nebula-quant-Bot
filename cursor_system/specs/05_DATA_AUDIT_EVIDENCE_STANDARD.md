# Data, Audit, and Evidence Standard

## Database-first evidence
Implement tables for at least:
- `phase_execution_log`
- `artifact_registry`
- `audit_run`
- `test_run`
- `promotion_review`
- `paper_trading_daily_snapshot`
- `venue_account_snapshot`
- `instrument_registry`
- `instrument_activation_log`

## Filesystem artifacts
Create and maintain:
- `artifacts/phases/`
- `artifacts/tests/`
- `artifacts/audits/`
- `artifacts/backtests/`
- `artifacts/walkforward/`
- `artifacts/paper-trading/`
- `artifacts/frontend-review/`
- `artifacts/releases/`

## Phase naming standard
- `phase_XX_result.md`
- `phase_XX_test_report.html`
- `phase_XX_audit_report.html`
- `phase_XX_artifact_manifest.json`
