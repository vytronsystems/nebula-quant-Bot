# NEBULA-QUANT v1 | nq_reporting system report integration tests

from __future__ import annotations

import unittest
from typing import Any

from nq_release import ReleaseStatus
from nq_reporting.models import ReportError, SystemReport
from nq_reporting.system_report import generate_system_report


def fixed_clock() -> float:
    return 1_000.0


def make_sre_input(component_name: str = "svc", status: str | None = None, degraded: bool | None = None) -> dict[str, Any]:
    return {
        "component_name": component_name,
        "status": status,
        "degraded": degraded,
    }


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


class TestSystemReportGeneration(unittest.TestCase):
    def test_full_system_report_generation(self) -> None:
        sre_inputs = [make_sre_input("svc_a", degraded=True)]
        module_records = [
            make_module_record("nq_risk"),
            make_module_record("nq_guardrails"),
        ]
        report = generate_system_report(
            sre_inputs=sre_inputs,
            incidents=None,
            module_records=module_records,
            architecture_gate=True,
            qa_gate=True,
            clock=fixed_clock,
        )
        self.assertIsInstance(report, SystemReport)
        self.assertIsNotNone(report.report_id)
        self.assertIsNotNone(report.sre_report)
        self.assertIsNotNone(report.runbook_report)
        self.assertIsNotNone(report.release_report)
        self.assertIsInstance(report.summary, dict)
        self.assertIn("system_status", report.summary)
        self.assertIn("release_status", report.summary)


class TestDeterministicOutput(unittest.TestCase):
    def test_same_input_same_output(self) -> None:
        sre_inputs = [make_sre_input("svc_a", degraded=True)]
        modules = [make_module_record("nq_risk")]
        r1 = generate_system_report(
            sre_inputs=sre_inputs,
            incidents=None,
            module_records=modules,
            architecture_gate=True,
            qa_gate=True,
            clock=fixed_clock,
        )
        r2 = generate_system_report(
            sre_inputs=sre_inputs,
            incidents=None,
            module_records=modules,
            architecture_gate=True,
            qa_gate=True,
            clock=fixed_clock,
        )
        self.assertEqual(r1.summary, r2.summary)
        self.assertEqual(r1.release_report.decision.status, r2.release_report.decision.status)
        self.assertEqual(r1.sre_report.overall_status, r2.sre_report.overall_status)


class TestMissingInputsFailClosed(unittest.TestCase):
    def test_invalid_sre_inputs_type_raises(self) -> None:
        with self.assertRaises(ReportError):
            generate_system_report(
                sre_inputs="not-a-list",  # type: ignore[arg-type]
                incidents=None,
                module_records=[],
                architecture_gate=True,
                qa_gate=True,
                clock=fixed_clock,
            )

    def test_invalid_module_records_type_raises(self) -> None:
        with self.assertRaises(ReportError):
            generate_system_report(
                sre_inputs=[],
                incidents=None,
                module_records="not-a-list",  # type: ignore[arg-type]
                architecture_gate=True,
                qa_gate=True,
                clock=fixed_clock,
            )


class TestEmptyIncidentsIntegration(unittest.TestCase):
    def test_empty_incident_list_still_builds_report(self) -> None:
        sre_inputs: list[Any] = []
        module_records: list[Any] = []
        report = generate_system_report(
            sre_inputs=sre_inputs,
            incidents=[],
            module_records=module_records,
            architecture_gate=True,
            qa_gate=True,
            clock=fixed_clock,
        )
        self.assertIsInstance(report, SystemReport)
        self.assertEqual(report.sre_report.summary.total_inputs, 0)
        self.assertGreaterEqual(report.runbook_report.summary.total_runbooks, 0)


class TestReleaseRejectedScenario(unittest.TestCase):
    def test_release_rejected_when_gate_fails(self) -> None:
        sre_inputs = [make_sre_input("svc_a")]
        module_records = [make_module_record("nq_risk")]
        report = generate_system_report(
            sre_inputs=sre_inputs,
            incidents=None,
            module_records=module_records,
            architecture_gate=False,  # force gate failure
            qa_gate=True,
            clock=fixed_clock,
        )
        self.assertEqual(report.release_report.decision.status, ReleaseStatus.REJECTED.value)
        self.assertEqual(report.summary["release_status"], ReleaseStatus.REJECTED.value)

