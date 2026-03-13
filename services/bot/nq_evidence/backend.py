"""
Evidence backbone: DB and filesystem helpers for phase execution, artifacts, and reports.
Call from repo root with services/bot on PYTHONPATH (or from scripts after path setup).
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path


def _dsn() -> str:
    return os.getenv("PG_DSN", "postgresql://nebula:nebula123@localhost:5432/trading")


def _artifacts_root() -> Path:
    root = os.getenv("NQ_REPO_ROOT")
    if root:
        return Path(root)
    return Path(__file__).resolve().parents[3] / ".." / "artifacts"


def _resolve_artifacts() -> Path:
    p = _artifacts_root().resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def ensure_artifacts_structure() -> Path:
    """Create artifacts/ subdirs per spec; return artifacts root."""
    root = _resolve_artifacts()
    for sub in ("phases", "tests", "audits", "backtests", "walkforward", "paper-trading", "frontend-review", "releases"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    return root


def register_phase_start(phase: str, details: str | None = None) -> str:
    """Insert phase_execution_log row; return log id (uuid)."""
    import psycopg
    log_id = str(uuid.uuid4())
    dsn = _dsn()
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO phase_execution_log (id, phase, status, details)
                VALUES (%s, %s, 'running', %s)
                """,
                (log_id, phase, details),
            )
        conn.commit()
    return log_id


def register_phase_end(log_id: str, status: str = "completed", details: str | None = None) -> None:
    """Update phase_execution_log with ended_at and status."""
    import psycopg
    from datetime import datetime
    dsn = _dsn()
    now = datetime.utcnow()
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE phase_execution_log
                   SET ended_at = %s, status = %s, details = COALESCE(%s, details)
                 WHERE id = %s
                """,
                (now, status, details, log_id),
            )
        conn.commit()


def register_artifact(phase: str, artifact_path: str, artifact_kind: str = "file") -> None:
    """Insert artifact_registry row."""
    import psycopg
    dsn = _dsn()
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO artifact_registry (phase, artifact_path, artifact_kind)
                VALUES (%s, %s, %s)
                """,
                (phase, artifact_path, artifact_kind),
            )
        conn.commit()


def write_manifest(phase: str, manifest: dict) -> str:
    """Write phase_XX_artifact_manifest.json under artifacts/phases/; return path."""
    ensure_artifacts_structure()
    path = _resolve_artifacts() / "phases" / f"phase_{phase}_artifact_manifest.json"
    path.write_text(json.dumps(manifest, indent=2))
    return str(path)


def write_html_report(phase: str, report_type: str, html: str) -> str:
    """Write phase_XX_<type>.html under artifacts/tests/ or artifacts/audits/; return path."""
    ensure_artifacts_structure()
    root = _resolve_artifacts()
    if report_type == "test":
        path = root / "tests" / f"phase_{phase}_test_report.html"
    elif report_type == "audit":
        path = root / "audits" / f"phase_{phase}_audit_report.html"
    else:
        path = root / "phases" / f"phase_{phase}_{report_type}.html"
    path.write_text(html)
    return str(path)
