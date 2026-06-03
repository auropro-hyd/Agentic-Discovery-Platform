"""Map an emit_findings payload (agent or scripted) onto the report models.

PR-A leak fix: the stakeholder layer cites SOURCE DOCUMENTS in business language via cite();
it never shows tool names, column names, locators, or filenames. The raw per-number trace
(computed_values / from_tool / locator) is preserved separately in the internal JSON.
"""
from __future__ import annotations

from . import docnames
from .models import (
    ConfidenceTier, DiscoveryResult, Document, Finding, Recommendation, Severity, SourceRef,
)


def _sev(v):
    try: return Severity(v)
    except ValueError: return Severity.AMBER


def _conf(v):
    try: return ConfidenceTier(v)
    except ValueError: return ConfidenceTier.AMBER


def cite(refs: list[SourceRef]) -> str:
    """Business citation for a set of sources — friendly phrases only, no doc_id/locator/tool."""
    return docnames.business_phrase_list([r.doc_id for r in refs])


def to_result(payload: dict, domain: str, domain_label: str, documents: list[Document],
              effort_comparison: dict) -> DiscoveryResult:
    findings = []
    for f in payload["findings"]:
        sources = [SourceRef(doc_id=s.get("doc_id", ""), locator=s.get("locator", ""),
                             quote=s.get("quote", "")) for s in f.get("sources", [])]
        # Fold ONLY business-safe derived detail into the description: computed numbers with
        # their label (no tool name), and narrative quotes attributed to the friendly doc name.
        derived = []
        for cv in f.get("computed_values", []):
            derived.append(f"{cv['label']}: {_fmt(cv['value'])}")
        for nv in f.get("narrative_values", []):
            attribution = docnames.friendly(nv["doc_id"]) if nv.get("doc_id") else ""
            derived.append(f"{nv['label']}: {_fmt(nv.get('value', ''))} "
                           f"(“{nv.get('quote', '')}” — {attribution})")
        desc = f.get("description", "")
        if derived:
            desc = desc + "\n\nWhat the data shows:\n" + "\n".join(f"- {d}" for d in derived)
        findings.append(Finding(
            id=f["id"], title=f["title"], severity=_sev(f.get("severity")),
            description=desc, business_consequence=f.get("business_consequence", ""),
            confidence=_conf(f.get("confidence")), sources=sources,
        ))
    result = DiscoveryResult(
        domain=domain, domain_label=domain_label, documents=documents,
        findings=findings, recommendations=[], effort_comparison=effort_comparison,
        process_summary=payload.get("_process_summary", ""),
    )
    result.raw_payload = payload  # preserved for the internal_trace JSON (audit)
    return result


def _fmt(v):
    if isinstance(v, float) and v.is_integer():
        return f"{int(v):,}"
    if isinstance(v, (int, float)):
        return f"{v:,}"
    return str(v)
