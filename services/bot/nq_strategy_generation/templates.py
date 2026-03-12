from __future__ import annotations

from typing import Any

from nq_strategy_generation.models import StrategyFamily, StrategyTemplate


def _base_template(
    template_id: str,
    family: StrategyFamily,
    title: str,
    description: str,
    regime_constraints: list[str],
    entry_conditions: dict[str, Any],
    exit_conditions: dict[str, Any],
    stop_loss_rule: dict[str, Any],
    take_profit_rule: dict[str, Any],
    sizing_rule: dict[str, Any],
) -> StrategyTemplate:
    return StrategyTemplate(
        template_id=template_id,
        family=family.value,
        title=title,
        description=description,
        regime_constraints=list(regime_constraints),
        entry_conditions=dict(entry_conditions),
        exit_conditions=dict(exit_conditions),
        stop_loss_rule=dict(stop_loss_rule),
        take_profit_rule=dict(take_profit_rule),
        sizing_rule=dict(sizing_rule),
        metadata={},
    )


def breakout_template() -> StrategyTemplate:
    """Deterministic breakout template."""
    return _base_template(
        template_id="tpl-breakout",
        family=StrategyFamily.BREAKOUT,
        title="Price/Volume Breakout",
        description="Enter in direction of breakout when price exceeds recent high with elevated relative volume.",
        regime_constraints=["TRENDING_UP", "TRENDING_DOWN", "HIGH_VOLATILITY"],
        entry_conditions={
            "breakout_signal": True,
            "relative_volume_min": 1.2,
        },
        exit_conditions={
            "trail_stop": True,
            "time_exit_bars": 40,
        },
        stop_loss_rule={
            "type": "atr_multiple",
            "atr_multiple": 1.0,
        },
        take_profit_rule={
            "type": "atr_multiple",
            "atr_multiple": 2.0,
        },
        sizing_rule={
            "type": "risk_fraction",
            "risk_fraction": 0.01,
        },
    )


def momentum_continuation_template() -> StrategyTemplate:
    """Deterministic momentum continuation template."""
    return _base_template(
        template_id="tpl-momo-cont",
        family=StrategyFamily.MOMENTUM_CONTINUATION,
        title="Trend Momentum Continuation",
        description="Enter in direction of prevailing trend when momentum and trend strength are aligned.",
        regime_constraints=["TRENDING_UP", "TRENDING_DOWN", "LOW_VOLATILITY"],
        entry_conditions={
            "trend_strength_min": 0.6,
            "momentum_score_min": 0.6,
        },
        exit_conditions={
            "momentum_fades_below": 0.3,
            "trend_reversal_signal": True,
        },
        stop_loss_rule={
            "type": "atr_multiple",
            "atr_multiple": 1.0,
        },
        take_profit_rule={
            "type": "rr_multiple",
            "reward_risk": 2.0,
        },
        sizing_rule={
            "type": "volatility_scaled",
            "target_volatility": 0.15,
        },
    )


def mean_reversion_template() -> StrategyTemplate:
    """Deterministic mean reversion template."""
    return _base_template(
        template_id="tpl-mean-rev",
        family=StrategyFamily.MEAN_REVERSION,
        title="Range-Bound Mean Reversion",
        description="Fade extremes back toward mean when deviation and volatility are within range-bound regime.",
        regime_constraints=["RANGE_BOUND", "LOW_VOLATILITY"],
        entry_conditions={
            "mean_reversion_distance_min": 1.5,
            "volatility_percentile_max": 0.7,
        },
        exit_conditions={
            "revert_to_mean": True,
            "time_exit_bars": 20,
        },
        stop_loss_rule={
            "type": "atr_multiple",
            "atr_multiple": 1.0,
        },
        take_profit_rule={
            "type": "mean_reversion",
            "target_to_mean": True,
        },
        sizing_rule={
            "type": "fixed_fraction",
            "fraction": 0.01,
        },
    )


def opening_range_breakout_template() -> StrategyTemplate:
    """Deterministic opening range breakout template."""
    return _base_template(
        template_id="tpl-orb",
        family=StrategyFamily.OPENING_RANGE_BREAKOUT,
        title="Opening Range Breakout",
        description="Trade breakouts of the opening range when session bias and volume confirm direction.",
        regime_constraints=["TRENDING_UP", "TRENDING_DOWN", "HIGH_VOLATILITY"],
        entry_conditions={
            "session_bias_present": True,
            "opening_range_breakout": True,
            "relative_volume_min": 1.5,
        },
        exit_conditions={
            "time_exit_bars": 10,
        },
        stop_loss_rule={
            "type": "range_fraction",
            "range_fraction": 0.5,
        },
        take_profit_rule={
            "type": "range_multiple",
            "range_multiple": 1.5,
        },
        sizing_rule={
            "type": "intraday_fixed",
            "fraction": 0.005,
        },
    )


def pullback_continuation_template() -> StrategyTemplate:
    """Deterministic pullback continuation template."""
    return _base_template(
        template_id="tpl-pullback-cont",
        family=StrategyFamily.PULLBACK_CONTINUATION,
        title="Trend Pullback Continuation",
        description="Enter in trend direction on controlled pullbacks that reset momentum without breaking structure.",
        regime_constraints=["TRENDING_UP", "TRENDING_DOWN"],
        entry_conditions={
            "trend_strength_min": 0.5,
            "pullback_depth_min": 0.2,
            "pullback_depth_max": 0.5,
        },
        exit_conditions={
            "trend_exhaustion": True,
            "time_exit_bars": 30,
        },
        stop_loss_rule={
            "type": "swing_low_high",
            "buffer_atr": 0.5,
        },
        take_profit_rule={
            "type": "rr_multiple",
            "reward_risk": 2.0,
        },
        sizing_rule={
            "type": "risk_fraction",
            "risk_fraction": 0.01,
        },
    )


def build_all_templates() -> list[StrategyTemplate]:
    """Return all static templates in deterministic order."""
    return [
        breakout_template(),
        momentum_continuation_template(),
        mean_reversion_template(),
        opening_range_breakout_template(),
        pullback_continuation_template(),
    ]

