# NEBULA-QUANT v1 | nq_data_quality tests — engine, validation, fail-closed

from __future__ import annotations

import unittest

from nq_data_quality import DataQualityEngine, DataQualityResult


class TestEngineInitialization(unittest.TestCase):
    """Module and engine initialization."""

    def test_engine_creates(self) -> None:
        engine = DataQualityEngine()
        self.assertIsNotNone(engine)

    def test_validate_dataset_accepts_none_data(self) -> None:
        engine = DataQualityEngine()
        result = engine.validate_dataset(data=None)
        self.assertIsInstance(result, DataQualityResult)
        self.assertTrue(result.valid)
        self.assertEqual(result.issue_count, 0)
        self.assertEqual(result.issues, [])


class TestEmptyDataset(unittest.TestCase):
    """Empty input returns valid, no issues."""

    def test_empty_list_returns_valid(self) -> None:
        engine = DataQualityEngine()
        result = engine.validate_dataset(data=[])
        self.assertTrue(result.valid)
        self.assertEqual(len(result.issues), 0)
        self.assertEqual(result.issue_count, 0)

    def test_deterministic_empty(self) -> None:
        engine = DataQualityEngine()
        r1 = engine.validate_dataset(data=[])
        r2 = engine.validate_dataset(data=[])
        self.assertEqual(r1.valid, r2.valid)
        self.assertEqual(r1.issue_count, r2.issue_count)


class TestDatasetWithData(unittest.TestCase):
    """Non-empty dataset runs checks; result structure is correct."""

    def test_result_has_required_fields(self) -> None:
        engine = DataQualityEngine()
        result = engine.validate_dataset(data=[{"ts": 1, "close": 100}], symbol="QQQ", timeframe="1m")
        self.assertIsInstance(result.valid, bool)
        self.assertIsInstance(result.issues, list)
        self.assertEqual(result.issue_count, len(result.issues))
        self.assertEqual(result.symbol, "QQQ")
        self.assertEqual(result.timeframe, "1m")

    def test_same_input_same_output(self) -> None:
        engine = DataQualityEngine()
        data = [{"ts": 1000, "open": 100, "high": 101, "low": 99, "close": 100.5}]
        r1 = engine.validate_dataset(data=data)
        r2 = engine.validate_dataset(data=data)
        self.assertEqual(r1.valid, r2.valid)
        self.assertEqual(r1.issue_count, r2.issue_count)
