# NEBULA-QUANT v1 | nq_guardrails config (placeholder limits)

# Placeholder: max drawdown (fraction) before shutdown.
# Not enforced until integration with PnL/account feed.
MAX_DRAWDOWN_LIMIT: float = 0.10  # 10%

# Placeholder: max daily loss (fraction) before halt.
# Not enforced until integration with daily PnL.
DAILY_LOSS_LIMIT: float = 0.05  # 5%

# Placeholder: volatility threshold for shutdown (e.g. VIX or realized vol).
# Not enforced until integration with volatility feed.
VOLATILITY_THRESHOLD: float = 50.0  # arbitrary units

# Placeholder: max open positions before blocking new trades.
# Not enforced until integration with position tracking.
MAX_OPEN_POSITIONS: int = 20
