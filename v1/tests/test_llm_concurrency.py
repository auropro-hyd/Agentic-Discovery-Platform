"""Concurrency-safety coverage for discovery/llm.py (the synthesis fan-out runs many sections on a
thread pool). llm.py is omitted from the coverage gate (real HTTP client), but these behaviours are
load-bearing for parallel synthesis and were flagged by the design review, so they're tested here.

All offline — no network. We exercise: (1) _provider_error classification (transient → retryable,
auth/config → hard, so a misconfigured run never silently omits a report); (2) atomic _write_cache
under concurrent same-key writes (no torn file → no corrupt golden artifact); (3) the locked lazy
client init building exactly one client across threads.
"""
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery.llm import LLMClient, LLMError, LLMRetryableError  # noqa: E402


# ── _provider_error: transient vs hard ────────────────────────────────────────────────────────────
class _NamedExc(Exception):
    """An exception whose class NAME we control, to simulate the SDK's error classes by name."""
    def __init__(self, name, msg=""):
        super().__init__(msg)
        self.__class__.__name__ = name


def test_provider_error_auth_is_hard_llmerror():
    # missing/invalid credentials must stay a plain LLMError (NOT retryable) so it aborts loudly
    e = LLMClient._provider_error("anthropic", _NamedExc("AuthenticationError", "bad api_key"))
    assert isinstance(e, LLMError) and not isinstance(e, LLMRetryableError)
    assert "credentials" in str(e).lower()


def test_provider_error_transient_is_retryable():
    for name in ("RateLimitError", "APIConnectionError", "InternalServerError", "OverloadedError"):
        e = LLMClient._provider_error("anthropic", _NamedExc(name, "boom"))
        assert isinstance(e, LLMRetryableError), name
    # also classified transient by message signal even with a generic class name
    assert isinstance(LLMClient._provider_error("anthropic", _NamedExc("X", "Error 429 overloaded")),
                      LLMRetryableError)


def test_provider_error_unknown_is_hard():
    # an unrecognised, non-auth, non-transient failure stays a hard LLMError (don't silently omit)
    e = LLMClient._provider_error("anthropic", _NamedExc("WeirdError", "??"))
    assert isinstance(e, LLMError) and not isinstance(e, LLMRetryableError)


# ── _write_cache: atomic + concurrent same-key ─────────────────────────────────────────────────────
def test_write_cache_atomic_concurrent_same_key(tmp_path):
    """Many threads writing the SAME key concurrently must never leave a torn/half-written file —
    every read must parse, and the final file must be valid JSON with the expected shape."""
    c = LLMClient(cache_dir=tmp_path / ".cache")
    key = "k" * 32
    errors: list[str] = []

    def writer(i):
        try:
            for _ in range(20):
                c._write_cache(key, "sys", "prompt", f"response-{i}")
                # read it straight back — must always be parseable (never a torn file)
                json.loads(c._cache_path(key).read_text())
        except Exception as e:  # noqa: BLE001 - capture for the assertion
            errors.append(repr(e))

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []                                   # no torn reads
    final = json.loads(c._cache_path(key).read_text())    # final file is valid + well-shaped
    assert final["system"] == "sys" and final["response"].startswith("response-")


def test_write_cache_uses_scratch_outside_cache_dir(tmp_path):
    """The temp file must NOT be written inside .cache/ (else --save-golden's copytree could capture
    a crash-orphaned temp). After a write, .cache/ holds exactly the final {key}.json, no *.tmp."""
    c = LLMClient(cache_dir=tmp_path / ".cache")
    c._write_cache("a" * 32, "s", "p", "r")
    names = [p.name for p in (tmp_path / ".cache").iterdir()]
    assert names == [f"{'a' * 32}.json"]                  # only the final file, no temp leftover


# ── locked lazy client init ─────────────────────────────────────────────────────────────────────
def test_client_init_is_locked_and_single(monkeypatch, tmp_path):
    """Under concurrent first-use from many threads, exactly ONE Anthropic client is constructed."""
    c = LLMClient(cache_dir=tmp_path / ".cache")
    built = {"n": 0}

    class _FakeAnthropic:
        def __init__(self, **kw):
            built["n"] += 1

    import types
    fake_mod = types.ModuleType("anthropic")
    fake_mod.Anthropic = _FakeAnthropic  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "anthropic", fake_mod)

    start = threading.Barrier(8)

    def use():
        start.wait(timeout=5)
        c._anthropic_client()

    threads = [threading.Thread(target=use) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert built["n"] == 1                                 # double-checked lock → constructed once
    assert c._client is not None
