NEBULA-QUANT v1 | Binance USDT-M Futures Adapter Foundation
===========================================================

Purpose
-------

The `adapters.binance` package provides the **Phase 51** foundation for
integrating NEBULA-QUANT v1 with **Binance USDT-M Futures**.

This phase focuses on:

- deterministic, typed models for market data, execution, and account state,
- explicit validation and fail-closed behavior,
- clear mapping between internal orders and Binance-specific payloads,
- architecture-level adapters with **simulated** behavior for tests.

No real network access or secrets are used in this phase.


Scope and Assumptions (Phase 51)
--------------------------------

- **Exchange**: Binance
- **Market**: USDT-M Futures only
- **Position mode**: One-Way only
- **Initial symbol scope**: `BTCUSDT` only
- **Leverage policy**: `1x`–`2x` maximum
- **Supported order types**:
  - `MARKET`
  - `LIMIT`
  - `STOP_MARKET`

Any unsupported combination (other symbols, hedge mode, higher leverage,
unsupported order types) **fails closed** via validation.


Module Structure
----------------

- `enums.py`:
  - `BinanceOrderSide`, `BinanceOrderType`, `BinanceTimeInForce`,
    `BinancePositionMode`, `BinanceMarginType`.

- `config.py`:
  - `BinanceSymbolConfig`, `BinanceFuturesConfig`.
  - `BINANCE_BTCUSDT_CONFIG` and `BINANCE_FUTURES_CONFIG` define:
    - base REST / websocket URLs (placeholders),
    - allowed symbols (`["BTCUSDT"]`),
    - leverage cap (`max_leverage=2`),
    - supported order types (`MARKET`, `LIMIT`, `STOP_MARKET`),
    - `position_mode=ONE_WAY`.

- `models.py`:
  - Market data: `BinanceKline`, `BinanceTicker`, `BinanceOrderBookSnapshot`,
    `BinanceContractSpec`.
  - Account state: `BinanceBalance`, `BinancePosition`, `BinanceAccountState`.
  - Execution: `BinanceOrderRequest`, `BinanceOrderResponse`,
    `BinanceCancelResponse`, `BinanceExecutionResult`.
  - Errors: `BinanceAdapterError`, `BinanceValidationError`.
  - Local normalized order intent: `NormalizedOrderRequest` for mapping tests.

- `validation.py`:
  - Symbol validation (BTCUSDT-only).
  - Futures mode validation (USDT-M, One-Way only).
  - Leverage validation (1 ≤ leverage ≤ 2).
  - Order type validation (MARKET, LIMIT, STOP_MARKET only).
  - Quantity/price/stop-price validation.
  - Basic payload validation for order/account responses.

- `mapper.py`:
  - Internal → Binance:
    - `map_internal_order_to_binance(NormalizedOrderRequest) -> BinanceOrderRequest`
    - `build_binance_order_payload(BinanceOrderRequest) -> dict`
  - Binance → Internal:
    - `map_binance_order_response(payload) -> BinanceOrderResponse`
    - `map_account_payload_to_state(payload) -> BinanceAccountState`

- `market_data.py`:
  - `normalize_kline`, `normalize_ticker`, `normalize_order_book` from
    Binance-style payloads into typed models.

- `execution.py`:
  - `BinanceExecutionAdapter`:
    - `validate_order(order)`
    - `map_order(order)` → `(BinanceOrderRequest, payload dict)`
    - `submit_order(order)` → `BinanceExecutionResult` (simulated)
    - `cancel_order(order_id, symbol)` (simulated)
    - `get_order_status(order_id, symbol)` (simulated)

- `account.py`:
  - `BinanceAccountAdapter`:
    - `normalize_account_state(payload)`
    - `normalize_positions(payload)`
    - `normalize_balances(payload)`


Adapter Boundaries
------------------

- This package:
  - defines **Binance-specific contracts** and mapping logic,
  - does not depend on higher-level modules like `nq_risk`, `nq_guardrails`,
    or `nq_strategy_governance`,
  - does not own strategy lifecycle or promotion logic.

- Future phases may:
  - register these adapters with `nq_exec` or a venue registry,
  - wire real REST/WebSocket transports behind the current simulated
    interfaces,
  - add reconciliation and multi-symbol support.


Mapping Philosophy
------------------

- **Internal → Binance**:
  - `NormalizedOrderRequest` captures a minimal, exchange-agnostic order intent
    (symbol, side, type, quantity, price/stop, time in force, leverage).
  - The mapper translates it into `BinanceOrderRequest` and then into a REST
    payload (`/fapi/v1/order` compatible, minus authentication fields).
  - Validation ensures symbol, leverage, order type, and required numeric
    fields are correct before mapping.

- **Binance → Internal**:
  - Order responses and account payloads are mapped into typed models:
    `BinanceOrderResponse`, `BinanceAccountState`, `BinancePosition`,
    `BinanceBalance`.
  - Malformed or incomplete payloads raise `BinanceAdapterError` (fail-closed).


Validation Philosophy
---------------------

- Validation is centralized in `validation.py` and enforced by adapters:
  - Reject unsupported symbols (`BTCUSDT`-only in Phase 51).
  - Enforce One-Way mode; hedge mode is rejected.
  - Enforce leverage cap (max 2x).
  - Restrict order types to MARKET, LIMIT, STOP_MARKET.
  - Enforce positive quantities, prices, and stop prices as appropriate.
  - Reject malformed Binance-like payloads before mapping.

- Errors are explicit:
  - `BinanceValidationError` for input validation failures.
  - `BinanceAdapterError` for mapping/payload-related failures.


Future Extensions
-----------------

Planned future work (outside Phase 51):

- Real REST transport wiring behind `BinanceExecutionAdapter`.
- WebSocket feeds for live market data and order updates.
- Reconciliation between internal state and exchange state.
- Multi-symbol and multi-venue expansion beyond BTCUSDT.
- Configurable paper/live switching at the adapter/transport level.
- Integration with `nq_exec`, `nq_risk`, `nq_guardrails`,
  and `nq_strategy_governance` via a venue/adapter registry.

