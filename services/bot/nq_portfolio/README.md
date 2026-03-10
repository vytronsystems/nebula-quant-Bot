# NEBULA-QUANT v1 | nq_portfolio

## Purpose

`nq_portfolio` is the **portfolio construction and exposure management layer** for NEBULA-QUANT v1.
It owns portfolio-level state such as:

- **position sizing at portfolio level**
- **portfolio exposure tracking** (gross, net, long, short)
- **capital allocation by strategy**
- **capital allocation by instrument**
- **strategy weight tracking and portfolio constraints**
- **placeholders for correlation-aware allocation**

This module **does not execute trades**, does **not talk to brokers**, and does **not persist to any
database** in this iteration. It is an in-memory, safe skeleton focused on structure and interfaces.

## Place in the institutional pipeline

The broader institutional pipeline is:

`nq_data → nq_data_quality → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_guardrails → nq_exec → nq_metrics → nq_experiments`

`nq_portfolio` sits logically between **strategy / risk** and **execution / reporting** as the layer
that:

- aggregates positions from multiple strategies,
- applies portfolio-level constraints,
- tracks capital and exposure across instruments and strategies,
- prepares clean, auditable state for downstream components (paper, execution, metrics, experiments).

In this skeleton, the module is implemented as an isolated package and **not yet wired** into the
runtime pipeline; it is safe to import and reason about without affecting current execution.

## Portfolio vs. execution layer

- **Portfolio layer (`nq_portfolio`)**
  - understands positions, allocations, exposure and constraints at the portfolio level;
  - decides *what* the portfolio should look like (target weights, allowed/not-allowed decisions);
  - works purely **in memory**, deterministic and side-effect free outside its own state.

- **Execution layer (`nq_paper`, `nq_exec`)**
  - is responsible for *how* to realize portfolio decisions in the market;
  - talks to brokers / APIs, manages orders, fills, and execution risk;
  - persists decisions and execution traces for audit and monitoring.

This separation keeps portfolio logic auditable and testable without coupling it to any specific
broker or execution venue.

## Skeleton-only scope (Phase 8)

This initial version is intentionally minimal:

- **dataclasses** for `PortfolioPosition`, `PortfolioAllocation`, `PortfolioSnapshot`,
  and `PortfolioDecision`.
- `PortfolioEngine` with in-memory state, safe defaults, and fail-closed behavior for new positions.
- Helper modules:
  - `allocation.py` — simple equal-split allocation helpers.
  - `exposure.py` — basic gross/net/long/short exposure computations.
  - `constraints.py` — safe placeholder checks for max weights, exposures, and position count.
  - `config.py` — conservative default limits for portfolio-level constraints.
  - `reporter.py` — dictionary representation of portfolio snapshots for dashboards/governance.

No external dependencies are introduced, and all logic is compatible with **Python 3.11** with full
type hints.

## Preparing for multi-strategy operation

By introducing `nq_portfolio` as a dedicated module, the system is ready to support:

- multiple concurrent strategies sharing a common capital pool;
- explicit **strategy-level weights and allocations**;
- central **exposure and constraint management** before any order is sent;
- clear separation between **strategy alpha generation**, **portfolio construction**, and
  **execution**.

Future iterations can:

- connect `nq_portfolio` to `nq_risk` for richer sizing and limit logic;
- wire portfolio decisions into `nq_paper` and `nq_exec`;
- add correlation-aware allocation, optimization, and advanced constraint handling;
- persist portfolio snapshots and decisions for full auditability.

For now, this module remains a **skeleton-only, in-memory portfolio management infrastructure**
component, safe to import and extend without impacting existing validated flows.

