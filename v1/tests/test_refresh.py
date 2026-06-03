"""Offline tests for discovery-refresh (run-over-run diff). Pure Python, no API."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import refresh  # noqa: E402


def _f(title, **vals):
    return {"title": title,
            "computed_values": [{"label": k, "value": v} for k, v in vals.items()]}


def test_diff_classifies_new_resolved_changed_unchanged():
    prev = {"findings": [
        _f("Customer master conflict", delta=600000),
        _f("EDI undocumented", pct=67.3),
        _f("Old issue now fixed", count=5),
    ]}
    curr = {"findings": [
        _f("Customer master conflict", delta=600000),     # unchanged
        _f("EDI undocumented", pct=72.0),                 # changed (pct moved)
        _f("Brand new finding", count=3),                 # new
    ]}
    d = refresh.diff_runs(prev, curr)
    assert d["new"] == ["Brand new finding"]
    assert d["resolved"] == ["Old issue now fixed"]
    assert [c["title"] for c in d["changed"]] == ["EDI undocumented"]
    assert d["unchanged"] == ["Customer master conflict"]
    assert d["changed"][0]["was"] == {"pct": 67.3}
    assert d["changed"][0]["now"] == {"pct": 72.0}


def test_baseline_diff_all_new():
    d = refresh.diff_runs({"findings": []}, {"findings": [_f("First finding", x=1)]})
    assert d["new"] == ["First finding"] and not d["resolved"] and not d["changed"]


def test_title_match_ignores_punctuation():
    # same issue, title punctuation/casing differs -> still matched (not new/resolved)
    prev = {"findings": [_f("EDI: undocumented channel!", pct=67)]}
    curr = {"findings": [_f("EDI undocumented channel", pct=67)]}
    d = refresh.diff_runs(prev, curr)
    assert d["unchanged"] == ["EDI undocumented channel"] and not d["new"] and not d["resolved"]
