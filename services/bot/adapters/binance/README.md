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
  - `BinanceSymbolConfig`, `BinanceFuturesConfig`, `BinanceOperationalConfig` (Phase 56–57).
  - `BINANCE_BTCUSDT_CONFIG`, `BINANCE_FUTURES_CONFIG`, `BINANCE_OPERATIONAL_CONFIG` define:
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
  - `BinanceExecutionAdapter(safeguards=None)`:
    - Optional `safeguards`: if set, `assert_can_send_live` is called before submit (fail closed).
    - `validate_order(order)`, `map_order(order)`, `submit_order(order)` → `BinanceExecutionResult`,
    - `cancel_order(order_id, symbol)`, `get_order_status(order_id, symbol)` (simulated when no transport).

- `paper.py` (Phase 56):
  - Paper/shadow execution: `BinancePaperTradingEngine(mode="paper"|"shadow", ...)`.
  - Models: `BinancePaperOrder`, `BinancePaperFill`, `BinancePaperPosition`, `BinancePaperAccountState`, `BinancePaperSessionReport`.
  - Paper: simulated fills and in-memory positions/balances. Shadow: records intended orders only, no live send.

- `safeguards.py` (Phase 57):
  - `BinanceLiveSafeguards`: max_daily_loss, max_position_size, max_notional_per_order, max_open_positions,
    order_rate_limit, venue_enabled, leverage cap, kill_switch, heartbeat, optional reconciliation.
  - 24/7: UTC-based daily reset, rolling order window, continuous kill switch. Fail closed.
  - `BinanceSafeguardDecision`, `BinanceSafeguardState`, `SAFEGUARD_FAILURE_CATEGORIES` for nq_sre/nq_runbooks.

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


Phase 56–57: Paper / Shadow and Live Safeguards
-----------------------------------------------

**Modes**

- **Paper**: Fully simulated execution on Binance-normalized market data; in-memory balances, positions, orders, fills, PnL. No live risk.
- **Shadow**: Strategy produces orders/signals; system records intended orders only; no live submission. Enables later comparison of intended vs observed state.
- **Live**: Controlled by config and safeguards; remains **disabled by default**. Requires venue enabled, kill switch off, heartbeat fresh, and all limits satisfied.

**24/7/365 assumptions**

Binance Futures runs continuously. This layer does **not** rely on market open/close or session-close resets. Instead:

- **UTC-based reset**: Daily risk controls (e.g. max_daily_loss, daily counts) use a configurable `binance_reset_hour_utc` (default 0). The “day” rolls at that hour in UTC.
- **Rolling windows**: Order rate and similar limits use a rolling window (e.g. last N minutes) rather than a fixed session.
- **Heartbeat**: If heartbeat/transport freshness is stale beyond `binance_heartbeat_timeout_seconds`, live routing fails closed.
- **Kill switch**: Works regardless of time; when active, no live orders are sent.

**Safeguards (fail closed)**

- Venue disabled → no live send.
- Kill switch active → no live send.
- Heartbeat stale → no live send.
- Daily loss limit, position size, notional, open positions, order rate, leverage cap → each enforced explicitly; breach raises `BinanceSafeguardError`.

**Integration**

- **nq_exec**: Execution path can pass a `BinanceLiveSafeguards` instance into `BinanceExecutionAdapter`; `submit_order` calls `assert_can_send_live` before mapping/send when safeguards are present.
- **nq_guardrails**: Existing guardrails remain in place; Binance safeguards are an additional exchange-facing layer.
- **nq_sre / nq_runbooks**: `BinanceSafeguardDecision.category` and `SAFEGUARD_FAILURE_CATEGORIES` (e.g. `heartbeat_stale`, `kill_switch_active`, `daily_loss_limit_hit`, `order_rate_limit_hit`) support future incident routing and runbook lookup.


Future Extensions
-----------------

Planned future work (outside Phase 51):

- Real REST transport wiring behind `BinanceExecutionAdapter`.
- WebSocket feeds for live market data and order updates.
- Reconciliation between internal state and exchange state.
- Multi-symbol and multi-venue expansion beyond BTCUSDT.
- Full live activation only after governance and risk sign-off; paper/shadow remain the default operational modes until then.
- Deeper integration with `nq_exec`, `nq_risk`, `nq_guardrails`, `nq_sre`, `nq_runbooks` via venue/adapter registry.

