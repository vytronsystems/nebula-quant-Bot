# NEBULA-QUANT v1 | Phase 75 — Recommendation Engine
# Deterministic state recommendation from metrics thresholds. Fail-closed.

from __future__ import annotations

from typing import Any

from nq_recommendation.models import RecommendationResult, RecommendedState


# Thresholds (configurable via env or caller)
MIN_WIN_RATE_LIVE = 0.55
MIN_PROFIT_FACTOR_LIVE = 1.2
MIN_TRADES_LIVE = 30
MIN_DAYS_LIVE = 14
MAX_DRAWDOWN_LIVE = 0.15

MIN_TRADES_DATA = 5
MIN_DAYS_DATA = 3


class RecommendationEngine:
    """Generate automated strategy state recommendations from metrics."""

    def recommend(
        self,
        deployment_id: str,
        current_stage: str,
        win_rate: float | None = None,
        profit_factor: float | None = None,
        trades_count: int = 0,
        days_count: int = 0,
        max_drawdown: float | None = None,
        pnl: float | None = None,
    ) -> RecommendationResult:
        metrics = {
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "trades_count": trades_count,
            "days_count": days_count,
            "max_drawdown": max_drawdown,
            "pnl": pnl,
        }
        state, reason = self._evaluate(metrics, current_stage)
        return RecommendationResult(
            deployment_id=deployment_id,
            current_stage=current_stage,
            recommended_state=state,
            reason=reason,
            metrics_used=metrics,
        )

    def _evaluate(self, m: dict[str, Any], stage: str) -> tuple[RecommendedState, str]:
        wr = m.get("win_rate")
        pf = m.get("profit_factor")
        trades = int(m.get("trades_count") or 0)
        days = int(m.get("days_count") or 0)
        dd = m.get("max_drawdown")

        if wr is not None and (wr < 0 or wr > 1):
            return RecommendedState.REJECTED, "invalid_win_rate"
        if trades < 0 or days < 0:
            return RecommendedState.REJECTED, "invalid_counts"
        if dd is not None and dd < 0:
            return RecommendedState.DEGRADED, "negative_drawdown"

        if trades < MIN_TRADES_DATA or days < MIN_DAYS_DATA:
            return RecommendedState.REQUIRES_MORE_DATA, "insufficient_trades_or_days"

        if dd is not None and dd > MAX_DRAWDOWN_LIVE:
            return RecommendedState.DEGRADED, "max_drawdown_exceeded"

        if wr is not None and wr < MIN_WIN_RATE_LIVE:
            return RecommendedState.KEEP_IN_PAPER, "win_rate_below_threshold"
        if pf is not None and pf < MIN_PROFIT_FACTOR_LIVE:
            return RecommendedState.KEEP_IN_PAPER, "profit_factor_below_threshold"
        if trades < MIN_TRADES_LIVE or days < MIN_DAYS_LIVE:
            return RecommendedState.KEEP_IN_PAPER, "need_more_trades_or_days"

        if stage == "live":
            return RecommendedState.READY_FOR_LIVE, "already_live"
        return RecommendedState.READY_FOR_LIVE, "thresholds_met"
