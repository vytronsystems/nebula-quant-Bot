# NEBULA-QUANT v1 | Project State

## Fase actual
**Fase 2** — Trading Core institucional.

## Paso actual
**Paso 5.5** — Cierre de chat y congelación de arquitectura (documentación institucional, sin implementar nq_risk en esta iteración).

## Commits recientes relevantes
- `15f9d57` feat: add nq_strategy skeleton (strategy engine + rules)
- `97c270b` feat: add nq_data skeleton (data ingestion module)
- `d25b2b6` chore: standardize DB access with single PG_DSN source
- `1bf87a9` fix: remove dead code and recursion bug in nq-run.sh
- `4d48719` docs(research): add quantitative research and backtesting framework
- `24f86db` docs(cursor): add master prompt and governance agents
- `9d93d83` docs(factory): add software factory operating framework
- `bd3d96d` chore: baseline validated phase 1 infrastructure and persistence

## Módulos implementados
- **nq_data** — skeleton: Bar, DataProviderProtocol, TradeStation stub, feed (get_bars, get_latest), normalización, timeframes 1m/5m/15m/1h/1d.
- **nq_strategy** — skeleton: StrategyEngine, Strategy, Signal (LONG/SHORT/EXIT/HOLD), rules (momentum, breakout, trend), ExampleStrategy.
- **Infraestructura Fase 1** — Docker Compose, Bot, Postgres, Redis, Grafana, Prometheus, Alertmanager, /metrics, nq-verify.sh, tablas y migraciones validadas.

## Módulos pendientes
- **nq_risk** — no implementado (directorio vacío; próxima iteración).
- **nq_backtest**, **nq_walkforward**, **nq_paper**, **nq_exec** — pendientes.
- **nq_audit**, **nq_research**, **nq_portfolio**, **nq_guardrails** y resto del catálogo — pendientes según prioridad.

## Próxima iteración aprobada
Implementar **nq_risk** (Risk Engine) en un chat nuevo, sin tocar nq_data ni nq_strategy. Seguir orden: Orchestrator → Architecture Gate → Builder → QA Gate → Git.

## Riesgos actuales
- nq_risk aún no existe; el flujo nq_data → nq_strategy → nq_risk → … queda bloqueado hasta su implementación.
- No llamadas reales a APIs externas en nq_data hasta iteración aprobada.
- Secretos y política de exclusión (apikey_cursor.txt, .env) deben mantenerse fuera del repo.
