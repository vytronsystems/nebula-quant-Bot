# NEBULA-QUANT v1  
## Pipeline Modules Overview

Status: Institutional Architecture Document

---

# Purpose

This document defines the **core trading pipeline modules** of NEBULA-QUANT.

The pipeline is responsible for transforming raw market data into validated trading strategies and ultimately promoting them to live trading.

The pipeline operates as a **deterministic research workflow**.

---

# Pipeline Order

The official pipeline must always follow this sequence:
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


The order of this pipeline **must not change**.

---

# Module Responsibilities

## nq_data

Provides market data feeds and bar structures.

Responsibilities:

- load OHLCV data
- provide feed abstraction
- standardize bar representation

---

## nq_data_quality

Validates market data before research or execution.

Responsibilities:

- detect missing data
- validate timestamps
- detect corrupted bars

---

## nq_strategy

Defines strategy logic and signal generation.

Responsibilities:

- define strategy rules
- produce trade signals
- enforce deterministic signal generation

---

## nq_risk

Evaluates trade decisions from a risk perspective.

Responsibilities:

- validate risk limits
- approve or reject trades

---

## nq_backtest

Evaluates strategies against historical data.

Responsibilities:

- simulate historical execution
- compute performance metrics
- ensure deterministic results

---

## nq_walkforward

Validates strategies across multiple time segments.

Responsibilities:

- perform rolling validation
- detect overfitting

---

## nq_paper

Simulates live trading without real capital.

Responsibilities:

- simulate order execution
- evaluate strategy behavior under live conditions

---

## nq_guardrails

Protects the system from unsafe trading behavior.

Responsibilities:

- enforce risk limits
- detect abnormal activity

---

## nq_exec

Handles execution logic.

Responsibilities:

- submit orders
- manage execution lifecycle

---

## nq_metrics

Tracks performance and system metrics.

Responsibilities:

- collect metrics
- generate observability data

---

## nq_experiments

Manages research experiments.

Responsibilities:

- run strategy experiments
- record experiment results

---

## nq_portfolio

Manages strategy allocation and portfolio construction.

Responsibilities:

- allocate capital
- manage strategy exposure

---

## nq_promotion

Determines whether a strategy can be promoted to live trading.

Responsibilities:

- evaluate strategy performance
- approve or reject promotion

---

# Research Pipeline

The strategy research pipeline operates as:
Alpha Discovery
→ Experiments
→ Backtest
→ Walkforward
→ Paper Trading
→ Promotion


Strategies that fail validation are returned to the research loop.

---

# Governance Rules

1. Strategies must pass deterministic validation.
2. Strategies must pass backtesting and walkforward validation.
3. Strategies must prove stability during paper trading.
4. Strategies must pass promotion governance before live deployment.

---

# Continuous Research Loop

The system continuously improves strategies through:
Learning
→ Improvement
→ Experiments
→ Backtesting


This creates a **self-improving quantitative research system**.
