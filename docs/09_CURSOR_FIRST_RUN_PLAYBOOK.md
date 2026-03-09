# NEBULA-QUANT v1 | Cursor First Run Playbook

## Objetivo
Usar Cursor sobre el repo real existente sin reconstruir desde cero.

## Orden de lectura en Cursor
1. docs/00_CURRENT_STATE_BASELINE.md
2. docs/00_MASTER_EXECUTION_PLAN.md
3. docs/01_PROJECT_CONSTITUTION.md
4. docs/02_FACTORY_OPERATING_MODEL.md
5. docs/03_MODULE_CATALOG.md
6. docs/04_GIT_WORKFLOW.md
7. docs/05_CURSOR_MASTER_PROMPT.md
8. docs/06_AGENT_ORCHESTRATOR.md
9. docs/07_AGENT_ARCHITECTURE_GATE.md
10. docs/08_AGENT_QA_GATE.md

## Primer prompt a pegar en Cursor
Pegar el contenido de docs/05_CURSOR_MASTER_PROMPT.md

## Primer mensaje después del prompt maestro
Actúa como Orchestrator + Architecture Gate de NEBULA-QUANT v1.

Analiza el repositorio actual y genera un baseline técnico del estado real del proyecto.

No reconstruyas desde cero.
No sobrescribas componentes existentes.
No cambies la arquitectura sin justificarlo.

Tu tarea inicial es:
1. identificar qué ya está implementado,
2. qué está parcialmente implementado,
3. qué falta respecto al Master Execution Plan,
4. proponer backlog incremental para Fase 2.

## Regla
La primera iteración en Cursor debe ser solo de análisis y planificación.
No debe crear código todavía.
