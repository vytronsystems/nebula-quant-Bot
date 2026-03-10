# NEBULA-QUANT v1 | nq_guardrails config — safe defaults, engine honors runtime overrides

# Max drawdown (fraction of equity/peak) before BLOCK. 0.10 = 10%.
MAX_DRAWDOWN_LIMIT: float = 0.10

# Max daily loss (fraction or absolute; interpretation by rule) before BLOCK. 0.05 = 5%.
DAILY_LOSS_LIMIT: float = 0.05

# Volatility threshold: above this → WARN; above EXTREME → BLOCK.
VOLATILITY_THRESHOLD: float = 50.0
EXTREME_VOLATILITY_THRESHOLD: float = 100.0

# Max open positions before blocking new trades.
MAX_OPEN_POSITIONS: int = 20
