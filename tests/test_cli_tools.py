from __future__ import annotations

import io
import pathlib
import sys
import unittest
from contextlib import redirect_stdout


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"


def _configure_path() -> None:
    services_bot = ROOT / "services" / "bot"
    if str(services_bot) not in sys.path:
        sys.path.insert(0, str(services_bot))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))


class TestCLITools(unittest.TestCase):
    def setUp(self) -> None:
        _configure_path()

    def test_generate_system_report_runs(self) -> None:
        from scripts import generate_system_report

        buf = io.StringIO()
        with redirect_stdout(buf):
            generate_system_report.main()
        out = buf.getvalue()
        self.assertIn("SYSTEM STATUS", out)
        self.assertIn("CRITICAL INCIDENTS", out)
        self.assertIn("RECOMMENDED RUNBOOKS", out)
        self.assertIn("RELEASE STATUS", out)

    def test_evaluate_system_health_runs(self) -> None:
        from scripts import evaluate_system_health

        buf = io.StringIO()
        with redirect_stdout(buf):
            evaluate_system_health.main()
        out = buf.getvalue()
        self.assertIn("OVERALL STATUS", out)
        self.assertIn("INCIDENT COUNT", out)
        self.assertIn("CRITICAL INCIDENTS", out)

    def test_release_check_returns_status(self) -> None:
        from scripts import release_check

        buf = io.StringIO()
        with redirect_stdout(buf):
            release_check.main()
        out = buf.getvalue()
        self.assertIn("RELEASE STATUS", out)
        # Status should be one of the known release statuses (case-insensitive)
        lines = [line.strip().upper() for line in out.splitlines()]
        self.assertTrue(
            any(line in {"APPROVED", "READY", "BLOCKED", "REJECTED", "DRAFT"} for line in lines),
            msg=f"Unexpected release status output: {out!r}",
        )


if __name__ == "__main__":
    unittest.main()

