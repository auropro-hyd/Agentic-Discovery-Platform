"""The human-in-the-loop SME resolution step.

This is the trust moment of the demo: the platform does not decide autonomously. For each
high-severity finding it surfaces the contradiction, the source documents, and 2-3 ranked
candidate answers. The SME picks one (or overrides), and that choice is recorded with its
provenance.

Three modes:
  interactive  - prompt the operator to choose per finding (the live demo)
  auto         - apply choices from a _resolutions.json (consistent / non-interactive)
  skip         - leave findings unresolved (e.g. amber items carried forward)
"""
from __future__ import annotations

from .models import Finding, Severity


def resolve_interactive(findings: list[Finding]) -> None:
    high = [f for f in findings if f.severity == Severity.HIGH]
    if not high:
        print("\nNo high-severity findings need SME input. Amber items carried forward.")
        return
    print(f"\n{'='*70}\n{len(high)} finding(s) need a quick SME decision.\n{'='*70}")
    for f in high:
        _present(f)
        choice = _ask(f)
        if choice:
            f.resolved = True
            f.chosen_candidate_id = choice.id
            f.resolution_note = choice.summary
            print(f"  -> Resolved: {choice.summary}\n")


def resolve_auto(findings: list[Finding], resolutions: dict) -> None:
    for f in findings:
        r = resolutions.get(f.id)
        if not r:
            continue
        chosen_id = r.get("chosen")
        cand = next((c for c in f.candidates if c.id == chosen_id), None)
        f.resolved = True
        f.chosen_candidate_id = chosen_id
        f.resolution_note = r.get("note") or (cand.summary if cand else "")


def _present(f: Finding) -> None:
    print(f"\n[{f.id}] {f.title}  ({f.severity.value.upper()})")
    print(f"  {f.description}")
    if f.business_consequence:
        print(f"  Business consequence: {f.business_consequence}")
    srcs = ", ".join(s.doc_id for s in f.sources)
    print(f"  Evidence from: {srcs}")
    print("  Candidate resolutions:")
    for i, c in enumerate(f.candidates, 1):
        strength = f" [{c.evidence_strength}]" if c.evidence_strength else ""
        print(f"    {i}. {c.summary}{strength}")
        if c.rationale:
            print(f"       {c.rationale}")


def _ask(f: Finding):
    if not f.candidates:
        return None
    while True:
        raw = input(f"  Choose 1-{len(f.candidates)} (or Enter to skip): ").strip()
        if raw == "":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(f.candidates):
            return f.candidates[int(raw) - 1]
        print("  Invalid choice.")
