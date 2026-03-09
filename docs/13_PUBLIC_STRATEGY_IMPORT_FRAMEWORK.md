# NEBULA-QUANT v1 | Public Strategy Import Framework

## Objetivo
Permitir importar ideas o implementaciones desde repos públicos sin contaminar el core operativo.

## Regla principal
No copiar directo a producción.
Toda estrategia importada entra primero al sandbox.

## Flujo
1. seleccionar repositorio público
2. seleccionar estrategia
3. documentar origen
4. extraer hipótesis
5. adaptar al formato local
6. correr backtest
7. auditar resultados
8. decidir si continúa

## Reglas
- siempre registrar URL de origen
- no asumir calidad del código externo
- revisar dependencia de librerías
- aislar código importado del core live
- no promover nada sin validación local

## Destino recomendado
research/imports/<repo>/<strategy>/
