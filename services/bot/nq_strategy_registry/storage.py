# NEBULA-QUANT v1 | nq_strategy_registry storage (in-memory placeholder, no DB)

from typing import Any

from nq_strategy_registry.models import StrategyDefinition

# Module-level in-memory store (skeleton). No persistence.
_registry: dict[str, StrategyDefinition] = {}


def add_strategy(definition: StrategyDefinition) -> None:
    """Store strategy by strategy_id. In-memory only."""
    _registry[definition.strategy_id] = definition


def update_strategy(definition: StrategyDefinition) -> None:
    """Overwrite existing strategy by strategy_id. In-memory only."""
    _registry[definition.strategy_id] = definition


def get_strategy_by_id(strategy_id: str) -> StrategyDefinition | None:
    """Return strategy by id or None if not found."""
    return _registry.get(strategy_id)


def list_all_strategies() -> list[StrategyDefinition]:
    """Return all stored strategies."""
    return list(_registry.values())
