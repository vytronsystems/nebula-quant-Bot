# NEBULA-QUANT v1 | nq_strategy_registry models

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StrategyDefinition:
    """Single strategy definition (skeleton). Aligned with docs/12_STRATEGY_REGISTRY_STANDARD.md."""

    strategy_id: str
    name: str
    version: str
    status: str
    market: str
    instrument_type: str
    timeframe: str
    regime_target: str
    risk_profile: str
    hypothesis: str
    activation_rules: dict[str, Any]
    deactivation_rules: dict[str, Any]
    owner: str
    created_at: float
    updated_at: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyRegistryResult:
    """Aggregate registry result (skeleton)."""

    strategies: list[StrategyDefinition]
    total_strategies: int
    active_strategies: int
    disabled_strategies: int
    metadata: dict[str, Any] = field(default_factory=dict)
