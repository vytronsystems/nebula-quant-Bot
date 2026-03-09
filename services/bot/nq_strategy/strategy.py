# NEBULA-QUANT v1 | nq_strategy base

from abc import ABC, abstractmethod
from typing import Any

from nq_strategy.signals import Signal


class Strategy(ABC):
    """Base class for strategies. Engine calls on_bar(bar) for each bar."""

    @abstractmethod
    def on_bar(self, bar: Any) -> Signal:
        """Process one bar; return signal. Bar type will be nq_data.Bar when integrated."""
        ...
