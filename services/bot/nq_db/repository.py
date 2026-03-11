# NEBULA-QUANT v1 | nq_db repositories

from __future__ import annotations

import json
from typing import Any, Iterable

from nq_db.engine import DatabaseEngine, DatabaseError
from nq_db.models import (
    DecisionRecord,
    ExecutionRecord,
    ExperimentRecord,
    ObservabilitySnapshotRecord,
    StrategyRecord,
)


def _dumps(obj: Any) -> str:
    try:
        return json.dumps(obj or {})
    except (TypeError, ValueError) as exc:
        raise DatabaseError(f"failed to serialize metadata: {exc}") from exc


def _loads(text: str | None) -> Any:
    if text is None:
        return {}
    try:
        return json.loads(text)
    except (TypeError, ValueError) as exc:
        raise DatabaseError(f"failed to deserialize JSON: {exc}") from exc


class BaseRepository:
    def __init__(self, engine: DatabaseEngine) -> None:
        self._engine = engine


class StrategyRepository(BaseRepository):
    def insert(self, record: StrategyRecord) -> None:
        self._engine.execute(
            "INSERT OR REPLACE INTO strategies (strategy_id, lifecycle_state, enabled, created_at, updated_at, metadata)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                record.strategy_id,
                record.lifecycle_state,
                int(record.enabled),
                record.created_at,
                record.updated_at,
                _dumps(record.metadata),
            ),
        )

    def fetch_by_id(self, strategy_id: str) -> StrategyRecord | None:
        row = self._engine.fetch_one(
            "SELECT strategy_id, lifecycle_state, enabled, created_at, updated_at, metadata FROM strategies WHERE strategy_id = ?",
            (strategy_id,),
        )
        if row is None:
            return None
        return StrategyRecord(
            strategy_id=row["strategy_id"],
            lifecycle_state=row["lifecycle_state"],
            enabled=bool(row["enabled"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            metadata=_loads(row["metadata"]),
        )


class ExecutionRepository(BaseRepository):
    def insert(self, record: ExecutionRecord) -> None:
        self._engine.execute(
            "INSERT OR REPLACE INTO executions (execution_id, strategy_id, symbol, side, quantity, price, status, timestamp, metadata)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                record.execution_id,
                record.strategy_id,
                record.symbol,
                record.side,
                record.quantity,
                record.price,
                record.status,
                record.timestamp,
                _dumps(record.metadata),
            ),
        )

    def fetch_by_id(self, execution_id: str) -> ExecutionRecord | None:
        row = self._engine.fetch_one(
            "SELECT execution_id, strategy_id, symbol, side, quantity, price, status, timestamp, metadata FROM executions WHERE execution_id = ?",
            (execution_id,),
        )
        if row is None:
            return None
        return ExecutionRecord(
            execution_id=row["execution_id"],
            strategy_id=row["strategy_id"],
            symbol=row["symbol"],
            side=row["side"],
            quantity=row["quantity"],
            price=row["price"],
            status=row["status"],
            timestamp=row["timestamp"],
            metadata=_loads(row["metadata"]),
        )

    def fetch_by_strategy(self, strategy_id: str, limit: int = 50) -> list[ExecutionRecord]:
        rows = self._engine.fetch_many(
            "SELECT execution_id, strategy_id, symbol, side, quantity, price, status, timestamp, metadata"
            " FROM executions WHERE strategy_id = ? ORDER BY timestamp DESC LIMIT ?",
            (strategy_id, limit),
        )
        return [
            ExecutionRecord(
                execution_id=r["execution_id"],
                strategy_id=r["strategy_id"],
                symbol=r["symbol"],
                side=r["side"],
                quantity=r["quantity"],
                price=r["price"],
                status=r["status"],
                timestamp=r["timestamp"],
                metadata=_loads(r["metadata"]),
            )
            for r in rows
        ]


class ObservabilityRepository(BaseRepository):
    def insert(self, record: ObservabilitySnapshotRecord) -> None:
        self._engine.execute(
            "INSERT OR REPLACE INTO observability_snapshots (snapshot_id, generated_at, system_summary, metadata)"
            " VALUES (?, ?, ?, ?)",
            (
                record.snapshot_id,
                record.generated_at,
                _dumps(record.system_summary),
                _dumps(record.metadata),
            ),
        )

    def fetch_recent(self, limit: int = 20) -> list[ObservabilitySnapshotRecord]:
        rows = self._engine.fetch_many(
            "SELECT snapshot_id, generated_at, system_summary, metadata"
            " FROM observability_snapshots ORDER BY generated_at DESC LIMIT ?",
            (limit,),
        )
        return [
            ObservabilitySnapshotRecord(
                snapshot_id=r["snapshot_id"],
                generated_at=r["generated_at"],
                system_summary=_loads(r["system_summary"]),
                metadata=_loads(r["metadata"]),
            )
            for r in rows
        ]


class ExperimentRepository(BaseRepository):
    def insert(self, record: ExperimentRecord) -> None:
        self._engine.execute(
            "INSERT OR REPLACE INTO experiments (experiment_id, strategy_id, start_time, end_time, result_status, metrics, metadata)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                record.experiment_id,
                record.strategy_id,
                record.start_time,
                record.end_time,
                record.result_status,
                _dumps(record.metrics),
                _dumps(record.metadata),
            ),
        )

    def fetch_by_id(self, experiment_id: str) -> ExperimentRecord | None:
        row = self._engine.fetch_one(
            "SELECT experiment_id, strategy_id, start_time, end_time, result_status, metrics, metadata"
            " FROM experiments WHERE experiment_id = ?",
            (experiment_id,),
        )
        if row is None:
            return None
        return ExperimentRecord(
            experiment_id=row["experiment_id"],
            strategy_id=row["strategy_id"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            result_status=row["result_status"],
            metrics=_loads(row["metrics"]),
            metadata=_loads(row["metadata"]),
        )


class DecisionRepository(BaseRepository):
    def insert(self, record: DecisionRecord) -> None:
        self._engine.execute(
            "INSERT OR REPLACE INTO decisions (decision_id, module_name, decision_type, strategy_id, timestamp, reason_codes, metadata)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                record.decision_id,
                record.module_name,
                record.decision_type,
                record.strategy_id,
                record.timestamp,
                _dumps(record.reason_codes),
                _dumps(record.metadata),
            ),
        )

    def fetch_recent(self, module_name: str | None = None, limit: int = 50) -> list[DecisionRecord]:
        if module_name:
            rows = self._engine.fetch_many(
                "SELECT decision_id, module_name, decision_type, strategy_id, timestamp, reason_codes, metadata"
                " FROM decisions WHERE module_name = ? ORDER BY timestamp DESC LIMIT ?",
                (module_name, limit),
            )
        else:
            rows = self._engine.fetch_many(
                "SELECT decision_id, module_name, decision_type, strategy_id, timestamp, reason_codes, metadata"
                " FROM decisions ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
        return [
            DecisionRecord(
                decision_id=r["decision_id"],
                module_name=r["module_name"],
                decision_type=r["decision_type"],
                strategy_id=r["strategy_id"],
                timestamp=r["timestamp"],
                reason_codes=_loads(r["reason_codes"]),
                metadata=_loads(r["metadata"]),
            )
            for r in rows
        ]
