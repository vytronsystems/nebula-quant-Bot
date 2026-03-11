from __future__ import annotations

# NEBULA-QUANT v1 | nq_scheduler engine

import time
from collections.abc import Callable
from typing import Any

from nq_scheduler.models import (
    IntervalSchedule,
    JobExecutionResult,
    JobStatus,
    ScheduledJob,
    SchedulerError,
    SchedulerStats,
)
from nq_scheduler.registry import JobRegistry
from nq_scheduler.schedule import compute_next_run, is_job_due


class SchedulerEngine:
    """
    Deterministic in-process scheduler for periodic jobs.

    - Uses an injectable clock (default: time.monotonic).
    - Evaluates due jobs explicitly based on a provided current_time or the clock.
    - Executes due jobs sequentially in registration order.
    - Records last run time, next run time, status, error, and stats.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        self._clock = clock or time.monotonic
        self._registry = JobRegistry()
        self._stats = SchedulerStats()

    def _now(self) -> float:
        return self._clock()

    # Registration / inspection -------------------------------------------------

    def register_job(
        self,
        job_id: str,
        name: str,
        interval_seconds: float,
        callback: Callable[[], Any],
        enabled: bool = True,
        metadata: dict[str, Any] | None = None,
        first_run_immediate: bool = False,
    ) -> ScheduledJob:
        """Register a new interval-based job. Raises SchedulerError on invalid input."""
        schedule = IntervalSchedule(interval_seconds=interval_seconds)
        now = self._now()
        next_run_at = now if first_run_immediate else now + schedule.interval_seconds
        job = ScheduledJob(
            job_id=job_id,
            name=name,
            schedule=schedule,
            callback=callback,
            enabled=enabled,
            last_run_at=None,
            next_run_at=next_run_at if enabled else None,
            last_status=JobStatus.IDLE if enabled else JobStatus.DISABLED,
            last_error=None,
            metadata=metadata or {},
        )
        self._registry.register_job(job)
        self._recompute_stats_counts()
        return job

    def get_job(self, job_id: str) -> ScheduledJob:
        return self._registry.get_job(job_id)

    def list_jobs(self) -> list[ScheduledJob]:
        return self._registry.list_jobs()

    def due_jobs(self, current_time: float | None = None) -> list[ScheduledJob]:
        now = current_time if current_time is not None else self._now()
        return [j for j in self._registry.jobs_in_order() if is_job_due(j, now)]

    # Execution -----------------------------------------------------------------

    def run_due_jobs(self, current_time: float | None = None) -> list[JobExecutionResult]:
        """Run all due jobs at or before current_time. Returns execution results in deterministic order."""
        now = current_time if current_time is not None else self._now()
        results: list[JobExecutionResult] = []
        for job in self._registry.jobs_in_order():
            if not is_job_due(job, now):
                continue
            res = self._run_job_internal(job, now, counted_as_due=True)
            results.append(res)
        return results

    def run_job(self, job_id: str, current_time: float | None = None) -> JobExecutionResult:
        """Run a single job manually. Disabled jobs fail closed."""
        job = self.get_job(job_id)
        if not job.enabled:
            raise SchedulerError(f"job_id {job_id!r} is disabled and cannot be run manually")
        now = current_time if current_time is not None else self._now()
        self._stats.manual_runs += 1
        return self._run_job_internal(job, now, counted_as_due=False)

    def _run_job_internal(self, job: ScheduledJob, run_time: float, counted_as_due: bool) -> JobExecutionResult:
        job.last_status = JobStatus.RUNNING
        job.last_run_at = run_time
        error_msg: str | None = None
        success = False
        try:
            job.callback()
            success = True
            job.last_status = JobStatus.SUCCESS
        except Exception as exc:  # pragma: no cover - error path
            error_msg = f"{type(exc).__name__}: {exc}"
            job.last_error = error_msg
            job.last_status = JobStatus.FAILED
        finished_at = run_time
        job.next_run_at = compute_next_run(job, finished_at) if job.enabled else None

        if success:
            self._stats.successful_runs += 1
        else:
            self._stats.failed_runs += 1
        if counted_as_due:
            self._stats.due_runs += 1

        self._recompute_stats_counts()

        return JobExecutionResult(
            job_id=job.job_id,
            started_at=run_time,
            finished_at=finished_at,
            success=success,
            error=error_msg,
            next_run_at=job.next_run_at,
        )

    # Enable/disable ------------------------------------------------------------

    def enable_job(self, job_id: str, current_time: float | None = None) -> None:
        job = self.get_job(job_id)
        if job.enabled:
            return
        job.enabled = True
        now = current_time if current_time is not None else self._now()
        job.next_run_at = now + job.schedule.interval_seconds
        job.last_status = JobStatus.IDLE
        self._recompute_stats_counts()

    def disable_job(self, job_id: str) -> None:
        job = self.get_job(job_id)
        job.enabled = False
        job.next_run_at = None
        job.last_status = JobStatus.DISABLED
        self._recompute_stats_counts()

    # Stats ---------------------------------------------------------------------

    def stats(self) -> SchedulerStats:
        """Return a snapshot of current scheduler stats."""
        return SchedulerStats(
            registered_jobs=self._stats.registered_jobs,
            enabled_jobs=self._stats.enabled_jobs,
            disabled_jobs=self._stats.disabled_jobs,
            successful_runs=self._stats.successful_runs,
            failed_runs=self._stats.failed_runs,
            manual_runs=self._stats.manual_runs,
            due_runs=self._stats.due_runs,
        )

    def _recompute_stats_counts(self) -> None:
        jobs = self._registry.list_jobs()
        self._stats.registered_jobs = len(jobs)
        self._stats.enabled_jobs = sum(1 for j in jobs if j.enabled)
        self._stats.disabled_jobs = sum(1 for j in jobs if not j.enabled)

