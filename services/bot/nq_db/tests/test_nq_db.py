# NEBULA-QUANT v1 | nq_db tests

from __future__ import annotations

import tempfile
import time
import unittest

from nq_db import (
    DatabaseEngine,
    DatabaseError,
    DecisionRecord,
    DecisionRepository,
    ExecutionRecord,
    ExecutionRepository,
    ExperimentRecord,
    ExperimentRepository,
    ObservabilityRepository,
    ObservabilitySnapshotRecord,
    StrategyRecord,
    StrategyRepository,
)


class TestDatabaseEngine(unittest.TestCase):
    def test_initialize_and_close(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".sqlite3") as tmp:
            engine = DatabaseEngine(db_path=tmp.name)
            engine.close()

    def test_transaction_commit_and_rollback(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".sqlite3") as tmp:
            engine = DatabaseEngine(db_path=tmp.name)
            with engine.transaction():
                engine.execute("CREATE TABLE IF NOT EXISTS t (id INTEGER PRIMARY KEY, v TEXT)")
                engine.execute("INSERT INTO t (v) VALUES (?)", ("a",))
            row = engine.fetch_one("SELECT v FROM t WHERE id = 1")
            self.assertEqual(row["v"], "a")
            with self.assertRaises(DatabaseError):
                with engine.transaction():
                    engine.execute("INSERT INTO t (v) VALUES (?)", ("b",))
                    engine.execute("INSERT INTO non_existing (v) VALUES (?)", ("c",))
            rows = engine.fetch_many("SELECT v FROM t")
            self.assertEqual(len(rows), 1)


class TestRepositories(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3")
        self.engine = DatabaseEngine(db_path=self.tmp.name)

    def tearDown(self) -> None:
        self.engine.close()
        self.tmp.close()

    def test_strategy_repository_insert_and_fetch(self) -> None:
        repo = StrategyRepository(self.engine)
        now = time.time()
        rec = StrategyRecord(
            strategy_id="s1",
            lifecycle_state="paper",
            enabled=True,
            created_at=now,
            updated_at=now,
            metadata={"owner": "system"},
        )
        with self.engine.transaction():
            repo.insert(rec)
        loaded = repo.fetch_by_id("s1")
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.strategy_id, "s1")
        self.assertTrue(loaded.enabled)
        self.assertEqual(loaded.metadata.get("owner"), "system")

    def test_execution_repository_insert_and_fetch(self) -> None:
        srepo = StrategyRepository(self.engine)
        now = time.time()
        with self.engine.transaction():
            srepo.insert(
                StrategyRecord(
                    strategy_id="s1",
                    lifecycle_state="paper",
                    enabled=True,
                    created_at=now,
                    updated_at=now,
                )
            )
        repo = ExecutionRepository(self.engine)
        rec = ExecutionRecord(
            execution_id="e1",
            strategy_id="s1",
            symbol="AAPL",
            side="buy",
            quantity=10.0,
            price=100.0,
            status="filled",
            timestamp=now,
            metadata={"note": "test"},
        )
        with self.engine.transaction():
            repo.insert(rec)
        loaded = repo.fetch_by_id("e1")
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.symbol, "AAPL")
        self.assertEqual(len(repo.fetch_by_strategy("s1")), 1)

    def test_observability_repository_insert_and_fetch_recent(self) -> None:
        repo = ObservabilityRepository(self.engine)
        now = time.time()
        rec = ObservabilitySnapshotRecord(
            snapshot_id="snap1",
            generated_at=now,
            system_summary={"total_strategies": 1},
            metadata={"source": "test"},
        )
        with self.engine.transaction():
            repo.insert(rec)
        snaps = repo.fetch_recent(limit=5)
        self.assertEqual(len(snaps), 1)
        self.assertEqual(snaps[0].system_summary.get("total_strategies"), 1)

    def test_experiment_repository_insert_and_fetch(self) -> None:
        repo = ExperimentRepository(self.engine)
        now = time.time()
        rec = ExperimentRecord(
            experiment_id="exp1",
            strategy_id="s1",
            start_time=now,
            end_time=now + 10,
            result_status="completed",
            metrics={"win_rate": 0.6},
            metadata={"note": "ok"},
        )
        with self.engine.transaction():
            repo.insert(rec)
        loaded = repo.fetch_by_id("exp1")
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.result_status, "completed")
        self.assertEqual(loaded.metrics.get("win_rate"), 0.6)

    def test_decision_repository_insert_and_fetch_recent(self) -> None:
        repo = DecisionRepository(self.engine)
        now = time.time()
        with self.engine.transaction():
            repo.insert(
                DecisionRecord(
                    decision_id="d1",
                    module_name="nq_risk",
                    decision_type="BLOCK",
                    strategy_id="s1",
                    timestamp=now,
                    reason_codes=["example_reason"],
                    metadata={"detail": "x"},
                )
            )
        recents = repo.fetch_recent(module_name="nq_risk", limit=10)
        self.assertEqual(len(recents), 1)
        self.assertEqual(recents[0].decision_type, "BLOCK")
        self.assertIn("example_reason", recents[0].reason_codes)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
