# nq_sre — Deterministic Operational Reliability

**NEBULA-QUANT v1** operational reliability (SRE) layer. This module evaluates service and subsystem health from structured inputs, classifies incidents deterministically, and produces reliability summaries and reports. It does **not** restart services, deploy fixes, or mutate runtime state.

## Purpose

- **Consume** structured health / status / reliability inputs (components, metrics, release context).
- **Evaluate** service and subsystem health with explicit, rule-based logic.
- **Classify** incidents and degradation states (severity: info, warning, critical).
- **Produce** structured reliability findings, evidence, and summaries for downstream use by:
  - `nq_reporting`
  - `nq_release`
  - `nq_runbooks`
  - Dashboards and operational tooling

## Supported Input Fields

Inputs may be dicts or objects with the following optional fields:

| Field | Description |
|-------|-------------|
| `component_name` / `component` | Component identifier |
| `component_type` | Optional type label |
| `status` | e.g. `healthy`, `degraded`, `unavailable`, `down`, `off` |
| `healthy` | Boolean |
| `degraded` | Boolean |
| `unavailable` | Boolean |
| `last_update` | Timestamp or freshness marker |
| `stale` | Stale signal indicator |
| `stale_data` | Stale data indicator |
| `missing_heartbeat` | Heartbeat missing |
| `error_count` | Numeric |
| `failed_jobs` | Numeric |
| `repeated_failures` | Numeric |
| `queue_backlog` | Numeric |
| `criticality` | Criticality level |
| `impacted_modules` | List of module names |
| `impacted_strategies` | List of strategy names |
| `release_status` | e.g. `blocked`, `rejected` |
| `metadata` | Optional extra data |

Missing optional fields are allowed; the evaluator uses safe defaults.

## Reliability and Incident Categories

- **component_unavailable** — Component reported unavailable/down/off.
- **component_degraded** — Component reported degraded.
- **stale_signal** — Stale signal detected.
- **stale_data** — Stale data detected.
- **missing_heartbeat** — Heartbeat missing (critical).
- **excessive_errors** — Error count above thresholds (warning/critical).
- **repeated_failures** — Failed jobs or repeated failures above thresholds.
- **queue_backlog** — Queue backlog above thresholds.
- **release_health_risk** — Release blocked/rejected with operational concerns (info).
- **inconsistent_sre_input** — Contradictory or insufficient input (fail closed).

## Rule-Based Evaluation

- **Direct health**: `unavailable=True` or status indicates unavailable → critical **component_unavailable**. `degraded=True` or status degraded → warning **component_degraded**. Healthy with no negative signals → no incident.
- **Staleness / heartbeat**: `stale=True` or `stale_data=True` → warning; `missing_heartbeat=True` → critical.
- **Thresholds**: Explicit numeric thresholds for `error_count`, `failed_jobs`, `repeated_failures`, `queue_backlog` (see `evaluators.py` constants). Exceeding them yields warning or critical incidents.
- **Release-linked**: If `release_status` is blocked/rejected and the component is degraded or has incidents, an **info** release_health_risk incident may be added.
- **Unknown / inconsistent**: Contradictory or insufficient inputs lead to fail-closed behavior (e.g. inconsistent_sre_input); the module does not guess.

## Rationale and Evidence

Every incident includes:

- **rationale** — Explicit text explaining why the incident was raised.
- **evidence_ids** — References to `SREEvidence` records (evidence_id, category, value, description).

Rationale is grounded in input and rules; no vague or unsupported rationale is produced.

## Overall Status Rules

- **UNAVAILABLE** — Any critical incident in `component_unavailable` or `missing_heartbeat`.
- **DEGRADED** — Any other critical or any warning incident (and no full unavailability).
- **HEALTHY** — No incidents and healthy signals dominate.
- **UNKNOWN** — No inputs (empty evaluation).

Derivation is deterministic and testable.

## Deterministic Guarantees

- Same inputs → identical incidents and ordering.
- Report IDs, incident IDs, and evidence IDs are deterministic (counter-based per input index or fingerprint).
- No random IDs; clock is injectable for tests.
- Empty input list returns a valid empty report (overall status `unknown`).

## Future Integration

- **nq_reporting** — Consume `SREReport` / `SRESummary` for operational reporting.
- **nq_release** — Use reliability summary in release gates and governance.
- **nq_runbooks** — Link incidents/categories to runbook triggers (no execution in this module).
- **Dashboards** — Expose overall status, component counts, and incident breakdowns.

This phase implements the evaluation foundation only; deeper wiring to the above is left to later phases.
