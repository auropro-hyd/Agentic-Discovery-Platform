"""Discovery-refresh: diff a new run against the previous one for the same domain.

Turns the point-in-time accelerator into a repeatable asset — on a re-run you see what's NEW,
what's been RESOLVED (gone since last time), and what CHANGED (same issue, different numbers),
rather than re-reading the whole report. Pure Python, no LLM.

Findings are matched across runs by a normalized title key (titles are stable descriptors of the
issue; ids are per-run). A finding is "changed" if its headline computed values differ.
"""
from __future__ import annotations

import re


def _key(title: str) -> str:
    """Stable match key: lowercased, alphanumerics only (ignores punctuation/number drift)."""
    return re.sub(r"[^a-z0-9 ]", "", (title or "").lower()).strip()


def _values(finding: dict) -> dict:
    """Headline numbers of a finding, keyed by label, for change-detection."""
    out = {}
    for cv in finding.get("computed_values", []):
        out[cv.get("label", "")] = cv.get("value")
    return out


def diff_runs(prev: dict, curr: dict) -> dict:
    """Return new / resolved / changed / unchanged finding lists comparing two emit_findings
    payloads (or DiscoveryResult dicts with a 'findings' list)."""
    pf = {_key(f.get("title", "")): f for f in prev.get("findings", [])}
    cf = {_key(f.get("title", "")): f for f in curr.get("findings", [])}
    new, resolved, changed, unchanged = [], [], [], []
    for k, f in cf.items():
        if k not in pf:
            new.append(f.get("title", ""))
        elif _values(f) != _values(pf[k]):
            changed.append({"title": f.get("title", ""),
                            "was": _values(pf[k]), "now": _values(f)})
        else:
            unchanged.append(f.get("title", ""))
    for k, f in pf.items():
        if k not in cf:
            resolved.append(f.get("title", ""))
    return {"new": new, "resolved": resolved, "changed": changed, "unchanged": unchanged}


def summary_line(d: dict) -> str:
    return (f"refresh vs. previous run: {len(d['new'])} new, {len(d['resolved'])} resolved, "
            f"{len(d['changed'])} changed, {len(d['unchanged'])} unchanged")
