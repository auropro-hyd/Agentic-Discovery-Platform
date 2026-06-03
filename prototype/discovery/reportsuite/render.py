"""Render a SynthesisContent into the 6-report client suite (standalone HTML + index).

Reads ONLY SynthesisContent — tool names, locators and filenames are unreachable by type. Each
report is leak-guarded before write; Report 01 additionally passes a factual-language lint.
"""
from __future__ import annotations

import html
from pathlib import Path

from .. import docnames
from ..models import SynthesisContent
from ..report import assert_no_leaks
from ..synthesis import assert_factual
from .assets import CSS, JS

REPORTS = [
    ("01-current-state", "Current State Assessment"),
    ("02-pain-points", "Pain Points & Opportunities"),
    ("03-recommendation", "Transformation Recommendation"),
    ("04-opportunity-portfolio", "AI Opportunity Portfolio"),
    ("05-roadmap", "Transformation Roadmap"),
    ("06-supporting-artefacts", "Supporting Artefacts"),
]
_PATTERN_LABEL = {"hitl_workflow": "HITL Workflow", "automation": "Automation Pipeline",
                  "ai_agent": "AI Agent"}
_QUAD = [("do_first", "Do First"), ("plan_for", "Plan For"),
         ("consider", "Consider"), ("deprioritise", "Deprioritise")]


def render_suite(s: SynthesisContent, meta: dict, outdir: Path,
                 suppress_names: list[str] | None = None) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "assets").mkdir(exist_ok=True)
    (outdir / "assets" / "report.css").write_text(CSS, encoding="utf-8")
    (outdir / "assets" / "report.js").write_text(JS, encoding="utf-8")
    # render each source document to a readable page so citations can click through (provenance)
    _render_source_pages(s, outdir, suppress_names)
    fns = {"01-current-state": r01, "02-pain-points": r02, "03-recommendation": r03,
           "04-opportunity-portfolio": r04, "05-roadmap": r05, "06-supporting-artefacts": r06}
    for slug, title in REPORTS:
        body = _scrub_names(fns[slug](s, meta), suppress_names)
        text = _strip_tags(body)
        # tool/jargon leaks still hard-fail; suppressed client names are scrubbed above, so the
        # guard here is a backstop that should never trip on a name post-scrub.
        assert_no_leaks(text, suppress_names=suppress_names)
        if slug == "01-current-state":
            assert_factual(text)
        (outdir / f"{slug}.html").write_text(_page(title, body, slug, meta), encoding="utf-8")
    index = outdir / "index.html"
    index_body = _scrub_names(fns["01-current-state"](s, meta), suppress_names)
    index.write_text(_page(REPORTS[0][1], index_body, "01-current-state", meta, is_index=True),
                     encoding="utf-8")
    return index


# ---- report bodies (return HTML fragments) --------------------------------
def r01(s: SynthesisContent, meta) -> str:
    cs = s.current_state
    dom = esc(meta.get("domain_label", "this process"))
    at_client = f" at {esc(meta['client'])}" if meta.get("client") else ""
    h = [f"<h1>Current State Assessment</h1>",
         f"<p class='lede'>How {dom} runs today{at_client}. "
         "A factual baseline — no judgements.</p>",
         "<h2>Domain overview</h2>", f"<p>{esc(cs.domain_overview)}</p>",
         f"<p>{esc(cs.process_summary)}</p>",
         "<h2>Process flow</h2>",
         process_flow_svg(cs.process_flow),
         "<table><thead><tr><th>Step</th><th>Performed by</th><th>System</th>"
         "<th>What happens</th></tr></thead><tbody>"]
    for st in cs.process_flow:
        h.append(f"<tr><td>{st.seq}. {esc(st.name)}</td><td>{esc(st.actor)}</td>"
                 f"<td>{esc(st.system)}</td><td>{esc(st.description)}</td></tr>")
    h.append("</tbody></table>")
    h.append("<h2>Process inventory</h2><ul>")
    for it in cs.process_inventory:
        h.append(f"<li><strong>{esc(it.name)}</strong> — {esc(it.purpose)}</li>")
    h.append("</ul>")
    h.append("<h2>Ownership map</h2>"
             "<table><thead><tr><th>Activity</th><th>Responsible</th><th>Accountable</th>"
             "</tr></thead><tbody>")
    for r in cs.ownership_map:
        h.append(f"<tr><td>{esc(r.activity)}</td><td>{esc(r.responsible)}</td>"
                 f"<td>{esc(r.accountable)}</td></tr>")
    h.append("</tbody></table>")
    h.append("<h2>System inventory</h2>"
             "<table><thead><tr><th>System</th><th>Role</th><th>System of record for</th>"
             "</tr></thead><tbody>")
    for it in cs.system_inventory:
        h.append(f"<tr><td>{esc(it.name)}</td><td>{esc(it.purpose)}</td>"
                 f"<td>{esc(it.system_of_record_for)}</td></tr>")
    h.append("</tbody></table>")
    h.append("<h2>Handoff catalogue</h2><ul>")
    for ho in cs.handoff_catalogue:
        h.append(f"<li>{esc(ho.from_step)} → {esc(ho.to_step)} "
                 f"<span class='prov'>({esc(ho.mechanism)})</span></li>")
    h.append("</ul>")
    return "\n".join(h)


