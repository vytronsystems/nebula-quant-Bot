# NEBULA-QUANT v1 | nq_decision_archive — in-memory decision repository

from __future__ import annotations

from copy import deepcopy
from typing import Any

from nq_decision_archive.models import (
    DecisionArchiveSummary,
    DecisionQuery,
    DecisionRecord,
)


class DecisionArchiveRepository:
    """
    In-memory repository for decision records. Deterministic ordering by timestamp then archive_id.
    Does not mutate stored records; returns copies where needed for stability.
    """

    def __init__(self) -> None:
        self._records: list[DecisionRecord] = []

    def archive(self, record: DecisionRecord) -> None:
        """Append one record; store a copy to avoid external mutation."""
        self._records.append(deepcopy(record))

    def archive_many(self, records: list[DecisionRecord]) -> None:
        """Append multiple records; store copies."""
        for r in records:
            self._records.append(deepcopy(r))

    def _apply_query(self, records: list[DecisionRecord], query: DecisionQuery | None) -> list[DecisionRecord]:
        """Filter and limit; deterministic sort by timestamp, then archive_id."""
        out = list(records)
        if query is None:
            out.sort(key=lambda r: (r.timestamp, r.archive_id))
            return out
        if query.strategy_id is not None:
            sid = query.strategy_id.strip()
            out = [r for r in out if r.strategy_id and r.strategy_id.strip() == sid]
        if query.source_module is not None:
            mod = query.source_module.strip()
            out = [r for r in out if r.source_module.strip() == mod]
        if query.decision_outcome is not None:
            out = [r for r in out if r.decision_outcome == query.decision_outcome.strip().lower()]
        if query.start_time is not None:
            out = [r for r in out if r.timestamp >= query.start_time]
        if query.end_time is not None:
            out = [r for r in out if r.timestamp <= query.end_time]
        out.sort(key=lambda r: (r.timestamp, r.archive_id))
        if query.limit is not None and query.limit > 0:
            out = out[: query.limit]
        return out

    def list_records(self, query: DecisionQuery | None = None) -> list[DecisionRecord]:
        """Return records matching query; deterministic order. Does not mutate storage."""
        return self._apply_query(list(self._records), query)

    def list_by_strategy(self, strategy_id: str) -> list[DecisionRecord]:
        """Return records for strategy_id; deterministic order."""
        return self.list_records(DecisionQuery(strategy_id=strategy_id))

    def list_by_module(self, source_module: str) -> list[DecisionRecord]:
        """Return records for source_module; deterministic order."""
        return self.list_records(DecisionQuery(source_module=source_module))

    def list_by_outcome(self, decision_outcome: str) -> list[DecisionRecord]:
        """Return records for decision_outcome; deterministic order."""
        return self.list_records(DecisionQuery(decision_outcome=decision_outcome.strip().lower()))

    def build_summary(self, records: list[DecisionRecord] | None = None) -> DecisionArchiveSummary:
        """
        Build deterministic summary from given records or all stored records.
        Does not mutate inputs. strategies_seen and counts in stable order.
        """
        if records is None:
            records = self.list_records()
        total = len(records)
        by_module: dict[str, int] = {}
        by_outcome: dict[str, int] = {}
        strategies_seen: set[str] = set()
        reason_code_counts: dict[str, int] = {}
        for r in records:
            by_module[r.source_module] = by_module.get(r.source_module, 0) + 1
            by_outcome[r.decision_outcome] = by_outcome.get(r.decision_outcome, 0) + 1
            if r.strategy_id and r.strategy_id.strip():
                strategies_seen.add(r.strategy_id.strip())
            for code in r.reason_codes:
                if code.strip():
                    reason_code_counts[code.strip()] = reason_code_counts.get(code.strip(), 0) + 1
        return DecisionArchiveSummary(
            total_records=total,
            by_module=dict(sorted(by_module.items())),
            by_outcome=dict(sorted(by_outcome.items())),
            strategies_seen=sorted(strategies_seen),
            reason_code_counts=dict(sorted(reason_code_counts.items())),
            metadata={},
        )
