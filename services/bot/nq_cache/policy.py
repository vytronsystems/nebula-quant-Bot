# NEBULA-QUANT v1 | nq_cache policy

from __future__ import annotations

from typing import Protocol

from nq_cache.models import CachePolicy


class CacheModuleConfigLike(Protocol):
    """Protocol for config with cache settings (e.g. nq_config.CacheModuleConfig)."""

    default_ttl_seconds: float | None
    max_entries: int | None
    allow_none_values: bool


def default_policy(
    default_ttl_seconds: float | None = None,
    max_entries: int | None = None,
    allow_none_values: bool = False,
) -> CachePolicy:
    """Build a cache policy with optional overrides."""
    return CachePolicy(
        default_ttl_seconds=default_ttl_seconds,
        max_entries=max_entries,
        allow_none_values=allow_none_values,
        namespace_defaults=None,
    )


def policy_from_config(config: CacheModuleConfigLike) -> CachePolicy:
    """Build CachePolicy from a config (e.g. AppConfig.cache from nq_config)."""
    return CachePolicy(
        default_ttl_seconds=config.default_ttl_seconds,
        max_entries=config.max_entries,
        allow_none_values=config.allow_none_values,
        namespace_defaults=None,
    )


DEFAULT_CACHE_POLICY = default_policy()
