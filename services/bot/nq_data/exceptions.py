# NEBULA-QUANT v1 | nq_data exceptions

class DataError(Exception):
    """Base for nq_data errors."""


class ProviderError(DataError):
    """Provider fetch or configuration error."""


class NormalizationError(DataError):
    """Raw data could not be normalized to canonical format."""
