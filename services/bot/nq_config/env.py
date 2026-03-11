# NEBULA-QUANT v1 | nq_config environment variable parsing

from __future__ import annotations

import os

from nq_config.models import ConfigError

# Deterministic boolean: only these values accepted. Case-insensitive.
_TRUTHY = frozenset({"true", "1", "yes", "on"})
_FALSY = frozenset({"false", "0", "no", "off"})


def get_env(key: str, default: str | None = None) -> str | None:
    """Return os.environ.get(key, default). No validation."""
    return os.environ.get(key, default)


def parse_bool(value: str | None, default: bool | None = None) -> bool:
    """
    Parse string to bool deterministically.
    Accepts (case-insensitive): true/1/yes/on -> True; false/0/no/off -> False.
    If value is None or empty, returns default; if default is None, raises ConfigError.
    """
    if value is None or not value.strip():
        if default is None:
            raise ConfigError("boolean env value required but got empty")
        return default
    v = value.strip().lower()
    if v in _TRUTHY:
        return True
    if v in _FALSY:
        return False
    raise ConfigError(f"invalid boolean env value: {value!r} (expected true/false/1/0/yes/no/on/off)")


def parse_float(value: str | None, default: float | None = None, min_val: float | None = None, max_val: float | None = None) -> float:
    """Parse string to float. Invalid or out-of-range raises ConfigError."""
    if value is None or not value.strip():
        if default is None:
            raise ConfigError("float env value required but got empty")
        return default
    try:
        x = float(value.strip())
    except ValueError as e:
        raise ConfigError(f"invalid float env value: {value!r}") from e
    if min_val is not None and x < min_val:
        raise ConfigError(f"float env value {x} below minimum {min_val}")
    if max_val is not None and x > max_val:
        raise ConfigError(f"float env value {x} above maximum {max_val}")
    return x


def parse_int(value: str | None, default: int | None = None, min_val: int | None = None, max_val: int | None = None) -> int:
    """Parse string to int. Invalid or out-of-range raises ConfigError."""
    if value is None or not value.strip():
        if default is None:
            raise ConfigError("int env value required but got empty")
        return default
    try:
        x = int(value.strip())
    except ValueError as e:
        raise ConfigError(f"invalid int env value: {value!r}") from e
    if min_val is not None and x < min_val:
        raise ConfigError(f"int env value {x} below minimum {min_val}")
    if max_val is not None and x > max_val:
        raise ConfigError(f"int env value {x} above maximum {max_val}")
    return x


def parse_float_optional(value: str | None) -> float | None:
    """Parse string to float or None if empty. Invalid numeric string raises ConfigError."""
    if value is None or not value.strip():
        return None
    try:
        return float(value.strip())
    except ValueError as e:
        raise ConfigError(f"invalid float env value: {value!r}") from e


def parse_int_optional(value: str | None) -> int | None:
    """Parse string to int or None if empty. Invalid numeric string raises ConfigError."""
    if value is None or not value.strip():
        return None
    try:
        return int(value.strip())
    except ValueError as e:
        raise ConfigError(f"invalid int env value: {value!r}") from e
