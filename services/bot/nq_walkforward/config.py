# NEBULA-QUANT v1 | nq_walkforward config — safe defaults

# Window sizes (number of bars per train and per test segment)
DEFAULT_TRAIN_WINDOWS: int = 20
DEFAULT_TEST_WINDOWS: int = 5

# Minimum fraction of windows that must pass for portfolio-level pass (0.0–1.0)
DEFAULT_MIN_PASS_RATE: float = 0.5

# Per-window pass/fail thresholds (conservative placeholders)
DEFAULT_MIN_TEST_TRADES: int = 1
DEFAULT_MIN_TEST_NET_PNL: float = -1e9  # allow any net pnl unless strongly negative
DEFAULT_MAX_TEST_DRAWDOWN: float = 1e12  # max allowed test drawdown (absolute); large = permissive

# Catastrophic divergence: if train is profitable, test must not lose more than this multiple of train profit
DEFAULT_MAX_TEST_TRAIN_DIVERGENCE: float = 0.5  # fail if test_net_pnl < -divergence * max(0, train_net_pnl)
