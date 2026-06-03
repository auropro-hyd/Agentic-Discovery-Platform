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
    ("00-executive-summary", "Executive Summary"),
    ("01-current-state", "Current State Assessment"),
    ("02-pain-points", "Pain Points & Opportunities"),
    ("03-recommendation", "Transformation Recommendation"),
    ("04-opportunity-portfolio", "AI Opportunity Portfolio"),
    ("05-roadmap", "Transformation Roadmap"),
    ("06-supporting-artefacts", "Supporting Artefacts"),
]
_PATTERN_LABEL = {"hitl_workflow": "HITL Workflow", "automation": "Automation Pipeline",
                  "modernisation": "Modernisation",
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
    fns = {"00-executive-summary": r00, "01-current-state": r01, "02-pain-points": r02,
           "03-recommendation": r03, "04-opportunity-portfolio": r04, "05-roadmap": r05,
           "06-supporting-artefacts": r06}
    for slug, title in REPORTS:
        body = _scrub_names(fns[slug](s, meta), suppress_names)
        text = _strip_tags(body)
        # tool/jargon leaks still hard-fail; suppressed client names are scrubbed above, so the
        # guard here is a backstop that should never trip on a name post-scrub.
        assert_no_leaks(text, suppress_names=suppress_names)
        if slug == "01-current-state":
            assert_factual(text)
        (outdir / f"{slug}.html").write_text(_page(title, body, slug, meta), encoding="utf-8")
    # index.html IS the executive summary (the natural entry point to the suite)
    index = outdir / "index.html"
    index_body = _scrub_names(fns["00-executive-summary"](s, meta), suppress_names)
    index.write_text(_page(REPORTS[0][1], index_body, "00-executive-summary", meta, is_index=True),
                     encoding="utf-8")
    return index


# ---- report bodies (return HTML fragments) --------------------------------
def r00(s: SynthesisContent, meta) -> str:
    """Executive Summary — the landing page that frames the whole assessment: a headline, the
    at-a-glance KPI strip, the top opportunities, and what was read. Visual-first, low prose."""
    es = s.executive_summary
    dom = esc(meta.get("domain_label", "this process"))
    at_client = f" at {esc(meta['client'])}" if meta.get("client") else ""
    headline = es.headline or (f"How {dom} runs today{at_client}, the issues found in the data, and "
                               "the opportunities to address them.")
    h = ["<h1>Executive Summary</h1>",
         f"<p class='lede'>{esc(headline)}</p>",
         kpi_tiles(s)]
    # situation / opportunity, side by side, short
    if es.situation or es.opportunity:
        h.append("<div class='two-col'>")
        if es.situation:
            h.append(f"<div class='panel'><h3>The situation</h3><p>{esc(es.situation)}</p></div>")
        if es.opportunity:
            h.append(f"<div class='panel'><h3>The opportunity</h3><p>{esc(es.opportunity)}</p></div>")
        h.append("</div>")
    # top opportunities as compact cards (the "do first" ones, else the first few)
    do_first = [o for o in s.opportunities if o.matrix_quadrant.value == "do_first"]
    top = do_first or s.opportunities[:3]
    if top:
        h.append("<h2>Where to start</h2>")
        h.append(value_feasibility_svg(s.opportunities))
        h.append("<div class='opp-cards'>")
        for o in top:
            pat = _PATTERN_LABEL.get(o.pattern.value, "")
            impact = ""
            if o.business_impact and o.business_impact.quantified:
                impact = " &nbsp; ".join(_metric(n) for n in o.business_impact.quantified[:2])
            h.append("<a class='opp-card' href='04-opportunity-portfolio.html'>"
                     f"<span class='pattern'>{esc(pat)}</span>"
                     f"<h4>{esc(o.title)}</h4>"
                     f"<p>{esc(_clip(o.overview, 150))}</p>"
                     + (f"<p class='kfig'>{impact}</p>" if impact else "")
                     + "</a>")
        h.append("</div>")
    # what we read
    if s.source_index:
        names = ", ".join(esc(d.business_name) for d in s.source_index[:8])
        more = f" and {len(s.source_index)-8} more" if len(s.source_index) > 8 else ""
        h.append("<h2>What we read</h2>")
        h.append(f"<p>{names}{more}. Every figure in this assessment is computed from these "
                 "sources and traces back to them.</p>")
    h.append("<p class='prov'>Read on: the "
             "<a href='01-current-state.html'>Current State</a>, the "
             "<a href='02-pain-points.html'>issues found</a>, and the recommended "
             "<a href='04-opportunity-portfolio.html'>opportunities</a>.</p>")
    return "\n".join(h)


def r01(s: SynthesisContent, meta) -> str:
    cs = s.current_state
    dom = esc(meta.get("domain_label", "this process"))
    at_client = f" at {esc(meta['client'])}" if meta.get("client") else ""
    h = [f"<h1>1. Current State Assessment</h1>",
         f"<p class='lede'>How {dom} runs today{at_client}. A factual baseline of the process, the "
         "systems that support it, and how information is structured — stated as fact, no judgements.</p>",
         "<h2>1.1 Domain overview</h2>", f"<p>{esc(cs.domain_overview)}</p>",
         f"<p>{esc(cs.process_summary)}</p>",
         "<h2>1.2 Process flow</h2>",
         "<p>The end-to-end flow, who performs each step and on which system:</p>",
         process_flow_svg(cs.process_flow),
         "<table><thead><tr><th>Step</th><th>Performed by</th><th>System</th>"
         "<th>What happens</th></tr></thead><tbody>"]
    for st in cs.process_flow:
        h.append(f"<tr><td>{st.seq}. {esc(st.name)}</td><td>{esc(st.actor)}</td>"
                 f"<td>{esc(st.system)}</td><td>{esc(st.description)}</td></tr>")
    h.append("</tbody></table>")

    # 1.3 deep per-system narrative profiles (the depth the prior-engagement bar has)
    if cs.system_profiles:
        h.append("<h2>1.3 Systems &amp; sources</h2>")
        h.append("<p>Each system that supports this process — what it is, how it is used, who owns "
                 "it, and the constraints observed.</p>")
        for p in cs.system_profiles:
            h.append("<div class='card'>")
            h.append(f"<h3>{esc(p.name)}</h3>")
            if p.role:
                h.append(f"<p>{esc(p.role)}</p>")
            if p.how_used:
                h.append(f"<p><strong>How it's used.</strong> {esc(p.how_used)}</p>")
            if p.owners:
                h.append(f"<p><strong>Ownership &amp; access.</strong> {esc(p.owners)}</p>")
            if p.limitations:
                h.append(f"<p><strong>Observed constraints.</strong> {esc(p.limitations)}</p>")
            h.append("</div>")

    # 1.4 data / document format taxonomy
    if cs.format_taxonomy:
        h.append("<h2>1.4 Information format &amp; structure</h2>")
        h.append("<p>The patterns the source information follows — this drives how it can be "
                 "ingested and reasoned over.</p>")
        h.append("<table><thead><tr><th>Pattern</th><th>Description</th><th>Where it appears</th>"
                 "</tr></thead><tbody>")
        for fp in cs.format_taxonomy:
            h.append(f"<tr><td><strong>{esc(fp.label)}</strong></td><td>{esc(fp.description)}</td>"
                     f"<td>{esc(fp.examples)}</td></tr>")
        h.append("</tbody></table>")

    if cs.process_inventory:
        h.append("<h2>1.5 Process inventory</h2><ul>")
        for it in cs.process_inventory:
            h.append(f"<li><strong>{esc(it.name)}</strong> — {esc(it.purpose)}</li>")
        h.append("</ul>")
    h.append("<h2>1.6 Ownership map</h2>"
             "<table><thead><tr><th>Activity</th><th>Responsible</th><th>Accountable</th>"
             "</tr></thead><tbody>")
    for r in cs.ownership_map:
        h.append(f"<tr><td>{esc(r.activity)}</td><td>{esc(r.responsible)}</td>"
                 f"<td>{esc(r.accountable)}</td></tr>")
    h.append("</tbody></table>")
    h.append("<h2>1.7 System inventory</h2>"
             "<table><thead><tr><th>System</th><th>Role</th><th>System of record for</th>"
             "</tr></thead><tbody>")
    for it in cs.system_inventory:
        h.append(f"<tr><td>{esc(it.name)}</td><td>{esc(it.purpose)}</td>"
                 f"<td>{esc(it.system_of_record_for)}</td></tr>")
    h.append("</tbody></table>")
    h.append("<h2>1.8 Handoff catalogue</h2><ul>")
    for ho in cs.handoff_catalogue:
        h.append(f"<li>{esc(ho.from_step)} → {esc(ho.to_step)} "
                 f"<span class='prov'>({esc(ho.mechanism)})</span></li>")
    h.append("</ul>")
    return "\n".join(h)


def r02(s: SynthesisContent, meta) -> str:
    h = ["<h1>Pain Points &amp; Opportunities</h1>",
         "<p class='lede'>The issues found in the discovery, ranked by business impact, "
         "each mapped to a recommended opportunity.</p>",
         impact_bars_svg(s.pain_points),
         render_charts(s.charts)]
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
         "<h2>Value vs. feasibility</h2>",
         value_feasibility_svg(s.opportunities),
         "<div class='matrix'>"]
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

    # Prioritization rationale across three readiness dimensions (the prior-engagement bar).
    rated = [o for o in s.opportunities
             if o.data_readiness or o.technical_complexity or o.operational_readiness]
    if rated:
        h.append("<h2>Prioritization rationale</h2>")
        h.append("<p>Each opportunity assessed across three readiness dimensions. The rating "
                 "(high / medium / low) is followed by the reason, so the sequence is defensible "
                 "rather than asserted.</p>")
        h.append("<table class='rationale'><thead><tr><th>Opportunity</th>"
                 "<th>Data readiness</th><th>Technical complexity</th>"
                 "<th>Operational readiness</th></tr></thead><tbody>")
        for o in rated:
            h.append(f"<tr><td><strong>{esc(o.title)}</strong></td>"
                     f"<td>{_rating_cell(o.data_readiness)}</td>"
                     f"<td>{_rating_cell(o.technical_complexity)}</td>"
                     f"<td>{_rating_cell(o.operational_readiness)}</td></tr>")
        h.append("</tbody></table>")

    h.append(f"<h2>Sequencing rationale</h2><p>{esc(s.sequencing_rationale)}</p>")
    if s.dependency_notes:
        h.append(f"<p><strong>Dependencies:</strong> {esc(s.dependency_notes)}</p>")
    h.append(f"<h2>Strategic readiness</h2><p>{esc(s.strategic_readiness)}</p>")
    if s.target_state:
        h.append("<h2>Where this should converge</h2>")
        h.append("<div class='panel target'><p>" + esc(s.target_state) + "</p></div>")
    return "\n".join(h)


