# NEBULA-QUANT v1 | nq_risk limits (stubs and default policy)

from nq_risk.models import RiskLimits

# Stub: max risk per trade (e.g. fraction of equity or absolute).
MAX_RISK_PER_TRADE: float = 0.02  # 2% placeholder

# Stub: max daily drawdown (fraction) before halting new risk.
MAX_DAILY_DRAWDOWN: float = 0.05  # 5% placeholder

# Stub: max concurrent open positions.
MAX_CONCURRENT_POSITIONS: int = 5  # placeholder

# Default risk limits for the decision engine.
DEFAULT_RISK_LIMITS: RiskLimits = RiskLimits(
    max_risk_per_trade_pct=0.02,
    max_daily_strategy_risk_pct=None,
    max_daily_account_risk_pct=None,
    require_stop_loss=False,
    max_stop_distance_pct=None,
    warning_risk_per_trade_pct=0.015,
)
