# NEBULA-QUANT v1 | Backtesting Standard

## Objetivo
Asegurar que todo backtest tenga rigor suficiente y no sea una ilusión estadística.

## Reglas obligatorias
1. No usar look-ahead bias.
2. No usar fills imposibles.
3. Incluir costos, spreads o slippage razonable.
4. Dejar evidencia reproducible.
5. Separar claramente train/test.
6. No promover estrategias solo por una curva bonita.

## Métricas mínimas
- total trades
- win rate
- average win
- average loss
- expectancy
- profit factor
- max drawdown
- avg RR real
- best regime
- worst regime

## Validaciones mínimas
- out-of-sample
- walk-forward
- Monte Carlo
- sensitivity review

## Regla de promoción
Una estrategia solo puede pasar de research a paper si:
- supera umbrales mínimos
- no muestra fragilidad obvia
- tiene documentación completa
- fue auditada