def r04(s: SynthesisContent, meta) -> str:
    h = ["<h1>AI Opportunity Portfolio</h1>",
         "<p class='lede'>The recommended interventions in full — what the problem is, how the "
         "process changes, and what it delivers.</p>"]
    # Summary table first (the use-case anatomy: pattern / who / sources / behaviour), then the
    # deep write-ups follow. Mirrors the prior-engagement use-case summary table.
    if s.opportunities:
        h.append("<h2>At a glance</h2>")
        h.append("<table class='usecase'><thead><tr><th>Opportunity</th><th>Pattern</th>"
                 "<th>Who it serves</th><th>Knowledge sources</th><th>Expected behaviour</th>"
                 "</tr></thead><tbody>")
        for o in s.opportunities:
            who = ", ".join(esc(p) for p in o.personas) or "—"
            srcs = ", ".join(esc(x) for x in o.knowledge_sources) or "—"
            beh = esc(_clip(o.expected_behaviour, 110)) if o.expected_behaviour else "—"
            h.append(f"<tr><td><strong>{esc(o.title)}</strong></td>"
                     f"<td>{_PATTERN_LABEL.get(o.pattern.value,'')}</td>"
                     f"<td>{who}</td><td>{srcs}</td><td>{beh}</td></tr>")
        h.append("</tbody></table>")
        h.append("<h2>In detail</h2>")
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
        # Operating model: who uses it, what it does, and when it hands back to a human.
        if o.personas or o.expected_behaviour or o.escalation:
            h.append("<div class='opmodel'>")
            if o.personas:
                h.append("<p><strong>Who uses it.</strong> " +
                         ", ".join(esc(x) for x in o.personas) + "</p>")
            if o.expected_behaviour:
                h.append(f"<p><strong>Expected behaviour.</strong> {esc(o.expected_behaviour)}</p>")
            if o.escalation:
                h.append(f"<p><strong>Escalation &amp; human fallback.</strong> "
                         f"{esc(o.escalation)}</p>")
            if o.knowledge_sources or o.document_formats:
                bits = []
                if o.knowledge_sources:
                    bits.append("<strong>Sources.</strong> " +
                                ", ".join(esc(x) for x in o.knowledge_sources))
                if o.document_formats:
                    bits.append("<strong>Formats.</strong> " +
                                ", ".join(esc(x) for x in o.document_formats))
                h.append("<p>" + " &nbsp; ".join(bits) + "</p>")
            h.append("</div>")
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
    if s.metrics_framework:
        h.append("<h2>Success metrics framework</h2>")
        h.append("<p>How the impact of the recommended interventions should be measured once live — "
                 "the dimension, what it means, and the target to hold delivery to.</p>")
        h.append("<table><thead><tr><th>Metric</th><th>Definition</th><th>Target</th>"
                 "</tr></thead><tbody>")
        for m in s.metrics_framework:
            h.append(f"<tr><td><strong>{esc(m.name)}</strong></td><td>{esc(m.definition)}</td>"
                     f"<td>{esc(m.target)}</td></tr>")
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


