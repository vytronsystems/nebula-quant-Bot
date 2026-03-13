# NEBULA-QUANT | Instrument registry and activation control

from nq_instrument_registry.models import ActivationLogEntry, InstrumentRecord

__all__ = [
    "InstrumentRecord",
    "ActivationLogEntry",
    "InstrumentRegistryService",
]


def __getattr__(name: str):  # lazy import for service (requires psycopg)
    if name == "InstrumentRegistryService":
        from nq_instrument_registry.service import InstrumentRegistryService
        return InstrumentRegistryService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
