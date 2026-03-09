# NEBULA-QUANT v1 | nq_strategy engine

from typing import Any

from nq_strategy.strategy import Strategy
from nq_strategy.signals import Signal
from nq_strategy.exceptions import EngineError


class StrategyEngine:
    """Runs a strategy: receives strategy, executes on_bar() per bar."""

    def __init__(self, strategy: Strategy) -> None:
        self._strategy = strategy

    def on_bar(self, bar: Any) -> Signal:
        """Execute strategy on one bar; return signal."""
        try:
            return self._strategy.on_bar(bar)
        except Exception as e:
            raise EngineError(f"Strategy on_bar failed: {e}") from e