def r02(s: SynthesisContent, meta) -> str:
    h = ["<h1>Pain Points &amp; Opportunities</h1>",
         "<p class='lede'>The issues found in the discovery, ranked by business impact, "
         "each mapped to a recommended opportunity.</p>"]
    for pp in sorted(s.pain_points, key=lambda p: p.impact_rank):
        h.append("<div class='card'>")
        h.append(f"<h3>{esc(pp.title)}</h3>")
        h.append(f"<p>{esc(pp.description)}</p>")
        if pp.quantified:
            h.append("<p>" + " &nbsp; ".join(_metric(n) for n in pp.quantified) + "</p>")
        h.append(f"<p><strong>Root cause:</strong> {esc(pp.root_cause)}</p>")
        h.append(f"<p><strong>Pattern:</strong> {esc(pp.failure_pattern)}</p>")
        if pp.opportunity_signal:
            h.append(f"<p><strong>Addressed by:</strong> {esc(pp.opportunity_signal)} "
                     f"(see the Opportunity Portfolio)</p>")
        h.append(f"<p class='prov'>Where this comes from: {_cite_links(pp.sources)}</p>")
        h.append("</div>")
    if s.cross_process_patterns:
        h.append("<h2>Cross-process patterns</h2>")
        for c in s.cross_process_patterns:
            h.append(f"<p><strong>{esc(c.get('pattern',''))}.</strong> "
                     f"{esc(c.get('description',''))}</p>")
    return "\n".join(h)


def r03(s: SynthesisContent, meta) -> str:
    by_q = {q: [o for o in s.opportunities if o.matrix_quadrant.value == q] for q, _ in _QUAD}
    h = ["<h1>Transformation Recommendation</h1>",
         "<p class='lede'>Which opportunities to pursue, in what order, by value and "
         "feasibility.</p>",
         "<h2>Value vs. feasibility</h2>", "<div class='matrix'>"]
    for q, label in _QUAD:
        chips = "".join(f"<span class='chip'>{esc(o.title)}</span>" for o in by_q[q])
        h.append(f"<div class='quad {q}'><h4>{label}</h4>{chips or '<span class=prov>—</span>'}</div>")
    h.append("</div>")
    h.append("<h2>Opportunity ratings</h2>"
             "<table><thead><tr><th>Opportunity</th><th>Pattern</th><th>Value</th>"
             "<th>Feasibility</th><th>Sequence</th></tr></thead><tbody>")
    for o in s.opportunities:
        seq = ("Requires Customer Master Reconciliation first" if o.dependencies
               else "Can start now")
        h.append(f"<tr><td>{esc(o.title)}</td><td>{_PATTERN_LABEL.get(o.pattern.value,'')}</td>"
                 f"<td>{esc(o.value_rating.title())}</td>"
                 f"<td>{esc(o.feasibility_rating.title())}</td><td>{esc(seq)}</td></tr>")
    h.append("</tbody></table>")
    h.append(f"<h2>Sequencing rationale</h2><p>{esc(s.sequencing_rationale)}</p>")
    if s.dependency_notes:
        h.append(f"<p><strong>Dependencies:</strong> {esc(s.dependency_notes)}</p>")
    h.append(f"<h2>Strategic readiness</h2><p>{esc(s.strategic_readiness)}</p>")
    return "\n".join(h)


