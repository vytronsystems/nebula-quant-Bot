# Phase 75 — Recommendation Engine — Result

## Summary

Automated strategy state recommendations from metrics thresholds. States: Ready for Live, Requires More Data, Keep in Paper, Degraded, Rejected.

## Implementation

- **Bot**: `nq_recommendation` — RecommendationEngine.recommend() with thresholds (MIN_WIN_RATE_LIVE, MIN_PROFIT_FACTOR_LIVE, MIN_TRADES_LIVE, MIN_DAYS_LIVE, MAX_DRAWDOWN_LIVE). Returns RecommendationResult with recommended_state and reason.
- **Control Plane**: RecommendationsController — GET /api/recommendations returns list of deploymentId, currentStage, recommendedState, reason (from StrategyDeployment + StrategyMetrics).

## Modules Affected

- services/bot/nq_recommendation/
- services/control-plane api/RecommendationsController.java
