# NEBULA-QUANT v1 | nq_event_store tests

from __future__ import annotations

import tempfile
import unittest

from nq_event_store import (
    EVENT_TYPE_RISK_DECISION,
    EventRecord,
    EventStoreEngine,
    EventStoreError,
    EventStoreRepository,
)


def _make_record(
    event_id: str = "ev-1",
    event_type: str = EVENT_TYPE_RISK_DECISION,
    aggregate_id: str = "agg-1",
    aggregate_type: str = "risk",
    timestamp: str = "2025-03-11T12:00:00Z",
    payload: dict | None = None,
    metadata: dict | None = None,
) -> EventRecord:
    return EventRecord(
        event_id=event_id,
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        timestamp=timestamp,
        payload=payload or {},
        metadata=metadata,
    )


class TestEventStoreSchema(unittest.TestCase):
    def test_schema_initializes_correctly(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".sqlite3") as tmp:
            store = EventStoreEngine(db_path=tmp.name)
            repo = EventStoreRepository(store.engine)
            out = repo.fetch_all()
            self.assertEqual(out, [])
            store.close()


class TestAppendAndFetch(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3")
        self.store = EventStoreEngine(db_path=self.tmp.name)
        self.repo = EventStoreRepository(self.store.engine)

    def tearDown(self) -> None:
        self.store.close()
        self.tmp.close()

    def test_valid_event_append_succeeds(self) -> None:
        rec = _make_record(event_id="ev-append-1", payload={"action": "allow"})
        with self.store.engine.transaction():
            out = self.repo.append_event(rec)
        self.assertIsNotNone(out.sequence_id)
        self.assertEqual(out.event_id, "ev-append-1")
        self.assertEqual(out.payload, {"action": "allow"})

    def test_fetched_event_matches_appended(self) -> None:
        rec = _make_record(event_id="ev-match-1", payload={"k": "v"}, metadata={"src": "test"})
        with self.store.engine.transaction():
            appended = self.repo.append_event(rec)
        fetched = self.repo.fetch_by_event_id("ev-match-1")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.event_id, appended.event_id)
        self.assertEqual(fetched.payload, {"k": "v"})
        self.assertEqual(fetched.metadata, {"src": "test"})
        self.assertEqual(fetched.sequence_id, appended.sequence_id)

    def test_fetch_all_returns_events_in_sequence_order(self) -> None:
        for i in range(3):
            rec = _make_record(event_id=f"ev-order-{i}", timestamp=f"2025-03-11T12:00:0{i}Z")
            with self.store.engine.transaction():
                self.repo.append_event(rec)
        all_events = self.repo.fetch_all()
        self.assertEqual(len(all_events), 3)
        self.assertEqual([e.event_id for e in all_events], ["ev-order-0", "ev-order-1", "ev-order-2"])
        for i, e in enumerate(all_events):
            self.assertIsNotNone(e.sequence_id)
            if i > 0:
                self.assertGreater(e.sequence_id, all_events[i - 1].sequence_id)

    def test_fetch_by_aggregate_id(self) -> None:
        with self.store.engine.transaction():
            self.repo.append_event(_make_record(event_id="a1", aggregate_id="agg-X"))
            self.repo.append_event(_make_record(event_id="a2", aggregate_id="agg-X"))
            self.repo.append_event(_make_record(event_id="b1", aggregate_id="agg-Y"))
        by_x = self.repo.fetch_by_aggregate_id("agg-X")
        self.assertEqual(len(by_x), 2)
        self.assertEqual({e.event_id for e in by_x}, {"a1", "a2"})
        by_x_lim = self.repo.fetch_by_aggregate_id("agg-X", limit=1)
        self.assertEqual(len(by_x_lim), 1)

    def test_fetch_by_event_type(self) -> None:
        with self.store.engine.transaction():
            self.repo.append_event(_make_record(event_id="r1", event_type="risk_decision"))
            self.repo.append_event(_make_record(event_id="r2", event_type="risk_decision"))
            self.repo.append_event(_make_record(event_id="e1", event_type="execution_event"))
        risk = self.repo.fetch_by_event_type("risk_decision")
        self.assertEqual(len(risk), 2)
        self.assertEqual({e.event_id for e in risk}, {"r1", "r2"})
        risk_lim = self.repo.fetch_by_event_type("risk_decision", limit=1)
        self.assertEqual(len(risk_lim), 1)

    def test_fetch_after_sequence(self) -> None:
        with self.store.engine.transaction():
            a = self.repo.append_event(_make_record(event_id="s1"))
            self.repo.append_event(_make_record(event_id="s2"))
            self.repo.append_event(_make_record(event_id="s3"))
        after = self.repo.fetch_after_sequence(a.sequence_id or 0)
        self.assertEqual(len(after), 2)
        self.assertEqual([e.event_id for e in after], ["s2", "s3"])

    def test_duplicate_event_id_fails_closed(self) -> None:
        rec = _make_record(event_id="dup-1")
        with self.store.engine.transaction():
            self.repo.append_event(rec)
        with self.assertRaises(EventStoreError) as ctx:
            with self.store.engine.transaction():
                self.repo.append_event(rec)
        self.assertIn("duplicate", str(ctx.exception).lower())

    def test_malformed_payload_fails_closed(self) -> None:
        rec = _make_record(event_id="bad-1")
        object.__setattr__(rec, "payload", "not a dict")  # type: ignore[arg-type]
        with self.assertRaises(EventStoreError):
            self.repo.append_event(rec)

    def test_missing_required_fields_fail_closed(self) -> None:
        with self.assertRaises(EventStoreError):
            self.repo.append_event(_make_record(event_id=""))
        with self.assertRaises(EventStoreError):
            self.repo.append_event(_make_record(event_id="x", event_type=""))
        with self.assertRaises(EventStoreError):
            self.repo.append_event(_make_record(event_id="x", aggregate_type=""))
        with self.assertRaises(EventStoreError):
            self.repo.append_event(_make_record(event_id="x", aggregate_id=""))
        with self.assertRaises(EventStoreError):
            self.repo.append_event(_make_record(event_id="x", timestamp=""))

    def test_append_only_no_update_delete_api(self) -> None:
        self.assertFalse(hasattr(EventStoreRepository, "update_event"))
        self.assertFalse(hasattr(EventStoreRepository, "delete_event"))

    def test_repeated_deterministic_inserts_preserve_replay_order(self) -> None:
        ids = [f"rep-{i}" for i in range(5)]
        with self.store.engine.transaction():
            for eid in ids:
                self.repo.append_event(_make_record(event_id=eid))
        all_events = self.repo.fetch_all()
        self.assertEqual([e.event_id for e in all_events], ids)

    def test_json_payload_metadata_roundtrip(self) -> None:
        payload = {"nested": {"a": 1, "b": [2, 3]}, "str": "ok"}
        metadata = {"trace_id": "tr-1", "tags": ["x", "y"]}
        rec = _make_record(event_id="json-1", payload=payload, metadata=metadata)
        with self.store.engine.transaction():
            appended = self.repo.append_event(rec)
        self.assertEqual(appended.payload, payload)
        self.assertEqual(appended.metadata, metadata)
        fetched = self.repo.fetch_by_event_id("json-1")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.payload, payload)
        self.assertEqual(fetched.metadata, metadata)

    def test_fetch_by_aggregate_type(self) -> None:
        with self.store.engine.transaction():
            self.repo.append_event(_make_record(event_id="t1", aggregate_type="strategy"))
            self.repo.append_event(_make_record(event_id="t2", aggregate_type="strategy"))
            self.repo.append_event(_make_record(event_id="t3", aggregate_type="execution"))
        strategy = self.repo.fetch_by_aggregate_type("strategy")
        self.assertEqual(len(strategy), 2)
        self.assertEqual({e.event_id for e in strategy}, {"t1", "t2"})

    def test_fetch_recent(self) -> None:
        with self.store.engine.transaction():
            for i in range(5):
                self.repo.append_event(_make_record(event_id=f"rec-{i}"))
        recent = self.repo.fetch_recent(limit=3)
        self.assertEqual(len(recent), 3)
        self.assertEqual([e.event_id for e in recent], ["rec-2", "rec-3", "rec-4"])
