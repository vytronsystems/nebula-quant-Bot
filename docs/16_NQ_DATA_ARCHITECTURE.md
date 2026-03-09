# NEBULA-QUANT v1 | nq_data Architecture

## Objetivo
Módulo de ingesta, normalización y feed de datos para estrategias, backtesting, paper y live. Arquitectura híbrida: múltiples proveedores (TradeStation primero; Polygon, Databento, etc. después).

## Alcance actual (skeleton)
- Estructura de paquetes bajo `services/bot/nq_data/`.
- Modelo canónico OHLCV (`Bar`).
- Interfaz de proveedor (`DataProviderProtocol`).
- Stub de TradeStation (sin llamadas reales).
- Feed mínimo: `get_bars`, `get_latest` (stub: sin cache, sin resampling).
- Timeframes permitidos: `1m`, `5m`, `15m`, `1h`, `1d`.
- Provider por defecto: TradeStation (configurable vía `NQ_DATA_PROVIDER`).

## Evolución futura
- Integración real con TradeStation (OHLCV).
- Ingesta de opciones (chains).
- Proveedores adicionales (Polygon, Databento).
- Cache (Redis + disco).
- Resampling (1m → 5m, 15m, 1h, 1d).
- Streaming / polling para live y paper.
- Persistencia de histórico (Postgres o Parquet).

## Capas
1. **Consumidores**: nq_strategy, nq_backtest, paper, live.
2. **Feed**: API unificada (`get_bars`, `get_latest`, luego `stream`).
3. **Resampling**: (futuro) 1m → timeframes superiores.
4. **Cache**: (futuro) Redis (hot), disco (cold).
5. **Normalización**: raw → `Bar` canónico.
6. **Providers**: TradeStation, Polygon, Databento (stubs/implementaciones).

## Ubicación
`services/bot/nq_data/` — mismo servicio que el bot; compatible con Docker actual.

## Reglas
- No llamadas reales a APIs externas hasta iteración aprobada.
- Todo dato OHLCV pasa por el modelo `Bar`.
- Nuevos proveedores implementan `DataProviderProtocol`.
