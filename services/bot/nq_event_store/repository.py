# NEBULA-QUANT v1 | nq_event_store repository (append-only)

from __future__ import annotations

import json
from typing import Any

from nq_db.engine import DatabaseEngine, DatabaseError
from nq_event_store.engine import EventStoreError
from nq_event_store.models import EventRecord


def _serialize_payload(obj: Any) -> str:
    """Serialize payload/metadata to JSON. Deterministic (sort_keys). Fail closed on invalid."""
    if obj is None:
        return "{}"
    if not isinstance(obj, dict):
        raise EventStoreError("payload and metadata must be dict or None")
    try:
        return json.dumps(obj, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise EventStoreError(f"failed to serialize JSON: {exc}") from exc


def _deserialize_payload(text: str | None) -> dict[str, Any]:
    """Deserialize JSON to dict. Fail closed on invalid."""
    if text is None or text.strip() == "":
        return {}
    try:
        out = json.loads(text)
        if not isinstance(out, dict):
            raise EventStoreError("stored payload/metadata must deserialize to dict")
        return out
    except (TypeError, ValueError) as exc:
        raise EventStoreError(f"failed to deserialize JSON: {exc}") from exc


def _validate_record(record: EventRecord) -> None:
    """Ensure required identity fields present. Fail closed."""
    if not (record.event_id and record.event_id.strip()):
        raise EventStoreError("event_id is required and non-empty")
    if not (record.event_type and record.event_type.strip()):
        raise EventStoreError("event_type is required and non-empty")
    if not (record.aggregate_type and record.aggregate_type.strip()):
        raise EventStoreError("aggregate_type is required and non-empty")
    if not (record.aggregate_id and record.aggregate_id.strip()):
        raise EventStoreError("aggregate_id is required and non-empty")
    if not (record.timestamp and record.timestamp.strip()):
        raise EventStoreError("timestamp is required and non-empty")
    if not isinstance(record.payload, dict):
        raise EventStoreError("payload must be a dict")


def _row_to_record(row: dict[str, Any]) -> EventRecord:
    return EventRecord(
        event_id=row["event_id"],
        event_type=row["event_type"],
        aggregate_type=row["aggregate_type"],
        aggregate_id=row["aggregate_id"],
        timestamp=row["timestamp"],
        payload=_deserialize_payload(row["payload"]),
        metadata=_deserialize_payload(row["metadata"]) if row.get("metadata") else {},
        sequence_id=row.get("sequence_id"),
    )


class EventStoreRepository:
    """Append-only repository for events. No update or delete methods."""

    def __init__(self, engine: DatabaseEngine) -> None:
        self._engine = engine

    def append_event(self, record: EventRecord) -> EventRecord:
        """Append a single event. Returns the record with sequence_id set. Duplicate event_id raises."""
        _validate_record(record)
        payload_str = _serialize_payload(record.payload)
        metadata_str = _serialize_payload(record.metadata) if record.metadata else "{}"
        try:
            self._engine.execute(
                """INSERT INTO events (event_id, event_type, aggregate_type, aggregate_id, timestamp, payload, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.event_id.strip(),
                    record.event_type.strip(),
                    record.aggregate_type.strip(),
                    record.aggregate_id.strip(),
                    record.timestamp.strip(),
                    payload_str,
                    metadata_str,
                ),
            )
            self._engine.commit()
        except DatabaseError as exc:
            if "UNIQUE" in str(exc) or "unique" in str(exc):
                raise EventStoreError(f"duplicate event_id: {record.event_id!r}") from exc
            raise EventStoreError(f"append failed: {exc}") from exc
        row = self._engine.fetch_one(
            "SELECT sequence_id, event_id, event_type, aggregate_type, aggregate_id, timestamp, payload, metadata FROM events WHERE event_id = ?",
            (record.event_id,),
        )
        if not row:
            raise EventStoreError("append succeeded but event not found by event_id")
        return _row_to_record(dict(row))

    def fetch_by_event_id(self, event_id: str) -> EventRecord | None:
        row = self._engine.fetch_one(
            "SELECT sequence_id, event_id, event_type, aggregate_type, aggregate_id, timestamp, payload, metadata FROM events WHERE event_id = ?",
            (event_id,),
        )
        return _row_to_record(dict(row)) if row else None

    def fetch_by_aggregate_id(
        self, aggregate_id: str, limit: int | None = None
    ) -> list[EventRecord]:
        sql = """SELECT sequence_id, event_id, event_type, aggregate_type, aggregate_id, timestamp, payload, metadata
                 FROM events WHERE aggregate_id = ? ORDER BY sequence_id ASC"""
        if limit is not None:
            sql += " LIMIT ?"
            rows = self._engine.fetch_many(sql, (aggregate_id, limit))
        else:
            rows = self._engine.fetch_many(sql, (aggregate_id,))
        return [_row_to_record(dict(r)) for r in rows]

    def fetch_by_event_type(
        self, event_type: str, limit: int | None = None
    ) -> list[EventRecord]:
        sql = """SELECT sequence_id, event_id, event_type, aggregate_type, aggregate_id, timestamp, payload, metadata
                 FROM events WHERE event_type = ? ORDER BY sequence_id ASC"""
        if limit is not None:
            sql += " LIMIT ?"
            rows = self._engine.fetch_many(sql, (event_type, limit))
        else:
            rows = self._engine.fetch_many(sql, (event_type,))
        return [_row_to_record(dict(r)) for r in rows]

    def fetch_by_aggregate_type(
        self, aggregate_type: str, limit: int | None = None
    ) -> list[EventRecord]:
        sql = """SELECT sequence_id, event_id, event_type, aggregate_type, aggregate_id, timestamp, payload, metadata
                 FROM events WHERE aggregate_type = ? ORDER BY sequence_id ASC"""
        if limit is not None:
            sql += " LIMIT ?"
            rows = self._engine.fetch_many(sql, (aggregate_type, limit))
        else:
            rows = self._engine.fetch_many(sql, (aggregate_type,))
        return [_row_to_record(dict(r)) for r in rows]

    def fetch_all(self, limit: int | None = None) -> list[EventRecord]:
        sql = """SELECT sequence_id, event_id, event_type, aggregate_type, aggregate_id, timestamp, payload, metadata
                 FROM events ORDER BY sequence_id ASC"""
        if limit is not None:
            sql += " LIMIT ?"
            rows = self._engine.fetch_many(sql, (limit,))
        else:
            rows = self._engine.fetch_many(sql)
        return [_row_to_record(dict(r)) for r in rows]

    def fetch_after_sequence(self, sequence_id: int) -> list[EventRecord]:
        rows = self._engine.fetch_many(
            """SELECT sequence_id, event_id, event_type, aggregate_type, aggregate_id, timestamp, payload, metadata
               FROM events WHERE sequence_id > ? ORDER BY sequence_id ASC""",
            (sequence_id,),
        )
        return [_row_to_record(dict(r)) for r in rows]

    def fetch_recent(self, limit: int = 100) -> list[EventRecord]:
        """Return most recent events by sequence_id (descending)."""
        rows = self._engine.fetch_many(
            """SELECT sequence_id, event_id, event_type, aggregate_type, aggregate_id, timestamp, payload, metadata
               FROM events ORDER BY sequence_id DESC LIMIT ?""",
            (limit,),
        )
        return [_row_to_record(dict(r)) for r in reversed(rows)]