def r04(s: SynthesisContent, meta) -> str:
    h = ["<h1>AI Opportunity Portfolio</h1>",
         "<p class='lede'>The recommended interventions in full — what the problem is, how the "
         "process changes, and what it delivers.</p>"]
    for o in s.opportunities:
        h.append("<div class='card'>")
        h.append(f"<h3>{esc(o.title)}<span class='pattern'>{_PATTERN_LABEL.get(o.pattern.value,'')}"
                 f"</span></h3>")
        h.append(f"<p>{esc(o.overview)}</p>")
        h.append("<div class='ba-grid'>")
        h.append("<div class='col before'><h4>Before</h4>" + _steps(o.before_process) + "</div>")
        h.append("<div class='col after'><h4>After</h4>" + _steps(o.after_process) + "</div>")
        h.append("</div>")
        bi = o.business_impact
        h.append("<p><strong>Business impact.</strong> " + esc(bi.narrative))
        if bi.quantified:
            h.append(" " + " &nbsp; ".join(_metric(n) for n in bi.quantified))
        h.append("</p>")
        if bi.derivation:
            h.append(f"<p class='prov'>How we get there: {esc(bi.derivation)}</p>")
        h.append(f"<p><strong>How it's delivered.</strong> {esc(o.implementation_approach)}</p>")
        if o.required_integrations:
            h.append("<p><strong>Connects:</strong> " +
                     ", ".join(esc(x) for x in o.required_integrations) + "</p>")
        if o.success_metrics:
            h.append("<p><strong>Success looks like:</strong></p><ul>" +
                     "".join(f"<li>{esc(x)}</li>" for x in o.success_metrics) + "</ul>")
        dep = ("Requires Customer Master Reconciliation first." if o.dependencies
               else "Independent — can start immediately.")
        if o.prerequisite_for:
            dep += " Prerequisite for the AI Credit Decisioning step."
        h.append(f"<p><strong>Dependencies:</strong> {esc(dep)}</p>")
        if o.risks:
            h.append("<p><strong>Risks:</strong></p><ul>" +
                     "".join(f"<li>{esc(x)}</li>" for x in o.risks) + "</ul>")
        h.append(f"<p class='prov'>Where this comes from: {_cite_links(o.sources)}</p>")
        h.append("</div>")
    return "\n".join(h)


def r05(s: SynthesisContent, meta) -> str:
    posture = s.strategy_profile.get("posture", "").replace("_", " + ")
    h = ["<h1>Transformation Roadmap</h1>",
         f"<p class='lede'>Sequenced across three horizons, aimed at a "
         f"<strong>{esc(posture)}</strong> direction.</p>"]
    for hz in s.roadmap:
        h.append(f"<div class='horizon'><h3>{esc(hz.horizon)} — {esc(hz.theme)} "
                 f"<span class='win'>({esc(hz.window)})</span></h3><ul>")
        for it in hz.items:
            tag = " <span class='chip'>opportunity</span>" if it.opportunity_id else ""
            h.append(f"<li><strong>{esc(it.title)}</strong>{tag} — {esc(it.rationale)}</li>")
        h.append("</ul></div>")
    return "\n".join(h)


def r06(s: SynthesisContent, meta) -> str:
    h = ["<h1>Supporting Artefacts</h1>",
         "<p class='lede'>Reference material behind this assessment.</p>",
         "<h2>Source document index</h2>",
         "<table><thead><tr><th>Document</th><th>Type</th><th>What it is</th>"
         "<th>Findings it supported</th></tr></thead><tbody>"]
    for d in s.source_index:
        fnd = ", ".join(d.supported_findings) if d.supported_findings else "—"
        name = f"<a href='{_src_href(d.doc_id)}'>{esc(d.business_name)}</a>"
        h.append(f"<tr><td>{name}</td><td>{esc(d.doc_type)}</td>"
                 f"<td>{esc(d.what_we_read)}</td><td>{esc(fnd)}</td></tr>")
    h.append("</tbody></table>")
    h.append("<h2>System &amp; data-flow map</h2>")
    h.append("<p class='prov'>The full step-by-step process flow is in the Current State "
             "Assessment; this is the systems view of the same domain.</p>")
    h.append(data_flow_svg(s.current_state.process_flow))
    h.append("<h2>Companion material</h2><ul>"
             "<li>Ownership and handoff maps</li>"
             "<li>Exception and workaround register</li></ul>")
    h.append("<p class='badge-note'>A full technical trace of every figure in this assessment is "
             "available to your data team on request.</p>")
    return "\n".join(h)


