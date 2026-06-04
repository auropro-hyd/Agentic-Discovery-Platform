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
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
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


# Vite prints its real URL ("➜  Local:   http://localhost:5173/") and bumps to the next free port
# if 5173 is taken — so we read the URL from its own output rather than guessing the port.
_VITE_LOCAL_RE = re.compile(r"Local:\s*(https?://\S+?)/?\s*$")

# The Console backend (server.py). Keep in sync with DISCOVERY_UI_PORT / server.py's default.
_BACKEND_PORT = int(os.environ.get("DISCOVERY_UI_PORT", "8742"))
_BACKEND_HEALTH = f"http://127.0.0.1:{_BACKEND_PORT}/healthz"


def _wait_backend(proc: subprocess.Popen, timeout: float = 20.0) -> bool:
    """Poll the backend's /healthz until it answers (True) or it dies / times out (False).
    Starting Vite only after the backend is reachable is what prevents the UI from loading
    against a dead backend and showing 'Failed to fetch' the moment you click Run."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            return False   # backend exited (e.g. port in use) — caller surfaces why
        try:
            with urllib.request.urlopen(_BACKEND_HEALTH, timeout=1):
                return True
        except Exception:
            time.sleep(0.4)
    return False


def _has_report_data() -> bool:
    """True if the engine has produced at least one synthesis JSON for the explorer to render.
    The explorer's predev step (sync-data) hard-fails without one, so the Console needs this first."""
    out = V1 / "out"
    return out.is_dir() and any(out.glob("discovery-*.json"))


def _popen_group(cmd: list[str], **kw) -> subprocess.Popen:
    """Start a child in its OWN process group so we can later kill it AND its grandchildren
    (npm -> vite -> esbuild) in one shot. Without this, terminating npm orphans esbuild."""
    if os.name == "nt":
        kw["creationflags"] = kw.get("creationflags", 0) | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kw["start_new_session"] = True   # setsid: child becomes its own process-group leader
    return subprocess.Popen(cmd, **kw)


def _kill_group(proc: subprocess.Popen) -> None:
    """Terminate a child and every process in its group; fall back to a hard kill."""
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            proc.terminate()
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        return
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            if os.name == "nt":
                proc.kill()
            else:
                os.killpg(os.getpgid(proc.pid), __import__("signal").SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass


def console(a) -> None:
    """Run both localhosts and keep them alive: the backend (server.py, :8742) and the explorer
    dev server (Vite). Tees Vite's output, opens the exact URL Vite reports (handles a bumped port),
    then leaves both running so you drive it. Ctrl-C stops both."""
    _require("uv", "Install uv first: https://docs.astral.sh/uv/")
    _require("npm", "Install Node.js 20+ from https://nodejs.org")
    # The explorer can't start without report data (its predev sync-data step exits 1 on an empty
    # out/). If none exists yet, generate the offline golden suite first — no key, no cost — so a
    # first `make console` just works instead of dying on a Node error.
    if not _has_report_data():
        print("→ No report data yet — rendering the offline golden suite first (no key, no cost)…")
        report(a)
    print(f"→ Starting Discovery Console backend on http://127.0.0.1:{_BACKEND_PORT} …")
    backend = _popen_group(["uv", "run", "python", "server.py"], cwd=str(V1), env=_uv_env())

    # Wait until the backend is actually answering before starting the UI. If it never comes up
    # (the common cause is a stale backend already holding the port — server.py prints that and
    # exits 1), abort with a clear message instead of opening a UI that can only say "Failed to
    # fetch". server.py's own stderr (incl. the port-in-use hint) is inherited, so it's visible.
    if not _wait_backend(backend):
        _kill_group(backend)
        sys.exit(f"✗ The Console backend did not come up on port {_BACKEND_PORT} (see its message "
                 f"above).\n  If a previous Console is still running, stop it:  "
                 f"lsof -ti tcp:{_BACKEND_PORT} | xargs kill   (then re-run).")
    print("✓ Backend is up.")

    print("→ Starting the explorer dev server (Ctrl-C to stop both)…")
    npm = shutil.which("npm") or "npm"
    # Pipe stdout so we can read the real Local URL; tee every line straight back to the terminal so
    # the dev server still looks/behaves normal (HMR logs, errors, the URL banner). Own process
    # group so teardown reaps the grandchildren (vite/esbuild), not just npm.
    vite = _popen_group([npm, "run", "dev"], cwd=str(UI),
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    opened = False
    try:
        assert vite.stdout is not None
        for line in vite.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            if not opened:
                m = _VITE_LOCAL_RE.search(line)
                if m:
                    url = m.group(1)
                    print(f"→ Opening {url} (both servers stay running; Ctrl-C to stop)…")
                    webbrowser.open(url)
                    opened = True
        vite.wait()
    except KeyboardInterrupt:
        pass
    finally:
        print("\n→ Stopping both servers…")
        _kill_group(vite)
        _kill_group(backend)


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
