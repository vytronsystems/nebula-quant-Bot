# nq_walkforward — Walk-Forward Validation (Real Engine)

## Purpose

`nq_walkforward` provides temporal robustness validation for strategies in NEBULA-QUANT. It is **research infrastructure only**: no execution logic, no broker integration, no live trading. It validates that a strategy holds up across sequential train/test windows before paper or live.

## What Is Implemented

- **Sequential train/test windows**: `build_windows(bars, train_size, test_size, ...)` splits an ordered bar dataset into non-overlapping windows; each window has `train_size` bars for training and `test_size` bars for test. Advances by `train_size + test_size`; skips invalid or incomplete windows; returns empty list if dataset is too small.
- **Backtest integration**: Each window runs **nq_backtest** on the train subset and on the test subset (same strategy, no look-ahead). Uses `BacktestEngine.run(bars=..., strategy=...)` and `build_backtest_summary()` for train and test summaries.
- **Pass/fail rules**: Per-window, deterministic. A test window passes only if: test `total_trades` ≥ `min_test_trades`; test `net_pnl` ≥ `min_test_net_pnl`; test `max_drawdown` ≤ `max_test_drawdown`; and train/test do not diverge catastrophically (test net PnL not worse than a configured multiple of train profit). Thresholds are in `config.py`.
- **WalkForwardResult**: Aggregates `windows` (list of `WalkForwardWindowResult`), `total_windows`, `passed_windows`, `failed_windows`, `pass_rate`, `metadata`.
- **WalkForwardWindowResult**: Per window: `config` (time bounds, window_id), `train_summary`, `test_summary`, `passed`, `notes`.
- **Reporter**: `build_walkforward_summary(result)` returns a dict with `total_windows`, `passed_windows`, `failed_windows`, `pass_rate`, and `windows` (each with window_id, passed, train_net_pnl, test_net_pnl, test_drawdown, notes). No persistence or file output.

## Current Limitations

- **No parameter optimization**: Fixed strategy per run; no grid search or optimization framework.
- **Non-overlapping windows only**: Step size is `train_size + test_size`; no rolling or expanding window variants yet.
- **Simple pass/fail**: No statistical significance tests; thresholds are conservative placeholders.
- **Data**: No data loading; caller supplies ordered bar-like iterable. No direct nq_data integration beyond type-compatible usage.

## Assumptions

- Bars are in chronological order and already normalized.
- Strategy is compatible with nq_backtest (callable or `on_bar(bar)` returning LONG/SHORT/EXIT/HOLD).
- **nq_backtest** real engine is available; walk-forward depends on it for per-window train/test evaluation.

## Role in the Pipeline

```
nq_data → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_exec
```

nq_walkforward sits after backtesting: each window has a train period and a test (out-of-sample) period. Results (pass/fail per window, pass rate) feed strategy approval gates and research reviews. A strategy is not promoted to paper unless backtesting **and** walk-forward confirm temporal robustness.

## Future Versions

- Rolling or expanding window options.
- Optional statistical tests and tighter pass criteria.
- Integration with nq_backtest for shared config (capital, costs) and optional persistence of window results for audit.
