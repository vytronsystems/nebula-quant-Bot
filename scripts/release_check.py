#!/usr/bin/env python3
"""
NEBULA-QUANT v1 | Operational CLI

release_check.py

Evaluate release readiness using nq_release and print the decision status:
  APPROVED / READY / BLOCKED / REJECTED / DRAFT

This script uses a minimal default module_records list; future versions
may accept JSON or CLI arguments for richer scenarios.
"""

from __future__ import annotations

import pathlib
import sys
from typing import Any


def _configure_path() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    services_bot = root / "services" / "bot"
    if str(services_bot) not in sys.path:
        sys.path.insert(0, str(services_bot))


def _default_module_records() -> list[dict[str, Any]]:
    # Minimal, deterministic module record list consistent with tests.
    return [
        {
            "module_name": "nq_risk",
            "included": True,
            "implemented": True,
            "integrated": True,
            "validation_status": "pass",
        },
        {
            "module_name": "nq_guardrails",
            "included": True,
            "implemented": True,
            "integrated": True,
            "validation_status": "pass",
        },
    ]


def main() -> None:
    _configure_path()

    from nq_release import ReleaseEngine

    engine = ReleaseEngine()
    module_records = _default_module_records()

    report = engine.evaluate_release(
        release_name="operational",
        version_label="v1",
        module_records=module_records,
        architecture_gate=True,
        qa_gate=True,
    )

    status = report.decision.status

    print("RELEASE STATUS")
    print(status)


if __name__ == "__main__":
    main()

