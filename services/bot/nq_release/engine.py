# NEBULA-QUANT v1 | nq_release — release evaluation engine

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nq_release.manifest import build_release_manifest
from nq_release.models import (
    ReleaseBlocker,
    ReleaseDecision,
    ReleaseError,
    ReleaseEvidence,
    ReleaseManifest,
    ReleaseReport,
    ReleaseStatus,
    ReleaseSummary,
)
from nq_release.validators import validate_gates, validate_module_records


class ReleaseEngine:
    """
    Deterministic release evaluation engine. Builds manifest, runs validators,
    produces blockers and evidence, decides status, and returns ReleaseReport.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time
        self._clock = clock or time.monotonic
        self._report_counter = 0
        self._manifest_counter = 0
        self._decision_counter = 0

    def _now(self) -> float:
        return self._clock()

    def _next_report_id(self) -> str:
        self._report_counter += 1
        return f"release-report-{self._report_counter}"

    def _next_manifest_id(self) -> str:
        self._manifest_counter += 1
        return f"manifest-{self._manifest_counter}"

    def _next_decision_id(self) -> str:
        self._decision_counter += 1
        return f"decision-{self._decision_counter}"

    def evaluate_release(
        self,
        release_name: str,
        version_label: str,
        module_records: Any,
        architecture_gate: Any = None,
        qa_gate: Any = None,
        branch: str | None = None,
        commit_hash: str | None = None,
        metadata: Any = None,
        report_id: str | None = None,
        generated_at: float | None = None,
    ) -> ReleaseReport:
        """
        Evaluate release candidate: build manifest, validate modules and gates,
        produce blockers/evidence, decide status, build summary and report.
        """
        now = generated_at if generated_at is not None else self._now()
        if report_id is not None:
            rid = report_id
            self._report_counter += 1
        else:
            rid = self._next_report_id()

        if module_records is not None and not isinstance(module_records, list):
            raise ReleaseError("module_records must be a list or None")

        records_list = module_records if isinstance(module_records, list) else []
        meta = metadata if isinstance(metadata, dict) else {}

        manifest_id = self._next_manifest_id()
        manifest = build_release_manifest(
            manifest_id=manifest_id,
            release_name=release_name or "draft",
            version_label=version_label or "0.0.0-draft",
            module_records=records_list,
            branch=branch,
            commit_hash=commit_hash,
            metadata=meta,
        )

        blockers: list[ReleaseBlocker] = []
        evidence: list[ReleaseEvidence] = []

        require_integrated = meta.get("require_included_integrated", False)
        blk1, ev1 = validate_module_records(
            records_list,
            evidence_id_prefix="ev",
            blocker_id_prefix="blocker",
            require_included_implemented=True,
            require_included_integrated=require_integrated,
        )
        blockers.extend(blk1)
        evidence.extend(ev1)

        blk2, ev2 = validate_gates(
            architecture_gate,
            qa_gate,
            evidence_id_prefix="ev",
            blocker_id_prefix="blocker",
            blk_start_idx=len(blockers),
        )
        blockers.extend(blk2)
        evidence.extend(ev2)

        critical_blockers = [b for b in blockers if b.severity == "CRITICAL"]
        warning_blockers = [b for b in blockers if b.severity == "WARNING"]
        gate_blockers = [b for b in blockers if b.category in ("architecture_gate_failed", "qa_gate_failed")]

        if gate_blockers:
            status = ReleaseStatus.REJECTED.value
            rationale = "Release rejected: one or more gates (architecture, QA) did not pass."
        elif critical_blockers:
            status = ReleaseStatus.BLOCKED.value
            rationale = f"Release blocked: {len(critical_blockers)} critical blocker(s) present."
        elif not blockers:
            status = ReleaseStatus.APPROVED.value
            rationale = "All validations passed; release candidate approved."
        elif warning_blockers:
            status = ReleaseStatus.READY.value
            rationale = f"Release ready with {len(warning_blockers)} warning(s); no critical blockers."
        else:
            status = ReleaseStatus.APPROVED.value
            rationale = "All validations passed."

        if not records_list and not gate_blockers and not critical_blockers:
            status = ReleaseStatus.DRAFT.value
            rationale = "Empty module list; release candidate is draft only."

        decision_id = self._next_decision_id()
        decision = ReleaseDecision(
            decision_id=decision_id,
            status=status,
            rationale=rationale,
            blocker_ids=[b.blocker_id for b in blockers],
            evidence_ids=[e.evidence_id for e in evidence],
            metadata={},
        )

        included = sum(1 for r in manifest.module_records if r.included)
        implemented = sum(1 for r in manifest.module_records if r.implemented)
        integrated = sum(1 for r in manifest.module_records if r.integrated)
        summary = ReleaseSummary(
            total_modules=len(manifest.module_records),
            included_modules_count=included,
            implemented_modules_count=implemented,
            integrated_modules_count=integrated,
            blockers_count=len(blockers),
            warnings_count=len(warning_blockers),
            critical_blockers_count=len(critical_blockers),
            metadata={},
        )

        return ReleaseReport(
            report_id=rid,
            generated_at=now,
            manifest=manifest,
            decision=decision,
            summary=summary,
            blockers=list(blockers),
            evidence=list(evidence),
            metadata={"report_type": "release"},
        )
