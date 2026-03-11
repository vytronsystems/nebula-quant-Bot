from __future__ import annotations

# NEBULA-QUANT v1 | nq_scheduler models

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class SchedulerError(Exception):
    """Deterministic scheduler exception raised on invalid jobs or state."""


class JobStatus(str, Enum):
    """Status of a scheduled job."""

    IDLE = "idle"
    DUE = "due"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass(slots=True)
class IntervalSchedule:
    """Fixed-interval schedule in seconds."""

    interval_seconds: float

    def __post_init__(self) -> None:
        if self.interval_seconds <= 0:
            raise SchedulerError("interval_seconds must be > 0")


@dataclass(slots=True)
class ScheduledJob:
    """Registered scheduled job."""

    job_id: str
    name: str
    schedule: IntervalSchedule
    callback: Callable[[], Any]
    enabled: bool = True
    last_run_at: float | None = None
    next_run_at: float | None = None
    last_status: JobStatus | None = None
    last_error: str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (self.job_id and self.job_id.strip()):
            raise SchedulerError("job_id must be non-empty")
        if not (self.name and self.name.strip()):
            raise SchedulerError("name must be non-empty")
        if not callable(self.callback):
            raise SchedulerError("callback must be callable")


@dataclass(slots=True)
class JobExecutionResult:
    """Result of a single job execution."""

    job_id: str
    started_at: float
    finished_at: float
    success: bool
    error: str | None
    next_run_at: float | None


@dataclass(slots=True)
class SchedulerStats:
    """Counters and derived stats for the scheduler."""

    registered_jobs: int = 0
    enabled_jobs: int = 0
    disabled_jobs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    manual_runs: int = 0
    due_runs: int = 0

