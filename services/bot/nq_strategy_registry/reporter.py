# NEBULA-QUANT v1 | nq_strategy_registry reporter

from typing import Any

from nq_strategy_registry.models import StrategyRegistryResult


def build_strategy_registry_report(result: StrategyRegistryResult) -> dict[str, Any]:
    """Build dictionary for dashboards and governance review. Skeleton only."""
    return {
        "total_strategies": result.total_strategies,
        "active_strategies": result.active_strategies,
        "disabled_strategies": result.disabled_strategies,
        "strategies": [
            {
                "strategy_id": s.strategy_id,
                "name": s.name,
                "version": s.version,
                "status": s.status,
                "market": s.market,
                "timeframe": s.timeframe,
                "owner": s.owner,
            }
            for s in result.strategies
        ],
        "metadata": result.metadata,
    }
