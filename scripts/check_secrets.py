#!/usr/bin/env python3
"""
NEBULA-QUANT | Secret validation check.
Scans repo for high-risk patterns (hardcoded tokens, passwords). Exit 0 if clean, 1 if hits.
Run from repo root; used by CI or pre-commit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "artifacts"}
EXCLUDE_SUFFIXES = (".bak", ".bak.", ".bak.2026")  # backup files not used at runtime
# Patterns that indicate likely hardcoded secrets (not env var names)
PATTERNS = [
    (re.compile(r"bot_token:\s*[\"'][0-9]{8,}:[A-Za-z0-9_-]{30,}[\"']"), "Telegram bot_token with token value"),
    (re.compile(r"chat_id:\s*[0-9]{6,}"), "Telegram chat_id numeric (use env)"),
    (re.compile(r"POSTGRES_PASSWORD:\s*[^$\s}\-]+", re.M), "POSTGRES_PASSWORD hardcoded (use ${VAR:-default})"),
    (re.compile(r"api[_-]?key\s*=\s*[\"'][^\"']{20,}[\"']", re.I), "API key literal"),
]
# Files we allow to document or example (e.g. .env.example)
ALLOW_FILES = {".env.example", "check_secrets.py", "phase_execution_log.jsonl"}


def main() -> int:
    hits: list[tuple[str, int, str]] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.name in ALLOW_FILES:
            continue
        if path.name.endswith(EXCLUDE_SUFFIXES) or ".bak." in path.name:
            continue
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue
        for pattern, desc in PATTERNS:
            for m in pattern.finditer(text):
                hits.append((str(rel), text[: m.start()].count("\n") + 1, desc))
    if not hits:
        print("OK: no hardcoded secret patterns found.")
        return 0
    print("SECRET CHECK FAILED: possible hardcoded secrets:", file=sys.stderr)
    for path, line, desc in hits:
        print(f"  {path}:{line} — {desc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
