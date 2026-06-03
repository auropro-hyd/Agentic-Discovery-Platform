"""Render the DiscoveryResult to a Markdown report and a styled HTML report.

The report is organised around the three trust pillars:
  1. Business Process - how the process actually works
  2. Findings - contradictions/gaps, each with source citations and SME resolution
  3. Transformation Assessment - recommendations, each with a justification + references
Plus an effort-comparison block (the stakeholder-effort reduction story) and a sources
appendix. Provenance is shown throughout - that is the point.
"""
from __future__ import annotations

import html
import re
from . import docnames
from .models import ConfidenceTier, DiscoveryResult, Finding, Severity

_SEV_BADGE = {Severity.HIGH: "🔴 High", Severity.AMBER: "🟡 Amber", Severity.INFO: "ℹ️ Info"}
_CONF_BADGE = {
    ConfidenceTier.VERIFIED: "🟢 Verified",
    ConfidenceTier.AMBER: "🟡 Amber",
    ConfidenceTier.GAP: "🔴 Gap",
}


def render_markdown(r: DiscoveryResult) -> str:
    L: list[str] = []
    L.append(f"# {r.domain_label} Discovery — Current State & Opportunity Assessment")
    L.append("")
    L.append("_Produced by the AuroPro discovery platform from your operational documents. "
             "Every finding cites the business documents it rests on._")
    L.append("")

    # inputs
    L.append("## Documents read")
    L.append("")
    L.append("| Document | Type |")
    L.append("|---|---|")
    for d in r.documents:
        L.append(f"| {docnames.friendly(d.doc_id)} | {docnames.kind(d.doc_id)} |")
    L.append("")

    # pillar 1: process
    L.append("## 1. How this process actually works")
    L.append("")
    L.append(r.process_summary or "_(not generated)_")
    L.append("")

    # pillar 2: findings
    L.append("## 2. Findings — contradictions & gaps")
    L.append("")
    for f in r.findings:
        L.append(f"### [{f.id}] {f.title}")
        L.append("")
        L.append(f"**Severity:** {_SEV_BADGE.get(f.severity, f.severity.value)} &nbsp; "
                 f"**Confidence:** {_CONF_BADGE.get(f.confidence, f.confidence.value)}")
        L.append("")
        L.append(f.description)
        if f.business_consequence:
            L.append("")
            L.append(f"**Business consequence:** {f.business_consequence}")
        L.append("")
        L.append(f"**Where this comes from:** {_cite(f)}")
        L.append("")
        if f.candidates:
            L.append("**Candidate resolutions (ranked):**")
            for c in f.candidates:
                mark = " ✅ *(SME selected)*" if f.resolved and c.id == f.chosen_candidate_id else ""
                strength = f" _[{c.evidence_strength}]_" if c.evidence_strength else ""
                L.append(f"- {c.summary}{strength}{mark}")
            L.append("")
        if f.resolved:
            L.append(f"**SME resolution:** {f.resolution_note}")
            L.append("")

    # pillar 3: recommendations
    L.append("## 3. Transformation assessment")
    L.append("")
    for horizon, label in (("now", "Now (0–6 months)"),
                           ("next", "Next (6–18 months)"),
                           ("later", "Later (18+ months)")):
        recs = [x for x in r.recommendations if x.horizon == horizon]
        if not recs:
            continue
        L.append(f"### {label}")
        L.append("")
        for rec in recs:
            L.append(f"- **{rec.title}** _({rec.intervention})_")
            if rec.justification:
                L.append(f"  - _Why:_ {rec.justification}")
            if rec.sources:
                L.append(f"  - _Based on:_ {docnames.business_phrase_list([s.doc_id for s in rec.sources])}")
        L.append("")

    # effort comparison
    if r.effort_comparison:
        ec = r.effort_comparison
        L.append("## Effort comparison")
        L.append("")
        trad, plat = ec.get("traditional", {}), ec.get("platform", {})
        L.append("| | Traditional discovery | With the platform |")
        L.append("|---|---|---|")
        L.append(f"| Duration | {trad.get('duration','—')} | {plat.get('duration','—')} |")
        L.append(f"| Stakeholders | {trad.get('stakeholders','—')} | "
                 f"{plat.get('touchpoints','—')} |")
        L.append(f"| Hours each | {trad.get('hours_each','—')} | (review & sign-off only) |")
        L.append("")
        L.append("_The compression is in extraction and first-draft synthesis. "
                 "Validation remains with the SME and the client._")
        L.append("")

    return "\n".join(L)


def _cite(f: Finding) -> str:
    return docnames.business_phrase_list([s.doc_id for s in f.sources]) or "—"


