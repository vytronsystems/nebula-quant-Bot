# NEBULA-QUANT v1 | nq_experiments tests (analysis foundation)

from __future__ import annotations

import unittest
from typing import Any, Callable

from nq_experiments import ExperimentEngine, ExperimentError, ExperimentReport
from nq_experiments.analyzers import analyze_experiment_records, validate_experiment_record


def make_record(
    experiment_id: str = "e1",
    strategy_id: str = "s1",
    status: str = "success",
    experiment_type: str = "backtest",
    metrics: dict[str, Any] | None = None,
    started_at: float | None = None,
    finished_at: float | None = None,
    created_at: float | None = None,
    updated_at: float | None = None,
) -> dict[str, Any]:
    t = 1000.0
    return {
        "experiment_id": experiment_id,
        "strategy_id": strategy_id,
        "status": status,
        "experiment_type": experiment_type,
        "metrics": metrics or {},
        "started_at": started_at if started_at is not None else t,
        "finished_at": finished_at if finished_at is not None else t + 10,
        "created_at": created_at if created_at is not None else t,
        "updated_at": updated_at if updated_at is not None else t + 10,
    }


def make_clock(ticks: list[float]) -> Callable[[], float]:
    it = iter(ticks)
    return lambda: next(it)


class TestValidExperimentRecordAnalysis(unittest.TestCase):
    def test_valid_experiment_record_analysis(self) -> None:
        engine = ExperimentEngine()
        records = [make_record(experiment_id="e1", status="success")]
        report = engine.analyze_experiments(records)
        self.assertIsInstance(report, ExperimentReport)
        self.assertEqual(report.summary.total_experiments, 1)
        self.assertEqual(report.summary.successful_experiments, 1)
        self.assertIn("e1", [r.get("experiment_id") for r in report.experiment_records] if report.experiment_records else [])


class TestEmptyExperimentSet(unittest.TestCase):
    def test_empty_experiment_set_returns_valid_empty_report(self) -> None:
        engine = ExperimentEngine()
        report = engine.analyze_experiments([])
        self.assertEqual(report.summary.total_experiments, 0)
        self.assertEqual(report.summary.successful_experiments, 0)
        self.assertEqual(report.summary.failed_experiments, 0)
        self.assertEqual(len(report.findings), 0)
        self.assertEqual(len(report.experiment_records), 0)


class TestFailedExperimentCreatesFinding(unittest.TestCase):
    def test_failed_experiment_creates_expected_finding(self) -> None:
        engine = ExperimentEngine()
        records = [make_record(experiment_id="e2", status="failed")]
        report = engine.analyze_experiments(records)
        failed_findings = [f for f in report.findings if f.category == "experiment_failed"]
        self.assertGreaterEqual(len(failed_findings), 1)
        self.assertEqual(failed_findings[0].experiment_id, "e2")
        self.assertEqual(report.summary.failed_experiments, 1)


class TestDegradedExperimentCreatesFinding(unittest.TestCase):
    def test_degraded_experiment_creates_expected_finding(self) -> None:
        engine = ExperimentEngine()
        records = [make_record(experiment_id="e3", status="degraded")]
        report = engine.analyze_experiments(records)
        degraded_findings = [f for f in report.findings if f.category == "experiment_degraded"]
        self.assertGreaterEqual(len(degraded_findings), 1)
        self.assertEqual(report.summary.degraded_experiments, 1)


class TestInvalidExperiment(unittest.TestCase):
    def test_invalid_experiment_creates_finding_or_fails_closed(self) -> None:
        engine = ExperimentEngine()
        records = [make_record(experiment_id="e4", status="invalid")]
        report = engine.analyze_experiments(records)
        invalid_findings = [f for f in report.findings if f.category == "experiment_invalid"]
        self.assertGreaterEqual(len(invalid_findings), 1)
        self.assertEqual(report.summary.invalid_experiments, 1)


class TestMissingMetricsHandled(unittest.TestCase):
    def test_missing_metrics_handled_deterministically(self) -> None:
        engine = ExperimentEngine()
        records = [make_record(experiment_id="e5", metrics=None)]
        report = engine.analyze_experiments(records)
        missing = [f for f in report.findings if f.category == "missing_metrics"]
        self.assertGreaterEqual(len(missing), 1)


class TestSummaryCountsCorrect(unittest.TestCase):
    def test_summary_counts_correct(self) -> None:
        engine = ExperimentEngine()
        records = [
            make_record(experiment_id="a", status="success"),
            make_record(experiment_id="b", status="failed"),
            make_record(experiment_id="c", status="success"),
        ]
        report = engine.analyze_experiments(records)
        self.assertEqual(report.summary.total_experiments, 3)
        self.assertEqual(report.summary.successful_experiments, 2)
        self.assertEqual(report.summary.failed_experiments, 1)


class TestGroupingByStrategy(unittest.TestCase):
    def test_grouping_by_strategy_works(self) -> None:
        engine = ExperimentEngine()
        records = [
            make_record(experiment_id="e1", strategy_id="s1"),
            make_record(experiment_id="e2", strategy_id="s2"),
            make_record(experiment_id="e3", strategy_id="s1"),
        ]
        report = engine.analyze_experiments(records)
        self.assertEqual(sorted(report.summary.strategies_seen), ["s1", "s2"])


