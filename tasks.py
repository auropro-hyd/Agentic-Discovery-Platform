#!/usr/bin/env python3
"""Cross-platform setup & run for the Agentic Discovery Platform (Mac / Linux / Windows).

`make` is not native on Windows, so this is the portable entrypoint — the Makefile just delegates
here, keeping ONE source of truth. Pure standard library, no third-party deps.

    python tasks.py                 # list the tasks (same as `help`)
    python tasks.py setup           # Python env (v1/, via uv) + explorer deps (npm)
    python tasks.py run             # OFFLINE demo: golden replay -> build UI -> open it (no key, no cost)
    python tasks.py live            # LIVE run: real agent pipeline (needs credentials; spends credits)
    python tasks.py console         # interactive 6-stage Console (backend + UI dev server)
    python tasks.py report|ui|open|doctor|test|clean|distclean

    python tasks.py run --domain p2p     # any task takes --domain (default: o2c)

Why this exists: a first-timer hit two setup traps — a stale VIRTUAL_ENV confusing `uv`, and a
keyless live run failing with a misleading message. This drives uv with the stray VIRTUAL_ENV
stripped and pins it to v1/, and the default `run` is an offline golden replay that needs no key.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V1 = ROOT / "v1"
UI = ROOT / "explorer"


# ── helpers ────────────────────────────────────────────────────────────────────
def _have(tool: str) -> bool:
    return shutil.which(tool) is not None


def _require(tool: str, hint: str) -> None:
    if not _have(tool):
        sys.exit(f"✗ '{tool}' is not installed.\n  {hint}")


def _uv_env() -> dict:
    """Env for uv calls: drop a stray VIRTUAL_ENV so uv always targets v1/.venv (not whatever venv
    the operator happens to have activated — the exact 'VIRTUAL_ENV does not match .venv' trap)."""
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    return env


def _run(cmd: list[str], cwd: Path, env: dict | None = None) -> None:
    """Run a command (arg list — handles spaces in paths on every OS) and fail loudly on error."""
    print(f"→ {' '.join(cmd)}  (in {cwd})")
    proc = subprocess.run(cmd, cwd=str(cwd), env=env)
    if proc.returncode != 0:
        sys.exit(proc.returncode)


def _uv(args: list[str], cwd: Path = V1) -> None:
    _require("uv", "Install it:  curl -LsSf https://astral.sh/uv/install.sh | sh   "
                   "(Windows: https://docs.astral.sh/uv/getting-started/installation/)")
    _run(["uv", *args], cwd=cwd, env=_uv_env())


def _npm(args: list[str], cwd: Path = UI) -> None:
    # On Windows npm is a .cmd shim; shutil.which finds it and subprocess runs it without shell=True.
    _require("npm", "Install Node.js 20+ from https://nodejs.org")
    npm = shutil.which("npm") or "npm"
    _run([npm, *args], cwd=cwd)


# ── tasks ───────────────────────────────────────────────────────────────────────
def setup(_a) -> None:
    setup_py(_a)
    setup_ui(_a)
    print("\n✓ Setup complete. Next:  python tasks.py run   (offline demo — no API key needed)")


def setup_py(_a) -> None:
    print("→ Python: creating v1/.venv and installing deps (this can take a minute)…")
    _uv(["sync"])
    env_file = V1 / ".env"
    if not env_file.exists():
        shutil.copyfile(V1 / ".env.example", env_file)
        print("→ Created v1/.env from the template. Add your ANTHROPIC_API_KEY for live runs.")
    print("✓ Python environment ready.")


def setup_ui(_a) -> None:
    print("→ Explorer: installing node_modules…")
    _npm(["install"])
    print("✓ Explorer dependencies ready.")


def report(a) -> None:
    """Golden replay = the saved run rendered offline. No network, no key, no cost."""
    print(f"→ Rendering the golden report suite for '{a.domain}' (offline replay)…")
    _uv(["run", "python", "run.py", "--domain", a.domain, "--golden", "--auto-resolve"])


def ui(_a) -> None:
    print("→ Building the explorer SPA…")
    _npm(["run", "build"])
    print("✓ Explorer built → explorer/dist/")


def run(a) -> None:
    report(a)
    ui(a)
    print(f"\n✓ Offline demo ready for '{a.domain}'.")
    print(f"  • Report suite:  v1/out/{a.domain}/index.html")
    print("  • Explorer SPA:  explorer/dist/index.html")
    open_report(a)


def live(a) -> None:
    """LIVE run. run.py itself preflights credentials and prints an actionable message if missing,
    so we don't duplicate the check here — just announce and hand off."""
    print(f"→ LIVE run for '{a.domain}' — this takes minutes and spends API credits…")
    _uv(["run", "python", "run.py", "--domain", a.domain, "--fresh", "--auto-resolve"])


