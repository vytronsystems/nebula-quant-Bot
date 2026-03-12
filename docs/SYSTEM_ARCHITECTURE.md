# NEBULA-QUANT v1  
## System Architecture

```mermaid
flowchart LR

subgraph DATA_LAYER
A[nq_data]
B[nq_data_quality]
end

subgraph STRATEGY_LAYER
C[nq_strategy]
D[nq_risk]
end

subgraph RESEARCH_LAYER
E[nq_backtest]
F[nq_walkforward]
G[nq_paper]
H[nq_experiments]
I[nq_alpha_discovery]
J[nq_regime]
end

subgraph EXECUTION_LAYER
K[nq_guardrails]
L[nq_exec]
end

subgraph GOVERNANCE_LAYER
M[nq_promotion]
N[nq_trade_review]
O[nq_audit]
P[nq_learning]
Q[nq_improvement]
R[nq_edge_decay]
end

subgraph INFRASTRUCTURE_LAYER
S[nq_db]
T[nq_event_store]
U[nq_cache]
V[nq_config]
W[nq_scheduler]
X[nq_orchestrator]
end

subgraph OPERATIONS_LAYER
Y[nq_sre]
Z[nq_runbooks]
AA[nq_release]
AB[nq_reporting]
AC[nq_obs]
end

A --> B
B --> C
C --> D
D --> E
E --> F
F --> G
G --> K
K --> L

E --> H
H --> I
I --> J

L --> N
N --> O
O --> P
P --> Q
Q --> R

R --> M

S --> X
T --> X
U --> X
V --> X
W --> X

X --> A
X --> AB

Y --> Z
Z --> AB
AA --> AB
AC --> AB
