# NEBULA-QUANT v1 | Module Map

## Lista de módulos y estado

| Módulo | Estado | Notas |
|--------|--------|--------|
| nq_data | **skeleton** | Bar, providers (base + TradeStation stub), feed, normalize, config, timeframes |
| nq_strategy | **skeleton** | Engine, Strategy, Signal, rules, ExampleStrategy |
| nq_risk | **pending** | Directorio vacío; próxima iteración |
| nq_backtest | pending | — |
| nq_walkforward | pending | — |
| nq_paper | pending | — |
| nq_exec | pending | — |
| nq_portfolio | pending | — |
| nq_guardrails | pending | — |
| nq_research | pending | — |
| nq_montecarlo | pending | — |
| nq_lab | pending | — |
| nq_strategy_registry | pending | — |
| nq_alpha_discovery | pending | — |
| nq_regime | pending | — |
| nq_edge_decay | pending | — |
| nq_audit | pending | — |
| nq_trade_review | pending | — |
| nq_learning | pending | — |
| nq_improvement | pending | — |
| nq_reporting | pending | — |
| nq_decision_archive | pending | — |
| nq_obs / nq_metrics / nq_alerting / nq_sre / nq_runbooks / nq_scheduler | pending / parcial | Observabilidad Fase 1 operativa (Grafana, Prometheus, Alertmanager) |
| nq_db / nq_cache / nq_event_store / nq_config | pending / parcial | Persistencia vía PG_DSN y tablas actuales |

## Orden de construcción recomendado
1. **nq_data** — hecho (skeleton).
2. **nq_strategy** — hecho (skeleton).
3. **nq_risk** — siguiente (límites, sizing, decisión).
4. **nq_backtest** — motor reproducible.
5. **nq_audit** — revisión y estándares.
6. **nq_research** — workflow de investigación.
7. nq_walkforward, nq_paper, nq_exec y resto según prioridad del Master Execution Plan.

## Convención de estados
- **implemented** — Módulo funcional y usado en flujo actual.
- **skeleton** — Estructura y API mínima lista; evolución en iteraciones.
- **pending** — Aún no construido o solo planificado.
