# nq_paper — Paper Trading (Real Engine)

## Purpose

`nq_paper` provides simulated paper trading for NEBULA-QUANT: bar-by-bar paper sessions, in-memory positions and trades, and session results for audit and promotion decisions. It is **paper/simulated only**: no broker connection, no real orders, no live execution.

## What Is Implemented

- **Bar-by-bar simulation**: `run_session(bars, strategy)` iterates over bar-like data, evaluates strategy per bar (callable or `on_bar(bar)`), and applies signals sequentially.
- **Strategy interface**: LONG / SHORT / EXIT / HOLD; same normalization as nq_backtest (works with `nq_strategy.Signal` or strings).
- **Paper positions**: One position at a time; open long on LONG (when flat), short on SHORT (when flat); close on EXIT or opposite signal. Fill at bar close with configurable commission and slippage (bps). Mark-to-market each bar (unrealized PnL).
- **Ledger**: `open_paper_position()`, `close_paper_position()`, `update_account_state()` — in-memory, deterministic; caller applies commission to cash and to stored trade PnL.
- **Account state**: Cash, equity, used/available buying power, open positions, closed trades, updated_ts.
- **Session result**: `PaperSessionResult` with session_id, started_ts, ended_ts, trades (closed), positions (open at end), account_state, summary (total_trades, net_pnl, win_rate, max_drawdown), metadata.
- **Metrics**: `compute_paper_win_rate`, `compute_paper_net_pnl`, `compute_paper_drawdown`, `compute_paper_basic_stats` on closed trades and equity curve; safe on empty input.
- **Reporter**: `build_paper_summary(result)` returns dict with session_id, started_ts, ended_ts, cash, equity, total_trades, closed_trades, open_positions, net_pnl, win_rate, max_drawdown. No persistence or file output.

## Current Limitations

- **One position at a time**: No multi-symbol or portfolio-level paper book.
- **Fill model**: Fill at bar close only; no intra-bar or partial fills.
- **Data**: No data loading; caller supplies ordered bar-like iterable. No direct nq_data integration.
- **No broker or live**: Paper only; no nq_exec coupling.

## Assumptions

- Bars are in chronological order and bar-like (at least `ts`, `close`; optional symbol, etc.).
- Strategy is callable(bar) or has `on_bar(bar)` returning LONG/SHORT/EXIT/HOLD.
- Same deterministic slippage/commission rules as backtest (auditable).

## Relationship: Walk-Forward, Paper, Live Promotion

- **Walk-forward** validates temporal robustness on historical train/test windows.
- **Paper trading** validates behavior on replay or live-like data with simulated execution; results are weekly-audited (see Weekly Audit Standard).
- **Live** is only after backtest, walk-forward, paper, and explicit approval; nq_exec handles real orders.

Paper sessions feed weekly audit and promotion decisions; no strategy moves to live without documented paper phase and audit.

## Future Versions

- Optional persistence of session results and trades for audit trail.
- Integration with nq_risk and nq_guardrails for pre-trade checks in paper.
- Multi-position or multi-symbol paper book if needed.