# ---- diagrams (self-contained SVG, no external deps) ----------------------
_SVG_DEFS = (
    "<defs>"
    "<marker id='arr' markerWidth='10' markerHeight='10' refX='8' refY='3.2' orient='auto'>"
    "<path d='M0,0 L8,3.2 L0,6.4 Z' fill='#1f6feb'/></marker>"
    "<linearGradient id='hdr' x1='0' y1='0' x2='0' y2='1'>"
    "<stop offset='0' stop-color='#2b76f0'/><stop offset='1' stop-color='#1f6feb'/></linearGradient>"
    "<filter id='sh' x='-20%' y='-20%' width='140%' height='150%'>"
    "<feDropShadow dx='0' dy='1.5' stdDeviation='2.5' flood-color='#1a2230' flood-opacity='0.12'/>"
    "</filter></defs>"
)


def process_flow_svg(steps) -> str:
    """The hero process-flow visual for Report 01: a wrapping chain of polished node cards with a
    coloured header band (step number + name), actor and system on separate lines, soft shadow, and
    blue connecting arrows. Pure inline SVG (offline-safe). Generated from this run's steps."""
    if not steps:
        return "<p class='prov'>No process flow available.</p>"
    WRAP = 3
    NW, NH = 234, 104
    GAP_X, GAP_Y = 58, 52
    PAD = 16
    HDR = 30                       # coloured header band height
    rows = [steps[i:i + WRAP] for i in range(0, len(steps), WRAP)]
    cols = min(WRAP, len(steps))
    width = PAD * 2 + cols * NW + (cols - 1) * GAP_X
    height = PAD * 2 + len(rows) * NH + (len(rows) - 1) * GAP_Y
    out = [f"<svg class='flow' viewBox='0 0 {width} {height}' width='100%' "
           f"role='img' aria-label='Process flow diagram' xmlns='http://www.w3.org/2000/svg'>",
           _SVG_DEFS]

    def node_xy(idx):
        r, c = idx // WRAP, idx % WRAP
        return PAD + c * (NW + GAP_X), PAD + r * (NH + GAP_Y)

    for i in range(len(steps) - 1):
        x1, y1 = node_xy(i)
        x2, y2 = node_xy(i + 1)
        if (i // WRAP) == ((i + 1) // WRAP):
            out.append(f"<line x1='{x1 + NW}' y1='{y1 + NH/2}' x2='{x2 - 3}' y2='{y2 + NH/2}' "
                       f"stroke='#1f6feb' stroke-width='2.2' marker-end='url(#arr)'/>")
        else:
            sx, sy = x1 + NW / 2, y1 + NH
            ex, ey = x2 + NW / 2, y2 - 3
            midy = sy + GAP_Y / 2
            out.append(f"<path d='M{sx},{sy} L{sx},{midy} L{ex},{midy} L{ex},{ey}' fill='none' "
                       f"stroke='#1f6feb' stroke-width='2.2' marker-end='url(#arr)'/>")

    for i, st in enumerate(steps):
        x, y = node_xy(i)
        actor = getattr(st, "actor", "")
        system = getattr(st, "system", "")
        out.append(f"<g filter='url(#sh)'>")
        out.append(f"<rect x='{x}' y='{y}' width='{NW}' height='{NH}' rx='12' fill='#fff' "
                   f"stroke='#dbe3ee' stroke-width='1'/>")
        # header band (rounded top only, via path)
        out.append(f"<path d='M{x},{y+12} a12,12 0 0 1 12,-12 h{NW-24} a12,12 0 0 1 12,12 "
                   f"v{HDR-12} h-{NW} z' fill='url(#hdr)'/>")
        out.append(f"<text x='{x+13}' y='{y+20}' font-size='13' font-weight='700' fill='#fff'>"
                   f"{st.seq}. {esc(_clip(st.name, 26))}</text>")
        if actor:
            out.append(f"<text x='{x+13}' y='{y+HDR+22}' font-size='11.5' fill='#1a2230'>"
                       f"<tspan font-weight='600'>Who </tspan>{esc(_clip(actor, 26))}</text>")
        if system:
            out.append(f"<text x='{x+13}' y='{y+HDR+44}' font-size='11.5' fill='#5b6776'>"
                       f"<tspan font-weight='600' fill='#1a2230'>System </tspan>"
                       f"{esc(_clip(system, 24))}</text>")
        out.append("</g>")
    out.append("</svg>")
    return ("<div class='flow-wrap'><div class='flow-cap'>How work moves, end to end</div>"
            + "".join(out) + "</div>")


def data_flow_svg(steps) -> str:
    """A DIFFERENT artefact for Supporting Artefacts (not a copy of the process flow): a system /
    data-flow map showing which business systems the process touches and the handoffs between them.
    Derived from the distinct systems named across the process steps."""
    # distinct systems in order of first appearance
    systems, seen = [], set()
    for st in steps:
        sysname = (getattr(st, "system", "") or "").strip()
        for part in [p.strip() for p in sysname.replace(" / ", "/").split("/") if p.strip()]:
            if part.lower() not in seen:
                seen.add(part.lower())
                systems.append(part)
    if len(systems) < 2:
        return "<p class='prov'>System map not available (too few named systems).</p>"
    NW, NH, GAP_X, PAD = 196, 58, 64, 16
    cols = min(4, len(systems))
    rows = [systems[i:i + 4] for i in range(0, len(systems), 4)]
    width = PAD * 2 + cols * NW + (cols - 1) * GAP_X
    height = PAD * 2 + len(rows) * NH + (len(rows) - 1) * 44
    out = [f"<svg class='flow' viewBox='0 0 {width} {height}' width='100%' role='img' "
           f"aria-label='System and data-flow map' xmlns='http://www.w3.org/2000/svg'>", _SVG_DEFS]

    def sxy(idx):
        r, c = idx // 4, idx % 4
        return PAD + c * (NW + GAP_X), PAD + r * (NH + 44)

    for i in range(len(systems) - 1):
        x1, y1 = sxy(i)
        x2, y2 = sxy(i + 1)
        if (i // 4) == ((i + 1) // 4):
            out.append(f"<line x1='{x1+NW}' y1='{y1+NH/2}' x2='{x2-3}' y2='{y2+NH/2}' "
                       f"stroke='#8aa6d6' stroke-width='2' stroke-dasharray='5 4' "
                       f"marker-end='url(#arr)'/>")
    for i, name in enumerate(systems):
        x, y = sxy(i)
        out.append(f"<g filter='url(#sh)'><rect x='{x}' y='{y}' width='{NW}' height='{NH}' rx='10' "
                   f"fill='#eaf1fe' stroke='#1f6feb' stroke-width='1.2'/>"
                   f"<text x='{x+NW/2}' y='{y+NH/2+5}' text-anchor='middle' font-size='13' "
                   f"font-weight='600' fill='#0a4bbd'>{esc(_clip(name, 22))}</text></g>")
    out.append("</svg>")
    return ("<div class='flow-wrap'><div class='flow-cap'>Systems the process touches, and how "
            "data moves between them</div>" + "".join(out) + "</div>")


def _clip(t: str, n: int) -> str:
    t = str(t)
    return t if len(t) <= n else t[: n - 1] + "…"


def _scrub_names(body: str, suppress_names) -> str:
    """Replace any suppressed organisation name in rendered report text with a neutral phrase.
    Belt-and-braces with the synthesis-prompt instruction: if the live agent still wrote the name,
    it's removed here rather than hard-failing the render. Whole-word, case-insensitive."""
    import re
    for name in (suppress_names or []):
        if not name:
            continue
        body = re.sub(rf"\b{re.escape(name)}\b", "the organisation", body, flags=re.I)
    return body


# ---- helpers --------------------------------------------------------------
def _steps(steps) -> str:
    out = []
    for st in steps:
        who = " · ".join(x for x in [st.actor, st.system] if x)
        fp = "".join(f"<span class='failpoint'>{esc(p)}</span>" for p in st.failure_points)
        out.append(f"<div class='step'><strong>{st.seq}. {esc(st.name)}</strong>"
                   f"<div class='who'>{esc(who)}</div><div>{esc(st.description)}</div>{fp}</div>")
    return "\n".join(out)


def _metric(n) -> str:
    return f"<span class='metric'>{esc(n.text or n.label)}</span>"


def _cite(refs) -> str:
    return docnames.business_phrase_list([r.doc_id for r in refs]) or "—"


def _src_href(doc_id: str) -> str:
    from .. import docnames as dn
    return f"sources/{dn.stem(doc_id)}.html"


def _cite_links(refs) -> str:
    """Like _cite but each source is a clickable link to its rendered source page (provenance)."""
    from .. import docnames as dn
    seen, out = set(), []
    for r in refs:
        sid = dn.stem(r.doc_id)
        if sid in seen:
            continue
        seen.add(sid)
        out.append(f"<a href='{_src_href(r.doc_id)}'>{esc(dn.friendly(r.doc_id))}</a>")
    if not out:
        return "—"
    if len(out) == 1:
        return out[0]
    return ", ".join(out[:-1]) + " and " + out[-1]


def _render_source_pages(s: SynthesisContent, outdir: Path, suppress_names) -> None:
    """Write a readable page per source document so citations can click through. CSV sources show
    a row-count + preview; narrative docs show their frozen text. Suppressed names are scrubbed."""
    from .. import docnames as dn, tools
    sdir = outdir / "sources"
    sdir.mkdir(exist_ok=True)
    for d in s.source_index:
        sid = dn.stem(d.doc_id)
        disp = _scrub_names(dn.friendly(sid), suppress_names)  # respect current noise words + scrub
        body = [f"<h1>{esc(disp)}</h1>",
                f"<p class='lede'>{esc(d.doc_type)} — referenced by findings: "
                f"{esc(', '.join(d.supported_findings) or '—')}</p>",
                "<p><a href='../06-supporting-artefacts.html'>&larr; back to the source index</a></p>"]
        text = tools.DOC_TEXT.get(sid)
        if text is None:  # a CSV source — show a compact preview
            path = tools.FILE_REGISTRY.get(sid)
            if path:
                import csv as _csv
                with path.open(encoding="utf-8-sig", newline="") as fh:
                    rdr = _csv.reader(fh)
                    rows = list(rdr)
                head = rows[0] if rows else []
                body.append(f"<p class='prov'>{len(rows)-1} rows · columns: {esc(', '.join(head))}</p>")
                prev = rows[1:21]
                body.append("<table><thead><tr>" + "".join(f"<th>{esc(c)}</th>" for c in head)
                            + "</tr></thead><tbody>"
                            + "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>"
                                      for r in prev) + "</tbody></table>")
                if len(rows) - 1 > 20:
                    body.append(f"<p class='prov'>… {len(rows)-1-20} more rows</p>")
        else:
            body.append("<pre class='srcdoc'>" + esc(text) + "</pre>")
        html_body = _scrub_names("\n".join(body), suppress_names)
        (sdir / f"{sid}.html").write_text(_src_page(disp, html_body), encoding="utf-8")


def _src_page(title: str, body: str) -> str:
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<title>{esc(title)}</title><link rel='stylesheet' href='../assets/report.css'>"
            f"</head><body><main class='content'>{body}</main></body></html>")


