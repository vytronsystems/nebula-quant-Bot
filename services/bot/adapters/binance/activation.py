# NEBULA-QUANT v1 | Phase 58 — Controlled live activation for Binance

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Governance decision type: accept string or enum for loose coupling
GOVERNANCE_APPROVED = "approved_for_live"


@dataclass(slots=True)
class BinanceLiveActivationConfig:
    """
    Explicit live activation configuration. All defaults conservative.
    JSON-compatible; no secrets.
    """

    shadow_enabled: bool = True
    paper_enabled: bool = True
    live_enabled: bool = False

    default_timeframe: str = "5m"

    risk_per_trade_pct: float = 0.01
    max_daily_loss_pct: float = 0.03
    max_position_size_pct: float = 0.20
    max_notional_per_order_pct: float = 0.20
    max_open_positions: int = 1

    heartbeat_timeout_seconds: int = 30
    max_order_rate_per_minute: int = 5
    reset_hour_utc: int = 0

    min_shadow_trades: int = 30
    min_paper_trades: int = 30
    min_win_rate: float = 0.58
    min_rr: float = 1.80
    min_profit_factor: float = 1.30
    min_expectancy: float = 0.0
    max_drawdown_pct: float = 0.20

    require_governance_approval: bool = True

    allowed_live_strategies: list[str] = field(default_factory=list)
    activation_mode: str = "performance_gated"

    metadata: dict[str, Any] = field(default_factory=dict)


# Default instance; live disabled, shadow/paper enabled
BINANCE_LIVE_ACTIVATION_CONFIG = BinanceLiveActivationConfig()


@dataclass(slots=True)
class StrategyPerformanceMetrics:
    """Performance metrics from shadow/paper used for eligibility."""

    strategy_id: str
    win_rate: float | None = None
    rr: float | None = None  # risk-reward ratio
    profit_factor: float | None = None
    expectancy: float | None = None
    max_drawdown_pct: float | None = None
    shadow_trade_count: int = 0
    paper_trade_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyEligibilityRecord:
    """Result of evaluating one strategy for live eligibility."""

    strategy_id: str
    eligible_for_live: bool
    not_eligible: bool
    reasons: list[str]
    failed_metrics: list[str]
    source_mode: str  # "shadow" | "paper"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinanceActivationReport:
    """Summary of activation state: eligible, pending, rejected."""

    live_enabled: bool
    eligible_strategies: list[str]
    pending_strategies: list[str]
    rejected_strategies: list[str]
    reasons_by_strategy: dict[str, list[str]]
    metadata: dict[str, Any] = field(default_factory=dict)


class BinanceActivationError(Exception):
    """Raised when live activation is not allowed (fail closed)."""


def _governance_acceptable(decision: Any, require: bool) -> bool:
    if not require:
        return True
    if decision is None:
        return False
    s = getattr(decision, "value", decision) if hasattr(decision, "value") else decision
    return str(s).strip() == GOVERNANCE_APPROVED


