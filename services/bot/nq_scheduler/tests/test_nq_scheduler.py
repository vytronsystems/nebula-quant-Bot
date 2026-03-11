from __future__ import annotations

# NEBULA-QUANT v1 | nq_scheduler tests

import unittest
from typing import Any, Callable

from nq_scheduler import (
    JobStatus,
    SchedulerEngine,
    SchedulerError,
)


def make_clock(ticks: list[float]) -> tuple[list[float], Callable[[], float]]:
    """Returns (ticks list, clock callable). clock() returns next tick."""
    it = iter(ticks)

    def clock() -> float:
        return next(it)

    return ticks, clock


class TestJobRegistration(unittest.TestCase):
    def test_valid_job_registration_works(self) -> None:
        ticks, clock = make_clock([0.0])
        engine = SchedulerEngine(clock=clock)

        executed: list[str] = []

        def cb() -> None:
            executed.append("run")

        job = engine.register_job(
            job_id="job1",
            name="Test Job",
            interval_seconds=10.0,
            callback=cb,
        )
        self.assertEqual(job.job_id, "job1")
        self.assertEqual(job.name, "Test Job")
        self.assertTrue(job.enabled)

    def test_duplicate_job_id_fails_closed(self) -> None:
        engine = SchedulerEngine()

        def cb() -> None:
            ...

        engine.register_job("job1", "Job 1", 5.0, cb)
        with self.assertRaises(SchedulerError):
            engine.register_job("job1", "Job 2", 5.0, cb)

    def test_invalid_interval_fails_closed(self) -> None:
        engine = SchedulerEngine()

        def cb() -> None:
            ...

        with self.assertRaises(SchedulerError):
            engine.register_job("job1", "Job 1", 0.0, cb)

    def test_invalid_callback_fails_closed(self) -> None:
        engine = SchedulerEngine()
        with self.assertRaises(SchedulerError):
            engine.register_job("job1", "Job 1", 5.0, callback=None)  # type: ignore[arg-type]


class TestDueEvaluation(unittest.TestCase):
    def test_due_evaluation_deterministic_with_injected_clock(self) -> None:
        ticks, clock = make_clock([0.0, 5.0, 10.0])
        engine = SchedulerEngine(clock=clock)

        seen: list[str] = []

        def cb() -> None:
            seen.append("run")

        engine.register_job("job1", "Job", 10.0, cb)

        # At t=5, nothing due
        res_at_5 = engine.run_due_jobs()
        self.assertEqual(len(res_at_5), 0)
        self.assertEqual(seen, [])

        # At t=10, job1 due
        res_at_10 = engine.run_due_jobs()
        self.assertEqual(len(res_at_10), 1)
        self.assertEqual(seen, ["run"])

    def test_non_due_jobs_not_executed(self) -> None:
        ticks, clock = make_clock([0.0, 3.0])
        engine = SchedulerEngine(clock=clock)

        seen: list[str] = []

        def cb() -> None:
            seen.append("run")

        engine.register_job("job1", "Job", 10.0, cb)
        res = engine.run_due_jobs()
        self.assertEqual(len(res), 0)
        self.assertEqual(seen, [])

    def test_due_jobs_execute_in_registration_order(self) -> None:
        engine = SchedulerEngine()

        runs: list[str] = []

        def cb1() -> None:
            runs.append("a")

        def cb2() -> None:
            runs.append("b")

        engine.register_job("job1", "Job A", 10.0, cb1, first_run_immediate=True)
        engine.register_job("job2", "Job B", 10.0, cb2, first_run_immediate=True)

        results = engine.run_due_jobs()
        self.assertEqual([r.job_id for r in results], ["job1", "job2"])
        self.assertEqual(runs, ["a", "b"])


