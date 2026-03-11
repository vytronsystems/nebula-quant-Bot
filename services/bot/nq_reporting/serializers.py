# NEBULA-QUANT v1 | nq_reporting serializers

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from nq_reporting.models import SystemReport


def report_to_dict(report: SystemReport) -> dict[str, Any]:
    """
    Convert SystemReport to a JSON-serializable dict. Deterministic and stable key order.
    Does not include runtime-only objects.
    """
    return asdict(report)


def report_to_json(report: SystemReport, sort_keys: bool = True, indent: int | None = None) -> str:
    """
    Serialize SystemReport to JSON string. Deterministic output when sort_keys=True (default).
    """
    d = report_to_dict(report)
    return json.dumps(d, sort_keys=sort_keys, indent=indent, default=str)
