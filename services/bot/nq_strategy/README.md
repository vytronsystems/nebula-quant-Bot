# nq_strategy — Strategy Engine and Signal Layer

**NEBULA-QUANT v1** strategy layer. This module defines the base `Strategy` interface, the `Signal` enum, reusable rule helpers, and a simple `StrategyEngine` that calls `on_bar(bar)` per bar. It does **not** execute trades, size positions, or talk to brokers.

## Purpose

- **Standardize** how strategies generate signals (`LONG`, `SHORT`, `EXIT`, `HOLD`) from bar-like inputs.
- **Provide** a base `Strategy` class and simple reusable rules (momentum, breakout, trend).
- **Offer** a small engine wrapper (`StrategyEngine`) so the rest of the system can treat strategies as black boxes.

## Responsibilities

- Define:
  - `Signal` enum (`long`, `short`, `exit`, `hold`).
  - Abstract `Strategy` base class with `on_bar(bar) -> Signal`.
  - Example strategy (`ExampleStrategy`) demonstrating usage and integration with rules.
  - Rule helpers under `nq_strategy.rules` (e.g. `rule_momentum_bullish`, `rule_breakout_above`, `rule_trend_up`).
- Provide `StrategyEngine` that:
  - Accepts a `Strategy` instance.
  - Calls `strategy.on_bar(bar)` and returns a `Signal`.
  - Wraps exceptions in `EngineError` (fail-closed).

## Public interfaces

- `Signal`: enum used by all strategies and downstream components.
- `Strategy`: abstract base class to inherit from when implementing new strategies.
- `StrategyEngine(strategy: Strategy)` with:
  - `on_bar(bar) -> Signal`
- Exceptions:
  - `StrategyError` (base).
  - `EngineError` (raised when `on_bar` fails).
- Rules (from `nq_strategy.rules`):
  - `rule_momentum_bullish(bar) -> bool`
  - `rule_breakout_above(bar, level: float) -> bool`
  - `rule_trend_up(bar) -> bool`
- Example:
  - `ExampleStrategy` in `nq_strategy.strategies.example_strategy`.

## Inputs and outputs

- **Inputs**:
  - `bar`: any bar-like object or dict; when integrated, this will typically be `nq_data.Bar` or compatible structures.
- **Outputs**:
  - `Signal` values indicating desired position action:
    - `Signal.LONG`, `Signal.SHORT`, `Signal.EXIT`, `Signal.HOLD`.

## Pipeline role

`nq_strategy` is the **alpha generation** step of the pipeline:

`nq_data → nq_data_quality → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_guardrails → nq_exec → …`

It consumes validated bars and produces **candidate trade directions** that must then be evaluated by `nq_risk`, `nq_backtest`, and later layers.

## Determinism guarantees

- Strategy determinism is a **design expectation**:
  - Given the same bar sequence and internal state, strategies should emit the same sequence of signals.
  - Reusable rules are pure functions of `bar` (currently skeleton stubs returning `False` but ready for real logic).
- `StrategyEngine` itself is deterministic: it forwards calls to `Strategy.on_bar` and either returns the signal or raises `EngineError`.
- There is no randomness, I/O, or external state in the engine/utility code.

## Fail-closed behavior

- If `Strategy.on_bar(bar)` raises any exception, `StrategyEngine.on_bar(bar)` raises `EngineError` rather than propagating arbitrary exceptions.
- Callers can treat any `EngineError` as a strategy failure and halt or downgrade the strategy safely.
- The example strategy is intentionally simple (always HOLD) to avoid accidental side effects.

## Integration notes

- **Upstream**:
  - `nq_data` and `nq_data_quality` supply canonical or validated bars to be used as `bar` inputs.
- **Downstream**:
  - `nq_risk` consumes the strategy’s signal (combined with pricing) to build a `RiskOrderIntent`.
  - `nq_backtest`, `nq_walkforward`, and `nq_paper` consume strategy functions or `Strategy` instances to drive simulations.
- **Authoring new strategies**:
  - Implement `Strategy.on_bar(self, bar) -> Signal`.
  - Prefer composing from `nq_strategy.rules` rather than embedding ad-hoc logic where possible.
  - Keep strategies deterministic and free from side effects (no I/O, no global state).