def console(_a) -> None:
    """Start the backend (server.py) then the Vite dev server. Ctrl-C stops both."""
    _require("uv", "Install uv first: https://docs.astral.sh/uv/")
    _require("npm", "Install Node.js 20+ from https://nodejs.org")
    print("→ Starting Discovery Console backend on http://127.0.0.1:8742 …")
    backend = subprocess.Popen(["uv", "run", "python", "server.py"], cwd=str(V1), env=_uv_env())
    try:
        print("→ Starting the explorer dev server (Ctrl-C to stop both)…")
        npm = shutil.which("npm") or "npm"
        subprocess.run([npm, "run", "dev"], cwd=str(UI))
    finally:
        backend.terminate()
        try:
            backend.wait(timeout=10)
        except subprocess.TimeoutExpired:
            backend.kill()


def doctor(_a) -> None:
    print("→ Checking provider connectivity (makes one tiny live call)…")
    _uv(["run", "python", "scripts/doctor.py"])


def open_report(a) -> None:
    f = V1 / "out" / a.domain / "index.html"
    if f.exists():
        webbrowser.open(f.as_uri())
        print(f"→ Opened {f}")
    else:
        print(f"No report yet for '{a.domain}'. Run 'python tasks.py report' (or 'run') first.")


def test(_a) -> None:
    print("→ Running the Python test suite + type-check…")
    _uv(["run", "pytest"])
    _uv(["run", "pyrefly", "check", "discovery", "run.py", "scripts"])


def clean(_a) -> None:
    print("→ Removing generated build output (keeps env, golden, and reports)…")
    shutil.rmtree(UI / "dist", ignore_errors=True)
    for pc in V1.rglob("__pycache__"):
        shutil.rmtree(pc, ignore_errors=True)
    print("✓ Clean.")


def distclean(a) -> None:
    clean(a)
    print("→ Full reset: removing v1/.venv and explorer/node_modules…")
    shutil.rmtree(V1 / ".venv", ignore_errors=True)
    shutil.rmtree(UI / "node_modules", ignore_errors=True)
    print("✓ Done. Re-run 'python tasks.py setup' to rebuild.")


TASKS = {
    "setup": (setup, "Install everything (Python env in v1/ + explorer deps)."),
    "run": (run, "OFFLINE demo: golden replay + build UI + open it. No API key, no cost."),
    "live": (live, "LIVE run: real agent pipeline (needs credentials; spends credits)."),
    "console": (console, "Start the Discovery Console (backend + UI dev server)."),
    "report": (report, "(Re)generate the golden report suite for a domain -> v1/out/<domain>/."),
    "ui": (ui, "Build the explorer SPA into explorer/dist/."),
    "open": (open_report, "Open the most recently built report suite in your browser."),
    "doctor": (doctor, "Check that your API provider/credentials are wired (one tiny call)."),
    "test": (test, "Run the Python test suite + type-check."),
    "clean": (clean, "Remove generated build output (dist/, __pycache__) — keeps env + golden."),
    "distclean": (distclean, "Also remove the venvs and node_modules (full reset)."),
}


def _help() -> None:
    print("\n  Agentic Discovery Platform — python tasks.py <task>")
    print("  " + "─" * 50)
    for name, (_fn, desc) in TASKS.items():
        print(f"  {name:10s} {desc}")
    print("\n  Vars:  --domain o2c|p2p   (default: o2c)")
    print("  First time?  →  python tasks.py setup && python tasks.py run\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("task", nargs="?", default="help")
    ap.add_argument("--domain", default="o2c")
    a = ap.parse_args(argv)
    if a.task in ("help", "-h", "--help"):
        _help()
        return 0
    entry = TASKS.get(a.task)
    if entry is None:
        print(f"unknown task: {a.task!r}")
        _help()
        return 2
    entry[0](a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
