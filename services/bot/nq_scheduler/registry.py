from __future__ import annotations

# NEBULA-QUANT v1 | nq_scheduler registry

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from nq_scheduler.models import ScheduledJob, SchedulerError


@dataclass(slots=True)
class JobRegistry:
    """In-memory registry for scheduled jobs, preserves registration order."""

    _jobs: Dict[str, ScheduledJob] = field(default_factory=dict)
    _order: List[str] = field(default_factory=list)

    def register_job(self, job: ScheduledJob) -> None:
        if job.job_id in self._jobs:
            raise SchedulerError(f"job_id {job.job_id!r} already registered")
        self._jobs[job.job_id] = job
        self._order.append(job.job_id)

    def get_job(self, job_id: str) -> ScheduledJob:
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise SchedulerError(f"job_id {job_id!r} not found") from exc

    def list_jobs(self) -> list[ScheduledJob]:
        return [self._jobs[jid] for jid in self._order]

    def jobs_in_order(self) -> Iterable[ScheduledJob]:
        for jid in self._order:
            yield self._jobs[jid]

