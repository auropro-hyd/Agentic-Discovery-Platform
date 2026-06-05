"""Guards for the Discovery Console case metadata (server.py). server.py is omitted from the
coverage gate (HTTP glue, exercised live), but the saved-case definition + the dashboard-card
projection are data the UI binds to, so they're worth a fast, server-free check.

The HTTP routes themselves (/api/cases, /api/case/:id, /archive/...) are verified against a running
backend; here we assert the in-memory case shape and that the curated archive/ artefacts it points
at actually exist on disk (so a stage never iframes a 404).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import server  # noqa: E402


def test_case_card_projects_summary_fields():
    card = server._case_card(server.OPELLA_CASE)
    # the card is the dashboard-list row — exactly these fields, no internal extras
    assert set(card) == {
        "id", "title", "domain", "client", "run_date", "duration_minutes",
        "stage", "status", "doc_count", "gaps", "findings", "opportunities"}
    assert card["domain"] == "o2c"
    assert 30 <= card["duration_minutes"] <= 38          # the presentation duration window
    assert card["doc_count"] == len(server.OPELLA_INPUT_DOCS)


def test_case_gap_counts_mirror_audit_trail():
    g = server.OPELLA_CASE["gaps"]
    # mirrors archive/preview/07-copilot-audit-trail.html (9 questions; 3 high / 2 clarif / 4 amber)
    assert g == {"questions": 9, "high_resolved": 3, "clarifications": 2, "carried_forward": 4}


def test_gap_ledger_matches_the_summary_counts():
    """The native decision ledger (rendered by the Co-pilot stage) must agree with the gap-gate
    summary counts, and every row must carry the fields the UI binds to."""
    ledger = server.OPELLA_GAP_LEDGER
    g = server.OPELLA_CASE["gaps"]
    assert len(ledger) == g["questions"]
    by_sev = {s: sum(1 for r in ledger if r["severity"] == s) for s in ("high", "clarification", "amber")}
    assert by_sev["high"] == g["high_resolved"]
    assert by_sev["clarification"] == g["clarifications"]
    assert by_sev["amber"] == g["carried_forward"]
    for r in ledger:
        assert {"id", "severity", "status", "question", "decision", "resolves"} <= set(r)
        assert r["severity"] in {"high", "clarification", "amber"}


def test_archive_artefacts_exist_on_disk():
    """Every archive/ path a stage points at must exist — otherwise the iframe/link 404s."""
    assert (server.ARCHIVE / "preview" / "07-copilot-audit-trail.html").is_file()
    assert (server.ARCHIVE / "preview" / "index.html").is_file()
    for r in server.OPELLA_REPORTS:
        assert (server.ARCHIVE / "output" / r["file"]).is_file(), r["file"]
    for d in server.OPELLA_INPUT_DOCS:
        assert (server.ARCHIVE / "input" / d["name"]).is_file(), d["name"]


def test_input_doc_kinds_are_known():
    # the UI colour-codes by kind; keep them to the handled set
    assert {d["kind"] for d in server.OPELLA_INPUT_DOCS} <= {"pdf", "csv", "txt"}


# ── "Initiate new case" upload helpers (do_POST /api/ingest support) ──────────
def test_slugify_makes_a_safe_domain():
    assert server._slugify("Acme · Procure-to-Pay 2026!") == "acme-procure-to-pay-2026"
    assert server._slugify("   ") == "case"            # empty → a sensible default, never ""
    assert len(server._slugify("x" * 200)) <= 40       # bounded so it can't blow up a path


def test_safe_name_strips_path_components():
    # an uploaded filename must never escape inputs/<slug>/ — only the basename survives
    assert server._safe_name("../../etc/passwd") == "passwd"
    assert server._safe_name("/abs/report.pdf") == "report.pdf"
    assert server._safe_name("plain.csv") == "plain.csv"


def test_ingest_accepts_only_pipeline_extensions():
    # the picker offers these; the backend enforces them so a bad upload can't reach the pipeline
    assert {".pdf", ".csv", ".txt"} <= server.INGEST_EXTS
    assert ".exe" not in server.INGEST_EXTS and ".sh" not in server.INGEST_EXTS


def test_run_tracks_label_and_latest_stage():
    """The in-progress indicator (/api/runs) reads Run.label + Run.stage; emitting a stage event
    must advance Run.stage, and the friendly label defaults to the domain."""
    r = server.Run("o2c", label="Acme · O2C")
    assert r.label == "Acme · O2C" and r.stage == "upload" and r.ok is None and not r.done
    r.emit({"type": "stage", "stage": "assessment", "state": "active"})
    assert r.stage == "assessment"
    assert server.Run("p2p").label == "P2P"          # no label → domain (upper) is the fallback
