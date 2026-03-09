# NEBULA-QUANT v1 | Factory Operating Model

## Modelo operativo
El desarrollo se ejecuta como software factory de una sola persona apoyada por agentes de IA en Cursor.

## Roles permanentes

### Orchestrator
- analiza el repo
- genera backlog
- define secuencia de trabajo
- evita improvisación

### Architecture Gate
- valida ubicación de cambios
- evita drift arquitectónico
- revisa antes y después de construir

### Builder Agent
- implementa tareas específicas
- no cambia arquitectura sin aprobación

### QA Gate
- valida funcionalidad
- valida regresión
- valida criterios de aceptación
- rechaza cambios incompletos

### Git/Release Discipline
- cada cambio importante se hace en rama
- todo cambio validado se commitea
- nada se hace directo sobre main

## Flujo obligatorio
1. Orchestrator define tarea
2. Architect Gate aprueba alcance técnico
3. Builder implementa
4. Architect Gate revisa
5. QA Gate valida
6. Git registra
7. solo entonces pasa a Done

## Regla de evidencia
Todo cambio debe dejar evidencia:
- comandos ejecutados
- logs
- salida de verificación
- o pruebas automatizadas

## Regla de baseline
Antes de desarrollar una fase nueva:
- validar estado actual
- documentar baseline
- no asumir

## Regla de seguridad operativa
Cualquier hallazgo de secreto expuesto, migración faltante, validación rota o inconsistencia de entorno bloquea el avance hasta corregirse.
