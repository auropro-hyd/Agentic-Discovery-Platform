"""Coverage for discovery/env.py credential preflight (missing_credentials / credentials_present).

env.py is omitted from the coverage gate (IO glue), but this preflight is the thing that turns a
keyless first run from a stack trace / misleading 'use golden' message into one clear line — so it
is worth guarding directly. All offline; env is isolated per-test via monkeypatch.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import env  # noqa: E402

_ALL_CRED_VARS = [
    "DISCOVERY_PROVIDER", "ANTHROPIC_API_KEY",
    "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_DEPLOYMENT", "AZURE_OPENAI_API_VERSION",
]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Start every test from a known-empty credential environment."""
    for v in _ALL_CRED_VARS:
        monkeypatch.delenv(v, raising=False)


def test_anthropic_missing_when_unset():
    assert env.missing_credentials("anthropic") == ["ANTHROPIC_API_KEY"]
    assert env.credentials_present("anthropic") is False


def test_anthropic_placeholder_counts_as_missing(monkeypatch):
    # the literal value shipped in .env.example must NOT pass — a freshly-copied .env has it
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-...")
    assert env.missing_credentials("anthropic") == ["ANTHROPIC_API_KEY"]
    assert env.credentials_present("anthropic") is False


def test_anthropic_real_key_passes(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-real-looking-value")
    assert env.missing_credentials("anthropic") == []
    assert env.credentials_present("anthropic") is True


def test_azure_requires_all_four(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "abc")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://x.openai.azure.com")
    # deployment + version still missing
    missing = env.missing_credentials("azure")
    assert "AZURE_OPENAI_DEPLOYMENT" in missing
    assert "AZURE_OPENAI_API_VERSION" in missing
    assert env.credentials_present("azure") is False


def test_azure_full_set_passes(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "abc")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://x.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "my-deployment")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
    assert env.missing_credentials("azure") == []
    assert env.credentials_present("azure") is True


def test_provider_defaults_to_env_then_anthropic(monkeypatch):
    # no provider arg, no DISCOVERY_PROVIDER -> defaults to anthropic
    assert env.missing_credentials() == ["ANTHROPIC_API_KEY"]
    # honour DISCOVERY_PROVIDER when no explicit arg is passed
    monkeypatch.setenv("DISCOVERY_PROVIDER", "azure")
    assert "AZURE_OPENAI_API_KEY" in env.missing_credentials()


def test_load_env_does_not_clobber_existing(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "already-set")
    p = tmp_path / ".env"
    p.write_text('ANTHROPIC_API_KEY="from-file"\n# comment\nNO_EQUALS_LINE\nDISCOVERY_PROVIDER=azure\n')
    env.load_env(p)
    import os
    assert os.environ["ANTHROPIC_API_KEY"] == "already-set"   # explicit env wins
    assert os.environ["DISCOVERY_PROVIDER"] == "azure"        # new key loaded, quotes stripped


def test_load_env_missing_file_is_noop(tmp_path):
    env.load_env(tmp_path / "does-not-exist.env")  # must not raise
