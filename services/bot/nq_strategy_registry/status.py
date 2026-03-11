# NEBULA-QUANT v1 | nq_strategy_registry status (lifecycle, aligned with 12_STRATEGY_REGISTRY_STANDARD.md)

# Lifecycle status constants per docs/12_STRATEGY_REGISTRY_STANDARD.md
STATUS_IDEA = "idea"
STATUS_RESEARCH = "research"
STATUS_BACKTEST = "backtest"
STATUS_WALKFORWARD = "walkforward"
STATUS_PAPER = "paper"
STATUS_LIVE = "live"
STATUS_DISABLED = "disabled"
STATUS_RETIRED = "retired"
STATUS_REJECTED = "rejected"

STRATEGY_STATUSES: tuple[str, ...] = (
    STATUS_IDEA,
    STATUS_RESEARCH,
    STATUS_BACKTEST,
    STATUS_WALKFORWARD,
    STATUS_PAPER,
    STATUS_LIVE,
    STATUS_DISABLED,
    STATUS_RETIRED,
    STATUS_REJECTED,
)

# Execution-compatible states only (paper, live)
EXECUTION_COMPATIBLE_STATUSES: frozenset[str] = frozenset({STATUS_PAPER, STATUS_LIVE})
