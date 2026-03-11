from __future__ import annotations

# NEBULA-QUANT v1 | nq_scheduler schedule helpers

from typing import Iterable

from nq_scheduler.models import IntervalSchedule, ScheduledJob, SchedulerError


def is_job_due(job: ScheduledJob, current_time: float) -> bool:
    """Return True if the job is due at current_time."""
    if not job.enabled:
        return False
    if job.next_run_at is None:
        return False
    return current_time >= job.next_run_at


def compute_next_run(job: ScheduledJob, run_time: float) -> float:
    """Compute next_run_at for a job given its schedule and the run time."""
    return run_time + job.schedule.interval_seconds


def validate_jobs_unique(jobs: Iterable[ScheduledJob]) -> None:
    """Ensure no duplicate job_id in the iterable; raises SchedulerError otherwise."""
    seen: set[str] = set()
    for job in jobs:
        if job.job_id in seen:
            raise SchedulerError(f"duplicate job_id detected: {job.job_id!r}")
        seen.add(job.job_id)

