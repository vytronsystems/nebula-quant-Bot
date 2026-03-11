# NEBULA-QUANT v1 | nq_decision_archive — decision archive engine

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nq_decision_archive.models import (
    DecisionArchiveReport,
    DecisionQuery,
    DecisionRecord,
)
from nq_decision_archive.normalizers import normalize_decision
from nq_decision_archive.repository import DecisionArchiveRepository


class DecisionArchiveEngine:
    """
    Deterministic decision archive engine. Normalizes decisions from control modules,
    stores them in the repository, and builds reports. Uses injectable clock and
    counter-based or caller-supplied ids.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time
        self._clock = clock or time.monotonic
        self._archive_counter = 0
        self._report_counter = 0
        self._repo = DecisionArchiveRepository()

    def _now(self) -> float:
        return self._clock()

    def _next_archive_id(self) -> str:
        self._archive_counter += 1
        return f"da-{self._archive_counter}"

    def _next_report_id(self) -> str:
        self._report_counter += 1
        return f"decision-archive-report-{self._report_counter}"

    def normalize_and_archive(
        self,
        source_module: str,
        decision_payload: Any,
        source_id: str | None = None,
        timestamp: float | None = None,
    ) -> DecisionRecord:
        """
        Normalize the decision payload for source_module, assign archive_id,
        store in repository, and return the stored record. Timestamp from clock if not provided.
        """
        if not source_module or not str(source_module).strip():
            from nq_decision_archive.models import DecisionArchiveError
            raise DecisionArchiveError("source_module is required")
        ts = timestamp if timestamp is not None else self._now()
        archive_id = self._next_archive_id()
        record = normalize_decision(source_module, decision_payload, archive_id, source_id, ts)
        self._repo.archive(record)
        return record

    def archive_record(self, record: DecisionRecord) -> None:
        """Store one pre-built record. Does not assign archive_id; record must have it."""
        self._repo.archive(record)

    def archive_records(self, records: list[DecisionRecord]) -> None:
        """Store multiple pre-built records."""
        self._repo.archive_many(records)

    def query(self, query: DecisionQuery | None = None) -> list[DecisionRecord]:
        """Return records matching query; deterministic order."""
        return self._repo.list_records(query)

    def list_by_strategy(self, strategy_id: str) -> list[DecisionRecord]:
        """Return records for strategy_id."""
        return self._repo.list_by_strategy(strategy_id)

    def list_by_module(self, source_module: str) -> list[DecisionRecord]:
        """Return records for source_module."""
        return self._repo.list_by_module(source_module)

    def list_by_outcome(self, decision_outcome: str) -> list[DecisionRecord]:
        """Return records for decision_outcome."""
        return self._repo.list_by_outcome(decision_outcome)

    def build_report(
        self,
        records: list[DecisionRecord] | None = None,
        report_id: str | None = None,
        generated_at: float | None = None,
    ) -> DecisionArchiveReport:
        """
        Build deterministic archive report from given records or all stored records.
        Uses counter-based report_id if not provided.
        """
        now = generated_at if generated_at is not None else self._now()
        if report_id is not None:
            rid = report_id
            self._report_counter += 1
        else:
            rid = self._next_report_id()
        recs = self._repo.list_records() if records is None else records
        summary = self._repo.build_summary(recs)
        return DecisionArchiveReport(
            report_id=rid,
            generated_at=now,
            records=list(recs),
            summary=summary,
            metadata={"report_type": "decision_archive"},
        )
