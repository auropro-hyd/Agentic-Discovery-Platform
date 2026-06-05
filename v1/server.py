#!/usr/bin/env python3
"""Minimal stdlib backend for the Discovery Console UI.

Drives the existing run.py pipeline as a subprocess, parses its phase signals from stdout, and
streams them to the browser as Server-Sent Events (SSE). No new Python dependencies — http.server
+ subprocess only, so the engine stays dependency-light.

Endpoints
  GET  /api/cases                      -> the saved case list (one: Opella O2C) for the dashboard.
  GET  /api/case/:id                   -> full stage metadata + archive/ URLs for a case.
  POST /api/run        {domain}        -> start a genuinely LIVE run (--fresh); returns {run_id}.
  GET  /api/stream/:id                 -> SSE stream of phase/activity/done events for that run.
  POST /api/feedback   {run_id, note}  -> record SME (discovery-copilot) feedback for the run.
  GET  /api/reports/:domain            -> the synthesis JSON (post-render) if present.
  GET  /reports/:domain/...            -> static report HTML/assets from out/<domain>/.
  GET  /archive/...                    -> the curated demo suite (preview/output/input), verbatim.
  GET  /healthz                        -> ok.

A triggered run is always live and takes the real time it needs; the displayed case deliverable is
the curated archive/ suite. The phase model mirrors run.py's stdout and Akhilesh's 6-stage flow:
  ingestion -> domain analysis -> discovery copilot -> transformation journey -> findings review
  -> report generation   (stage ids kept stable: upload/assessment/discovery_copilot/analysis/
  preview/report_generation; the UI renders the new labels.)
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
REPO = ROOT.parent                       # repo root (v1/ lives one level down)
OUT = ROOT / "out"
PORT = int(os.environ.get("DISCOVERY_UI_PORT", "8742"))


def _find_archive() -> Path:
    """Locate the curated demo-artefacts dir at the repo root. Resolved case-INSENSITIVELY so it
    works whether the dir is `archive` or `Archive` and on case-sensitive filesystems (Linux CI)."""
    for child in REPO.iterdir():
        if child.is_dir() and child.name.lower() == "archive":
            return child
    return REPO / "Archive"              # sensible default if absent (routes will 404 cleanly)


ARCHIVE = _find_archive()                # Akhilesh's curated demo artefacts (input/preview/output)

# ── The saved case shown on the dashboard ─────────────────────────────────────
# A single, pre-executed demo case. Its STAGE CONTENT is the curated archive/ suite (served as-is,
# never re-parsed). The fields below are presentation metadata for the dashboard card + stage shells
# — the gap-gate counts mirror the Copilot audit trail (archive/preview/07-copilot-audit-trail.html);
# the duration is a deliberately-realistic figure for the "discovery took ~34 min" narrative.
OPELLA_INPUT_DOCS = [
    {"name": "accounts-receivable-review-notes-q4-2025.txt", "kind": "txt", "kb": 3},
    {"name": "credit-management-policy-opella-europe.pdf", "kind": "pdf", "kb": 28},
    {"name": "customer-service-escalation-log-2025.csv", "kind": "csv", "kb": 20},
    {"name": "edi-dispute-resolution-cs-working-notes.txt", "kind": "txt", "kb": 6},
    {"name": "edi-integration-register-opella-europe.pdf", "kind": "pdf", "kb": 19},
    {"name": "o2c-process-raci-opella-europe.pdf", "kind": "pdf", "kb": 14},
    {"name": "order-flow-analysis-export-2025.csv", "kind": "csv", "kb": 737},
    {"name": "order-management-sop-opella-europe.pdf", "kind": "pdf", "kb": 45},
    {"name": "retail-customer-onboarding-guide-opella-europe.pdf", "kind": "pdf", "kb": 23},
    {"name": "sanofi-consumer-healthcare-o2c-sop-2023.pdf", "kind": "pdf", "kb": 34},
    {"name": "sap-crm-customer-export.csv", "kind": "csv", "kb": 29},
    {"name": "sap-s4-customer-master-export.csv", "kind": "csv", "kb": 21},
]
# the 6 client-facing report deliverables (archive/output/), in suite order
OPELLA_REPORTS = [
    {"id": "01", "title": "Current State Assessment", "file": "report-01-current-state.html"},
    {"id": "02", "title": "Pain Points & Opportunities", "file": "report-02-pain-points.html"},
    {"id": "03", "title": "Transformation Recommendation", "file": "report-03-transformation.html"},
    {"id": "04", "title": "AI Opportunity Portfolio", "file": "report-04-ai-opportunity.html"},
    {"id": "05", "title": "Transformation Roadmap", "file": "report-05-roadmap.html"},
    {"id": "06", "title": "Supporting Artefacts", "file": "report-06-artefacts.html"},
]
# The gap-resolution ledger the Discovery Co-pilot stage renders NATIVELY (so it reads as an SME
# decision console, not a re-shown report). Mirrors archive/preview/07-copilot-audit-trail.html
# row-for-row; the full working record is still iframed below for the complete chain of evidence.
OPELLA_GAP_LEDGER = [
    {"id": "G1", "severity": "high", "status": "Resolved",
     "question": "Which system is authoritative for customer credit limits — SAP CRM or S/4HANA?",
     "decision": "S/4HANA per the Credit Management Policy; CRM deltas classed as post-carve-out drift.",
     "resolves": "OPP-01 · Report 01"},
    {"id": "G2", "severity": "high", "status": "Resolved",
     "question": "Who owns EDI order processing, and under what documented procedure?",
     "decision": "Confirmed ungoverned — EDI excluded from the O2C SOP/RACI; logged as the core gap.",
     "resolves": "OPP-01 / OPP-02 · Report 01"},
    {"id": "G3", "severity": "high", "status": "Resolved",
     "question": "Is a credit assessment run on the EDI channel?",
     "decision": "No systematic credit check on EDI; flagged as a control-coverage gap.",
     "resolves": "OPP-03 · Report 03"},
    {"id": "T1", "severity": "clarification", "status": "Accepted",
     "question": "Ownership of the 6 EDI connections still under the Sanofi TSA.",
     "decision": "SME accepted: TSA transfer tracked as a roadmap dependency (non-blocking).",
     "resolves": "TSA Transfer · Report 05"},
    {"id": "T2", "severity": "clarification", "status": "Accepted",
     "question": "Pace of retail-EDI modernisation vs. stabilisation capacity.",
     "decision": "SME accepted: sequenced across roadmap H2/H3.",
     "resolves": "Roadmap H2/H3 · Report 05"},
    {"id": "C1", "severity": "amber", "status": "Carried fwd",
     "question": "Payment-terms system of record across 228 accounts.",
     "decision": "Low severity — carried into Block 3 as an amber node.",
     "resolves": "OPP-05 · Report 02"},
    {"id": "C2", "severity": "amber", "status": "Carried fwd",
     "question": "Fax-channel sanctioning status (184 orders).",
     "decision": "Low severity — carried forward for channel rationalisation.",
     "resolves": "Channel rationalisation · Report 05"},
    {"id": "C3", "severity": "amber", "status": "Carried fwd",
     "question": "Dispute-resolution workflow ownership.",
     "decision": "Ambiguous ownership — carried forward as amber.",
     "resolves": "OPP-04 · Report 02"},
    {"id": "C4", "severity": "amber", "status": "Carried fwd",
     "question": "Demand-forecast → escalation domain boundary.",
     "decision": "Cross-domain boundary — carried into the Block 3 context map.",
     "resolves": "Context map · Report 06"},
]
OPELLA_CASE = {
    "id": "opella-o2c",
    "title": "Opella · Order-to-Cash",
    "domain": "o2c",
    "client": "Opella (Sanofi Consumer Healthcare)",
    "run_date": "2026-06-04",
    "duration_minutes": 34,           # presentation figure for the discovery-took-~34-min narrative
    "stage": "report_generation",     # the case is fully complete, signed off
    "status": "Signed off",
    "doc_count": len(OPELLA_INPUT_DOCS),
    # gap-gate summary — mirrors archive/preview/07-copilot-audit-trail.html
    "gaps": {"questions": 9, "high_resolved": 3, "clarifications": 2, "carried_forward": 4},
    "findings": 5,
    "opportunities": 5,
}

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

    def __init__(self, domain: str) -> None:
        self.id = uuid.uuid4().hex[:12]
        self.domain = domain
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
    """Launch run.py and translate its stdout into phase/activity events. Always LIVE (--fresh):
    a triggered run executes the real pipeline for the real time it takes. The displayed case
    deliverable is the curated archive/ suite regardless — the live run proves the engine runs."""
    cmd = ["uv", "run", "python", "run.py", "--domain", run.domain, "--agent", "--auto-resolve",
           "--fresh"]               # genuinely live — bypass the read-cache, hit the provider
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

    def _send(self, code: int, body: bytes, ctype: str, disposition: str | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        if disposition:                     # forces a download even cross-origin (the download=
            self.send_header("Content-Disposition", disposition)   # attribute is ignored x-origin)
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
            if not (ROOT / "inputs" / domain).is_dir():
                return self._json(400, {"error": f"unknown domain '{domain}'"})
            run = Run(domain)          # always live (--fresh); no mode selector
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
        if self.path == "/api/cases":
            return self._json(200, {"cases": [_case_card(OPELLA_CASE)]})
        if self.path.startswith("/api/case/"):
            return self._case(self.path[len("/api/case/"):])
        if self.path.startswith("/reports/"):
            return self._static(self.path[len("/reports/"):])
        if self.path.startswith("/archive/"):
            return self._archive(self.path[len("/archive/"):])
        self._json(404, {"error": "not found"})

    def _case(self, case_id: str) -> None:
        """Full stage metadata for a case — the dashboard card plus everything the stage shells need
        (the ingested doc list, the gap-gate summary, and the archive/ URLs each stage iframes)."""
        case_id = case_id.split("?", 1)[0].rstrip("/")
        if case_id != OPELLA_CASE["id"]:
            return self._json(404, {"error": f"unknown case '{case_id}'"})
        c = OPELLA_CASE
        return self._json(200, {
            **_case_card(c),
            "input_docs": OPELLA_INPUT_DOCS,
            "gap_ledger": OPELLA_GAP_LEDGER,   # rendered natively by the Co-pilot stage
            "reports": [{**r, "url": f"/archive/output/{r['file']}"} for r in OPELLA_REPORTS],
            # stage content lives in the self-contained archive/ suite, served via /archive/
            "copilot_audit_url": "/archive/preview/07-copilot-audit-trail.html",
            "preview_url": "/archive/preview/index.html",
        })

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

    # MIME map shared by the static servers (archive/ adds pdf/csv/txt for the ingested docs)
    _CTYPES = {".html": "text/html", ".css": "text/css", ".js": "text/javascript",
               ".json": "application/json", ".svg": "image/svg+xml", ".pdf": "application/pdf",
               ".csv": "text/csv", ".txt": "text/plain", ".png": "image/png"}

    def _serve_under(self, base: Path, rel: str) -> None:
        """Serve base/<rel> as a static file, guarding against path traversal outside base.
        `?download=1` forces an attachment download (the HTML <a download> attribute is ignored for
        cross-origin requests, and the app on :5173 fetches archive files from :8742)."""
        path, _, query = rel.partition("?")
        path = path.split("#", 1)[0]
        target = (base / path).resolve()
        if not str(target).startswith(str(base.resolve())) or not target.is_file():
            return self._json(404, {"error": "not found"})
        ctype = self._CTYPES.get(target.suffix.lower(), "application/octet-stream")
        disposition = f'attachment; filename="{target.name}"' if "download=1" in query else None
        self._send(200, target.read_bytes(), ctype, disposition)

    def _static(self, rel: str) -> None:
        self._serve_under(OUT, rel)

    def _archive(self, rel: str) -> None:
        # the curated demo suite (preview/output/input) — self-contained, served verbatim
        self._serve_under(ARCHIVE, rel)


def _case_card(c: dict) -> dict:
    """The dashboard-card view of a case (the list row + summary fields)."""
    return {k: c[k] for k in (
        "id", "title", "domain", "client", "run_date", "duration_minutes",
        "stage", "status", "doc_count", "gaps", "findings", "opportunities")}


class _Server(ThreadingHTTPServer):
    # Avoid a TIME_WAIT socket from a just-stopped backend blocking an immediate restart.
    allow_reuse_address = True


def main() -> int:
    try:
        srv = _Server(("127.0.0.1", PORT), Handler)
    except OSError as e:
        # The usual cause: a previous Console backend is still running on this port. Fail with a
        # clear, actionable message instead of a raw traceback (which the UI would see as a silent
        # "Failed to fetch" — the backend never came up).
        import errno
        if e.errno == errno.EADDRINUSE:
            print(f"error: port {PORT} is already in use — another Discovery Console backend is "
                  f"probably running.\n"
                  f"  Stop it (find it with:  lsof -ti tcp:{PORT} | xargs kill), or start this one "
                  f"on a different port:  DISCOVERY_UI_PORT=8743 uv run python server.py",
                  flush=True)
            return 1
        raise
    print(f"Discovery Console backend on http://127.0.0.1:{PORT}  (Ctrl-C to stop)", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
