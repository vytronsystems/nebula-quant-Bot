# nq_metrics

**NEBULA-QUANT v1** — Performance analytics layer (skeleton).

## Purpose

`nq_metrics` is the **performance analytics layer** of the platform. It computes trading performance statistics used to evaluate strategies. It does **not** execute trades and does **not** connect to brokers; it only analyzes performance data (e.g. trade lists or equity series).

## Examples of metrics computed

Typical metrics (placeholders or real in this skeleton):

- **Win rate** — Fraction of winning trades.
- **Profit factor** — Gross profit / |gross loss|.
- **Expectancy** — Expected PnL per trade.
- **Average win / average loss** — Mean PnL of winners and losers.
- **Max drawdown** — Peak-to-trough decline in equity curve.
- **Sharpe ratio** — Risk-adjusted return (annualized when configured).
- **Equity curve** — Cumulative PnL over time.
- **Trade distribution** — Counts by symbol, PnL buckets, etc.
- **Risk/reward** — Can be derived from avg_win / avg_loss and related stats.

## How metrics feed strategy evaluation

- **Backtest / walk-forward:** `MetricsEngine.compute_metrics(trades)` yields a `MetricsResult` used to accept or reject a strategy (e.g. min Sharpe, max drawdown).
- **Paper / live:** Same engine can consume closed trades to produce periodic performance reports.
- **Dashboards:** `reporter.build_metrics_report(result)` returns a dictionary suitable for Grafana or other dashboards.

This module is skeleton-only: no database, no external APIs, no broker connectivity. Calculations use safe defaults for empty or insufficient data.
