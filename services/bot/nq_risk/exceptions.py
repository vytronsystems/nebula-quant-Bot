# NEBULA-QUANT v1 | nq_risk exceptions


class RiskError(Exception):
    """Base for nq_risk errors."""


class RiskEngineError(RiskError):
    """Risk engine runtime error."""


class RiskLimitError(RiskError):
    """Limit check or policy violation."""
