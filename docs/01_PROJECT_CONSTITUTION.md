# NEBULA-QUANT v1 | Project Constitution

## Identidad del proyecto
NEBULA-QUANT es una plataforma institucional de trading cuantitativo orientada a:
- investigación
- backtesting
- auditoría
- ejecución controlada
- mejora continua

No es un script aislado.
No es un bot improvisado.
Es un sistema cuantitativo con disciplina de software factory.

## Principios no negociables
1. El riesgo manda sobre la estrategia.
2. No se rompe lo ya validado sin justificación.
3. Toda decisión importante debe ser auditable.
4. No se hardcodean secretos.
5. El sistema debe ser observable.
6. Fail-closed antes que fail-open.
7. Ningún cambio va a Done sin QA.
8. Ningún cambio estructural va a Done sin Architect Gate.
9. Toda estrategia requiere validación estadística.
10. Nada va a live sin pasar por research, backtest y paper.

## Alcance v1
Mercado principal:
- QQQ options en TradeStation

Mercado secundario:
- BTCUSDT futures en Binance
Estado: previsto, no prioritario para el núcleo inicial.

## Regla de continuidad
Cada respuesta o iteración de desarrollo debe comenzar con:
NEBULA-QUANT v1 | Fase X | Paso Y | Estado: ...

## Regla de seguridad
Se prohíbe subir a Git:
- tokens
- credenciales
- secrets
- archivos sensibles locales

## Regla de evolución
El sistema debe aprender desde el día 1:
- auditoría de trades
- auditoría de backtests
- revisión semanal
- mejora continua
- propuestas de nuevas estrategias
