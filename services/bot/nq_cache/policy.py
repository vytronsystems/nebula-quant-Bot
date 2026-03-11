# NEBULA-QUANT v1 | nq_cache policy

from __future__ import annotations

from nq_cache.models import CachePolicy


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


DEFAULT_CACHE_POLICY = default_policy()
