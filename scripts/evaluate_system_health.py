#!/usr/bin/env python3
"""
NEBULA-QUANT v1 | Operational CLI

evaluate_system_health.py

Run SRE reliability evaluation independently and print a simple summary:
  overall_status
  incident_count
  critical_incidents
"""

from __future__ import annotations

import pathlib
import sys


def _configure_path() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    services_bot = root / "services" / "bot"
    if str(services_bot) not in sys.path:
        sys.path.insert(0, str(services_bot))


def main() -> None:
    _configure_path()

    from nq_sre import SREEngine

    sre_engine = SREEngine()
    sre_report = sre_engine.evaluate_reliability([])

    overall_status = getattr(sre_report, "overall_status", "unknown")
    incidents = sre_report.incidents or []
    incident_count = len(incidents)
    critical_incidents = sum(
        1 for inc in incidents if getattr(inc, "severity", "").lower() == "critical"
    )

    print("OVERALL STATUS")
    print(overall_status)
    print()

    print("INCIDENT COUNT")
    print(incident_count)
    print()

    print("CRITICAL INCIDENTS")
    print(critical_incidents)


if __name__ == "__main__":
    main()

