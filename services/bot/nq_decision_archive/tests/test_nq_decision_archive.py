# NEBULA-QUANT v1 | nq_decision_archive tests

from __future__ import annotations

import unittest
from typing import Any

from nq_decision_archive import (
    DecisionArchiveEngine,
    DecisionArchiveError,
    DecisionQuery,
    normalize_guardrails_decision,
    normalize_portfolio_decision,
    normalize_promotion_decision,
    normalize_risk_decision,
)


def make_clock(now: float = 100.0):
    def clock() -> float:
        return now
    return clock


# --- Risk: decision "allow" | "reduce" | "block", reason_codes, optional strategy_id, symbol, timestamp
def make_risk_payload(
    decision: str = "allow",
    reason_codes: list[str] | None = None,
    strategy_id: str | None = "s1",
    symbol: str | None = "AAPL",
    timestamp: float = 200.0,
) -> dict[str, Any]:
    return {
        "decision": decision,
        "reason_codes": reason_codes or [],
        "strategy_id": strategy_id,
        "symbol": symbol,
        "timestamp": timestamp,
    }


# --- Guardrails: allowed, reason, signals (optional), timestamp
def make_guardrails_payload(
    allowed: bool = True,
    reason: str = "ok",
    timestamp: float = 200.0,
    strategy_id: str | None = None,
) -> dict[str, Any]:
    return {
        "allowed": allowed,
        "reason": reason,
        "timestamp": timestamp,
        "strategy_id": strategy_id,
    }


# --- Portfolio: decision allow/throttle/block, reason_codes, timestamp
def make_portfolio_payload(
    decision: str = "allow",
    reason_codes: list[str] | None = None,
    strategy_id: str | None = "s1",
    timestamp: float = 200.0,
) -> dict[str, Any]:
    return {
        "decision": decision,
        "reason_codes": reason_codes or [],
        "strategy_id": strategy_id,
        "timestamp": timestamp,
    }


# --- Promotion: allowed, blocking_issues, reason, strategy_id; or decision.allowed, evaluated_at
def make_promotion_payload(
    allowed: bool = True,
    blocking_issues: list[str] | None = None,
    reason: str = "ok",
    strategy_id: str | None = "s1",
    evaluated_at: float = 200.0,
) -> dict[str, Any]:
    return {
        "allowed": allowed,
        "blocking_issues": blocking_issues or [],
        "reason": reason,
        "strategy_id": strategy_id,
        "evaluated_at": evaluated_at,
    }


class TestNormalizeRiskDecision(unittest.TestCase):
    def test_normalize_risk_decision_allow(self) -> None:
        r = normalize_risk_decision(
            make_risk_payload(decision="allow", reason_codes=["ok"]),
            "da-1",
            timestamp=300.0,
        )
        self.assertEqual(r.source_module, "nq_risk")
        self.assertEqual(r.decision_outcome, "allow")
        self.assertEqual(r.reason_codes, ["ok"])
        self.assertEqual(r.strategy_id, "s1")
        self.assertEqual(r.symbol, "AAPL")
        self.assertEqual(r.timestamp, 300.0)

    def test_normalize_risk_decision_block(self) -> None:
        r = normalize_risk_decision(
            make_risk_payload(decision="block", reason_codes=["max_risk"]),
            "da-2",
            source_id="src-2",
            timestamp=301.0,
        )
        self.assertEqual(r.decision_outcome, "block")
        self.assertEqual(r.source_id, "src-2")


class TestNormalizeGuardrailsDecision(unittest.TestCase):
    def test_normalize_guardrails_allowed(self) -> None:
        r = normalize_guardrails_decision(
            make_guardrails_payload(allowed=True),
            "da-1",
            timestamp=300.0,
        )
        self.assertEqual(r.source_module, "nq_guardrails")
        self.assertEqual(r.decision_outcome, "allow")

    def test_normalize_guardrails_blocked(self) -> None:
        r = normalize_guardrails_decision(
            make_guardrails_payload(allowed=False, reason="drawdown limit"),
            "da-2",
            timestamp=300.0,
        )
        self.assertEqual(r.decision_outcome, "block")
        self.assertIn("drawdown limit", r.reason_codes)


class TestNormalizePortfolioDecision(unittest.TestCase):
    def test_normalize_portfolio_allow(self) -> None:
        r = normalize_portfolio_decision(
            make_portfolio_payload(decision="allow"),
            "da-1",
            timestamp=300.0,
        )
        self.assertEqual(r.source_module, "nq_portfolio")
        self.assertEqual(r.decision_outcome, "allow")

    def test_normalize_portfolio_throttle(self) -> None:
        r = normalize_portfolio_decision(
            make_portfolio_payload(decision="throttle", reason_codes=["capital_usage"]),
            "da-2",
            timestamp=300.0,
        )
        self.assertEqual(r.decision_outcome, "throttle")
        self.assertEqual(r.reason_codes, ["capital_usage"])