# ---- data-viz helpers (pure inline SVG, offline-safe, grounded inputs only) -------------------
# A restrained categorical palette for multi-series visuals — all in the calm blue/slate family,
# no traffic-light status colours (those are reserved for the H/M/L readiness badges).
_SERIES = ["#1f6feb", "#5b8def", "#8fb0f0", "#b9cdf3", "#d7e3f8"]


def _fmt_compact(v: float) -> str:
    """Human-readable money/number: 30675000 -> '€30.7M', 1196 -> '1,196'."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    a = abs(f)
    if a >= 1_000_000:
        return f"€{f/1_000_000:.1f}M".replace(".0M", "M")
    if a >= 1_000 and f == int(f):
        return f"{int(f):,}"
    return f"{f:g}"


def impact_bars_svg(pain_points) -> str:
    """Horizontal bars ranking pain points by impact_rank (1 = most material). Bar length encodes
    rank position (not a fabricated metric); the label carries the title. Calm, single-accent."""
    pts = sorted(pain_points, key=lambda p: p.impact_rank)
    if not pts:
        return ""
    rows = len(pts)
    BARH, GAP, PAD, LBLW = 30, 14, 12, 8
    W, innerW = 760, 520
    H = PAD * 2 + rows * BARH + (rows - 1) * GAP
    out = [f"<svg class='chart' viewBox='0 0 {W} {H}' width='100%' role='img' "
           f"aria-label='Pain points ranked by impact' xmlns='http://www.w3.org/2000/svg'>",
           _SVG_DEFS]
    for i, p in enumerate(pts):
        y = PAD + i * (BARH + GAP)
        # length: most-material (rank 1) longest, descending by rank
        frac = (rows - i) / rows
        w = int(innerW * frac)
        x0 = 150
        out.append(f"<rect x='{x0}' y='{y}' width='{w}' height='{BARH}' rx='5' "
                   f"fill='url(#hdr)' filter='url(#sh)'/>")
        out.append(f"<text x='{x0-10}' y='{y+BARH/2+4}' text-anchor='end' font-size='12.5' "
                   f"font-weight='700' fill='#1a2230'>{esc(p.id)}</text>")
        out.append(f"<text x='{x0+12}' y='{y+BARH/2+4}' font-size='12' fill='#fff' "
                   f"font-weight='600'>{esc(_clip(p.title, 64))}</text>")
    out.append("</svg>")
    return ("<div class='chart-wrap'><div class='chart-cap'>Issues ranked by business impact "
            "(most material first)</div>" + "".join(out) + "</div>")


def value_feasibility_svg(opportunities) -> str:
    """A value (y) vs feasibility (x) bubble plot. Positions use value_score/feasibility_score
    (1-5, set by synthesis); bubbles are labelled with the opportunity id. Quadrant guides shown."""
    opps = [o for o in opportunities if o.value_score and o.feasibility_score]
    if not opps:
        return ""
    W, H, PAD = 520, 420, 56
    plotW, plotH = W - PAD * 2, H - PAD * 2
    def px(score): return PAD + (score - 1) / 4 * plotW           # feasibility 1..5 -> x
    def py(score): return PAD + plotH - (score - 1) / 4 * plotH   # value 1..5 -> y (inverted)
    out = [f"<svg class='chart' viewBox='0 0 {W} {H}' width='100%' role='img' "
           f"aria-label='Value versus feasibility' xmlns='http://www.w3.org/2000/svg'>", _SVG_DEFS]
    # shade the top-right "do first" quadrant softly so the map reads as intentional
    midx, midy = px(3), py(3)
    out.append(f"<rect x='{midx}' y='{PAD}' width='{PAD+plotW-midx}' height='{midy-PAD}' "
               f"fill='var(--accent-soft)'/>")
    # quadrant guide lines at the midpoint
    out.append(f"<line x1='{midx}' y1='{PAD}' x2='{midx}' y2='{PAD+plotH}' stroke='#e3e8ee'/>")
    out.append(f"<line x1='{PAD}' y1='{midy}' x2='{PAD+plotW}' y2='{midy}' stroke='#e3e8ee'/>")
    # axes labels
    out.append(f"<text x='{PAD+plotW/2}' y='{H-14}' text-anchor='middle' font-size='12' "
               f"fill='#5b6776' font-weight='600'>Feasibility →</text>")
    out.append(f"<text x='16' y='{PAD+plotH/2}' text-anchor='middle' font-size='12' fill='#5b6776' "
               f"font-weight='600' transform='rotate(-90 16 {PAD+plotH/2})'>Value →</text>")
    # quadrant captions in all four corners so empty space reads as the map, not missing data
    for qx, qy, anchor, label in [
            (PAD + plotW - 6, PAD + 16, "end", "Do first"),
            (PAD + 6, PAD + 16, "start", "Plan for"),
            (PAD + plotW - 6, PAD + plotH - 8, "end", "Quick wins"),
            (PAD + 6, PAD + plotH - 8, "start", "Reconsider")]:
        out.append(f"<text x='{qx}' y='{qy}' text-anchor='{anchor}' font-size='10' "
                   f"fill='#9aa7b6' font-weight='600'>{label}</text>")
    # spread bubbles that land on the same coordinate so labels never collide (deterministic)
    placed: dict[tuple, int] = {}
    for o in opps:
        key = (o.feasibility_score, o.value_score)
        k = placed.get(key, 0)
        placed[key] = k + 1
        ox = (k % 3 - 1) * 22 if k else 0           # fan out: 0, then -22/0/+22, ...
        oy = (k // 3) * 22 if k else 0
        cx, cy = px(o.feasibility_score) + ox, py(o.value_score) + oy
        out.append(f"<circle cx='{cx}' cy='{cy}' r='17' fill='var(--accent)' fill-opacity='0.16' "
                   f"stroke='var(--accent)'/>")
        out.append(f"<text x='{cx}' y='{cy+4}' text-anchor='middle' font-size='11' "
                   f"font-weight='700' fill='#0a4bbd'>{esc(o.id)}</text>")
    out.append("</svg>")
    return ("<div class='chart-wrap'><div class='chart-cap'>Where each opportunity sits on value "
            "versus feasibility</div>" + "".join(out) + "</div>")


def donut_svg(segments, caption: str) -> str:
    """A donut from (label, value) pairs — e.g. order value by channel. Values must be grounded
    (the caller passes only figures already in the findings). Returns '' if nothing to show."""
    segs = [(l, float(v)) for l, v in segments if _to_number_safe(v) and float(v) > 0]
    total = sum(v for _, v in segs)
    if not segs or total <= 0:
        return ""
    import math
    cx, cy, r, rin = 90, 90, 78, 46
    out = [f"<svg class='chart donut' viewBox='0 0 360 184' width='100%' role='img' "
           f"aria-label='{esc(caption)}' xmlns='http://www.w3.org/2000/svg'>"]
    a0 = -math.pi / 2
    legend = []
    for i, (label, v) in enumerate(segs):
        frac = v / total
        a1 = a0 + frac * 2 * math.pi
        large = 1 if (a1 - a0) > math.pi else 0
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        xi0, yi0 = cx + rin * math.cos(a1), cy + rin * math.sin(a1)
        xi1, yi1 = cx + rin * math.cos(a0), cy + rin * math.sin(a0)
        col = _SERIES[i % len(_SERIES)]
        out.append(f"<path d='M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} 1 {x1:.1f},{y1:.1f} "
                   f"L{xi0:.1f},{yi0:.1f} A{rin},{rin} 0 {large} 0 {xi1:.1f},{yi1:.1f} Z' "
                   f"fill='{col}'/>")
        ly = 34 + i * 26
        legend.append(f"<rect x='196' y='{ly-10}' width='12' height='12' rx='2' fill='{col}'/>"
                      f"<text x='214' y='{ly}' font-size='12' fill='#1a2230'>"
                      f"{esc(_clip(label, 22))} · {esc(_fmt_compact(v))} "
                      f"({frac*100:.0f}%)</text>")
        a0 = a1
    out += legend
    out.append("</svg>")
    return ("<div class='chart-wrap'><div class='chart-cap'>" + esc(caption) + "</div>"
            + "".join(out) + "</div>")


def _to_number_safe(v):
    try:
        float(v); return True
    except (TypeError, ValueError):
        return False


def _nice_label(s: str) -> str:
    """Tidy a derived series label: uppercase known acronyms, else title-case."""
    s = str(s).strip()
    return "EDI" if s.lower() == "edi" else s


def value_bar_svg(segments, caption: str, unit: str = "") -> str:
    """A horizontal bar chart from (label, value) pairs — bar length proportional to value, the
    real figure labelled on each. For grounded breakdowns (e.g. unfulfilled orders by channel)."""
    segs = [(_nice_label(l), float(v)) for l, v in segments if _to_number_safe(v) and float(v) > 0]
    if not segs:
        return ""
    mx = max(v for _, v in segs)
    BARH, GAP, PAD, LBLW, VALW = 30, 16, 14, 130, 90
    W = 700
    innerW = W - PAD * 2 - LBLW - VALW
    H = PAD * 2 + len(segs) * BARH + (len(segs) - 1) * GAP
    out = [f"<svg class='chart' viewBox='0 0 {W} {H}' width='100%' role='img' "
           f"aria-label='{esc(caption)}' xmlns='http://www.w3.org/2000/svg'>", _SVG_DEFS]
    for i, (label, v) in enumerate(segs):
        y = PAD + i * (BARH + GAP)
        w = max(2, int(innerW * (v / mx)))
        out.append(f"<text x='{PAD}' y='{y+BARH/2+4}' font-size='12.5' font-weight='600' "
                   f"fill='#1a2230'>{esc(_clip(label, 18))}</text>")
        out.append(f"<rect x='{PAD+LBLW}' y='{y}' width='{w}' height='{BARH}' rx='5' "
                   f"fill='url(#hdr)' filter='url(#sh)'/>")
        val = _fmt_compact(v) if unit == "eur" else (f"{int(v):,}" if v == int(v) else f"{v:g}")
        out.append(f"<text x='{PAD+LBLW+w+10}' y='{y+BARH/2+4}' font-size='12' font-weight='700' "
                   f"fill='#0a4bbd'>{esc(val)}</text>")
    out.append("</svg>")
    return ("<div class='chart-wrap'><div class='chart-cap'>" + esc(caption) + "</div>"
            + "".join(out) + "</div>")


def render_charts(charts) -> str:
    """Render the code-owned grounded chart series (donut for shares, bar for counts/values)."""
    out = []
    for c in charts or []:
        segs = [(s.get("label", ""), s.get("value")) for s in c.get("segments", [])]
        title = c.get("title", "")
        if c.get("kind") == "donut":
            out.append(donut_svg(segs, title))
        else:
            out.append(value_bar_svg(segs, title, unit=c.get("unit", "")))
    return "\n".join(x for x in out if x)


def kpi_tiles(s: SynthesisContent) -> str:
    """The 'at a glance' strip on the executive summary. Every figure is DERIVED in code from the
    grounded content (counts + the largest quantified pain-point numbers) — never model-set, so it
    cannot carry a fabricated number. Picks the most material money/percent figures to surface."""
    tiles = [(str(len(s.pain_points)), "issues identified"),
             (str(len(s.opportunities)), "opportunities mapped"),
             (str(len(s.source_index)), "sources analysed")]
    # surface up to two headline grounded figures from the ranked pain points: the LARGEST money
    # figure (most material) and the first percentage — both already grounded, never model-set.
    money, pct = [], []
    for p in sorted(s.pain_points, key=lambda x: x.impact_rank):
        for n in p.quantified:
            label = (n.label or "").strip() or p.title
            if n.unit == "eur":
                money.append((float(n.value), _fmt_compact(n.value), _clip(label, 34)))
            elif n.unit == "percent":
                pct.append((f"{n.value:g}%", _clip(label, 34)))
    headline = []
    if money:
        _, v, l = max(money, key=lambda m: m[0])      # the biggest € figure leads
        headline.append((v, l))
    if pct:
        headline.append(pct[0])
    tiles = headline + tiles
    cells = "".join(f"<div class='kpi'><div class='kpi-v'>{esc(v)}</div>"
                    f"<div class='kpi-l'>{esc(l)}</div></div>" for v, l in tiles[:5])
    return f"<div class='kpis'>{cells}</div>"


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
    """Render a NumberRef as a chip. If the model's text/label already carries a digit, show it as
    is; otherwise prepend the formatted grounded value so the figure is always visible (the model
    sometimes writes 'aggregate divergence addressed' and expects the number rendered separately)."""
    import re as _re
    text = (n.text or n.label or "").strip()
    if not _re.search(r"\d", text):
        figure = _fmt_compact(n.value) if n.unit == "eur" else (
            f"{n.value:g}%" if n.unit == "percent" else
            (f"{int(n.value):,}" if float(n.value) == int(n.value) else f"{n.value:g}"))
        text = f"{figure} — {text}" if text else figure
    return f"<span class='metric'>{esc(text)}</span>"


def _rating_cell(raw: str) -> str:
    """Render a readiness rating of the form 'high — reason' as a coloured H/M/L badge followed by
    the reason. Tolerant of an em-dash, hyphen, or colon separator, or a bare rating."""
    if not raw:
        return "—"
    rating, _, reason = raw.partition("—")
    if not reason:
        rating, _, reason = raw.partition(" - ")
    if not reason:
        rating, _, reason = raw.partition(":")
    level = rating.strip().lower()
    cls = level if level in ("high", "medium", "low") else "na"
    badge = f"<span class='rate rate-{cls}'>{esc(rating.strip().title() or '—')}</span>"
    reason = reason.strip()
    return f"{badge} {esc(reason)}" if reason else badge


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


# The AuroPro brand mark — inline SVG (offline-safe), the cyan/teal twin-triangle device.
_LOGO = ("<svg viewBox='0 0 32 32' xmlns='http://www.w3.org/2000/svg' aria-hidden='true'>"
         "<path d='M16 3 L27 26 H19 L16 18 L13 26 H5 Z' fill='#0f7c8c'/>"
         "<path d='M16 3 L21 13 L16 13 Z' fill='#22c3d6'/></svg>")


def _toc(meta: dict) -> str:
    """A table of contents over the report sections (print-quality navigation)."""
    rows = []
    for i, (slug, label) in enumerate(REPORTS):
        num = slug.split("-")[0]
        rows.append(f"<a href='{slug}.html'><span class='toc-num'>{num}</span>"
                    f"<span class='toc-t'>{esc(label)}</span></a>")
    return "<div class='toc'>" + "".join(rows) + "</div>"


def _cover(meta: dict) -> str:
    """The branded cover page (print only). Domain + AuroPro brand; the client name appears only
    when it is known AND not suppressed (meta['client'] is already blanked when suppressed)."""
    client = (meta.get("client") or "").strip()
    domain = esc(meta.get("domain_label", "Discovery"))
    title = f"{domain} Discovery Report"
    sub = esc(client) if client else "Autonomous Discovery Assessment"
    return (f"<section class='cover'><div class='ctitle'>{esc(title)}</div>"
            f"<div class='csub'>{sub}</div>"
            f"<div class='cbrand'>{_LOGO}<span>AuroPro · Autonomous Discovery Platform</span></div>"
            f"</section>")


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
    # running header/footer: in the DOM always, shown only in print (via CSS). The header carries
    # the brand mark + engagement; the footer a confidentiality note. Page numbers come from @page.
    hdr_label = f"{domain} Discovery Report" + (f" · {esc(client)}" if client else "")
    rep_header = ""   # omitted in print (a fixed top band collides with headings)
    rep_footer = (f"<div class='rep-footer'><span class='brandmark'>{_LOGO}{hdr_label}</span>"
                  f"<span>Confidential</span></div>")
    # the index page leads with the branded cover + a table of contents (print only — on screen the
    # index shows the executive summary directly; the cover/TOC are for the PDF deliverable)
    cover = (_cover(meta)
             + f"<main class='content cover-toc'><h1>Contents</h1>{_toc(meta)}</main>"
             if is_index else "")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<link rel="stylesheet" href="assets/report.css"></head><body>
{rep_header}{rep_footer}
{cover}
<div class="layout">
<nav class="sidebar">
  <span class="brandmark" style="color:#fff;margin-bottom:1rem">{_LOGO}AuroPro</span>
  <h1>{heading}</h1>
  <div class="sub">{sub}</div>
  {''.join(nav)}
</nav>
<main class="content">
{body}
</main></div></body></html>"""
