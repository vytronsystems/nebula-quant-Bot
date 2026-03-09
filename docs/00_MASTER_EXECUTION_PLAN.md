# NEBULA-QUANT v1 | Master Execution Plan

## Estado actual validado
Fase 1 cerrada técnicamente:
- Docker Compose operativo
- Bot, Postgres, Redis, Grafana, Prometheus, Alertmanager y Postgres Exporter activos
- Endpoint /metrics operativo
- Grafana accesible
- Prometheus healthy
- Persistencia mínima validada
- Script scripts/nq-verify.sh pasando

## Principio rector
No reconstruir desde cero.
Todo el trabajo futuro debe partir del repositorio real existente.

## Fases del proyecto

### Fase 0
Baseline, auditoría, Git y publicación inicial.
Estado: completada.

### Fase 0.5
Integración de software factory sobre el repo existente.
Incluye:
- documentación institucional
- prompts de Cursor
- Orchestrator
- Architecture Gate
- QA Gate
- workflow Git
- backlog incremental

### Fase 1
Infraestructura, observabilidad y persistencia mínima.
Estado: completada técnicamente.

### Fase 2
Trading Core institucional.
Incluye:
- Strategy Engine
- Risk Engine
- Data Ingestion
- Broker Execution base
- Logging institucional ampliado
- Guardrails

### Fase 3
Backtesting y Research Lab.
Incluye:
- motor de backtesting
- strategy registry
- research workflow
- walk-forward
- Monte Carlo
- auditoría de estrategias

### Fase 4
Auditoría continua y mejora del sistema.
Incluye:
- trade review diario/semanal/mensual
- edge decay monitoring
- learning loop
- alpha discovery
- reportes institucionales

### Fase 5
Paper trading institucional

### Fase 6
Live trading controlado

## Regla de ejecución
Toda iteración debe seguir:
Orchestrator -> Architect Gate -> Builder -> QA Gate -> Git

## Regla de done
Nada está Done hasta que:
1. Architect Gate apruebe
2. QA Gate apruebe
3. exista evidencia reproducible
4. quede versionado en Git
