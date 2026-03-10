# nq_exec — Execution Layer (Real Engine)

## Purpose

`nq_exec` is the execution abstraction layer for NEBULA-QUANT: order validation, routing through adapters, and deterministic execution results. It is **simulated/in-memory by default**: no real broker authentication, no live order placement, no external API or exchange connectivity. Real broker integration can be added later behind the same adapter interface.

## What Is Implemented

- **Order validation**: Orders must have order_id, symbol, side, qty > 0; missing or invalid fields yield a rejected result and no fill.
- **ExecutionEngine**: `submit_order(order)` validates, then routes via adapter when execution is enabled and adapter is available; `cancel_order(order_id)` and `get_order_status(order_id)` delegate to adapter. Fail-closed: when execution is disabled or adapter is unavailable, all submits are rejected and no placeholder fill is created.
- **Adapters**: `ExecutionAdapterProtocol` (submit, cancel, status, health_check). `TradeStationAdapter` and `BinanceAdapter` implement the protocol with in-memory state: store orders by order_id, simulate accept (with placeholder fill), cancel (mark cancelled), status (lookup). Adapters can be marked unavailable; then submit/cancel/status return rejected or not_found.
- **Router**: `route_order(order, adapter)` checks adapter presence and `health_check()`; if missing or unavailable returns rejected result; otherwise returns `adapter.submit(order)`.
- **Fills**: `build_placeholder_fill(order=..., fill_price_mode="limit")` creates a deterministic placeholder fill from an order; `build_fill_summary(fills)` returns total_fills, total_qty, avg_price. No persistence.
- **Config**: DEFAULT_EXECUTION_MODE ("simulated"), DEFAULT_ORDER_TYPE ("market"), DEFAULT_BROKER ("none"), DEFAULT_EXECUTION_ENABLED (False), DEFAULT_SIMULATED_FILL_PRICE_MODE ("limit").

## Current Limitations

- **No live trading**: All execution is in-memory and simulated. No real broker auth, no HTTP/WebSocket, no exchange connectivity.
- **No persistence**: Orders and fills exist only in adapter in-memory state.
- **Placeholder fills only**: Fill price from order limit_price (or caller); no real market data or tick feed.

## Assumptions

- Callers supply fully formed `ExecutionOrder` objects (order_id, symbol, side, qty, order_type, limit_price, status, created_ts). Engine normalizes created_ts when missing.
- Fail-closed: when execution is disabled or adapter is unavailable, the engine must not simulate a fill; it returns rejected.

## How This Differs From Real Broker Connectivity

- **This layer**: Validates and normalizes orders, routes to an adapter interface, produces deterministic results and placeholder fills. Adapters are in-memory stubs that simulate accept/cancel/status.
- **Future real connectivity**: Same engine and router; swap in adapters that perform real auth, HTTP/WebSocket calls, and exchange order placement. Engine behavior (validation, fail-closed, result shape) stays the same.

## Relationship to Paper Trading

- **nq_paper**: Simulates positions and fills over bar data without sending orders anywhere.
- **nq_exec**: Abstraction for “send order → get result/fill.” In current form it only simulates; when real adapters are added, nq_exec is the single place where live orders are sent, subject to guardrails and risk.

## Future Versions

- Real TradeStation/Binance adapters (auth, API, order placement) behind the same protocol.
- Optional persistence of orders and fills for audit.
- Integration with nq_guardrails (e.g. no submit when guardrails block).
