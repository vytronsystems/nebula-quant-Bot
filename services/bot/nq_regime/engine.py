# NEBULA-QUANT v1 | nq_regime — regime classification engine

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nq_regime.classifiers import _classify_single
from nq_regime.models import RegimeClassification, RegimeError, RegimeReport
from nq_regime.summaries import build_regime_summary, build_regime_report


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


class RegimeEngine:
    """
    Deterministic regime classification engine. Classifies each structured input,
    builds evidence and classifications, and produces RegimeReport.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time
        self._clock = clock or time.monotonic
        self._report_counter = 0
        self._classification_counter = 0

    def _now(self) -> float:
        return self._clock()

    def _next_report_id(self) -> str:
        self._report_counter += 1
        return f"regime-report-{self._report_counter}"

    def _next_classification_id(self) -> str:
        self._classification_counter += 1
        return f"cl-{self._classification_counter}"

    def classify_regimes(
        self,
        regime_inputs: Any,
        report_id: str | None = None,
        generated_at: float | None = None,
    ) -> RegimeReport:
        """
        Classify each input, build evidence and classifications, then summary and report.
        regime_inputs must be a list of dict or RegimeInput-like objects.
        """
        now = generated_at if generated_at is not None else self._now()
        if report_id is not None:
            rid = report_id
            self._report_counter += 1
        else:
            rid = self._next_report_id()

        if regime_inputs is None:
            return build_regime_report(rid, now, [], metadata={"report_type": "regime"})

        if not isinstance(regime_inputs, list):
            raise RegimeError("regime_inputs must be a list")

        classifications: list[RegimeClassification] = []
        for idx, inp in enumerate(regime_inputs):
            if inp is None:
                raise RegimeError("regime_inputs must not contain None")
            ev_prefix = f"ev-{idx}"
            cl_id = self._next_classification_id()
            primary, secondary, confidence, rationale, evidence_list = _classify_single(inp, ev_prefix, cl_id)
            symbol = _get(inp, "symbol")
            if symbol is not None:
                symbol = str(symbol).strip() or None
            timestamp = _get(inp, "timestamp")
            if timestamp is not None and isinstance(timestamp, (int, float)):
                timestamp = float(timestamp)
            else:
                timestamp = None
            evidence_ids = [e.evidence_id for e in evidence_list]
            classifications.append(RegimeClassification(
                classification_id=cl_id,
                symbol=symbol,
                timestamp=timestamp,
                primary_regime=primary,
                secondary_regimes=list(secondary),
                confidence_score=confidence,
                rationale=rationale,
                evidence_ids=evidence_ids,
                metadata={},
            ))

        summary = build_regime_summary(classifications)
        return build_regime_report(rid, now, classifications, summary=summary, metadata={"report_type": "regime"})