class TestNormalizePromotionDecision(unittest.TestCase):
    def test_normalize_promotion_approve(self) -> None:
        r = normalize_promotion_decision(
            make_promotion_payload(allowed=True),
            "da-1",
            timestamp=300.0,
        )
        self.assertEqual(r.source_module, "nq_promotion")
        self.assertEqual(r.decision_outcome, "approve")

    def test_normalize_promotion_reject(self) -> None:
        r = normalize_promotion_decision(
            make_promotion_payload(allowed=False, blocking_issues=["insufficient_evidence"]),
            "da-2",
            timestamp=300.0,
        )
        self.assertEqual(r.decision_outcome, "reject")
        self.assertIn("insufficient_evidence", r.reason_codes)


class TestMalformedCriticalInputFailsClosed(unittest.TestCase):
    def test_risk_none_fails(self) -> None:
        with self.assertRaises(DecisionArchiveError):
            normalize_risk_decision(None, "da-1", timestamp=1.0)

    def test_risk_missing_decision_fails(self) -> None:
        with self.assertRaises(DecisionArchiveError):
            normalize_risk_decision({"reason_codes": []}, "da-1", timestamp=1.0)

    def test_risk_missing_timestamp_fails(self) -> None:
        payload = make_risk_payload(timestamp=100.0)
        del payload["timestamp"]
        with self.assertRaises(DecisionArchiveError):
            normalize_risk_decision(payload, "da-1", timestamp=None)

    def test_guardrails_missing_allowed_fails(self) -> None:
        with self.assertRaises(DecisionArchiveError):
            normalize_guardrails_decision({"reason": "x"}, "da-1", timestamp=1.0)

    def test_unsupported_source_fails(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock())
        with self.assertRaises(DecisionArchiveError):
            engine.normalize_and_archive("nq_unknown", {}, timestamp=1.0)

    def test_empty_source_module_fails(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock())
        with self.assertRaises(DecisionArchiveError):
            engine.normalize_and_archive("", make_risk_payload(), timestamp=1.0)


class TestArchiveSingleRecord(unittest.TestCase):
    def test_archive_single_record(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock(50.0))
        rec = engine.normalize_and_archive(
            "nq_risk",
            make_risk_payload(decision="block", timestamp=50.0),
            timestamp=50.0,
        )
        self.assertEqual(rec.archive_id, "da-1")
        listed = engine.query()
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0].decision_outcome, "block")


class TestArchiveMultipleRecords(unittest.TestCase):
    def test_archive_multiple_records(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock())
        for i, dec in enumerate(["allow", "block", "reduce"]):
            engine.normalize_and_archive(
                "nq_risk",
                make_risk_payload(decision=dec, strategy_id="s1", timestamp=100.0 + i),
                timestamp=100.0 + i,
            )
        listed = engine.query()
        self.assertEqual(len(listed), 3)
        outcomes = [r.decision_outcome for r in listed]
        self.assertIn("allow", outcomes)
        self.assertIn("block", outcomes)
        self.assertIn("reduce", outcomes)


class TestQueryByStrategy(unittest.TestCase):
    def test_query_by_strategy_works(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock())
        engine.normalize_and_archive("nq_risk", make_risk_payload(strategy_id="s1", timestamp=1.0), timestamp=1.0)
        engine.normalize_and_archive("nq_risk", make_risk_payload(strategy_id="s2", timestamp=2.0), timestamp=2.0)
        engine.normalize_and_archive("nq_portfolio", make_portfolio_payload(strategy_id="s1", timestamp=3.0), timestamp=3.0)
        s1_records = engine.list_by_strategy("s1")
        self.assertEqual(len(s1_records), 2)
        self.assertTrue(all(r.strategy_id == "s1" for r in s1_records))


class TestQueryByModule(unittest.TestCase):
    def test_query_by_module_works(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock())
        engine.normalize_and_archive("nq_risk", make_risk_payload(timestamp=1.0), timestamp=1.0)
        engine.normalize_and_archive("nq_guardrails", make_guardrails_payload(timestamp=2.0), timestamp=2.0)
        engine.normalize_and_archive("nq_risk", make_risk_payload(decision="block", timestamp=3.0), timestamp=3.0)
        risk_records = engine.list_by_module("nq_risk")
        self.assertEqual(len(risk_records), 2)
        self.assertTrue(all(r.source_module == "nq_risk" for r in risk_records))


class TestQueryByOutcome(unittest.TestCase):
    def test_query_by_outcome_works(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock())
        engine.normalize_and_archive("nq_risk", make_risk_payload(decision="allow", timestamp=1.0), timestamp=1.0)
        engine.normalize_and_archive("nq_risk", make_risk_payload(decision="block", timestamp=2.0), timestamp=2.0)
        engine.normalize_and_archive("nq_risk", make_risk_payload(decision="block", timestamp=3.0), timestamp=3.0)
        block_records = engine.list_by_outcome("block")
        self.assertEqual(len(block_records), 2)
        self.assertTrue(all(r.decision_outcome == "block" for r in block_records))


