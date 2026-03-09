import os
import time
import random
from typing import Callable, TypeVar

T = TypeVar("T")

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default

def retry(fn: Callable[[], T], *, name: str = "op") -> T:
    """
    Exponential backoff con jitter.
    Env vars:
      RETRY_MAX_ATTEMPTS (default 12)
      RETRY_BASE_SECONDS (default 0.5)
      RETRY_MAX_SLEEP_SECONDS (default 10)
    """
    max_attempts = _env_int("RETRY_MAX_ATTEMPTS", 12)
    base = float(os.getenv("RETRY_BASE_SECONDS", "0.5"))
    max_sleep = float(os.getenv("RETRY_MAX_SLEEP_SECONDS", "10"))

    last_err = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as e:
            last_err = e
            sleep = min(max_sleep, base * (2 ** (attempt - 1)))
            sleep = sleep * (0.7 + random.random() * 0.6)  # jitter 0.7x..1.3x
            time.sleep(sleep)

    # si llegamos aquí, falló todo
    raise last_err
