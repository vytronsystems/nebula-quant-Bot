# nq_scheduler

Deterministic in-process scheduler for NEBULA-QUANT v1. Schedules and runs periodic infrastructure tasks (e.g. audits, observability snapshots, reports) using fixed intervals and an injectable clock; no threads, no external services.

## Purpose

- **Register** periodic jobs with fixed intervals.
- **Evaluate** which jobs are due at a given time (clock-injectable).
- **Execute** due jobs sequentially in deterministic order.
- **Record** last run, next run, status, and errors.
- **Expose** inspection helpers and stats for debugging and observability.

## Interval-based design

- Each job uses an `IntervalSchedule(interval_seconds)` with `interval_seconds > 0`.
- On registration, `next_run_at` is set to:
  - `now + interval_seconds` by default, or
  - `now` when `first_run_immediate=True`.
- Due evaluation compares `current_time` (from injected clock or explicit argument) against `next_run_at`.

## Deterministic clock model

- Scheduler uses an injectable `clock()` (default: `time.monotonic`).
- All due checks and timestamps (`last_run_at`, `next_run_at`) derive from this clock or an explicit `current_time` argument.
- Tests can provide a fake clock (e.g. a list of ticks) for reproducible behavior.

## Due evaluation and execution

- A job is **due** when:
  - `enabled` is `True`, and
  - `next_run_at` is not `None`, and
  - `current_time >= next_run_at`.
- `run_due_jobs(current_time=None)`:
  - evaluates due jobs,
  - executes them in **registration order**,
  - updates `last_run_at`, `next_run_at = run_time + interval_seconds`,
  - records `last_status` (`SUCCESS` / `FAILED`) and `last_error` if any,
  - returns a list of `JobExecutionResult`.

## Manual execution

- `run_job(job_id, current_time=None)` runs a single job manually.
- Disabled jobs fail closed on manual run by default (raise `SchedulerError`).
- Manual runs update run metadata and stats but are not counted as “due” executions.

## Failure handling

- If a job callback raises, the engine:
  - captures the exception as a string in `last_error`,
  - sets `last_status = FAILED`,
  - still computes `next_run_at` deterministically (next interval),
  - increments `failed_runs` in `SchedulerStats`,
  - **does not** swallow errors silently or crash the scheduler.

## Inspection and stats

- `get_job(job_id)` — return a `ScheduledJob` or raise `SchedulerError`.
- `list_jobs()` — return jobs in registration order.
- `due_jobs(current_time=None)` — list of jobs due at given time.
- `stats()` — `SchedulerStats` with:
  - `registered_jobs`, `enabled_jobs`, `disabled_jobs`,
  - `successful_runs`, `failed_runs`, `manual_runs`, `due_runs`.

## Intended future integration points

- **nq_audit / nq_reporting**: schedule periodic audits and reports.
- **nq_obs / nq_metrics**: schedule observability snapshots or metrics aggregation.
- **nq_experiments**: schedule periodic experiment review or cleanup tasks.
- **nq_orchestrator**: drive recurring system tasks in a deterministic main loop.

No deep wiring is done in this phase; `nq_scheduler` is ready for callers to register jobs.

## Usage example

```python
from nq_scheduler import SchedulerEngine

engine = SchedulerEngine()  # uses time.monotonic by default

def weekly_audit() -> None:
    run_audit_pipeline()

engine.register_job(
    job_id="weekly_audit",
    name="Weekly Audit",
    interval_seconds=7 * 24 * 60 * 60,
    callback=weekly_audit,
    first_run_immediate=False,
)

# In a main loop:
while True:
    engine.run_due_jobs()
    sleep(1)  # or orchestrator-controlled loop
```

