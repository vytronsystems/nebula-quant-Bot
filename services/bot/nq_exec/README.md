# nq_exec — Execution Layer (Skeleton)

## Purpose

`nq_exec` provides the architectural foundation for order routing, execution events, fills, and broker adapters in NEBULA-QUANT. It is **execution infrastructure only** in skeleton form: no real broker connectivity, no live execution, no external API calls.

## Role in the Pipeline

```
nq_data → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_exec
```

nq_exec sits at the end of the pipeline. Strategies that pass research, backtest, walk-forward, and paper (with weekly audit) may eventually be routed through nq_exec for live execution—only after explicit approval and risk controls. This module defines the interfaces (ExecutionEngine, adapters, order/fill/result models) so that real broker integration can be added in a later iteration without breaking callers.

## Why Skeleton-Only

- **Clean foundation**: Fixed public API (`ExecutionEngine`, `ExecutionOrder`, `ExecutionFill`, `ExecutionResult`) and adapter protocol so that TradeStation/Binance (or other venues) can be wired in later.
- **No live risk**: Real execution is not enabled until the full promotion path (research → backtest → walk-forward → paper → audit) is satisfied and governance approves.

## Why Real Execution Is Not Enabled Yet

Live trading requires validated strategies, operational runbooks, and risk limits. The skeleton exists so that the execution layer is architecturally in place; real broker connectivity and order placement will be added in a controlled iteration after paper and audit confirm edge and operations are ready.

## Relationship to Paper Trading

Paper trading (nq_paper) simulates fills and positions without sending orders to a broker. nq_exec is the layer that would send real orders when enabled. Paper and execution share the same pipeline position conceptually (paper = simulated execution, nq_exec = real execution); both consume signals and risk decisions from upstream modules.