def esc(x) -> str:
    return html.escape(str(x or ""))


def _strip_tags(htmlfrag: str) -> str:
    import re
    return re.sub(r"<[^>]+>", " ", htmlfrag)


def _page(title: str, body: str, active: str, meta: dict, is_index=False) -> str:
    nav = []
    for slug, label in REPORTS:
        num = slug.split("-")[0]
        cls = " active" if slug == active else ""
        nav.append(f"<a class='{cls.strip()}' href='{slug}.html'>"
                   f"<span class='num'>{num}</span>{esc(label)}</a>")
    client = (meta.get("client") or "").strip()
    domain = esc(meta.get("domain_label", "Discovery"))
    # title: "<report> — <client>" only when we have a client name; else just the report
    page_title = f"{esc(title)} — {esc(client)}" if client else esc(title)
    # sidebar heading: the client name if known, otherwise the engagement (domain) — never a placeholder
    heading = esc(client) if client else f"{domain} Discovery"
    sub = f"{domain} Discovery" if client else "Discovery assessment"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<link rel="stylesheet" href="assets/report.css"></head><body>
<div class="layout">
<nav class="sidebar">
  <h1>{heading}</h1>
  <div class="sub">{sub}</div>
  {''.join(nav)}
</nav>
<main class="content">
{body}
</main></div></body></html>"""
