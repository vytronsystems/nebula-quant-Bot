# nq_trade_review

Deterministic individual-trade review module for NEBULA-QUANT v1. Analyzes a single trade (or batch via repeated calls) for entry/exit quality, RR, slippage, completeness, and consistency; produces structured findings and recommendations. **Analysis infrastructure only** — no trading decisions, no execution, no mutation of source records.

## Purpose

- **Analyze** one trade at a time with typed `TradeReviewInput`.
- **Compare** expected vs actual entry/exit and RR when data exists.
- **Detect** poor entry/exit quality, excessive slippage, RR underperformance, incomplete or inconsistent records.
- **Classify** outcome (win/loss/breakeven) and exit reason (stop_hit/target_hit/manual_exit/unknown_exit) when derivable.
- **Produce** deterministic `TradeReviewReport` with summary, findings, and recommendations.

## Input model

**TradeReviewInput** (one trade per review):

- **trade_id**, **symbol**, **side** (required; side must be long/short/buy/sell).
- **strategy_id** (optional).
- **expected_entry_price**, **actual_entry_price**, **expected_exit_price**, **actual_exit_price** (optional).
- **stop_loss_price**, **take_profit_price**, **quantity**, **notional** (optional).
- **expected_rr**, **actual_rr** (optional; can be derived from prices when missing).
- **entry_timestamp**, **exit_timestamp**, **metadata** (optional).

Critical malformed input (empty trade_id/symbol/side, invalid side, negative prices/quantity) raises **TradeReviewError**. Missing optional fields do not crash; they produce incomplete findings or are skipped.

## Finding model

Each **TradeReviewFinding** has: **finding_id**, **category**, **severity** (info/warning/critical), **title**, **description**, **trade_id**, **strategy_id**, **metadata**.

Categories: `poor_entry_quality`, `poor_exit_quality`, `rr_underperformance`, `excessive_slippage`, `missing_trade_controls`, `inconsistent_trade_record`, `incomplete_trade_record`.

## Severity model

- **INFO**: incomplete record, missing controls, minor notes.
- **WARNING**: material entry/exit deviation, slippage, or RR underperformance (above warning thresholds).
- **CRITICAL**: severe deviation/slippage, or inconsistent record (e.g. long with stop > entry).

Thresholds are in code (e.g. entry deviation 1% warning, 5% critical; slippage 2% warning, 5% critical; RR ratio &lt; 0.5 warning, &lt; 0.25 critical).

## Outcome classification

When entry and exit prices exist: **outcome** = win | loss | breakeven | unknown; **exit_reason** = stop_hit | target_hit | manual_exit | unknown_exit. Derived from PnL and proximity to stop/target; no guessing when data is insufficient.

## Recommendation generation

Recommendations are derived only from findings (e.g. “Review entry discipline for trade X due to entry deviation”, “Investigate slippage conditions for trade X”). No speculation beyond finding fields.

## Intended future integration

- **nq_audit**: aggregate trade review results.
- **nq_learning** / **nq_improvement**: consume findings for learning pipelines.
- **nq_reporting**: publish trade review reports.
- **nq_scheduler** / **nq_orchestrator**: trigger periodic or batch trade reviews.

No wiring in this phase; API is ready for integration.

## Simple usage example

```python
from nq_trade_review import TradeReviewEngine, TradeReviewInput

engine = TradeReviewEngine()
trade = TradeReviewInput(
    trade_id="T1",
    symbol="AAPL",
    side="long",
    strategy_id="s1",
    expected_entry_price=100.0,
    actual_entry_price=101.5,
    actual_exit_price=105.0,
    stop_loss_price=98.0,
    take_profit_price=106.0,
    quantity=10.0,
)
report = engine.run_review(trade)
print(report.summary.outcome, report.summary.exit_reason)
for f in report.findings:
    print(f.category, f.severity)
for r in report.recommendations:
    print(r)
```