class TestSummaryCountsCorrect(unittest.TestCase):
    def test_summary_counts_correct(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock())
        engine.normalize_and_archive("nq_risk", make_risk_payload(decision="allow", timestamp=1.0), timestamp=1.0)
        engine.normalize_and_archive("nq_risk", make_risk_payload(decision="block", reason_codes=["r1"], timestamp=2.0), timestamp=2.0)
        engine.normalize_and_archive("nq_portfolio", make_portfolio_payload(decision="block", timestamp=3.0), timestamp=3.0)
        report = engine.build_report()
        self.assertEqual(report.summary.total_records, 3)
        self.assertEqual(report.summary.by_module["nq_risk"], 2)
        self.assertEqual(report.summary.by_module["nq_portfolio"], 1)
        self.assertEqual(report.summary.by_outcome["allow"], 1)
        self.assertEqual(report.summary.by_outcome["block"], 2)


class TestReasonCodeCountsCorrect(unittest.TestCase):
    def test_reason_code_counts_correct(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock())
        engine.normalize_and_archive(
            "nq_risk",
            make_risk_payload(decision="block", reason_codes=["max_risk"], timestamp=1.0),
            timestamp=1.0,
        )
        engine.normalize_and_archive(
            "nq_risk",
            make_risk_payload(decision="block", reason_codes=["max_risk"], timestamp=2.0),
            timestamp=2.0,
        )
        engine.normalize_and_archive(
            "nq_risk",
            make_risk_payload(decision="block", reason_codes=["daily_budget"], timestamp=3.0),
            timestamp=3.0,
        )
        report = engine.build_report()
        self.assertEqual(report.summary.reason_code_counts.get("max_risk"), 2)
        self.assertEqual(report.summary.reason_code_counts.get("daily_budget"), 1)


class TestEmptyArchiveReturnsValidEmptyReport(unittest.TestCase):
    def test_empty_archive_returns_valid_empty_report(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock())
        report = engine.build_report()
        self.assertEqual(report.summary.total_records, 0)
        self.assertEqual(report.records, [])
        self.assertEqual(report.summary.by_module, {})
        self.assertEqual(report.summary.by_outcome, {})
        self.assertEqual(report.summary.strategies_seen, [])


class TestDeterministicOrderingPreserved(unittest.TestCase):
    def test_deterministic_ordering_preserved(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock())
        engine.normalize_and_archive("nq_risk", make_risk_payload(timestamp=3.0), timestamp=3.0)
        engine.normalize_and_archive("nq_risk", make_risk_payload(timestamp=1.0), timestamp=1.0)
        engine.normalize_and_archive("nq_risk", make_risk_payload(timestamp=2.0), timestamp=2.0)
        records = engine.query()
        timestamps = [r.timestamp for r in records]
        self.assertEqual(timestamps, sorted(timestamps))


class TestDeterministicReportIds(unittest.TestCase):
    def test_deterministic_report_ids(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock())
        r1 = engine.build_report(report_id="custom-1")
        r2 = engine.build_report()
        r3 = engine.build_report()
        self.assertEqual(r1.report_id, "custom-1")
        self.assertEqual(r2.report_id, "decision-archive-report-2")
        self.assertEqual(r3.report_id, "decision-archive-report-3")


class TestSameInputSameOutput(unittest.TestCase):
    def test_same_input_same_normalized_output(self) -> None:
        p = make_risk_payload(decision="allow", reason_codes=["a"], timestamp=1.0)
        r1 = normalize_risk_decision(p, "da-1", timestamp=1.0)
        r2 = normalize_risk_decision(p, "da-2", timestamp=1.0)
        self.assertEqual(r1.decision_outcome, r2.decision_outcome)
        self.assertEqual(r1.reason_codes, r2.reason_codes)
        self.assertEqual(r1.source_module, r2.source_module)
        self.assertEqual(r1.timestamp, r2.timestamp)

    def test_same_input_same_archive_output(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock(50.0))
        engine.normalize_and_archive("nq_risk", make_risk_payload(timestamp=50.0), timestamp=50.0)
        r1 = engine.build_report(generated_at=50.0)
        r2 = engine.build_report(generated_at=50.0)
        self.assertEqual(r1.summary.total_records, r2.summary.total_records)
        self.assertEqual(r1.summary.by_outcome, r2.summary.by_outcome)


class TestNoHiddenDependencies(unittest.TestCase):
    def test_no_hidden_dependencies_on_external_services(self) -> None:
        """Import and basic run without network or file I/O."""
        from nq_decision_archive import DecisionArchiveEngine
        from nq_decision_archive.models import DecisionArchiveSummary
        engine = DecisionArchiveEngine()
        report = engine.build_report()
        self.assertIsInstance(report.summary, DecisionArchiveSummary)
        self.assertEqual(report.summary.total_records, 0)


class TestQueryWithLimit(unittest.TestCase):
    def test_query_with_limit(self) -> None:
        engine = DecisionArchiveEngine(clock=make_clock())
        for i in range(5):
            engine.normalize_and_archive(
                "nq_risk",
                make_risk_payload(timestamp=float(i)),
                timestamp=float(i),
            )
        q = DecisionQuery(limit=2)
        records = engine.query(q)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].timestamp, 0.0)
        self.assertEqual(records[1].timestamp, 1.0)
