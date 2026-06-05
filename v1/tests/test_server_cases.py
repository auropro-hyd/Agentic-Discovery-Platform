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
