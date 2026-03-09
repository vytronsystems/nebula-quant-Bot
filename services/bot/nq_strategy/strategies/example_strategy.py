# NEBULA-QUANT v1 | nq_strategy example (skeleton)

from typing import Any

from nq_strategy.strategy import Strategy
from nq_strategy.signals import Signal
from nq_strategy.rules import rule_momentum_bullish, rule_breakout_above, rule_trend_up


class ExampleStrategy(Strategy):
    """Example strategy using reusable rules. Skeleton: always HOLD."""

    def on_bar(self, bar: Any) -> Signal:
        # Stub: call rules for structure; no real logic
        rule_momentum_bullish(bar)
        rule_breakout_above(bar, 0.0)
        rule_trend_up(bar)
        return Signal.HOLD
