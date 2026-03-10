# NEBULA-QUANT v1 | nq_promotion config — conservative default thresholds

# Backtest: minimum evidence to promote backtest -> walkforward
MIN_BACKTEST_TRADES: int = 30
MIN_BACKTEST_WIN_RATE: float = 0.45
MIN_BACKTEST_PROFIT_FACTOR: float = 1.0
MAX_BACKTEST_DRAWDOWN: float = 0.20  # fraction; 20% max

# Walk-forward: minimum to promote walkforward -> paper
MIN_WALKFORWARD_PASS_RATE: float = 0.5

# Paper: minimum to promote paper -> live
MIN_PAPER_TRADES: int = 20
MIN_PAPER_WIN_RATE: float = 0.45
MAX_PAPER_DRAWDOWN: float = 0.15  # fraction

# Live: guardrails must be clear (allowed=True)
ALLOW_LIVE_ONLY_IF_GUARDRAILS_CLEAR: bool = True
