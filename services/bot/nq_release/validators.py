# NEBULA-QUANT v1 | nq_release — deterministic release validation rules

from __future__ import annotations

from typing import Any

from nq_release.models import (
    ReleaseBlocker,
    ReleaseEvidence,
    ReleaseModuleRecord,
    ReleaseValidationStatus,
)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _ensure_list(val: Any, name: str) -> list[Any]:
    if val is None:
        return []
    if not isinstance(val, list):
        raise TypeError(f"{name} must be a list")
    return list(val)


def validate_module_records(
    module_records: list[Any],
    evidence_id_prefix: str,
    blocker_id_prefix: str,
    require_included_implemented: bool = True,
    require_included_integrated: bool = False,
) -> tuple[list[ReleaseBlocker], list[ReleaseEvidence]]:
    """
    Validate module records. Produce blockers when included modules are not implemented
    or validation_status is fail. Produce evidence for each module checked.
    Does not mutate inputs. Returns (blockers, evidence).
    """
    blockers: list[ReleaseBlocker] = []
    evidence: list[ReleaseEvidence] = []
    ev_idx = [0]
    blk_idx = [0]

    def add_ev(category: str, value: Any, description: str) -> str:
        eid = f"{evidence_id_prefix}-{ev_idx[0]}"
        ev_idx[0] += 1
        evidence.append(ReleaseEvidence(evidence_id=eid, category=category, value=value, description=description, metadata={}))
        return eid

    def add_blocker(category: str, severity: str, title: str, description: str, related_module: str | None) -> str:
        bid = f"{blocker_id_prefix}-{blk_idx[0]}"
        blk_idx[0] += 1
        blockers.append(ReleaseBlocker(
            blocker_id=bid,
            category=category,
            severity=severity,
            title=title,
            description=description,
            related_module=related_module,
            metadata={},
        ))
        return bid

    for rec in module_records:
        name = _get(rec, "module_name") or _get(rec, "module")
        if not name:
            continue
        name = str(name).strip()
        included = bool(_get(rec, "included", False))
        implemented = bool(_get(rec, "implemented", False))
        integrated = bool(_get(rec, "integrated", False))
        val_status = _get(rec, "validation_status")
        if val_status is not None:
            val_status = str(val_status).strip().lower()
        else:
            val_status = ReleaseValidationStatus.NOT_EVALUATED.value

        add_ev("module_record", name, f"Module {name}: included={included}, implemented={implemented}, integrated={integrated}, validation={val_status}")

        if not included:
            continue

        if require_included_implemented and not implemented:
            add_blocker(
                "module_not_implemented",
                "CRITICAL",
                f"Module {name} not implemented",
                f"Included module {name} is not marked as implemented.",
                name,
            )
        if require_included_integrated and not integrated:
            add_blocker(
                "module_not_integrated",
                "WARNING",
                f"Module {name} not integrated",
                f"Included module {name} is not marked as integrated.",
                name,
            )
        if val_status == ReleaseValidationStatus.FAIL.value:
            add_blocker(
                "module_validation_failed",
                "CRITICAL",
                f"Module {name} validation failed",
                f"Included module {name} has validation status fail.",
                name,
            )

    return blockers, evidence


def validate_gates(
    architecture_gate: Any,
    qa_gate: Any,
    evidence_id_prefix: str,
    blocker_id_prefix: str,
    blk_start_idx: int,
) -> tuple[list[ReleaseBlocker], list[ReleaseEvidence]]:
    """
    Validate architecture and QA gate. If either is explicitly False, add CRITICAL blocker.
    Returns (blockers, evidence).
    """
    blockers = []
    evidence = []
    ev_idx = [0]
    blk_idx = [blk_start_idx]

    def add_ev(category: str, value: Any, description: str) -> str:
        eid = f"{evidence_id_prefix}-{ev_idx[0]}"
        ev_idx[0] += 1
        evidence.append(ReleaseEvidence(evidence_id=eid, category=category, value=value, description=description, metadata={}))
        return eid

    def add_blocker(category: str, title: str, description: str) -> str:
        bid = f"{blocker_id_prefix}-{blk_idx[0]}"
        blk_idx[0] += 1
        blockers.append(ReleaseBlocker(
            blocker_id=bid,
            category=category,
            severity="CRITICAL",
            title=title,
            description=description,
            related_module=None,
            metadata={},
        ))
        return bid

    arch_ok = architecture_gate if isinstance(architecture_gate, bool) else _get(architecture_gate, "pass", architecture_gate)
    qa_ok = qa_gate if isinstance(qa_gate, bool) else _get(qa_gate, "pass", qa_gate)

    add_ev("architecture_gate", arch_ok, "Architecture gate result")
    add_ev("qa_gate", qa_ok, "QA gate result")

    if architecture_gate is not None and arch_ok is False:
        add_blocker("architecture_gate_failed", "Architecture gate failed", "Release blocked: architecture gate did not pass.")
    if qa_gate is not None and qa_ok is False:
        add_blocker("qa_gate_failed", "QA gate failed", "Release blocked: QA gate did not pass.")

    return blockers, evidence
