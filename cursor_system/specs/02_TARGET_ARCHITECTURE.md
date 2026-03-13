# Target Architecture

## Keep
- `services/bot/` as Python quant core.

## Add
- `services/control-plane/` as Spring Boot 3 / Java 21 / Drools control plane.
- `apps/web/` as Next.js + React + Tailwind + shadcn/ui futuristic GUI.
- `artifacts/` as persistent filesystem evidence tree.

## Mandatory new capabilities
- instrument registry and activation control
- TradeStation options adapter stack
- cross-venue abstraction and capital visibility
- order / position / PnL reconciliation
- operator and executive UI
- DB-first artifact registry
- alert routing via dashboard + telegram + email
- account sync for Binance and TradeStation
