#!/usr/bin/env python3
"""
NEBULA-QUANT v1 | Operational CLI

generate_system_report.py

Generate a full operational SystemReport by wiring:
  nq_sre → nq_runbooks → nq_release → nq_reporting.

This script is deterministic for the same inputs, does not call external
services, and only prints a human-readable summary.
"""

from __future__ import annotations

import pathlib
import sys


def _configure_path() -> None:
    # Ensure services/bot is on sys.path so `nq_*` packages can be imported.
    root = pathlib.Path(__file__).resolve().parents[1]
    services_bot = root / "services" / "bot"
    if str(services_bot) not in sys.path:
        sys.path.insert(0, str(services_bot))


def main() -> None:
    _configure_path()

    from nq_reporting.system_report import generate_system_report

    # For now we use empty/default inputs; future versions can accept JSON/CLI args.
    sre_inputs: list[object] = []
    incidents: list[object] | None = None
    module_records: list[object] = []

    report = generate_system_report(
        sre_inputs=sre_inputs,
        incidents=incidents,
        module_records=module_records,
        architecture_gate=True,
        qa_gate=True,
    )

    summary = report.summary or {}
    system_status = summary.get("system_status", "unknown")
    critical_incidents = summary.get("critical_incidents", 0)
    recommended_runbooks = summary.get("recommended_runbooks", []) or []
    release_status = summary.get("release_status", "unknown")

    print("SYSTEM STATUS")
    print(system_status)
    print()

    print("CRITICAL INCIDENTS")
    print(critical_incidents)
    print()

    print("RECOMMENDED RUNBOOKS")
    if recommended_runbooks:
        print(", ".join(str(r) for r in recommended_runbooks))
    else:
        print("none")
    print()

    print("RELEASE STATUS")
    print(release_status)


if __name__ == "__main__":
    main()

