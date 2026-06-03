"""Tiny .env loader (no dependency). Reads v1/.env into os.environ if present.

Existing environment variables win over .env (so you can override per-run). Lines are KEY=VALUE;
blank lines and # comments ignored; surrounding quotes stripped.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_env(path: Path | None = None) -> None:
    path = path or (ROOT / ".env")
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:   # don't clobber an explicit export
            os.environ[key] = value
