# NEBULA-QUANT v1 | Strategy Registry Standard

## Objetivo
Mantener un registro institucional de estrategias activas, experimentales, retiradas o rechazadas.

## Estados posibles
- idea
- research
- backtest
- paper
- live
- disabled
- retired
- rejected

## Campos mínimos
- strategy_id
- name
- status
- version
- owner
- created_at
- updated_at
- market
- instrument_type
- timeframe
- regime_target
- risk_profile
- hypothesis
- activation_rules
- deactivation_rules

## Regla
Toda estrategia debe poder rastrearse por versión y estado.
