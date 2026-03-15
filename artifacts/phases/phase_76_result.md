# Phase 76 — Live Routing — Result

## Summary

Route orders by deployment stage: live → production credentials; else → testnet/paper. Fail-closed.

## Implementation

- **Bot**: `nq_exec/live_routing.py` — route_by_stage(stage) returns RoutingDecision (use_production, use_testnet, use_paper, reason). select_adapter_key(stage) returns "production" | "paper" | "testnet". Unknown/missing stage → paper.

## Modules Affected

- services/bot/nq_exec/live_routing.py