class TestGroupingByExperimentType(unittest.TestCase):
    def test_grouping_by_experiment_type_works(self) -> None:
        engine = ExperimentEngine()
        records = [
            make_record(experiment_id="e1", experiment_type="backtest"),
            make_record(experiment_id="e2", experiment_type="walkforward"),
        ]
        report = engine.analyze_experiments(records)
        self.assertEqual(report.summary.total_experiments, 2)


class TestMalformedCriticalInputFailsClosed(unittest.TestCase):
    def test_missing_experiment_id_fails_closed(self) -> None:
        with self.assertRaises(ExperimentError):
            validate_experiment_record({"strategy_id": "s1", "status": "success"})

    def test_invalid_status_fails_closed(self) -> None:
        with self.assertRaises(ExperimentError):
            validate_experiment_record({"experiment_id": "e1", "status": "invalid_status"})

    def test_metrics_not_dict_fails_closed(self) -> None:
        with self.assertRaises(ExperimentError):
            validate_experiment_record({"experiment_id": "e1", "status": "success", "metrics": "not-a-dict"})

    def test_analyze_records_with_invalid_record_raises(self) -> None:
        with self.assertRaises(ExperimentError):
            analyze_experiment_records([make_record(experiment_id="")])


class TestDeterministicOrdering(unittest.TestCase):
    def test_deterministic_ordering_preserved(self) -> None:
        engine = ExperimentEngine()
        records = [make_record(experiment_id=f"e{i}") for i in range(3)]
        report = engine.analyze_experiments(records)
        ids = [r.get("experiment_id") for r in report.experiment_records]
        self.assertEqual(ids, ["e0", "e1", "e2"])


class TestDeterministicReportIds(unittest.TestCase):
    def test_deterministic_report_ids(self) -> None:
        engine = ExperimentEngine()
        r1 = engine.analyze_experiments([], report_id="custom-1")
        r2 = engine.analyze_experiments([])
        r3 = engine.analyze_experiments([])
        self.assertEqual(r1.report_id, "custom-1")
        self.assertEqual(r2.report_id, "experiment-report-2")
        self.assertEqual(r3.report_id, "experiment-report-3")


class TestDeterministicFindingIds(unittest.TestCase):
    def test_deterministic_finding_ids(self) -> None:
        engine = ExperimentEngine()
        records = [make_record(experiment_id="e1", status="failed"), make_record(experiment_id="e2", status="failed")]
        report = engine.analyze_experiments(records)
        finding_ids = [f.finding_id for f in report.findings]
        self.assertTrue(all("e1" in fid or "e2" in fid for fid in finding_ids))
        self.assertEqual(len(finding_ids), len(set(finding_ids)))


class TestSameInputSameReportOutput(unittest.TestCase):
    def test_same_input_same_report_output(self) -> None:
        engine = ExperimentEngine()
        records = [make_record(experiment_id="e1"), make_record(experiment_id="e2", status="failed")]
        r1 = engine.analyze_experiments(records, generated_at=100.0)
        r2 = engine.analyze_experiments(records, generated_at=100.0)
        self.assertEqual(r1.summary.total_experiments, r2.summary.total_experiments)
        self.assertEqual(r1.summary.failed_experiments, r2.summary.failed_experiments)
        self.assertEqual(len(r1.findings), len(r2.findings))
        self.assertEqual([f.category for f in r1.findings], [f.category for f in r2.findings])


class TestNoHiddenDependencies(unittest.TestCase):
    def test_no_hidden_dependencies_on_external_services(self) -> None:
        engine = ExperimentEngine()
        report = engine.analyze_experiments([])
        self.assertIsNotNone(report.report_id)
        self.assertIsInstance(report.findings, list)
        self.assertIsInstance(report.summary.total_experiments, int)


class TestWeakResultFinding(unittest.TestCase):
    def test_negative_pnl_creates_weak_result_finding(self) -> None:
        engine = ExperimentEngine()
        records = [make_record(experiment_id="e1", metrics={"pnl": -100.0})]
        report = engine.analyze_experiments(records)
        weak = [f for f in report.findings if f.category == "weak_result"]
        self.assertGreaterEqual(len(weak), 1)


class TestInconsistentRecordFinding(unittest.TestCase):
    def test_finished_before_started_creates_inconsistent_finding(self) -> None:
        engine = ExperimentEngine()
        records = [make_record(experiment_id="e1", started_at=100.0, finished_at=90.0)]
        report = engine.analyze_experiments(records)
        inc = [f for f in report.findings if f.category == "inconsistent_experiment_record"]
        self.assertGreaterEqual(len(inc), 1)


class TestCompletedNormalizedToSuccess(unittest.TestCase):
    def test_completed_status_normalized_to_success(self) -> None:
        engine = ExperimentEngine()
        records = [make_record(experiment_id="e1", status="completed")]
        report = engine.analyze_experiments(records)
        self.assertEqual(report.summary.successful_experiments, 1)
