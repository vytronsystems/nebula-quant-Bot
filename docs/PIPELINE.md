# NEBULA-QUANT v1 | Pipeline

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

This pipeline defines the deterministic flow of information and decisions in NEBULA-QUANT v1.

## Stage responsibilities

- **nq_data**: obtain and normalize market data into canonical `Bar` objects.
- **nq_data_quality**: perform data quality checks (gaps, anomalies, consistency) before strategies consume data.
- **nq_strategy**: transform cleaned data into trading signals; does not size or execute.
- **nq_risk**: evaluate each proposed trade against account and strategy risk limits; may ALLOW, REDUCE size or BLOCK.
- **nq_backtest**: run historical simulations for research and validation.
- **nq_walkforward**: orchestrate train/test windows and aggregate backtest evidence.
- **nq_paper**: simulate live trading without touching brokers; used before promotion to live.
- **nq_guardrails**: enforce system-level safety constraints (drawdown, daily loss, volatility, strategy disable).
- **nq_exec**: perform abstracted execution of orders; produces `ExecutionResult` objects.
- **nq_metrics**: compute metrics and observability reports from normalized inputs.
- **nq_experiments**: track experiments and comparisons (skeleton).
- **nq_portfolio**: enforce portfolio-level governance (capital usage, exposures, drawdowns) as the final approval gate before execution.
- **nq_promotion**: govern lifecycle transitions for strategies across research, backtest, paper and live.

## Non-pipeline integrations

- **nq_strategy_registry**: registry and lifecycle source of truth used by promotion, portfolio, risk and observability.
- **nq_obs**: observability integration layer that consumes outputs from the pipeline and builds inputs for `nq_metrics`.
