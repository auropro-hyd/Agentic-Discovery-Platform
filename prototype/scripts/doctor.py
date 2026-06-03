#!/usr/bin/env python3
"""Credential + connectivity check. Confirms a provider is wired before a full run.

Usage:
  ./.venv/bin/python scripts/doctor.py                 # checks the default provider
  ./.venv/bin/python scripts/doctor.py --provider azure
  ./.venv/bin/python scripts/doctor.py --provider anthropic

Makes ONE tiny live call (a 1-word reply) so it costs almost nothing. Prints exactly which
env vars are present/missing so setup problems are obvious.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # prototype/ (this file lives in prototype/scripts/)
sys.path.insert(0, str(ROOT))
from discovery import env  # noqa: E402
env.load_env()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=["anthropic", "azure"])
    args = ap.parse_args(argv)
    if args.provider:
        os.environ["DISCOVERY_PROVIDER"] = args.provider
    provider = os.environ.get("DISCOVERY_PROVIDER", "anthropic").lower()
    print(f"provider: {provider}")

    required = {
        "anthropic": ["ANTHROPIC_API_KEY"],
        "azure": ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY",
                  "AZURE_OPENAI_DEPLOYMENT", "AZURE_OPENAI_API_VERSION"],
    }[provider]
    missing = [v for v in required if not os.environ.get(v)]
    for v in required:
        val = os.environ.get(v, "")
        shown = (val[:6] + "…" + str(len(val)) + "ch") if val else "MISSING"
        print(f"  {v:28s} {shown}")
    if missing:
        print(f"\nFAIL: missing {missing}. Add them to prototype/.env (see .env.example).")
        return 2

    print("\nmaking a tiny live call...")
    from discovery.llm import LLMClient, LLMError
    llm = LLMClient(offline=False)
    try:
        reply = llm.complete("You are a connectivity check.",
                             "Reply with exactly the word: OK", max_tokens=16)
        print(f"  reply: {reply.strip()!r}")
        print("\nPASS — provider is reachable. Ready for: python run.py --domain o2c"
              + (f" --provider {provider}" if args.provider else ""))
        return 0
    except LLMError as e:
        print(f"\nFAIL: {e}")
        return 1
    except Exception as e:  # surface provider SDK errors clearly
        print(f"\nFAIL ({type(e).__name__}): {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
