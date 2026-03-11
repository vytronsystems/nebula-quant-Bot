# NEBULA-QUANT v1 | Architecture

## System overview
NEBULA-QUANT v1 is a modular, deterministic trading research and execution platform. All core modules live under `services/bot/` and communicate through a strict linear pipeline. The architecture is **fail-closed**: missing or ambiguous data must BLOCK instead of silently degrading behavior.

## Official pipeline

nq_data  
→ nq_data_quality  
→ nq_strategy  
→ nq_risk  
→ nq_backtest  
→ nq_walkforward  
→ nq_paper  
→ nq_guardrails  
→ nq_exec  
→ nq_metrics  
→ nq_experiments  
→ nq_portfolio  
→ nq_promotion

This order encodes the institutional decision flow: data → signal → risk → validation → paper → safety → execution → observability → portfolio governance → lifecycle governance.

## Module responsibilities

- **nq_data**: ingest and normalize market data into canonical `Bar` objects; no external providers are wired yet in v1.
- **nq_data_quality**: validate data quality (gaps, anomalies, consistency).
- **nq_strategy**: generate deterministic trading signals from data; does not execute or manage risk.
- **nq_risk**: evaluate proposed trades (`RiskOrderIntent`) against account and strategy context; enforce max risk-per-trade and daily risk budgets; return **ALLOW / REDUCE / BLOCK**.
- **nq_backtest**: run reproducible historical simulations over signals; compute performance metrics and equity curves.
- **nq_walkforward**: orchestrate train/test windows across time, aggregating multiple backtests into robust validation.
- **nq_paper**: simulate live trading in-memory using the same decision logic, without connecting to brokers.
- **nq_guardrails**: enforce global safety constraints (drawdown, daily loss, volatility, strategy disable); fail-closed controller.
- **nq_exec**: abstract execution; validate orders, simulate fills and produce `ExecutionResult`; no broker routing in v1.
- **nq_metrics**: compute performance metrics and system observability reports from normalized inputs.
- **nq_experiments**: track experiments and comparisons (skeleton at this phase).
- **nq_portfolio**: manage portfolio-level governance (capital allocation, exposure limits, drawdown limits); final portfolio approval gate before `nq_exec`.
- **nq_promotion**: lifecycle governance (idea → research → backtest → walkforward → paper → live → retired) using evidence from validation and paper trading.

### Supporting components

- **nq_strategy_registry**: registry and lifecycle source of truth for strategies; used by promotion, portfolio and observability.
- **nq_obs**: observability integration layer; gathers outputs from registry, risk, guardrails, exec, portfolio, promotion and experiments and normalizes them for `nq_metrics`.
- **Database & infra**: Docker Compose, Postgres, Redis, Prometheus, Grafana, Alertmanager and supporting scripts (`nq-verify.sh`).

## Separation of concerns

- **Data layer**: `nq_data`, `nq_data_quality` — ingestion and validation only.
- **Signal layer**: `nq_strategy` — deterministic signal generation; no sizing, risk or execution.
- **Risk layer**: `nq_risk` — per-trade risk limits, risk budgets and REDUCE/BLOCK logic; does not execute trades.
- **Validation layer**: `nq_backtest`, `nq_walkforward` — offline validation.
- **Simulated execution layer**: `nq_paper` — paper trading.
- **Safety layer**: `nq_guardrails` — system-level kill-switch and guardrails.
- **Execution layer**: `nq_exec` — abstract execution; no signal generation.
- **Observability layer**: `nq_obs` (integration) + `nq_metrics` (metrics & reporting).
- **Governance layer**: `nq_strategy_registry`, `nq_promotion`, `nq_portfolio`.

## Deterministic and fail-closed design

- No random behavior in core decision paths.
- All engines validate inputs; missing or inconsistent state returns BLOCK or explicit errors.
- Lifecycle and risk checks are explicit and reproducible.
- Observability does not affect trading decisions by side effect; it consumes events and produces reports only.

## Lifecycle governance

Strategies move forward only through validated evidence:

1. **Idea / research** — hypotheses and early experiments (future `nq_research`, `nq_lab`).
2. **Backtest** — rigorous historical testing (`nq_backtest`).
3. **Walk-forward** — out-of-sample validation (`nq_walkforward`).
4. **Paper** — simulated live trading (`nq_paper`) with weekly audit.
5. **Live** — only after promotion via `nq_promotion` and consistency with registry and risk controls.
6. **Retired** — explicit lifecycle state when edge decays or risk profile changes.

`nq_strategy_registry` stores lifecycle state; `nq_promotion` and `nq_portfolio` enforce governance decisions using that truth.
