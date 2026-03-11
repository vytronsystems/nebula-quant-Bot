# NEBULA-QUANT v1 | nq_regime tests

from __future__ import annotations

import unittest
from typing import Any

from nq_regime import RegimeEngine, RegimeError, RegimeLabel
from nq_regime.classifiers import _classify_single


def make_clock(now: float = 100.0):
    def clock() -> float:
        return now
    return clock


def make_input(
    observation_id: str | None = "obs-1",
    symbol: str | None = "AAPL",
    timestamp: float | None = 100.0,
    moving_average_short: float | None = None,
    moving_average_long: float | None = None,
    trend_strength: float | None = None,
    volatility_percentile: float | None = None,
    momentum_score: float | None = None,
    structure_hint: str | None = None,
) -> dict[str, Any]:
    return {
        "observation_id": observation_id,
        "symbol": symbol,
        "timestamp": timestamp,
        "moving_average_short": moving_average_short,
        "moving_average_long": moving_average_long,
        "trend_strength": trend_strength,
        "volatility_percentile": volatility_percentile,
        "momentum_score": momentum_score,
        "structure_hint": structure_hint,
    }


class TestTrendUpClassification(unittest.TestCase):
    def test_trend_up_classification(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        inp = make_input(
            moving_average_short=110.0,
            moving_average_long=100.0,
            trend_strength=0.3,
        )
        report = engine.classify_regimes([inp])
        self.assertEqual(len(report.classifications), 1)
        self.assertEqual(report.classifications[0].primary_regime, RegimeLabel.TRENDING_UP.value)
        self.assertIn("Short MA above long MA", report.classifications[0].rationale)


class TestTrendDownClassification(unittest.TestCase):
    def test_trend_down_classification(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        inp = make_input(
            moving_average_short=90.0,
            moving_average_long=100.0,
            trend_strength=-0.25,
        )
        report = engine.classify_regimes([inp])
        self.assertEqual(report.classifications[0].primary_regime, RegimeLabel.TRENDING_DOWN.value)
        self.assertIn("Short MA below long MA", report.classifications[0].rationale)


class TestHighVolatilityClassification(unittest.TestCase):
    def test_high_volatility_classification(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        inp = make_input(volatility_percentile=85.0)
        report = engine.classify_regimes([inp])
        self.assertEqual(report.classifications[0].primary_regime, RegimeLabel.HIGH_VOLATILITY.value)
        self.assertIn("75", report.classifications[0].rationale)


class TestLowVolatilityClassification(unittest.TestCase):
    def test_low_volatility_classification(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        inp = make_input(volatility_percentile=15.0)
        report = engine.classify_regimes([inp])
        self.assertEqual(report.classifications[0].primary_regime, RegimeLabel.LOW_VOLATILITY.value)


class TestRangeBoundClassification(unittest.TestCase):
    def test_range_bound_by_structure_hint(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        inp = make_input(structure_hint="range_bound")
        report = engine.classify_regimes([inp])
        self.assertEqual(report.classifications[0].primary_regime, RegimeLabel.RANGE_BOUND.value)
        self.assertIn("range", report.classifications[0].rationale.lower())

    def test_range_bound_weak_trend_neutral_momentum(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        inp = make_input(trend_strength=0.05, momentum_score=0.05)
        report = engine.classify_regimes([inp])
        self.assertEqual(report.classifications[0].primary_regime, RegimeLabel.RANGE_BOUND.value)


class TestMixedClassification(unittest.TestCase):
    def test_mixed_when_signals_conflict(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        # Trend up but momentum down
        inp = make_input(
            moving_average_short=110.0,
            moving_average_long=100.0,
            trend_strength=0.2,
            momentum_score=-0.3,
        )
        report = engine.classify_regimes([inp])
        self.assertEqual(report.classifications[0].primary_regime, RegimeLabel.MIXED.value)
        self.assertIn("Conflicting", report.classifications[0].rationale)


class TestMomentumClassification(unittest.TestCase):
    def test_momentum_up(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        inp = make_input(momentum_score=0.5)
        report = engine.classify_regimes([inp])
        self.assertEqual(report.classifications[0].primary_regime, RegimeLabel.MOMENTUM_UP.value)

    def test_momentum_down(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        inp = make_input(momentum_score=-0.4)
        report = engine.classify_regimes([inp])
        self.assertEqual(report.classifications[0].primary_regime, RegimeLabel.MOMENTUM_DOWN.value)


class TestUnknownOrFailClosed(unittest.TestCase):
    def test_unknown_for_insufficient_input(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        inp = make_input()  # no trend, vol, momentum, structure
        inp.pop("volatility_percentile", None)
        inp.pop("moving_average_short", None)
        inp.pop("moving_average_long", None)
        inp.pop("trend_strength", None)
        inp.pop("momentum_score", None)
        inp.pop("structure_hint", None)
        report = engine.classify_regimes([inp])
        self.assertEqual(report.classifications[0].primary_regime, RegimeLabel.UNKNOWN.value)
        self.assertEqual(report.classifications[0].confidence_score, 0.0)
        self.assertIn("Insufficient", report.classifications[0].rationale)


class TestRationaleAndEvidenceLinkage(unittest.TestCase):
    def test_rationale_and_evidence_ids_exist(self) -> None:
        primary, secondary, confidence, rationale, evidence = _classify_single(
            make_input(volatility_percentile=80.0),
            "ev-0",
            "cl-1",
        )
        self.assertTrue(len(rationale) > 0)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0].category, "volatility_percentile")
        self.assertEqual(evidence[0].value, 80.0)

    def test_classification_has_evidence_ids(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        report = engine.classify_regimes([make_input(trend_strength=0.2, moving_average_short=101, moving_average_long=100)])
        self.assertEqual(len(report.classifications), 1)
        self.assertGreaterEqual(len(report.classifications[0].evidence_ids), 1)
        self.assertTrue(all(eid.startswith("ev-") for eid in report.classifications[0].evidence_ids))


class TestMalformedCriticalInputFailsClosed(unittest.TestCase):
    def test_regime_inputs_not_list_raises(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        with self.assertRaises(RegimeError):
            engine.classify_regimes("not-a-list")

    def test_regime_inputs_contains_none_raises(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        with self.assertRaises(RegimeError):
            engine.classify_regimes([make_input(), None])


class TestEmptyInputReturnsValidEmptyReport(unittest.TestCase):
    def test_empty_input_returns_valid_empty_report(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        report = engine.classify_regimes([])
        self.assertEqual(report.summary.total_classifications, 0)
        self.assertEqual(report.classifications, [])
        self.assertEqual(report.summary.by_primary_regime, {})
        self.assertEqual(report.summary.symbols_seen, [])

    def test_none_input_returns_empty_report(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        report = engine.classify_regimes(None)
        self.assertEqual(report.summary.total_classifications, 0)


class TestSameInputSameReportOutput(unittest.TestCase):
    def test_same_input_same_report_output(self) -> None:
        engine = RegimeEngine(clock=make_clock(50.0))
        inp = make_input(volatility_percentile=50.0, momentum_score=0.3)
        r1 = engine.classify_regimes([inp], generated_at=50.0)
        r2 = engine.classify_regimes([inp], generated_at=50.0)
        self.assertEqual(r1.classifications[0].primary_regime, r2.classifications[0].primary_regime)
        self.assertEqual(r1.classifications[0].rationale, r2.classifications[0].rationale)
        self.assertEqual(r1.summary.total_classifications, r2.summary.total_classifications)


class TestDeterministicReportIds(unittest.TestCase):
    def test_deterministic_report_ids(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        r1 = engine.classify_regimes([make_input(momentum_score=0.1)], report_id="custom-1")
        r2 = engine.classify_regimes([make_input(momentum_score=0.1)])
        r3 = engine.classify_regimes([make_input(momentum_score=0.1)])
        self.assertEqual(r1.report_id, "custom-1")
        self.assertEqual(r2.report_id, "regime-report-2")
        self.assertEqual(r3.report_id, "regime-report-3")


class TestDeterministicClassificationIds(unittest.TestCase):
    def test_deterministic_classification_ids(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        report = engine.classify_regimes([
            make_input(momentum_score=0.1),
            make_input(momentum_score=-0.1),
        ])
        ids = [c.classification_id for c in report.classifications]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(cid.startswith("cl-") for cid in ids))


class TestDeterministicEvidenceIds(unittest.TestCase):
    def test_deterministic_evidence_ids(self) -> None:
        primary, _, _, _, evidence = _classify_single(
            make_input(volatility_percentile=60.0),
            "ev-0",
            "cl-1",
        )
        self.assertEqual(len(evidence), 1)
        self.assertTrue(evidence[0].evidence_id.startswith("ev-0-"))


class TestSummaryCountsCorrect(unittest.TestCase):
    def test_summary_counts_correct(self) -> None:
        engine = RegimeEngine(clock=make_clock())
        report = engine.classify_regimes([
            make_input(volatility_percentile=80.0, symbol="A"),
            make_input(volatility_percentile=10.0, symbol="B"),
            make_input(momentum_score=0.5, symbol="C"),
        ])
        self.assertEqual(report.summary.total_classifications, 3)
        self.assertEqual(len(report.summary.symbols_seen), 3)
        self.assertIn("A", report.summary.symbols_seen)
        total_by_regime = sum(report.summary.by_primary_regime.values())
        self.assertEqual(total_by_regime, 3)


class TestNoHiddenDependencies(unittest.TestCase):
    def test_no_hidden_dependencies_on_external_services(self) -> None:
        from nq_regime import RegimeEngine
        from nq_regime.models import RegimeReport
        engine = RegimeEngine()
        report = engine.classify_regimes([])
        self.assertIsInstance(report, RegimeReport)
        self.assertEqual(report.summary.total_classifications, 0)
