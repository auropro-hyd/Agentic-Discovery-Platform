#!/usr/bin/env python3
"""Minimal stdlib backend for the Discovery Console UI.

Drives the existing run.py pipeline as a subprocess, parses its phase signals from stdout, and
streams them to the browser as Server-Sent Events (SSE). No new Python dependencies — http.server
+ subprocess only, so the engine stays dependency-light.

Endpoints
  POST /api/run        {domain, mode}  -> start a run; returns {run_id}. mode: "live" | "golden".
  GET  /api/stream/:id                 -> SSE stream of phase/activity/done events for that run.
  POST /api/feedback   {run_id, note}  -> record SME (discovery-copilot) feedback for the run.
  GET  /api/reports/:domain            -> the synthesis JSON (post-render) if present.
  GET  /reports/:domain/...            -> static report HTML/assets from out/<domain>/.
  GET  /healthz                        -> ok.

The phase model mirrors run.py's stdout and Akhilesh's 6-stage flow:
  upload -> assessment -> discovery_copilot -> analysis -> preview -> report_generation
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
PORT = int(os.environ.get("DISCOVERY_UI_PORT", "8742"))

# ── phase map: (id, label) in Akhilesh's order. Stages light up as run.py emits its signals. ──
STAGES = [
    ("upload", "Uploading documents"),
    ("assessment", "Assessment"),
    ("discovery_copilot", "Discovery copilot"),
    ("analysis", "Analysis"),
    ("preview", "Preview"),
    ("report_generation", "Report generation"),
]

# stdout substring -> the stage it marks as ACTIVE (first match wins, in scan order)
_PHASE_SIGNALS: list[tuple[str, str]] = [
    ("Reading the", "upload"),
    ("data files,", "assessment"),
    ("The platform is reading your landscape", "assessment"),
    ("discovery complete via", "discovery_copilot"),
    ("verification:", "analysis"),
    ("Assembling the report suite", "preview"),
    ("Done. Open the suite", "report_generation"),
]


class Run:
    """One pipeline run: its subprocess, an event queue per subscriber, and shared feedback."""

    def __init__(self, domain: str, mode: str) -> None:
        self.id = uuid.uuid4().hex[:12]
        self.domain = domain
        self.mode = mode  # "live" | "golden"
        self.events: list[dict] = []  # full history (so a late subscriber can replay)
        self.subscribers: list[queue.Queue] = []
        self.done = False
        self.feedback: list[str] = []
        self._lock = threading.Lock()

    def emit(self, event: dict) -> None:
        with self._lock:
            self.events.append(event)
            for q in self.subscribers:
                q.put(event)

    def subscribe(self) -> queue.Queue:
        q: queue.Queue = queue.Queue()
        with self._lock:
            for e in self.events:  # replay history to a new subscriber
                q.put(e)
            self.subscribers.append(q)
        return q


RUNS: dict[str, Run] = {}


def _spawn(run: Run) -> None:
    """Launch run.py and translate its stdout into phase/activity events."""
    cmd = ["uv", "run", "python", "run.py", "--domain", run.domain, "--agent", "--auto-resolve"]
    if run.mode == "golden":
        cmd.append("--golden")
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    run.emit({"type": "stage", "stage": "upload", "state": "active"})
    try:
        proc = subprocess.Popen(
            cmd, cwd=str(ROOT), env=env, text=True, bufsize=1,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
    except OSError as e:
        run.emit({"type": "error", "message": f"could not launch pipeline: {e}"})
        run.emit({"type": "done", "ok": False})
        run.done = True
        return

    seen_stage: str | None = None
    assert proc.stdout is not None
    for raw in proc.stdout:
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        # per-tool agent activity ("   · ...") -> activity feed under the current stage
        if line.lstrip().startswith("·"):
            run.emit({"type": "activity", "text": line.lstrip("· ").strip()})
            continue
        # a fixture-fallback / warning line surfaces verbatim (honest signalling)
        if line.lstrip().startswith("!"):
            run.emit({"type": "warn", "text": line.lstrip("! ").strip()})
        # phase transition?
        for needle, stage in _PHASE_SIGNALS:
            if needle in line:
                if stage != seen_stage:
                    seen_stage = stage
                    run.emit({"type": "stage", "stage": stage, "state": "active",
                              "note": line.strip()})
                break
        else:
            # an informative line that isn't a phase marker — pass it through as activity
            run.emit({"type": "activity", "text": line.strip()})

    code = proc.wait()
    ok = code == 0 and (OUT / f"discovery-{run.domain}.json").exists()
    if ok:
        run.emit({"type": "stage", "stage": "report_generation", "state": "done"})
    run.emit({"type": "done", "ok": ok, "domain": run.domain})
    run.done = True


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # quiet  # noqa: A002
        pass

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: dict) -> None:
        self._send(code, json.dumps(obj).encode(), "application/json")

    def _read_json(self) -> dict:
        n = int(self.headers.get("Content-Length", 0) or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, OSError):
            return {}

    def do_OPTIONS(self) -> None:  # CORS preflight
        self._send(204, b"", "text/plain")

    def do_POST(self) -> None:
        if self.path == "/api/run":
            body = self._read_json()
            domain = str(body.get("domain", "o2c")).strip() or "o2c"
            mode = "golden" if str(body.get("mode", "live")) == "golden" else "live"
            if not (ROOT / "inputs" / domain).is_dir():
                return self._json(400, {"error": f"unknown domain '{domain}'"})
            run = Run(domain, mode)
            RUNS[run.id] = run
            threading.Thread(target=_spawn, args=(run,), daemon=True).start()
            return self._json(200, {"run_id": run.id, "stages": [
                {"id": s, "label": lbl} for s, lbl in STAGES]})
        if self.path == "/api/feedback":
            body = self._read_json()
            run = RUNS.get(str(body.get("run_id", "")))
            note = str(body.get("note", "")).strip()
            if not run:
                return self._json(404, {"error": "unknown run_id"})
            if note:
                run.feedback.append(note)
                run.emit({"type": "feedback", "text": note})
            return self._json(200, {"ok": True, "count": len(run.feedback)})
        self._json(404, {"error": "not found"})

    def do_GET(self) -> None:
        if self.path == "/healthz":
            return self._json(200, {"ok": True})
        if self.path.startswith("/api/stream/"):
            return self._stream(self.path.rsplit("/", 1)[-1])
        if self.path.startswith("/api/reports/"):
            domain = self.path.rsplit("/", 1)[-1]
            f = OUT / f"discovery-{domain}.json"
            if not f.exists():
                return self._json(404, {"error": "no report yet"})
            return self._send(200, f.read_bytes(), "application/json")
        if self.path.startswith("/api/findings/"):
            return self._findings(self.path.rsplit("/", 1)[-1])
        if self.path.startswith("/reports/"):
            return self._static(self.path[len("/reports/"):])
        self._json(404, {"error": "not found"})

    def _stream(self, run_id: str) -> None:
        run = RUNS.get(run_id)
        if not run:
            return self._json(404, {"error": "unknown run_id"})
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        q = run.subscribe()
        try:
            while True:
                try:
                    event = q.get(timeout=15)
                except queue.Empty:
                    self.wfile.write(b": keepalive\n\n")  # comment frame keeps the socket open
                    self.wfile.flush()
                    continue
                self.wfile.write(f"data: {json.dumps(event)}\n\n".encode())
                self.wfile.flush()
                if event.get("type") == "done":
                    break
        except (BrokenPipeError, ConnectionResetError):
            pass  # client navigated away — normal

    def _findings(self, domain: str) -> None:
        """The discovery-copilot review items: each finding with its verification status, so the SME
        can see what was challenged (the 'gaps') and give feedback. Reads the internal trace."""
        f = OUT / f"discovery-{domain}.json"
        if not f.exists():
            return self._json(404, {"error": "no run yet"})
        try:
            trace = json.loads(f.read_text()).get("internal_trace", {})
        except (ValueError, OSError):
            return self._json(500, {"error": "could not read run"})
        items = []
        for fnd in trace.get("findings", []):
            v = fnd.get("verification", {}) or {}
            items.append({
                "id": fnd.get("id", ""),
                "title": fnd.get("title", ""),
                "confidence": fnd.get("confidence", ""),
                "severity": fnd.get("severity", ""),
                # a challenged finding (supported is False) is a gap the SME should review
                "challenged": v.get("supported") is False,
                "challenge": v.get("challenge", "") or v.get("note", ""),
                "sources": [s.get("doc_id", "") for s in fnd.get("sources", []) if s.get("doc_id")],
            })
        return self._json(200, {"domain": domain, "findings": items})

    def _static(self, rel: str) -> None:
        # serve out/<rel>; guard against path traversal
        target = (OUT / rel).resolve()
        if not str(target).startswith(str(OUT.resolve())) or not target.is_file():
            return self._json(404, {"error": "not found"})
        ext = target.suffix.lower()
        ctype = {".html": "text/html", ".css": "text/css", ".js": "text/javascript",
                 ".json": "application/json", ".svg": "image/svg+xml"}.get(ext, "text/plain")
        self._send(200, target.read_bytes(), ctype)


def main() -> int:
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Discovery Console backend on http://127.0.0.1:{PORT}  (Ctrl-C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
