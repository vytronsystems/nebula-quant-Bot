# NEBULA-QUANT v1 | nq_risk limits (stubs)

# Stub: max risk per trade (e.g. fraction of equity or absolute).
# Not enforced until integration with portfolio/broker.
MAX_RISK_PER_TRADE: float = 0.02  # 2% placeholder

# Stub: max daily drawdown (fraction) before halting new risk.
# Not enforced until integration with PnL feed.
MAX_DAILY_DRAWDOWN: float = 0.05  # 5% placeholder

# Stub: max concurrent open positions.
# Not enforced until integration with position tracking.
MAX_CONCURRENT_POSITIONS: int = 5  # placeholder
