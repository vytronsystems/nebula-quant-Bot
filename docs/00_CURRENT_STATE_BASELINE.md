# NEBULA-QUANT v1 | Current State Baseline

## Fecha
2026-03-09

## Estado validado
Fase 1 cerrada técnicamente:
- Docker Compose operativo
- Bot, Postgres, Redis, Grafana, Prometheus, Alertmanager y Postgres Exporter activos
- Endpoint /metrics operativo
- Grafana accesible
- Prometheus healthy
- Script scripts/nq-verify.sh pasa correctamente
- Migraciones aplicadas correctamente
- Tablas presentes:
  - bot_runs
  - decision_snapshots
  - orders
  - executions
  - trades
  - errors
  - bot_errors
  - bot_state

## Hallazgos pendientes
- Proyecto aún no inicializado con Git
- Existe archivo sensible en raíz: apikey_cursor.txt
- Falta validar política de exclusión de secretos
- Falta formalizar software factory sobre el proyecto existente
- Falta comenzar Fase 2:
  - Strategy Engine
  - Risk Engine
  - Execution Engine
  - Data Ingestion
  - Backtesting
  - Logging institucional ampliado
  - Observabilidad avanzada

## Nota
La causa raíz del fallo previo era la ausencia de la migración base 001_initial_schema.sql.
Se creó y aplicó antes de reaplicar 002_phase1_hardening.sql.