class TestExecutionMetadata(unittest.TestCase):
    def test_successful_run_updates_timestamps_and_status(self) -> None:
        ticks, clock = make_clock([0.0, 10.0])
        engine = SchedulerEngine(clock=clock)

        def cb() -> None:
            ...

        job = engine.register_job("job1", "Job", 10.0, cb)
        results = engine.run_due_jobs()
        self.assertEqual(len(results), 1)
        job_after = engine.get_job("job1")
        self.assertEqual(job_after.last_status, JobStatus.SUCCESS)
        self.assertEqual(job_after.last_run_at, 10.0)
        self.assertEqual(job_after.next_run_at, 20.0)

    def test_failed_run_records_error_and_failed_status(self) -> None:
        ticks, clock = make_clock([0.0, 10.0])
        engine = SchedulerEngine(clock=clock)

        def cb() -> None:
            raise RuntimeError("boom")

        engine.register_job("job1", "Job", 10.0, cb)
        results = engine.run_due_jobs()
        self.assertEqual(len(results), 1)
        res = results[0]
        self.assertFalse(res.success)
        self.assertIsNotNone(res.error)
        job = engine.get_job("job1")
        self.assertEqual(job.last_status, JobStatus.FAILED)
        self.assertIn("boom", job.last_error or "")


class TestManualRun(unittest.TestCase):
    def test_manual_run_works_for_valid_job(self) -> None:
        engine = SchedulerEngine()
        seen: list[str] = []

        def cb() -> None:
            seen.append("run")

        engine.register_job("job1", "Job", 10.0, cb)
        res = engine.run_job("job1", current_time=5.0)
        self.assertTrue(res.success)
        self.assertEqual(seen, ["run"])

    def test_manual_run_missing_job_fails_closed(self) -> None:
        engine = SchedulerEngine()
        with self.assertRaises(SchedulerError):
            engine.run_job("missing", current_time=0.0)

    def test_disabled_jobs_not_run_by_due_evaluation(self) -> None:
        ticks, clock = make_clock([0.0, 10.0])
        engine = SchedulerEngine(clock=clock)
        seen: list[str] = []

        def cb() -> None:
            seen.append("run")

        engine.register_job("job1", "Job", 10.0, cb, enabled=False)
        results = engine.run_due_jobs()
        self.assertEqual(len(results), 0)
        self.assertEqual(seen, [])

    def test_manual_run_disabled_job_fails_closed(self) -> None:
        engine = SchedulerEngine()

        def cb() -> None:
            ...

        engine.register_job("job1", "Job", 10.0, cb, enabled=False)
        with self.assertRaises(SchedulerError):
            engine.run_job("job1", current_time=0.0)


class TestStatsAndDeterminism(unittest.TestCase):
    def test_stats_update_correctly(self) -> None:
        engine = SchedulerEngine()

        def cb_ok() -> None:
            ...

        def cb_fail() -> None:
            raise RuntimeError("fail")

        engine.register_job("ok", "OK Job", 10.0, cb_ok, first_run_immediate=True)
        engine.register_job("bad", "Bad Job", 10.0, cb_fail, first_run_immediate=True)

        engine.run_due_jobs()
        engine.run_due_jobs()
        stats = engine.stats()
        self.assertEqual(stats.registered_jobs, 2)
        self.assertEqual(stats.enabled_jobs, 2)
        self.assertEqual(stats.disabled_jobs, 0)
        # Each job ran once via due execution
        self.assertEqual(stats.successful_runs, 1)
        self.assertEqual(stats.failed_runs, 1)
        self.assertEqual(stats.manual_runs, 0)
        self.assertEqual(stats.due_runs, 2)

    def test_repeated_same_time_progression_yields_same_results(self) -> None:
        def scenario() -> list[tuple[str, bool]]:
            engine = SchedulerEngine()

            def cb1() -> None:
                ...

            def cb2() -> None:
                ...

            engine.register_job("a", "A", 10.0, cb1)
            engine.register_job("b", "B", 10.0, cb2)
            res1 = engine.run_due_jobs()
            res2 = engine.run_due_jobs()
            return [(r.job_id, r.success) for r in res1 + res2]

        out1 = scenario()
        out2 = scenario()
        self.assertEqual(out1, out2)


if __name__ == "__main__":
    unittest.main()