# ---- stakeholder-facing leak guard ----------------------------------------
_TOOL_TOKENS = (r"join_diff", r"group_by", r"filter_count", r"find_mentions",
                r"n_mismatch", r"sum_delta", r"key=", r"locator", r"from_tool")
_PARENS = re.compile(r"\((?:computed by|describe|aggregate)[^)]*\)", re.I)
_FILES = re.compile(r"\.(csv|pdf|txt|json)\b", re.I)
# Generic platform-jargon phrases (NO client name — the engine is client-agnostic).
_PHRASES = re.compile(r"\b(knowledge graph|evidence synthesis|gap detected|gap resolved|"
                      r"nodes and edges)\b", re.I)


def assert_no_leaks(md: str, suppress_names: list[str] | None = None) -> None:
    """Raise if any internal/tool term leaked into a stakeholder report. Run before md/html
    write only (never against the internal JSON).

    suppress_names: optional per-run list of names the run chose NOT to show on screen (e.g. a
    client name the operator suppressed for a demo). The engine hardcodes no client name.
    """
    bad = _PARENS.findall(md) + _FILES.findall(md) + _PHRASES.findall(md)
    for t in _TOOL_TOKENS:
        if re.search(rf"(?<![A-Za-z]){t}", md):
            bad.append(t)
    for name in (suppress_names or []):
        if name and re.search(rf"\b{re.escape(name)}\b", md, re.I):
            bad.append(name)
    if bad:
        raise AssertionError(f"stakeholder report leaked internal terms: {sorted(set(bad))}")


def render_html(markdown_text: str, title: str) -> str:
    """Minimal self-contained HTML wrapper. Renders the markdown as readable HTML
    without external libraries (good enough for the demo; polish later)."""
    body = _md_to_html(markdown_text)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         max-width: 880px; margin: 2rem auto; padding: 0 1.25rem; color: #1a1a1a;
         line-height: 1.55; }}
  h1 {{ border-bottom: 3px solid #0b5; padding-bottom: .4rem; }}
  h2 {{ margin-top: 2.2rem; border-bottom: 1px solid #ddd; padding-bottom: .3rem; }}
  h3 {{ margin-top: 1.6rem; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
  th, td {{ border: 1px solid #ddd; padding: .5rem .65rem; text-align: left;
            vertical-align: top; font-size: .92rem; }}
  th {{ background: #f5f7f9; }}
  code {{ background: #f0f2f4; padding: .1rem .35rem; border-radius: 4px; font-size: .88em; }}
  em {{ color: #555; }}
  li {{ margin: .2rem 0; }}
</style></head><body>
{body}
</body></html>
"""


def _md_to_html(md: str) -> str:
    """Tiny markdown renderer: headings, tables, lists, bold/italic/code, paragraphs.
    Intentionally small — covers what this report emits."""
    import re

    lines = md.split("\n")
    out: list[str] = []
    i = 0

    def inline(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
        s = s.replace("&amp;nbsp;", "&nbsp;")
        return s

    while i < len(lines):
        line = lines[i]
        if line.startswith("### "):
            out.append(f"<h3>{inline(line[4:])}</h3>"); i += 1; continue
        if line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>"); i += 1; continue
        if line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>"); i += 1; continue
        if line.startswith("|"):  # table block
            tbl = []
            while i < len(lines) and lines[i].startswith("|"):
                tbl.append(lines[i]); i += 1
            out.append(_html_table(tbl, inline)); continue
        if line.lstrip().startswith(("- ", "* ")):  # list block
            items = []
            while i < len(lines) and lines[i].lstrip().startswith(("- ", "* ")):
                indent = len(lines[i]) - len(lines[i].lstrip())
                items.append((indent, lines[i].lstrip()[2:])); i += 1
            out.append(_html_list(items, inline)); continue
        if line.strip() == "":
            i += 1; continue
        out.append(f"<p>{inline(line)}</p>"); i += 1
    return "\n".join(out)


def _html_table(rows: list[str], inline) -> str:
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    if len(cells) >= 2 and set("".join(cells[1]).replace("-", "").strip()) <= set():
        header, body = cells[0], cells[2:]
    else:
        header, body = cells[0], cells[1:]
    h = "".join(f"<th>{inline(c)}</th>" for c in header)
    b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>"
                for row in body)
    return f"<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"


def _html_list(items: list[tuple[int, str]], inline) -> str:
    # supports one level of nesting based on indent
    out = ["<ul>"]
    open_sub = False
    for indent, text in items:
        if indent >= 2:
            if not open_sub:
                out.append("<ul>"); open_sub = True
            out.append(f"<li>{inline(text)}</li>")
        else:
            if open_sub:
                out.append("</ul>"); open_sub = False
            out.append(f"<li>{inline(text)}</li>")
    if open_sub:
        out.append("</ul>")
    out.append("</ul>")
    return "\n".join(out)
