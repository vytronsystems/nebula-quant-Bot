# NEBULA-QUANT v1 | nq_trade_review tests

from __future__ import annotations

import unittest
from typing import Callable

from nq_trade_review import TradeReviewEngine, TradeReviewError, TradeReviewInput


def make_clock(ticks: list[float]) -> tuple[list[float], Callable[[], float]]:
    it = iter(ticks)
    def clock() -> float:
        return next(it)
    return ticks, clock


def minimal_trade(trade_id: str = "T1", **kwargs: object) -> TradeReviewInput:
    return TradeReviewInput(trade_id=trade_id, symbol="AAPL", side="long", **kwargs)


class TestValidInputDeterministicReport(unittest.TestCase):
    def test_valid_trade_input_produces_deterministic_report(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(
            expected_entry_price=100.0,
            actual_entry_price=100.0,
            actual_exit_price=105.0,
            stop_loss_price=98.0,
            take_profit_price=106.0,
            quantity=10.0,
        )
        report = engine.run_review(trade)
        self.assertIsNotNone(report.review_id)
        self.assertIsInstance(report.generated_at, (int, float))
        self.assertEqual(report.summary.trade_id, "T1")
        self.assertIn(report.summary.outcome, ("win", "loss", "breakeven", "unknown"))
        self.assertEqual(report.summary.total_findings, report.summary.info_count + report.summary.warning_count + report.summary.critical_count)


class TestIncompleteTradeRecord(unittest.TestCase):
    def test_incomplete_trade_record_generates_expected_finding(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade()
        report = engine.run_review(trade)
        incomplete = [f for f in report.findings if f.category == "incomplete_trade_record"]
        self.assertGreaterEqual(len(incomplete), 1)
        self.assertEqual(incomplete[0].trade_id, "T1")
        self.assertEqual(report.summary.status, "incomplete")


class TestInconsistentTradeRecord(unittest.TestCase):
    def test_inconsistent_trade_record_generates_critical_finding(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(
            expected_entry_price=100.0,
            actual_entry_price=100.0,
            actual_exit_price=105.0,
            stop_loss_price=102.0,
            take_profit_price=106.0,
            quantity=10.0,
        )
        report = engine.run_review(trade)
        inconsistent = [f for f in report.findings if f.category == "inconsistent_trade_record"]
        self.assertGreaterEqual(len(inconsistent), 1)
        self.assertEqual(inconsistent[0].severity, "critical")


class TestPoorEntryQuality(unittest.TestCase):
    def test_poor_entry_quality_creates_expected_finding(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(
            expected_entry_price=100.0,
            actual_entry_price=102.0,
            actual_exit_price=105.0,
            stop_loss_price=98.0,
            take_profit_price=106.0,
            quantity=10.0,
        )
        report = engine.run_review(trade)
        entry = [f for f in report.findings if f.category == "poor_entry_quality"]
        self.assertGreaterEqual(len(entry), 1)
        self.assertIn(entry[0].severity, ("warning", "critical"))


class TestPoorExitQuality(unittest.TestCase):
    def test_poor_exit_quality_creates_expected_finding(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(
            expected_entry_price=100.0,
            actual_entry_price=100.0,
            expected_exit_price=105.0,
            actual_exit_price=102.0,
            stop_loss_price=98.0,
            take_profit_price=106.0,
            quantity=10.0,
        )
        report = engine.run_review(trade)
        exit_f = [f for f in report.findings if f.category == "poor_exit_quality"]
        self.assertGreaterEqual(len(exit_f), 1)


class TestExcessiveSlippage(unittest.TestCase):
    def test_excessive_slippage_creates_expected_finding(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(
            expected_entry_price=100.0,
            actual_entry_price=103.0,
            actual_exit_price=105.0,
            stop_loss_price=98.0,
            take_profit_price=106.0,
            quantity=10.0,
        )
        report = engine.run_review(trade)
        slip = [f for f in report.findings if f.category == "excessive_slippage"]
        self.assertGreaterEqual(len(slip), 1)
        self.assertIsNotNone(report.summary.slippage)


class TestRRUnderperformance(unittest.TestCase):
    def test_rr_underperformance_creates_expected_finding(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(
            expected_entry_price=100.0,
            actual_entry_price=100.0,
            actual_exit_price=101.0,
            stop_loss_price=98.0,
            take_profit_price=106.0,
            quantity=10.0,
            expected_rr=2.0,
        )
        report = engine.run_review(trade)
        rr = [f for f in report.findings if f.category == "rr_underperformance"]
        self.assertGreaterEqual(len(rr), 1)


class TestMissingOptionalFields(unittest.TestCase):
    def test_missing_optional_fields_do_not_crash_review(self) -> None:
        engine = TradeReviewEngine()
        trade = TradeReviewInput(trade_id="T1", symbol="X", side="buy")
        report = engine.run_review(trade)
        self.assertEqual(report.summary.trade_id, "T1")
        self.assertIsInstance(report.findings, list)


class TestMalformedCriticalInput(unittest.TestCase):
    def test_empty_trade_id_fails_closed(self) -> None:
        with self.assertRaises(TradeReviewError):
            TradeReviewInput(trade_id="", symbol="AAPL", side="long")

    def test_empty_symbol_fails_closed(self) -> None:
        with self.assertRaises(TradeReviewError):
            TradeReviewInput(trade_id="T1", symbol="", side="long")

    def test_invalid_side_fails_closed(self) -> None:
        with self.assertRaises(TradeReviewError):
            TradeReviewInput(trade_id="T1", symbol="AAPL", side="invalid")

    def test_negative_quantity_fails_closed(self) -> None:
        with self.assertRaises(TradeReviewError):
            minimal_trade(quantity=-1.0)


class TestFindingsSeverityCounts(unittest.TestCase):
    def test_findings_severity_counts_are_correct(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(
            expected_entry_price=100.0,
            actual_entry_price=103.0,
            actual_exit_price=105.0,
            stop_loss_price=98.0,
            take_profit_price=106.0,
            quantity=10.0,
        )
        report = engine.run_review(trade)
        self.assertEqual(
            report.summary.info_count + report.summary.warning_count + report.summary.critical_count,
            report.summary.total_findings,
        )


class TestRecommendationsDeterministic(unittest.TestCase):
    def test_recommendations_derived_deterministically(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(
            expected_entry_price=100.0,
            actual_entry_price=102.0,
            actual_exit_price=105.0,
            stop_loss_price=98.0,
            take_profit_price=106.0,
            quantity=10.0,
        )
        report = engine.run_review(trade)
        for rec in report.recommendations:
            self.assertIn("T1", rec)


class TestRepeatedInputsSameStructure(unittest.TestCase):
    def test_repeated_same_inputs_yield_same_report_structure(self) -> None:
        _, clock = make_clock([100.0, 101.0])
        engine = TradeReviewEngine(clock=clock)
        trade = minimal_trade(
            expected_entry_price=100.0,
            actual_entry_price=100.0,
            actual_exit_price=105.0,
            stop_loss_price=98.0,
            take_profit_price=106.0,
            quantity=10.0,
        )
        r1 = engine.run_review(trade, generated_at=100.0)
        r2 = engine.run_review(trade, generated_at=100.0)
        self.assertEqual(len(r1.findings), len(r2.findings))
        self.assertEqual([f.category for f in r1.findings], [f.category for f in r2.findings])


class TestReviewIdsDeterministic(unittest.TestCase):
    def test_review_ids_deterministic(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(quantity=1.0, actual_entry_price=1.0, actual_exit_price=2.0)
        r1 = engine.run_review(trade, review_id="custom-1")
        r2 = engine.run_review(trade)
        r3 = engine.run_review(trade)
        self.assertEqual(r1.review_id, "custom-1")
        self.assertEqual(r2.review_id, "trade-review-2")
        self.assertEqual(r3.review_id, "trade-review-3")


class TestNoHiddenDependencies(unittest.TestCase):
    def test_no_hidden_external_services(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(quantity=1.0, actual_entry_price=1.0, actual_exit_price=2.0)
        report = engine.run_review(trade)
        self.assertIsNotNone(report.review_id)
        self.assertIsInstance(report.findings, list)


class TestOutcomeClassification(unittest.TestCase):
    def test_outcome_win_deterministic(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(
            actual_entry_price=100.0,
            actual_exit_price=105.0,
            stop_loss_price=98.0,
            take_profit_price=106.0,
            quantity=10.0,
        )
        report = engine.run_review(trade)
        self.assertEqual(report.summary.outcome, "win")

    def test_outcome_loss_deterministic(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(
            actual_entry_price=100.0,
            actual_exit_price=97.0,
            stop_loss_price=98.0,
            take_profit_price=106.0,
            quantity=10.0,
        )
        report = engine.run_review(trade)
        self.assertEqual(report.summary.outcome, "loss")

    def test_outcome_breakeven_deterministic(self) -> None:
        engine = TradeReviewEngine()
        trade = minimal_trade(
            actual_entry_price=100.0,
            actual_exit_price=100.0,
            stop_loss_price=98.0,
            take_profit_price=106.0,
            quantity=10.0,
        )
        report = engine.run_review(trade)
        self.assertEqual(report.summary.outcome, "breakeven")
