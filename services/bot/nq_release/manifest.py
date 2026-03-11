# NEBULA-QUANT v1 | nq_release — deterministic manifest generation

from __future__ import annotations

from typing import Any

from nq_release.models import ReleaseModuleRecord, ReleaseManifest


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _normalize_record(rec: Any) -> ReleaseModuleRecord:
    """Convert dict or object to ReleaseModuleRecord. Does not mutate input."""
    name = _get(rec, "module_name") or _get(rec, "module") or ""
    name = str(name).strip()
    return ReleaseModuleRecord(
        module_name=name,
        included=bool(_get(rec, "included", False)),
        implemented=bool(_get(rec, "implemented", False)),
        integrated=bool(_get(rec, "integrated", False)),
        validation_status=str(_get(rec, "validation_status") or "not_evaluated").strip().lower(),
        metadata=_get(rec, "metadata") if isinstance(_get(rec, "metadata"), dict) else {},
    )


def build_release_manifest(
    manifest_id: str,
    release_name: str,
    version_label: str,
    module_records: list[Any],
    branch: str | None = None,
    commit_hash: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ReleaseManifest:
    """
    Build deterministic release manifest. Does not mutate inputs.
    Module ordering: sorted by module_name for stability.
    """
    records = [_normalize_record(r) for r in (module_records or []) if _get(r, "module_name") or _get(r, "module")]
    records.sort(key=lambda r: r.module_name)
    included_modules = sorted([r.module_name for r in records if r.included])
    return ReleaseManifest(
        manifest_id=manifest_id,
        release_name=release_name or "",
        version_label=version_label or "",
        branch=branch,
        commit_hash=commit_hash,
        included_modules=included_modules,
        module_records=records,
        metadata=metadata or {},
    )
