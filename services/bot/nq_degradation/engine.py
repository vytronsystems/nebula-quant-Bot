# NEBULA-QUANT v1 | Phase 77 — Strategy Degradation Engine
# Fail-closed: if thresholds violated → degraded, trading_enabled = False; emit alert.

from __future__ import annotations

from typing import Any

from nq_degradation.models import DegradationResult, DegradationSignal

MIN_ROLLING_WIN_RATE = 0.45
MAX_DRAWDOWN = 0.20
MIN_PROFIT_FACTOR = 0.95


class DegradationEngine:
    """Detect loss of edge; recommend degraded state and trading_enabled = false."""

    def evaluate(
        self,
        deployment_id: str,
        rolling_win_rate: float | None = None,
        rolling_pnl: float | None = None,
        drawdown: float | None = None,
        profit_factor: float | None = None,
    ) -> DegradationResult:
        alerts: list[str] = []
        reason = "ok"
        if rolling_win_rate is not None and rolling_win_rate < MIN_ROLLING_WIN_RATE:
            reason = "rolling_win_rate_below_threshold"
            alerts.append("degradation:win_rate")
        if drawdown is not None and drawdown > MAX_DRAWDOWN:
            reason = "drawdown_exceeded"
            alerts.append("degradation:drawdown")
        if profit_factor is not None and profit_factor < MIN_PROFIT_FACTOR:
            reason = "profit_factor_below_threshold"
            alerts.append("degradation:profit_factor")

        should_degrade = reason != "ok"
        signal = None
        if should_degrade:
            signal = DegradationSignal(
                deployment_id=deployment_id,
                reason=reason,
                rolling_win_rate=rolling_win_rate,
                rolling_pnl=rolling_pnl,
                drawdown=drawdown,
                profit_factor=profit_factor,
            )
        return DegradationResult(
            should_degrade=should_degrade,
            trading_enabled=not should_degrade,
            signal=signal,
            alerts_emitted=alerts,
        )
