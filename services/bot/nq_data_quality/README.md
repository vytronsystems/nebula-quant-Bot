# nq_data_quality

**NEBULA-QUANT v1** — Data validation and integrity layer (skeleton).

## Purpose

`nq_data_quality` is the **data validation and integrity layer** used before any dataset is accepted by backtesting, walk-forward testing, paper trading, or live execution. It ensures the market data pipeline is reliable and helps prevent corrupted or invalid datasets from entering the strategy pipeline. The module does **not** modify data; it only produces validation signals (issues and a valid/invalid result).

## Where it fits in the pipeline

```
data → data_quality → strategy → risk → execution
```

Market data is validated by `nq_data_quality` before it is used by strategy, risk, and execution layers. A dataset that fails validation should not be used for backtest, walk-forward, paper, or live.

## Validation only

This module currently runs **validation only**: it runs checks (missing candles, duplicates, timestamp gaps, negative prices, OHLC integrity, volume anomalies) and returns a `DataQualityResult` with `valid` and `issues`. No database, no external APIs, no broker integration. Skeleton checks return empty issue lists; real checks can be added in a later iteration.
