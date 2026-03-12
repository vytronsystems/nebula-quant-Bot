# nq_runbooks — Operational Runbook Registry and Recommendations

**NEBULA-QUANT v1** operational playbook / runbook management. This module provides a structured way to define runbooks, map incidents to procedures, and generate deterministic runbook recommendations. It does **not** execute remediation, restart services, or modify runtime state.

## Purpose

- **Define** operational runbooks (steps, categories, applicable modules).
- **Map** incidents or findings (SRE, release blockers, audit, edge decay) to runbooks.
- **Generate** actionable operational guidance (recommendations only).
- **Answer** which runbook applies, what steps to follow, which incidents need manual intervention, and which have no runbook.

Output is consumable by **nq_reporting**, **nq_release**, **nq_sre**, dashboards, and operational review workflows.

## Runbook Lifecycle

1. **Register** — Runbooks are registered via `register_runbook(runbook)`. Structure is validated (runbook_id, incident_category, steps with step_id, description, action_type).
2. **Match** — Incidents (with `category` or `incident_category`) are matched to runbooks by category; optional secondary match by module/component in `applicable_modules`.
3. **Recommend** — `RunbookEngine.generate_runbook_recommendations(incidents)` produces a `RunbookReport` with recommendations and unmatched incidents.
4. **Consume** — Downstream modules use the report for reporting, release gates, or dashboards; this module does not execute steps.

## Runbook Structure

- **runbook_id** — Unique identifier.
- **title**, **description** — Human-readable info.
- **incident_category** — Category this runbook applies to (e.g. `component_unavailable`, `stale_signal`).
- **applicable_modules** — Optional list of module/component names for secondary matching.
- **severity** — info | warning | critical.
- **steps** — List of steps; each has `step_id`, `description`, `action_type` (check, restart, inspect, validate, notify, manual), optional `expected_outcome`.
- **version** — Version string.

## Matching Strategy

- **Primary**: `incident.category` (or `incident_category`) equals `runbook.incident_category`. First matching runbook in registry order is used.
- **Secondary**: If `incident.module` or `incident.component_name` is in `runbook.applicable_modules`, confidence is "high"; otherwise "medium" when category matches.
- Incidents with no matching runbook are recorded as **unmatched** in the report.

## Deterministic Behavior

- Same incidents → same recommendations and ordering.
- Report IDs: `runbook-report-{fingerprint}` or `runbook-report-empty`.
- Recommendation IDs: `rec-{incident_index}-{runbook_id}`.
- No random behavior; ordering follows incident list and registry order.

## Future Integration

- **nq_sre** — Feed SRE incidents into `generate_runbook_recommendations`; show recommended runbooks in operational views.
- **nq_reporting** — Include runbook recommendations and unmatched counts in reports.
- **nq_release** — Use runbook coverage and unmatched incidents in release gates.
- **Dashboards** — Display runbook recommendations and steps; manual execution only.
