# NEBULA-QUANT v1 | Research Framework

## Objetivo
Descubrir, validar, comparar, promover y retirar estrategias con base estadística.

## Regla principal
Ninguna estrategia entra al sistema operativo sin pasar por:
1. hipótesis
2. backtest
3. walk-forward
4. Monte Carlo
5. paper trading
6. auditoría

## Pipeline institucional
Idea
↓
Hypothesis
↓
Backtest
↓
Walk-forward
↓
Monte Carlo
↓
Paper trading
↓
Live controlled
↓
Audit
↓
Improve or retire

## Criterios mínimos de validación
- lógica económica razonable
- evidencia estadística
- métricas reproducibles
- control de drawdown
- criterio claro de activación y desactivación

## Estrategias objetivo iniciales
- momentum breakout
- trend pullback
- opening range breakout
- volatility expansion
- mean reversion intraday
- squeeze breakout
- VWAP reclaim/rejection
- ATR continuation
- liquidity sweep continuation
- regime-based intraday bias

## Artefactos por estrategia
Cada estrategia debe tener:
- strategy_id
- hypothesis.md
- config.yaml
- backtest_report.md
- walkforward_report.md
- montecarlo_report.md
- paper_report.md
- audit_notes.md
