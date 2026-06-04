"""Deterministic LLM client with on-disk caching.

Design goals for the demo:
- **Consistent output.** temperature=0, pinned model + prompt, and every call cached by a
  hash of (model, system, prompt). A repeated run replays from cache => identical output.
- **Provider-agnostic.** Works with the Anthropic API or an Azure OpenAI deployment,
  selected by env var, so we can switch to the team's Azure resource without code changes.
- **Offline/golden mode.** If ``DISCOVERY_OFFLINE=1`` (or no creds), calls must hit cache;
  a miss raises a clear error instead of making a network call. This is what makes the
  ``--golden`` fallback safe on demo day.

Env:
  DISCOVERY_PROVIDER   "anthropic" (default) | "azure"
  DISCOVERY_OFFLINE    "1" to forbid network calls (cache-only)
  ANTHROPIC_API_KEY / ANTHROPIC_MODEL
  AZURE_OPENAI_API_KEY / AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_DEPLOYMENT / AZURE_OPENAI_API_VERSION
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

DEFAULT_ANTHROPIC_MODEL = "claude-opus-4-8"
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(self, *, cache_dir: Path | None = None, offline: bool | None = None) -> None:
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.provider = os.environ.get("DISCOVERY_PROVIDER", "anthropic").lower()
        self.offline = (
            offline
            if offline is not None
            else os.environ.get("DISCOVERY_OFFLINE", "0") == "1"
        )
        # DISCOVERY_NO_CACHE=1 forces a genuinely fresh run: skip the READ-cache so every call hits
        # the provider (results are still WRITTEN, so a later replay is fast). Incompatible with
        # offline — a fresh run by definition needs the network.
        self.no_cache = os.environ.get("DISCOVERY_NO_CACHE", "0") == "1" and not self.offline
        self._client = None  # lazily created

    # ---- caching -----------------------------------------------------------
    def _cache_key(self, system: str, prompt: str, model: str) -> str:
        h = hashlib.sha256()
        h.update(model.encode())
        h.update(b"\x00")
        h.update(system.encode())
        h.update(b"\x00")
        h.update(prompt.encode())
        return h.hexdigest()[:32]

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def _read_cache(self, key: str) -> str | None:
        if self.no_cache:                  # forced-fresh run: never serve from the read-cache
            return None
        p = self._cache_path(key)
        if p.exists():
            return json.loads(p.read_text())["response"]
        return None

    def _write_cache(self, key: str, system: str, prompt: str, response: str) -> None:
        self._cache_path(key).write_text(
            json.dumps(
                {"system": system, "prompt": prompt, "response": response},
                indent=2,
                ensure_ascii=False,
            )
        )

    # ---- public API --------------------------------------------------------
    def complete(self, system: str, prompt: str, *, model: str | None = None,
                 max_tokens: int = 4096) -> str:
        """Return model text for (system, prompt). Cache-first, deterministic."""
        model = model or self._default_model()
        key = self._cache_key(system, prompt, model)

        cached = self._read_cache(key)
        if cached is not None:
            return cached

        if self.offline:
            raise LLMError(
                f"offline mode: no cached response for this call (key={key}). "
                "Run online once to populate the cache, or use the golden run."
            )

        response = self._call_provider(system, prompt, model, max_tokens)
        self._write_cache(key, system, prompt, response)
        return response

    def complete_json(self, system: str, prompt: str, **kw) -> object:
        """Like ``complete`` but parses a JSON object/array out of the response."""
        raw = self.complete(system, prompt, **kw)
        return _extract_json(raw)

    # ---- multi-turn tool use ----------------------------------------------
    def messages_with_tools(self, *, system: str, messages: list, tools: list,
                            model: str | None = None, max_tokens: int = 4096):
        """One assistant turn with tool support. Cache key covers the FULL message history +
        tool schemas, so a multi-turn loop replays byte-identically offline/golden.

        Returns a normalized object: ``ToolTurn(content=[...blocks...], stop_reason=str)``
        where each block is a dict: {"type":"text","text":...} or
        {"type":"tool_use","id":...,"name":...,"input":{...}}.
        """
        model = model or self._default_model()
        key = self._tools_cache_key(system, messages, tools, model)
        cached = self._read_cache(key)
        if cached is not None:
            return ToolTurn.from_json(cached)
        if self.offline:
            raise LLMError(
                f"offline mode: no cached tool-turn for this state (key={key}). "
                "Run online once to populate the cache, or use the scripted/golden path."
            )
        turn = self._call_anthropic_tools(system, messages, tools, model, max_tokens)
        self._write_cache(key, system, json.dumps(messages, sort_keys=True, ensure_ascii=False),
                          turn.to_json())
        return turn

    def _tools_cache_key(self, system, messages, tools, model) -> str:
        h = hashlib.sha256()
        h.update(model.encode()); h.update(b"\x00")
        h.update(system.encode()); h.update(b"\x00")
        h.update(json.dumps(messages, sort_keys=True, ensure_ascii=False).encode()); h.update(b"\x00")
        h.update(json.dumps(tools, sort_keys=True, ensure_ascii=False).encode())
        return h.hexdigest()[:32]

    @staticmethod
    def _temp_kwargs(model: str) -> dict:
        """Some newer models (e.g. Opus 4.8) deprecate `temperature` and reject temperature=0.
        They are deterministic-leaning by default, so we simply omit the param for those."""
        deprecated = ("claude-opus-4-8",)
        return {} if any(model.startswith(d) for d in deprecated) else {"temperature": 0}

    def _call_anthropic_tools(self, system, messages, tools, model, max_tokens):
        try:
            import anthropic
        except ImportError as e:  # pragma: no cover
            raise LLMError("pip install anthropic") from e
        if self._client is None:
            self._client = anthropic.Anthropic()
        # we never stream, so .create() returns a Message (not a Stream); narrow for the checker
        msg: Any = self._client.messages.create(
            model=model, max_tokens=max_tokens, **self._temp_kwargs(model),
            system=system, tools=tools, tool_choice={"type": "auto"},
            messages=messages,
        )
        blocks = []
        for b in msg.content:
            if b.type == "text":
                blocks.append({"type": "text", "text": b.text})
            elif b.type == "tool_use":
                blocks.append({"type": "tool_use", "id": b.id, "name": b.name, "input": b.input})
        return ToolTurn(content=blocks, stop_reason=msg.stop_reason)

    # ---- providers ---------------------------------------------------------
    def _default_model(self) -> str:
        if self.provider == "azure":
            return os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        return os.environ.get("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)

    def _call_provider(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        if self.provider == "azure":
            return self._call_azure(system, prompt, model, max_tokens)
        return self._call_anthropic(system, prompt, model, max_tokens)

    def _call_anthropic(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        try:
            import anthropic
        except ImportError as e:  # pragma: no cover
            raise LLMError("pip install anthropic") from e
        if self._client is None:
            self._client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
        msg: Any = self._client.messages.create(   # non-streaming -> Message; narrow for the checker
            model=model,
            max_tokens=max_tokens,
            **self._temp_kwargs(model),
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")

    def _call_azure(self, system: str, prompt: str, model: str, max_tokens: int) -> str:
        try:
            from openai import AzureOpenAI
        except ImportError as e:  # pragma: no cover
            raise LLMError("pip install openai") from e
        if self._client is None:
            self._client = AzureOpenAI(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
            )
        resp = self._client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return resp.choices[0].message.content or ""


class ToolTurn:
    """Normalized, JSON-serializable view of one assistant turn (text + tool_use blocks)."""

    def __init__(self, content: list, stop_reason: str):
        self.content = content
        self.stop_reason = stop_reason

    @property
    def tool_uses(self) -> list:
        return [b for b in self.content if b.get("type") == "tool_use"]

    @property
    def text(self) -> str:
        return "".join(b.get("text", "") for b in self.content if b.get("type") == "text")

    def to_json(self) -> str:
        return json.dumps({"content": self.content, "stop_reason": self.stop_reason},
                          sort_keys=True, ensure_ascii=False)

    @classmethod
    def from_json(cls, raw: str) -> "ToolTurn":
        d = json.loads(raw)
        return cls(content=d["content"], stop_reason=d["stop_reason"])


def _extract_json(raw: str) -> object:
    """Pull the first JSON object/array out of a model response (handles code fences)."""
    s = raw.strip()
    if s.startswith("```"):
        s = s.split("```", 2)[1]
        if s.startswith("json"):
            s = s[4:]
        s = s.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    # fall back: find the outermost { } or [ ]
    for open_c, close_c in (("{", "}"), ("[", "]")):
        start = s.find(open_c)
        end = s.rfind(close_c)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(s[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise LLMError(f"could not parse JSON from response:\n{raw[:500]}")
