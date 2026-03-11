# NEBULA-QUANT v1 | nq_edge_decay — edge decay analysis engine

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nq_edge_decay.analyzers import analyze_single_input
from nq_edge_decay.models import EdgeDecayFinding, EdgeDecayError, EdgeDecayReport
from nq_edge_decay.summaries import build_edge_decay_summary, build_edge_decay_report


class EdgeDecayEngine:
    """
    Deterministic edge decay analysis engine. Analyzes each structured input,
    builds evidence and findings, then summary and report.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time
        self._clock = clock or time.monotonic
        self._report_counter = 0
        self._finding_counter = 0

    def _now(self) -> float:
        return self._clock()

    def _next_report_id(self) -> str:
        self._report_counter += 1
        return f"edge-decay-report-{self._report_counter}"

    def _next_finding_id_prefix(self, idx: int) -> str:
        self._finding_counter += 1
        return f"find-{idx}"

    def analyze_edge_decay(
        self,
        edge_inputs: Any,
        report_id: str | None = None,
        generated_at: float | None = None,
    ) -> EdgeDecayReport:
        """
        Analyze each input for edge decay, build findings and evidence, then summary and report.
        edge_inputs must be a list of dict or EdgeDecayInput-like objects.
        """
        now = generated_at if generated_at is not None else self._now()
        if report_id is not None:
            rid = report_id
            self._report_counter += 1
        else:
            rid = self._next_report_id()

        if edge_inputs is None:
            return build_edge_decay_report(rid, now, [], metadata={"report_type": "edge_decay"})

        if not isinstance(edge_inputs, list):
            raise EdgeDecayError("edge_inputs must be a list")

        all_findings: list[EdgeDecayFinding] = []
        for idx, inp in enumerate(edge_inputs):
            if inp is None:
                raise EdgeDecayError("edge_inputs must not contain None")
            find_prefix = f"find-{idx}"
            ev_prefix = f"ev-{idx}"
            findings, _evidence = analyze_single_input(inp, find_prefix, ev_prefix)
            all_findings.extend(findings)

        summary = build_edge_decay_summary(all_findings)
        return build_edge_decay_report(rid, now, all_findings, summary=summary, metadata={"report_type": "edge_decay"})
