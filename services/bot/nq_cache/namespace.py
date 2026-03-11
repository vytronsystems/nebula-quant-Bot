# NEBULA-QUANT v1 | nq_cache namespace constants

from __future__ import annotations

DEFAULT_NAMESPACE = "default"
NAMESPACE_STRATEGY_REGISTRY = "strategy_registry"
NAMESPACE_OBSERVABILITY = "observability"
NAMESPACE_RISK = "risk"
NAMESPACE_PORTFOLIO = "portfolio"
NAMESPACE_SYSTEM = "system"

NAMESPACES: frozenset[str] = frozenset({
    DEFAULT_NAMESPACE,
    NAMESPACE_STRATEGY_REGISTRY,
    NAMESPACE_OBSERVABILITY,
    NAMESPACE_RISK,
    NAMESPACE_PORTFOLIO,
    NAMESPACE_SYSTEM,
})
