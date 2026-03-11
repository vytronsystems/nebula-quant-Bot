# NEBULA-QUANT v1 | nq_release tests

from __future__ import annotations

import unittest
from typing import Any

from nq_release import ReleaseEngine, ReleaseError, ReleaseStatus


def make_clock(now: float = 100.0):
    def clock() -> float:
        return now
    return clock


def make_module_record(
    module_name: str,
    included: bool = True,
    implemented: bool = True,
    integrated: bool = True,
    validation_status: str = "pass",
) -> dict[str, Any]:
    return {
        "module_name": module_name,
        "included": included,
        "implemented": implemented,
        "integrated": integrated,
        "validation_status": validation_status,
    }


class TestApprovedReleaseWhenAllPass(unittest.TestCase):
    def test_approved_release_when_all_required_conditions_pass(self) -> None:
        engine = ReleaseEngine(clock=make_clock())
        report = engine.evaluate_release(
            release_name="v1.0",
            version_label="1.0.0",
            module_records=[
                make_module_record("nq_risk"),
                make_module_record("nq_guardrails"),
            ],
            architecture_gate=True,
            qa_gate=True,
        )
        self.assertEqual(report.decision.status, ReleaseStatus.APPROVED.value)
        self.assertEqual(len(report.blockers), 0)
        self.assertIn("approved", report.decision.rationale.lower())


class TestBlockedReleaseWhenCriticalModuleFails(unittest.TestCase):
    def test_blocked_release_when_critical_module_readiness_fails(self) -> None:
        engine = ReleaseEngine(clock=make_clock())
        report = engine.evaluate_release(
            release_name="v1.0",
            version_label="1.0.0",
            module_records=[
                make_module_record("nq_risk"),
                make_module_record("nq_guardrails", included=True, implemented=False),
            ],
        )
        self.assertEqual(report.decision.status, ReleaseStatus.BLOCKED.value)
        self.assertGreaterEqual(len(report.blockers), 1)
        critical = [b for b in report.blockers if b.severity == "CRITICAL"]
        self.assertGreaterEqual(len(critical), 1)
        self.assertIn("not implemented", critical[0].title.lower() or "")


class TestRejectedReleaseWhenGateFails(unittest.TestCase):
    def test_rejected_release_when_architecture_gate_fails(self) -> None:
        engine = ReleaseEngine(clock=make_clock())
        report = engine.evaluate_release(
            release_name="v1.0",
            version_label="1.0.0",
            module_records=[make_module_record("nq_risk")],
            architecture_gate=False,
        )
        self.assertEqual(report.decision.status, ReleaseStatus.REJECTED.value)
        self.assertGreaterEqual(len(report.blockers), 1)
        self.assertIn("gate", report.decision.rationale.lower())

    def test_rejected_release_when_qa_gate_fails(self) -> None:
        engine = ReleaseEngine(clock=make_clock())
        report = engine.evaluate_release(
            release_name="v1.0",
            version_label="1.0.0",
            module_records=[make_module_record("nq_risk")],
            qa_gate=False,
        )
        self.assertEqual(report.decision.status, ReleaseStatus.REJECTED.value)


class TestReadyDraftBehavior(unittest.TestCase):
    def test_ready_when_only_warnings(self) -> None:
        engine = ReleaseEngine(clock=make_clock())
        report = engine.evaluate_release(
            release_name="v1.0",
            version_label="1.0.0",
            module_records=[
                make_module_record("nq_risk"),
                make_module_record("nq_other", included=True, integrated=False),
            ],
            metadata={"require_included_integrated": True},
        )
        self.assertEqual(report.decision.status, ReleaseStatus.READY.value)
        self.assertGreaterEqual(len(report.blockers), 1)
        warnings = [b for b in report.blockers if b.severity == "WARNING"]
        self.assertGreaterEqual(len(warnings), 1)
        self.assertIn("warning", report.decision.rationale.lower())

    def test_draft_when_empty_module_list(self) -> None:
        engine = ReleaseEngine(clock=make_clock())
        report = engine.evaluate_release(
            release_name="draft",
            version_label="0.0.0-draft",
            module_records=[],
        )
        self.assertEqual(report.decision.status, ReleaseStatus.DRAFT.value)
        self.assertIn("Empty", report.decision.rationale)


class TestManifestGenerationDeterministic(unittest.TestCase):
    def test_manifest_generation_deterministic(self) -> None:
        engine = ReleaseEngine(clock=make_clock())
        records = [
            make_module_record("nq_b"),
            make_module_record("nq_a"),
        ]
        report = engine.evaluate_release("v1", "1.0.0", records)
        self.assertEqual(report.manifest.included_modules, ["nq_a", "nq_b"])
        self.assertEqual([r.module_name for r in report.manifest.module_records], ["nq_a", "nq_b"])