class BinanceActivationEngine:
    """
    Controlled live activation: performance-gated strategy selection,
    venue policy (Binance first, TradeStation disabled), and execution gating.
    """

    def __init__(
        self,
        config: BinanceLiveActivationConfig | None = None,
        binance_venue_enabled: bool = True,
        tradestation_venue_enabled: bool = False,
    ) -> None:
        self._config = config or BINANCE_LIVE_ACTIVATION_CONFIG
        self._binance_enabled = binance_venue_enabled
        self._tradestation_enabled = tradestation_venue_enabled

    def evaluate_strategy_eligibility(
        self,
        strategy_id: str,
        strategy_metrics: StrategyPerformanceMetrics | dict[str, Any],
        governance_decision: Any,
        source_mode: str,
    ) -> StrategyEligibilityRecord:
        """
        Evaluate whether a strategy is live-eligible from shadow/paper metrics.
        Returns a record with eligible_for_live, not_eligible, reasons, failed_metrics.
        """
        reasons: list[str] = []
        failed_metrics: list[str] = []

        if source_mode not in ("shadow", "paper"):
            reasons.append(f"invalid source_mode {source_mode!r}")
            return StrategyEligibilityRecord(
                strategy_id=strategy_id,
                eligible_for_live=False,
                not_eligible=True,
                reasons=reasons,
                failed_metrics=["source_mode"],
                source_mode=source_mode,
            )

        m = strategy_metrics
        if isinstance(m, dict):
            win_rate = m.get("win_rate")
            rr = m.get("rr")
            profit_factor = m.get("profit_factor")
            expectancy = m.get("expectancy")
            max_drawdown_pct = m.get("max_drawdown_pct")
            shadow_trades = int(m.get("shadow_trade_count", 0) or 0)
            paper_trades = int(m.get("paper_trade_count", 0) or 0)
        else:
            win_rate = getattr(m, "win_rate", None)
            rr = getattr(m, "rr", None)
            profit_factor = getattr(m, "profit_factor", None)
            expectancy = getattr(m, "expectancy", None)
            max_drawdown_pct = getattr(m, "max_drawdown_pct", None)
            shadow_trades = int(getattr(m, "shadow_trade_count", 0) or 0)
            paper_trades = int(getattr(m, "paper_trade_count", 0) or 0)

        cfg = self._config

        # Trade count: require both min_shadow_trades and min_paper_trades
        if shadow_trades < cfg.min_shadow_trades:
            reasons.append(f"shadow_trade_count {shadow_trades} < min_shadow_trades {cfg.min_shadow_trades}")
            failed_metrics.append("shadow_trade_count")
        if paper_trades < cfg.min_paper_trades:
            reasons.append(f"paper_trade_count {paper_trades} < min_paper_trades {cfg.min_paper_trades}")
            failed_metrics.append("paper_trade_count")

        # Win rate
        if win_rate is not None and win_rate < cfg.min_win_rate:
            reasons.append(f"win_rate {win_rate} < min_win_rate {cfg.min_win_rate}")
            failed_metrics.append("win_rate")

        # RR
        if rr is not None and rr < cfg.min_rr:
            reasons.append(f"rr {rr} < min_rr {cfg.min_rr}")
            failed_metrics.append("rr")

        # Profit factor
        if profit_factor is not None and profit_factor < cfg.min_profit_factor:
            reasons.append(f"profit_factor {profit_factor} < min_profit_factor {cfg.min_profit_factor}")
            failed_metrics.append("profit_factor")

        # Expectancy
        if expectancy is not None and expectancy < cfg.min_expectancy:
            reasons.append(f"expectancy {expectancy} < min_expectancy {cfg.min_expectancy}")
            failed_metrics.append("expectancy")

        # Drawdown
        if max_drawdown_pct is not None and max_drawdown_pct > cfg.max_drawdown_pct:
            reasons.append(f"max_drawdown_pct {max_drawdown_pct} > max_drawdown_pct {cfg.max_drawdown_pct}")
            failed_metrics.append("max_drawdown_pct")

        # Governance
        if cfg.require_governance_approval and not _governance_acceptable(governance_decision, True):
            reasons.append("governance approval required but not approved")
            failed_metrics.append("governance")

        not_eligible = len(failed_metrics) > 0 or len(reasons) > 0
        eligible_for_live = not not_eligible

        return StrategyEligibilityRecord(
            strategy_id=strategy_id,
            eligible_for_live=eligible_for_live,
            not_eligible=not_eligible,
            reasons=reasons,
            failed_metrics=failed_metrics,
            source_mode=source_mode,
        )

    def update_allowed_live_strategies(
        self,
        candidate_metrics_list: list[tuple[str, StrategyPerformanceMetrics | dict[str, Any], Any, str]],
    ) -> BinanceActivationReport:
        """
        Recompute allowed_live_strategies from candidate list.
        Each candidate is (strategy_id, metrics, governance_decision, source_mode).
        Returns report with eligible, pending, rejected.
        """
        eligible: list[str] = []
        rejected: list[str] = []
        reasons_by_strategy: dict[str, list[str]] = {}

        for strategy_id, metrics, gov_decision, source_mode in candidate_metrics_list:
            rec = self.evaluate_strategy_eligibility(strategy_id, metrics, gov_decision, source_mode)
            if rec.eligible_for_live:
                eligible.append(strategy_id)
                reasons_by_strategy[strategy_id] = []
            else:
                rejected.append(strategy_id)
                reasons_by_strategy[strategy_id] = rec.reasons

        # Pending = not in eligible and not in rejected from this batch; could be strategies not yet evaluated
        allowed = list(dict.fromkeys(eligible))
        self._config.allowed_live_strategies = allowed

        pending: list[str] = []
        return BinanceActivationReport(
            live_enabled=self._config.live_enabled,
            eligible_strategies=allowed,
            pending_strategies=pending,
            rejected_strategies=rejected,
            reasons_by_strategy=reasons_by_strategy,
        )

    def assert_strategy_live_eligible(self, strategy_id: str) -> None:
        """Fail closed if strategy is not in allowed_live_strategies."""
        allowed = getattr(self._config, "allowed_live_strategies", []) or []
        if strategy_id not in allowed:
            raise BinanceActivationError(f"strategy {strategy_id!r} is not live-eligible (not in allowed_live_strategies)")

    def assert_live_activation_allowed(self, strategy_id: str, venue: str = "binance") -> None:
        """
        Fail closed if live is disabled, venue is disabled, or strategy is not eligible.
        TradeStation must remain non-live by default.
        """
        if not self._config.live_enabled:
            raise BinanceActivationError("live is disabled")
        if venue == "binance" and not self._binance_enabled:
            raise BinanceActivationError("Binance venue is disabled")
        if venue == "tradestation" and not self._tradestation_enabled:
            raise BinanceActivationError("TradeStation venue is disabled")
        if venue not in ("binance", "tradestation"):
            raise BinanceActivationError(f"unknown venue {venue!r}")
        self.assert_strategy_live_eligible(strategy_id)


# Venue policy: Binance first live venue, TradeStation disabled by default
def binance_venue_enabled_default() -> bool:
    return True


def tradestation_venue_enabled_default() -> bool:
    return False
