# NEBULA-QUANT v1 | Architecture

## Arquitectura actual del sistema
Sistema modular bajo `services/bot/`: datos, estrategia, riesgo, backtest, walk-forward, paper y ejecución viven en el mismo servicio (bot). Infraestructura Fase 1: Docker Compose, Postgres, Redis, observabilidad (Grafana, Prometheus, Alertmanager). Persistencia validada (bot_runs, decision_snapshots, orders, executions, trades, errors, bot_errors, bot_state).

## Flujo de datos y decisión
1. **nq_data** — Ingesta, normalización y feed de OHLCV (Bar); múltiples proveedores (TradeStation primero).
2. **nq_strategy** — Motor de estrategias (clases + reglas reutilizables); emite señales (LONG/SHORT/EXIT/HOLD).
3. **nq_risk** — Motor de riesgo (pendiente): límites, sizing, decisión go/no-go.
4. **nq_backtest** — Backtesting reproducible (pendiente).
5. **nq_walkforward** — Walk-forward y validación (pendiente).
6. **nq_paper** — Paper trading (pendiente).
7. **nq_exec** — Ejecución real (pendiente).

Flujo lineal: **nq_data → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_exec**.

## Separación por capas
- **Capa de datos**: nq_data (providers, normalize, feed, Bar).
- **Capa de decisión**: nq_strategy (engine, signals, rules) + nq_risk (límites, sizing).
- **Capa de validación**: nq_backtest, nq_walkforward.
- **Capa de ejecución**: nq_paper, nq_exec.
- **Capa de observabilidad y operaciones**: métricas, logs, alertas, runbooks (Fase 1 en marcha).

## Filosofía de datos híbrida
- Múltiples proveedores (TradeStation, luego Polygon, Databento, etc.) tras una interfaz unificada (`DataProviderProtocol`).
- Modelo canónico único: OHLCV → `Bar`.
- Evolución prevista: cache (Redis + disco), resampling (1m → 5m, 15m, 1h, 1d), streaming para paper/live.
- Ubicación: mismo servicio que el bot; sin llamadas reales a APIs externas hasta iteración aprobada.

## Regla de promoción
Una estrategia solo avanza por etapas validadas:
1. **Research** — Hipótesis y experimentos en nq_research / nq_lab.
2. **Backtesting** — Rigor (sin look-ahead, costos, train/test), métricas mínimas y validaciones (OOS, walk-forward, Monte Carlo).
3. **Walk-Forward** — Validación fuera de muestra y robustez.
4. **Paper Trading** — Con auditoría semanal (weekly audit); hallazgos documentados.
5. **Live Trading** — Solo tras aprobación explícita y control de riesgo.

No se promueve por curva bonita; se exigen umbrales, documentación y auditoría.
