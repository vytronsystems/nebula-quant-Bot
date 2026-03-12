from __future__ import annotations

from itertools import product
from typing import Any

from nq_strategy_generation.models import StrategyFamily, StrategyParameterSet, StrategyTemplate


MAX_PARAMETER_SETS_PER_TEMPLATE = 16


def _cartesian_parameters(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    """Deterministic cartesian expansion with explicit cap."""
    keys = sorted(grid.keys())
    values = [list(grid[k]) for k in keys]
    combos: list[dict[str, Any]] = []
    for vals in product(*values):
        combos.append({k: v for k, v in zip(keys, vals)})
        if len(combos) >= MAX_PARAMETER_SETS_PER_TEMPLATE:
            break
    return combos


def _family_grid(family: str) -> dict[str, list[Any]]:
    """Return deterministic parameter grid for a strategy family."""
    fam = StrategyFamily(family)
    if fam == StrategyFamily.BREAKOUT:
        return {
            "lookback_bars": [10, 20, 30],
            "relvol_min": [1.2, 1.5],
            "stop_atr": [1.0, 1.5],
            "target_atr": [2.0, 2.5],
        }
    if fam == StrategyFamily.MOMENTUM_CONTINUATION:
        return {
            "lookback_bars": [20, 40],
            "momentum_threshold": [0.6, 0.8],
            "trail_atr": [1.0],
        }
    if fam == StrategyFamily.MEAN_REVERSION:
        return {
            "zscore_threshold": [1.5, 2.0],
            "stop_atr": [1.0],
            "target_to_mean": [True],
        }
    if fam == StrategyFamily.OPENING_RANGE_BREAKOUT:
        return {
            "opening_range_minutes": [15, 30],
            "range_filter_multiple": [0.5, 1.0],
        }
    if fam == StrategyFamily.PULLBACK_CONTINUATION:
        return {
            "pullback_depth_min": [0.2, 0.3],
            "pullback_depth_max": [0.4, 0.5],
        }
    # Other families can be added later with explicit grids.
    return {}


def expand_parameters_for_template(
    template: StrategyTemplate,
    *,
    max_sets: int | None = None,
) -> list[StrategyParameterSet]:
    """
    Deterministically expand a bounded set of parameters for a template.

    The combination count is capped globally by MAX_PARAMETER_SETS_PER_TEMPLATE
    and additionally by max_sets when provided.
    """
    grid = _family_grid(template.family)
    if not grid:
        return []
    combos = _cartesian_parameters(grid)
    if max_sets is not None:
        combos = combos[: max(0, int(max_sets))]
    params: list[StrategyParameterSet] = []
    for idx, combo in enumerate(combos):
        parameter_set_id = f"{template.template_id}-ps-{idx}"
        params.append(
            StrategyParameterSet(
                parameter_set_id=parameter_set_id,
                parameters=combo,
                metadata={"family": template.family},
            )
        )
    return params

