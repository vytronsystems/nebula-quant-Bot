# nq_backtest — Backtesting Module (Real Engine)

## Purpose

`nq_backtest` provides reproducible, bar-by-bar backtesting for strategy validation in NEBULA-QUANT. It is **research infrastructure only**: no execution logic, no broker integration, no live trading.

## What Is Implemented

- **Bar-by-bar simulation**: Sequential iteration over normalized bar-like data; strategy is evaluated once per bar.
- **Strategy interface**: Accepts a callable `(bar) -> signal` or an object with `on_bar(bar) -> signal`. Signals: `LONG`, `SHORT`, `EXIT`, `HOLD`.
- **Trade simulation**: One position at a time; open long on LONG (when flat), short on SHORT (when flat), close on EXIT; HOLD does nothing. Fills at bar close with configurable slippage (bps) and commission per trade.
- **Trade recording**: Each closed trade is recorded (entry/exit ts, side, prices, qty, net PnL, PnL %, reason).
- **Equity curve**: Built at each bar (cash + mark-to-market position value); drawdown tracked from running peak.
- **Metrics**: Win rate, gross/net PnL, max drawdown, Sharpe-like ratio (annualized from equity returns). Safe defaults on empty input.
- **BacktestResult**: Contains config, total_trades, wins, losses, win_rate, gross_pnl, net_pnl, max_drawdown, sharpe_like, trades, equity_curve, metadata.
- **Reporter**: `build_backtest_summary(result)` returns a dictionary for dashboards and governance (no persistence or file output).

## Current Limitations

- **One position at a time**: No multi-symbol or portfolio-level sizing in this engine.
- **Fill model**: Fill at bar close only; no intra-bar orders, partial fills, or advanced order types.
- **Data**: No data loading inside the module; caller supplies bar-like iterables (with at least `ts` and `close`; optional open, high, low, volume, symbol, timeframe).
- **Time bounds**: Optional `start_ts` / `end_ts` on config filter bars by timestamp; both 0 means use all bars.
- **Sharpe-like**: Simple annualization (252 periods/year); no regime or timeframe-specific tuning yet.

## Assumptions

- Bars are in chronological order and already normalized (no look-ahead).
- Strategy returns a signal compatible with LONG/SHORT/EXIT/HOLD (string or enum with `.value`/`.name`).
- Bar-like objects support attribute or key access for `ts` and `close` (e.g. `nq_data.Bar` or dict).
- Commission is applied once per side (entry and exit); slippage is applied deterministically to fill prices.

## Role in the Pipeline

```
nq_data → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_exec
```

nq_backtest sits in the validation layer: strategies are tested on historical data here before paper or live. Results feed walk-forward, paper audits, and reporting. Promotion rule: Research → Backtesting → Walk-Forward → Paper (audited) → Live.

## Future Versions

- Optional integration with `nq_data` for bar type hints only (no direct data loading in this module).
- Walk-forward and out-of-sample orchestration in `nq_walkforward`.
- Richer metrics (profit factor, avg win/loss, regime stats) and optional persistence of results for audit.