class TestBlockerGenerationDeterministic(unittest.TestCase):
    def test_blocker_generation_deterministic(self) -> None:
        engine = ReleaseEngine(clock=make_clock())
        report = engine.evaluate_release(
            "v1", "1.0.0",
            [make_module_record("x", included=True, implemented=False)],
        )
        self.assertEqual(len(report.blockers), 1)
        self.assertTrue(report.blockers[0].blocker_id.startswith("blocker-"))
        self.assertIn(report.decision.blocker_ids[0], [b.blocker_id for b in report.blockers])


class TestSummaryCountsCorrect(unittest.TestCase):
    def test_summary_counts_correct(self) -> None:
        engine = ReleaseEngine(clock=make_clock())
        report = engine.evaluate_release(
            "v1", "1.0.0",
            [
                make_module_record("a", included=True),
                make_module_record("b", included=True),
                make_module_record("c", included=False),
            ],
        )
        self.assertEqual(report.summary.total_modules, 3)
        self.assertEqual(report.summary.included_modules_count, 2)
        self.assertEqual(report.summary.implemented_modules_count, 3)
        self.assertEqual(report.summary.blockers_count, len(report.blockers))


class TestMissingCriticalInputFailsClosed(unittest.TestCase):
    def test_module_records_not_list_raises(self) -> None:
        engine = ReleaseEngine(clock=make_clock())
        with self.assertRaises(ReleaseError):
            engine.evaluate_release("v1", "1.0.0", module_records="not-a-list")


class TestEmptyModuleListHandled(unittest.TestCase):
    def test_empty_module_list_returns_draft(self) -> None:
        engine = ReleaseEngine(clock=make_clock())
        report = engine.evaluate_release("v1", "1.0.0", [])
        self.assertEqual(report.decision.status, ReleaseStatus.DRAFT.value)
        self.assertEqual(len(report.manifest.module_records), 0)
        self.assertEqual(report.summary.total_modules, 0)


class TestSameInputSameReportOutput(unittest.TestCase):
    def test_same_input_same_report_output(self) -> None:
        engine = ReleaseEngine(clock=make_clock(50.0))
        records = [make_module_record("nq_risk")]
        r1 = engine.evaluate_release("v1", "1.0.0", records, generated_at=50.0)
        r2 = engine.evaluate_release("v1", "1.0.0", records, generated_at=50.0)
        self.assertEqual(r1.decision.status, r2.decision.status)
        self.assertEqual(r1.decision.rationale, r2.decision.rationale)
        self.assertEqual(r1.summary.total_modules, r2.summary.total_modules)


class TestDeterministicIds(unittest.TestCase):
    def test_deterministic_report_manifest_decision_ids(self) -> None:
        engine = ReleaseEngine(clock=make_clock())
        r1 = engine.evaluate_release("v1", "1.0.0", [make_module_record("a")], report_id="custom-1")
        r2 = engine.evaluate_release("v1", "1.0.0", [make_module_record("b")])
        r3 = engine.evaluate_release("v1", "1.0.0", [make_module_record("c")])
        self.assertEqual(r1.report_id, "custom-1")
        self.assertEqual(r2.report_id, "release-report-2")
        self.assertEqual(r3.report_id, "release-report-3")
        self.assertTrue(r1.manifest.manifest_id.startswith("manifest-"))
        self.assertTrue(r1.decision.decision_id.startswith("decision-"))


class TestStableModuleOrderingPreserved(unittest.TestCase):
    def test_stable_module_ordering_preserved(self) -> None:
        from nq_release.manifest import build_release_manifest
        recs = [
            {"module_name": "z", "included": True},
            {"module_name": "a", "included": True},
        ]
        m = build_release_manifest("m1", "v1", "1.0.0", recs)
        self.assertEqual([r.module_name for r in m.module_records], ["a", "z"])
        self.assertEqual(m.included_modules, ["a", "z"])


class TestNoHiddenDependencies(unittest.TestCase):
    def test_no_hidden_dependencies_on_external_services(self) -> None:
        from nq_release import ReleaseEngine
        from nq_release.models import ReleaseReport
        engine = ReleaseEngine()
        report = engine.evaluate_release("v1", "1.0.0", [])
        self.assertIsInstance(report, ReleaseReport)
        self.assertEqual(report.decision.status, ReleaseStatus.DRAFT.value)
