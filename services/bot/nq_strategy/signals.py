# NEBULA-QUANT v1 | nq_strategy signals

from enum import Enum


class Signal(str, Enum):
    LONG = "long"
    SHORT = "short"
    EXIT = "exit"
    HOLD = "hold"
