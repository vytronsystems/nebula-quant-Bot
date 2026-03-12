# nq_data — Data Ingestion and Canonical Feed

**NEBULA-QUANT v1** data ingestion and canonical bar feed layer. This module exposes a deterministic, fail-closed API for fetching OHLCV bars and the canonical `Bar` model. It is currently backed by a **stub provider** (no network), so all behavior is safe and reproducible.

## Purpose

- **Provide** a canonical OHLCV `Bar` model for all upstream modules.
- **Expose** a unified feed API (`get_bars`, `get_latest`) for research, backtest, walkforward, paper, and live layers.
- **Abstract** provider details behind a simple `DataProviderProtocol`.
- **Fail closed** on invalid configuration or unsupported timeframes.

## Responsibilities

- Define the canonical `Bar` model (timestamp, OHLCV, symbol, timeframe, source).
- Resolve the configured provider (`get_data_provider` → `TradeStationProvider` stub).
- Validate timeframes against `ALLOWED_TIMEFRAMES`.
- Provide deterministic, side-effect free functions:
  - `get_bars(symbol, timeframe, since, until) -> list[Bar]` (currently returns an empty list after exercising the provider stub).
  - `get_latest(symbol, timeframe, n=1) -> list[Bar]` (currently returns an empty list).

## Public interfaces

- `ALLOWED_TIMEFRAMES`: tuple of allowed timeframe strings (e.g. `"1m"`, `"5m"`, `"15m"`, `"1h"`, `"1d"`).
- `DEFAULT_PROVIDER`: default provider name (`"tradestation"` in v1).
- `get_data_provider() -> str`: reads `NQ_DATA_PROVIDER` or falls back to `DEFAULT_PROVIDER`.
- `Bar`: canonical OHLCV bar model (`nq_data.models.ohlcv.Bar`).
- `get_bars(symbol, timeframe, since, until) -> list[Bar]`
- `get_latest(symbol, timeframe, n=1) -> list[Bar]`
- Exceptions: `DataError`, `ProviderError`, `NormalizationError`.

## Inputs and outputs

- **Inputs**:
  - `symbol`: string ticker (e.g. `"QQQ"`).
  - `timeframe`: one of `ALLOWED_TIMEFRAMES`.
  - `since` / `until`: `datetime` bounds for `get_bars`.
  - `n`: positive integer for `get_latest`.
  - Optional env `NQ_DATA_PROVIDER` for provider selection.
- **Outputs**:
  - Lists of `Bar` instances (currently empty, by design) or exceptions on invalid input.
  - `Bar` instances are immutable and validated; in environments without `pydantic`, a frozen dataclass fallback enforces minimal invariants (e.g. `volume >= 0`).

## Pipeline role

`nq_data` is the **first stage** of the institutional pipeline:

`nq_data → nq_data_quality → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_guardrails → nq_exec → nq_metrics → nq_experiments → nq_portfolio → nq_promotion`

All market data used in the pipeline should originate as `Bar` instances (or equivalent structures) defined here, then be validated by `nq_data_quality` before reaching strategy and risk layers.

## Determinism guarantees

- Same `(symbol, timeframe, since, until)` input and provider configuration yield the **same result** (currently: empty list after a no-op provider call).
- The provider stub (`TradeStationProvider`) performs no network I/O and yields an empty iterator, ensuring deterministic behavior in tests and development.
- `Bar` is immutable (pydantic model with `frozen=True` or frozen dataclass fallback).

## Fail-closed behavior

- If `timeframe` is not in `ALLOWED_TIMEFRAMES`, `get_bars` and `get_latest` raise `DataError`.
- If `NQ_DATA_PROVIDER` is set to an unknown provider name, `_get_provider()` raises `DataError("Unknown data provider: ...")`.
- If `n < 1` for `get_latest`, a `DataError("n must be >= 1")` is raised.
- In the dataclass fallback, `Bar(volume < 0)` raises `ValueError`, preventing obviously invalid bars from entering the pipeline.
- No data is fabricated; unknown providers or invalid parameters always fail with explicit errors.

## Integration notes

- **Upstream**:
  - External data sources will eventually implement `DataProviderProtocol` (e.g. TradeStation, Polygon, Databento).
  - Provider integration will remain behind `get_bars` / `get_latest` without changing callers.
- **Downstream**:
  - `nq_data_quality` expects `Bar`-like objects for validation.
  - `nq_strategy`, `nq_risk`, `nq_backtest`, `nq_walkforward`, and `nq_paper` consume bar-like objects; `Bar` is the canonical choice.
- **Environment**:
  - No network or database access is performed in the current stub; safe to use in tests and offline environments.
  - When real providers are added, their integrations will be kept deterministic and strictly behind `DataProviderProtocol`.

