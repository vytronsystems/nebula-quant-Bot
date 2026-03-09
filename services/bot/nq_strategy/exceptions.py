# NEBULA-QUANT v1 | nq_strategy exceptions


class StrategyError(Exception):
    """Base for nq_strategy errors."""


class EngineError(StrategyError):
    """Strategy engine runtime error."""
