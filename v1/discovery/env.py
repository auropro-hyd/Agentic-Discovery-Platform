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


# The literal placeholder shipped in .env.example — a freshly-copied .env still has this, and it is
# NOT a usable credential. Treat it as "missing" so a first run fails the preflight cleanly instead
# of handing a bogus key to the SDK.
_ANTHROPIC_PLACEHOLDER = "sk-ant-..."


def missing_credentials(provider: str | None = None) -> list[str]:
    """Return the env vars the given provider needs but does not have (empty list == ready to call).

    Mirrors scripts/doctor.py so the preflight and the doctor agree. The Anthropic placeholder from
    .env.example counts as missing. Does NOT make a network call — presence only.
    """
    provider = (provider or os.environ.get("DISCOVERY_PROVIDER", "anthropic")).lower()
    if provider == "azure":
        required = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY",
                    "AZURE_OPENAI_DEPLOYMENT", "AZURE_OPENAI_API_VERSION"]
        return [v for v in required if not os.environ.get(v)]
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    return [] if key and key != _ANTHROPIC_PLACEHOLDER else ["ANTHROPIC_API_KEY"]


def credentials_present(provider: str | None = None) -> bool:
    """True when the selected provider has all the env vars it needs to make a live call."""
    return not missing_credentials(provider)
