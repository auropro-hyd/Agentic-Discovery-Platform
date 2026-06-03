"""Render a SynthesisContent into the formal discovery report suite.

Each of the seven reports is a STANDALONE deliverable: its own branded cover, its own table of
contents, and hierarchically numbered sections — matching the reference deliverables. There is no
Document Control or Input-Documents section (dropped by request). The visual identity is formal
navy/blue corporate (see assets.py).

Reads ONLY SynthesisContent — tool names, locators and filenames are unreachable by type. Each
report is leak-guarded before write; Report 01 additionally passes a factual-language lint. Every
number, label, node, and quote shown traces to a verified finding; components and infographics omit
themselves when their grounded data is absent (never fabricated).
"""
from __future__ import annotations

import html
import re
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
                  "modernisation": "Modernisation", "ai_agent": "AI Agent"}
_QUAD = [("do_first", "Do First"), ("plan_for", "Plan For"),
         ("consider", "Consider"), ("deprioritise", "Deprioritise")]
_HORIZON_CLASS = {"H1": "al-h1", "H2": "al-h2", "H3": "al-h3"}


def render_suite(s: SynthesisContent, meta: dict, outdir: Path,
                 suppress_names: list[str] | None = None) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "assets").mkdir(exist_ok=True)
    (outdir / "assets" / "report.css").write_text(CSS, encoding="utf-8")
    (outdir / "assets" / "report.js").write_text(JS, encoding="utf-8")
    _render_source_pages(s, outdir, suppress_names)
    fns = {"00-executive-summary": r00, "01-current-state": r01, "02-pain-points": r02,
           "03-recommendation": r03, "04-opportunity-portfolio": r04, "05-roadmap": r05,
           "06-supporting-artefacts": r06}
    for slug, title in REPORTS:
        body = _secnum_chips(_scrub_names(fns[slug](s, meta), suppress_names))
        text = _strip_tags(body)
        assert_no_leaks(text, suppress_names=suppress_names)
        if slug == "01-current-state":
            assert_factual(text)
        (outdir / f"{slug}.html").write_text(
            _page(slug, title, body, meta), encoding="utf-8")
    # index.html IS the executive summary (the natural entry point to the suite)
    index = outdir / "index.html"
    index_body = _secnum_chips(_scrub_names(fns["00-executive-summary"](s, meta), suppress_names))
    index.write_text(_page("00-executive-summary", REPORTS[0][1], index_body, meta),
                     encoding="utf-8")
    return index


# ---------------------------------------------------------------------------
# section builder — each report appends numbered sections; the TOC is derived
# from exactly the sections present, so it can never drift from the body.
# ---------------------------------------------------------------------------
class _Doc:
    """Accumulates numbered sections for one report. h1(title) opens a section (1, 2, …); h2(title)
    opens a subsection (1.1, 1.2, …). Both record a TOC entry. raw() appends arbitrary HTML to the
    current section without numbering. The rendered body and the TOC come from the same source."""

    def __init__(self, report_title: str, lede: str = ""):
        self.report_title = report_title
        self.lede = lede
        self._parts: list[str] = []
        self._toc: list[tuple[str, str, bool]] = []   # (number, title, is_sub)
        self._sec = 0
        self._sub = 0

    def h1(self, title: str) -> "_Doc":
        self._sec += 1
        self._sub = 0
        num = str(self._sec)
        self._toc.append((num, title, False))
        self._parts.append(f"<h2>{esc(num)}. {esc(title)}</h2>")
        return self

    def h2(self, title: str) -> "_Doc":
        self._sub += 1
        num = f"{self._sec}.{self._sub}"
        self._toc.append((num, title, True))
        self._parts.append(f"<h3>{esc(num)} &nbsp;{esc(title)}</h3>")
        return self

    def raw(self, html_str: str) -> "_Doc":
        if html_str:
            self._parts.append(html_str)
        return self

    def p(self, text: str) -> "_Doc":
        if text:
            self._parts.append(f"<p>{esc(text)}</p>")
        return self

    def body(self) -> str:
        head = [f"<h1>{esc(self.report_title)}</h1>"]
        if self.lede:
            head.append(f"<p class='lede'>{esc(self.lede)}</p>")
        return "\n".join(head + self._parts)

    def toc_html(self) -> str:
        if not self._toc:
            return ""
        rows = []
        for num, title, is_sub in self._toc:
            cls = "ti-sub" if is_sub else ""
            rows.append(f"<a class='{cls}'><span class='ti-num'>{esc(num)}</span>"
                        f"<span class='ti-title'>{esc(title)}</span>"
                        f"<span class='ti-dots'></span></a>")
        return f"<div class='report-toc'><h1>Contents</h1><div class='toc'>{''.join(rows)}</div></div>"


# ---------------------------------------------------------------------------
# report bodies — each returns (toc_html + numbered body) as one fragment.
# The cover is added by _page(); the report-toc is print-only (CSS-hidden on screen).
# ---------------------------------------------------------------------------
def r00(s: SynthesisContent, meta) -> str:
    es = s.executive_summary
    dom = esc(meta.get("domain_label", "this process"))
    at_client = f" at {esc(meta['client'])}" if meta.get("client") else ""
    headline = es.headline or (f"How {dom} runs today{at_client}, the issues found in the data, and "
                               "the opportunities to address them.")
    d = _Doc("Executive Summary", headline)
    d.h1("At a glance").raw(stat_tiles(_exec_tiles(s)))
    if es.situation or es.opportunity:
        cells = []
        if es.situation:
            cells.append(f"<div class='panel'><h3>The situation</h3><p>{esc(es.situation)}</p></div>")
        if es.opportunity:
            cells.append(f"<div class='panel'><h3>The opportunity</h3><p>{esc(es.opportunity)}</p>"
                         "</div>")
        d.h2("Situation & opportunity").raw("<div class='two-col'>" + "".join(cells) + "</div>")
    do_first = [o for o in s.opportunities if o.matrix_quadrant.value == "do_first"]
    top = do_first or s.opportunities[:3]
    if top:
        d.h1("Where to start")
        d.raw(value_matrix_svg(s.opportunities))
        cards = ["<div class='opp-cards'>"]
        for o in top:
            pat = _PATTERN_LABEL.get(o.pattern.value, "")
            impact = ""
            if o.business_impact and o.business_impact.quantified:
                impact = " &nbsp; ".join(_metric(n) for n in o.business_impact.quantified[:2])
            cards.append("<a class='opp-card' href='04-opportunity-portfolio.html'>"
                         f"<span class='pattern'>{esc(pat)}</span>"
                         f"<h4>{esc(o.title)}</h4><p>{esc(_clip(o.overview, 150))}</p>"
                         + (f"<p class='kfig'>{impact}</p>" if impact else "") + "</a>")
        cards.append("</div>")
        d.raw("".join(cards))
    if s.source_index:
        names = ", ".join(esc(x.business_name) for x in s.source_index[:8])
        more = f" and {len(s.source_index)-8} more" if len(s.source_index) > 8 else ""
        d.h1("What we read")
        d.p(f"{names}{more}. Every figure in this assessment is computed from these sources and "
            "traces back to them.")
        d.raw("<p class='prov'>Read on: the "
              "<a href='01-current-state.html'>Current State</a>, the "
              "<a href='02-pain-points.html'>issues found</a>, and the recommended "
              "<a href='04-opportunity-portfolio.html'>opportunities</a>.</p>")
    return d.toc_html() + d.body()


def _tables_titled(tables, *needles):
    """Return the grounded data tables whose title contains any of the given (lowercased) needles,
    in declared order. Lets r01 place each table in the right numbered section without hardcoding."""
    out = []
    for t in tables or []:
        low = (t.title or "").lower()
        if any(n in low for n in needles):
            out.append(t)
    return out


def r01(s: SynthesisContent, meta) -> str:
    cs = s.current_state
    dom = esc(meta.get("domain_label", "this process"))
    at_client = f" at {esc(meta['client'])}" if meta.get("client") else ""
    d = _Doc("Current State Assessment",
             f"How {dom} runs today{at_client}. A factual baseline of the process, the systems that "
             "support it, and how information is structured — stated as fact, no judgements.")

    # 1. Domain overview — context + grounded volume baseline + channel mix
    d.h1("Domain overview")
    d.h2("Context and scope").p(cs.domain_overview).p(cs.process_summary)
    if cs.baseline_stats:
        d.h2("Volume baseline")
        d.raw(stat_tiles([(k.value, k.label + (f" — {k.sublabel}" if k.sublabel else ""), "blue")
                          for k in cs.baseline_stats]))
    for t in _tables_titled(cs.data_tables, "channel mix"):
        d.raw(_data_table(t))

    # 2. Process flow — diagram + step table
    d.h1("Process flow")
    d.p("The end-to-end flow, who performs each step and on which system:")
    d.raw(process_flow_svg(cs.process_flow))
    rows = ["<table><thead><tr><th>Step</th><th>Performed by</th><th>System</th>"
            "<th>What happens</th></tr></thead><tbody>"]
    for st in cs.process_flow:
        rows.append(f"<tr><td>{st.seq}. {esc(st.name)}</td><td>{esc(st.actor)}</td>"
                    f"<td>{esc(st.system)}</td><td>{esc(st.description)}</td></tr>")
    rows.append("</tbody></table>")
    d.raw("".join(rows))

    # 3. Process inventory — per-step detail + the supporting reference tables
    if cs.process_detail:
        d.h1("Process inventory")
        d.p("Each stage of the process in detail — how it runs today, who performs it, and on which "
            "system.")
        for pd in cs.process_detail:
            who = " · ".join(x for x in [pd.actor, pd.system] if x)
            d.raw(f"<div class='card'><h4>{esc(pd.title)}</h4>"
                  + (f"<div class='who'>{esc(who)}</div>" if who else "")
                  + f"<p>{esc(pd.body)}</p>"
                  + (f"<p class='prov'>Source: {_cite_links(pd.sources)}</p>" if pd.sources else "")
                  + "</div>")
        for t in _tables_titled(cs.data_tables, "credit limit approval", "lead time",
                                "collections escalation"):
            d.raw(_data_table(t))

    # 4. Ownership map — RACI
    d.h1("Ownership map")
    if cs.process_inventory:
        d.h2("Process inventory summary")
        d.raw("<ul>" + "".join(f"<li><strong>{esc(it.name)}</strong> — {esc(it.purpose)}</li>"
                               for it in cs.process_inventory) + "</ul>")
    d.h2("RACI matrix")
    om = ["<table><thead><tr><th>Activity</th><th>Responsible</th><th>Accountable</th>"
          "</tr></thead><tbody>"]
    for r in cs.ownership_map:
        om.append(f"<tr><td>{esc(r.activity)}</td><td>{esc(r.responsible)}</td>"
                  f"<td>{esc(r.accountable)}</td></tr>")
    om.append("</tbody></table>")
    d.raw("".join(om))

    # 5. System inventory — systems table + EDI connections + deep profiles + format taxonomy
    d.h1("System inventory")
    for t in _tables_titled(cs.data_tables, "systems in scope"):
        d.h2("Systems in scope").raw(_data_table(t, show_title=False))
    si = ["<table><thead><tr><th>System</th><th>Role</th><th>System of record for</th>"
          "</tr></thead><tbody>"]
    for it in cs.system_inventory:
        si.append(f"<tr><td>{esc(it.name)}</td><td>{esc(it.purpose)}</td>"
                  f"<td>{esc(it.system_of_record_for)}</td></tr>")
    si.append("</tbody></table>")
    d.raw("".join(si))
    for t in _tables_titled(cs.data_tables, "edi connection"):
        d.h2("EDI connection inventory").raw(_data_table(t, show_title=False))
    if cs.system_profiles:
        d.h2("System profiles")
        d.p("Each system that supports this process — what it is, how it is used, who owns it, and "
            "the constraints observed.")
        for p in cs.system_profiles:
            card = [f"<div class='card'><h4>{esc(p.name)}</h4>"]
            if p.role:
                card.append(f"<p>{esc(p.role)}</p>")
            if p.how_used:
                card.append(f"<p><strong>How it's used.</strong> {esc(p.how_used)}</p>")
            if p.owners:
                card.append(f"<p><strong>Ownership &amp; access.</strong> {esc(p.owners)}</p>")
            if p.limitations:
                card.append(f"<p><strong>Observed constraints.</strong> {esc(p.limitations)}</p>")
            card.append("</div>")
            d.raw("".join(card))
    if cs.format_taxonomy:
        d.h2("Information format & structure")
        d.p("The patterns the source information follows — this drives how it can be ingested and "
            "reasoned over.")
        tx = ["<table><thead><tr><th>Pattern</th><th>Description</th><th>Where it appears</th>"
              "</tr></thead><tbody>"]
        for fp in cs.format_taxonomy:
            tx.append(f"<tr><td><strong>{esc(fp.label)}</strong></td><td>{esc(fp.description)}</td>"
                      f"<td>{esc(fp.examples)}</td></tr>")
        tx.append("</tbody></table>")
        d.raw("".join(tx))

    # 6. Handoff map
    d.h1("Handoff map")
    d.p("How work crosses between steps and systems — each handoff is where information changes "
        "hands or format.")
    d.raw(context_map_svg(cs.process_flow, cs.handoff_catalogue))
    d.raw("<ul>" + "".join(
        f"<li>{esc(ho.from_step)} → {esc(ho.to_step)} "
        f"<span class='prov'>({esc(ho.mechanism)})</span></li>" for ho in cs.handoff_catalogue)
        + "</ul>")

    # Appendix — account baseline
    appendix = _tables_titled(cs.data_tables, "top trading accounts")
    if appendix:
        d.h1("Appendix — account baseline")
        for t in appendix:
            d.raw(_data_table(t))
    return d.toc_html() + d.body()


def r02(s: SynthesisContent, meta) -> str:
    d = _Doc("Pain Points & Opportunities",
             "The issues found in the discovery, ranked by business impact, each mapped to a "
             "recommended opportunity.")
    d.h1("Issues at a glance")
    d.raw(stat_tiles(_pp_tiles(s)))
    d.raw(impact_bars_svg(s.pain_points))
    d.raw(render_charts(s.charts, kinds={"bar"}))
    d.h1("Root cause")
    d.p("How the issues found trace back to shared structural causes:")
    d.raw(root_cause_svg(s.pain_points, s.cross_process_patterns))
    if s.cross_process_patterns:
        for c in s.cross_process_patterns:
            d.raw(f"<p><strong>{esc(c.get('pattern',''))}.</strong> "
                  f"{esc(c.get('description',''))}</p>")
    d.h1("Pain points in detail")
    for idx, pp in enumerate(sorted(s.pain_points, key=lambda p: p.impact_rank), start=1):
        d.raw(_pain_point_card(pp, idx))
    if s.evidence_register:
        d.h1("Appendix — evidence register")
        d.p("Every finding traced to the source it rests on, with the confidence tier.")
        er = ["<table><thead><tr><th>Finding</th><th>Source</th><th>Evidence type</th>"
              "<th>Key data point</th><th>Confidence</th></tr></thead><tbody>"]
        for e in s.evidence_register:
            conf = e.confidence.lower()
            cls = ("b-low" if conf == "verified" else "b-med" if conf == "amber"
                   else "b-high" if conf == "gap" else "b-pat")
            er.append(f"<tr><td><strong>{esc(e.finding)}</strong></td><td>{esc(e.source)}</td>"
                      f"<td>{esc(e.evidence_type)}</td><td>{esc(e.data_point)}</td>"
                      f"<td><span class='badge {cls}'>{esc(e.confidence)}</span></td></tr>")
        er.append("</tbody></table>")
        d.raw("".join(er))
    return d.toc_html() + d.body()


def r03(s: SynthesisContent, meta) -> str:
    by_q = {q: [o for o in s.opportunities if o.matrix_quadrant.value == q] for q, _ in _QUAD}
    titles = {o.id: o.title for o in s.opportunities}
    d = _Doc("Transformation Recommendation",
             "Which opportunities to pursue, in what order, by value and feasibility.")

    d.h1("Transformation intent")
    if s.target_state:
        d.raw("<div class='panel target'><p>" + esc(s.target_state) + "</p></div>")
    principles = _principles(s)
    if principles:
        d.h2("Guiding principles")
        cards = ["<div class='principles'>"]
        for i, (title, text) in enumerate(principles, start=1):
            cards.append(f"<div class='prin-card'><div class='prin-num'>P{i}</div>"
                         f"<div class='prin-title'>{esc(title)}</div>"
                         f"<div class='prin-text'>{esc(text)}</div></div>")
        cards.append("</div>")
        d.raw("".join(cards))

    d.h1("Value vs. feasibility")
    d.raw(value_matrix_svg(s.opportunities))
    mx = ["<div class='matrix'>"]
    for q, label in _QUAD:
        chips = "".join(f"<span class='chip'>{esc(o.title)}</span>" for o in by_q[q])
        empty = "<span class='prov'>None in this quadrant</span>"
        mx.append(f"<div class='quad {q}'><h4>{label}</h4>{chips or empty}</div>")
    mx.append("</div>")
    d.raw("".join(mx))

    d.h1("Recommendations")
    d.p("Each opportunity as a recommendation — what it addresses, the phased actions, and what "
        "success looks like.")
    for idx, o in enumerate(_seq_order(s.opportunities), start=1):
        d.raw(_rec_card(o, idx, s, titles))

    d.h1("Sequencing & readiness")
    rated = [o for o in s.opportunities
             if o.data_readiness or o.technical_complexity or o.operational_readiness]
    if rated:
        d.h2("Prioritization rationale")
        d.p("Each opportunity assessed across three readiness dimensions. The rating "
            "(high / medium / low) is followed by the reason, so the sequence is defensible rather "
            "than asserted.")
        rt = ["<table class='rationale'><thead><tr><th>Opportunity</th><th>Data readiness</th>"
              "<th>Technical complexity</th><th>Operational readiness</th></tr></thead><tbody>"]
        for o in rated:
            rt.append(f"<tr><td><strong>{esc(o.title)}</strong></td>"
                      f"<td>{_rating_cell(o.data_readiness)}</td>"
                      f"<td>{_rating_cell(o.technical_complexity)}</td>"
                      f"<td>{_rating_cell(o.operational_readiness)}</td></tr>")
        rt.append("</tbody></table>")
        d.raw("".join(rt))
    d.h2("Implementation roadmap")
    d.p("The recommendations sequenced across three horizons (now → later).")
    d.raw(roadmap_timeline_svg(s.roadmap))
    d.h2("Sequencing rationale").p(s.sequencing_rationale)
    if s.dependency_notes:
        d.raw(f"<p><strong>Dependencies:</strong> {esc(s.dependency_notes)}</p>")
    d.raw(dependency_map_svg(s.opportunities))
    d.h2("Strategic readiness").p(s.strategic_readiness)

    if s.metrics_framework:
        d.h1("Success metrics")
        d.p("How to measure delivery once live — the baseline today and the directional target.")
        mt = ["<table><thead><tr><th>Metric</th><th>What it measures</th><th>Target</th>"
              "</tr></thead><tbody>"]
        for m in s.metrics_framework:
            mt.append(f"<tr><td><strong>{esc(m.name)}</strong></td><td>{esc(m.definition)}</td>"
                      f"<td>{esc(m.target)}</td></tr>")
        mt.append("</tbody></table>")
        d.raw("".join(mt))

    if s.risk_register:
        d.h1("Risk register")
        d.p("The delivery risks, how likely and how serious each is, and how it is mitigated.")
        rk = ["<table><thead><tr><th>Risk</th><th>Likelihood</th><th>Impact</th><th>Mitigation</th>"
              "<th>Owner</th></tr></thead><tbody>"]
        for r in s.risk_register:
            rk.append(f"<tr><td>{esc(r.risk)}</td><td>{_level_badge(r.likelihood)}</td>"
                      f"<td>{_level_badge(r.impact)}</td><td>{esc(r.mitigation)}</td>"
                      f"<td>{esc(r.owner)}</td></tr>")
        rk.append("</tbody></table>")
        d.raw("".join(rk))

    if s.traceability:
        d.h1("Appendix — traceability matrix")
        d.p("Each pain point traced through to the recommendation, opportunity, expected outcome "
            "and horizon that addresses it.")
        tr = ["<table><thead><tr><th>Pain point</th><th>Summary</th><th>Severity</th>"
              "<th>Recommendation</th><th>Opportunity</th><th>Expected outcome</th><th>Horizon</th>"
              "</tr></thead><tbody>"]
        for t in s.traceability:
            tr.append(f"<tr><td><strong>{esc(t.pain_point)}</strong></td><td>{esc(t.summary)}</td>"
                      f"<td>{esc(t.severity)}</td><td>{esc(t.recommendation)}</td>"
                      f"<td>{esc(t.opportunity)}</td><td>{esc(t.expected_outcome)}</td>"
                      f"<td>{esc(t.horizon)}</td></tr>")
        tr.append("</tbody></table>")
        d.raw("".join(tr))
    return d.toc_html() + d.body()


def _level_badge(level: str) -> str:
    """A High/Medium/Low level as a coloured badge (risk likelihood/impact)."""
    lo = (level or "").strip().lower()
    cls = "b-high" if lo == "high" else "b-med" if lo == "medium" else "b-low" if lo == "low" \
        else "b-pat"
    return f"<span class='badge {cls}'>{esc(level)}</span>" if level else "—"


def r04(s: SynthesisContent, meta) -> str:
    d = _Doc("AI Opportunity Portfolio",
             "The recommended interventions in full — what the problem is, how the process changes, "
             "and what it delivers.")
    if s.opportunities:
        d.h1("Portfolio at a glance")
        ug = ["<table class='usecase'><thead><tr><th>Opportunity</th><th>Pattern</th>"
              "<th>Who it serves</th><th>Knowledge sources</th><th>Expected behaviour</th>"
              "</tr></thead><tbody>"]
        for o in s.opportunities:
            who = ", ".join(esc(p) for p in o.personas) or "—"
            srcs = ", ".join(esc(x) for x in o.knowledge_sources) or "—"
            beh = esc(_clip(o.expected_behaviour, 110)) if o.expected_behaviour else "—"
            ug.append(f"<tr><td><strong>{esc(o.title)}</strong></td>"
                      f"<td>{_PATTERN_LABEL.get(o.pattern.value,'')}</td>"
                      f"<td>{who}</td><td>{srcs}</td><td>{beh}</td></tr>")
        ug.append("</tbody></table>")
        d.raw("".join(ug))
    d.h1("Opportunities in detail")
    opp_titles = {x.id: x.title for x in s.opportunities}
    for o in s.opportunities:
        d.raw(_opportunity_detail(o, s, opp_titles))
    return d.toc_html() + d.body()


def r05(s: SynthesisContent, meta) -> str:
    posture = s.strategy_profile.get("posture", "").replace("_", " ").strip()
    # a SHORT posture reads as a direction phrase in the standfirst; a long one (a full sentence)
    # would garble the sentence, so it becomes its own framing line under a clean lede.
    if posture and len(posture.split()) <= 5:
        lede = f"Sequenced across three horizons, aimed at a {posture} direction."
    else:
        lede = "The recommended opportunities, sequenced across three horizons."
    d = _Doc("Transformation Roadmap", lede)
    if posture and len(posture.split()) > 5:
        d.raw(f"<p><strong>Strategic direction.</strong> {esc(posture[:1].upper() + posture[1:])}</p>")
    d.h1("Implementation roadmap")
    d.raw(roadmap_timeline_svg(s.roadmap))
    d.h1("Horizon detail")
    for hz in s.roadmap:
        items = []
        for it in hz.items:
            tag = " <span class='chip'>opportunity</span>" if it.opportunity_id else ""
            items.append(f"<li><strong>{esc(it.title)}</strong>{tag} — {esc(it.rationale)}</li>")
        d.raw(f"<div class='horizon'><h4>{esc(hz.horizon)} — {esc(hz.theme)} "
              f"<span class='win'>({esc(hz.window)})</span></h4><ul>" + "".join(items) + "</ul></div>")
    d.h1("How the work connects")
    d.p("The enabling relationships between the opportunities — what unlocks what.")
    d.raw(dependency_map_svg(s.opportunities))
    return d.toc_html() + d.body()


def r06(s: SynthesisContent, meta) -> str:
    d = _Doc("Supporting Artefacts", "Reference material behind this assessment.")
    d.h1("Source provenance")
    d.p("Every figure in this assessment is computed from the sources below and traces back to "
        "them.")
    si = ["<table><thead><tr><th>Source</th><th>Type</th><th>What it is</th>"
          "<th>Findings it supported</th></tr></thead><tbody>"]
    for doc in s.source_index:
        fnd = ", ".join(doc.supported_findings) if doc.supported_findings else "—"
        name = f"<a href='{_src_href(doc.doc_id)}'>{esc(doc.business_name)}</a>"
        si.append(f"<tr><td>{name}</td><td>{esc(doc.doc_type)}</td>"
                  f"<td>{esc(doc.what_we_read)}</td><td>{esc(fnd)}</td></tr>")
    si.append("</tbody></table>")
    d.raw("".join(si))
    if s.metrics_framework:
        d.h1("Success metrics framework")
        d.p("How the impact of the recommended interventions should be measured once live — the "
            "dimension, what it means, and the target to hold delivery to.")
        mt = ["<table><thead><tr><th>Metric</th><th>Definition</th><th>Target</th>"
              "</tr></thead><tbody>"]
        for m in s.metrics_framework:
            mt.append(f"<tr><td><strong>{esc(m.name)}</strong></td><td>{esc(m.definition)}</td>"
                      f"<td>{esc(m.target)}</td></tr>")
        mt.append("</tbody></table>")
        d.raw("".join(mt))
    donut = render_charts(s.charts, kinds={"donut"})
    if donut:
        d.h1("Where the failures concentrate")
        d.raw(donut)
    d.h1("System & data-flow map")
    d.p("The systems view of the same domain — which business systems the process touches and how "
        "data moves between them.")
    d.raw(data_flow_svg(s.current_state.process_flow))
    d.raw("<p class='badge-note'>A full technical trace of every figure in this assessment is "
          "available to your data team on request.</p>")
    return d.toc_html() + d.body()


# ---------------------------------------------------------------------------
# grounded component renderers (HTML)
# ---------------------------------------------------------------------------
def _severity(rank: int, explicit: str = "") -> tuple[str, str]:
    """Severity badge for a pain point. Uses an explicit grounded severity when set
    (high|medium|lower), else falls back to the impact rank. Red/amber for high/medium; neutral blue
    for lower (green would read as 'good' and clash in a pain-point context)."""
    level = (explicit or "").strip().lower()
    if not level:
        level = "high" if rank <= 1 else "medium" if rank == 2 else "lower"
    if level == "high":
        return "b-high", "High Severity"
    if level == "medium":
        return "b-med", "Medium Severity"
    return "b-pat", "Lower Severity"


def _is_high(pp) -> bool:
    lvl = (pp.severity or "").strip().lower()
    return lvl == "high" if lvl else pp.impact_rank <= 1


def _pain_point_card(pp, idx: int) -> str:
    sev_cls, sev_lbl = _severity(pp.impact_rank, pp.severity)
    badges = [f"<span class='badge {sev_cls}'>{sev_lbl}</span>"]
    cat = pp.category or pp.failure_pattern
    if cat:
        badges.append(f"<span class='badge b-cat'>{esc(_clip(cat, 28))}</span>")
    h = ["<div class='card'>",
         "<div class='pp-hdr'>",
         f"<div class='pp-id'>PP<br>{idx:02d}</div>",
         f"<div><div class='pp-name'>{esc(pp.title)}</div>"
         f"<div class='pp-badges'>{''.join(badges)}</div></div>",
         "</div>",
         f"<p>{esc(pp.description)}</p>"]
    mini = _mini_stats(pp.quantified)
    if mini:
        h.append(mini)
    if pp.detail_table:
        h.append(_data_table(pp.detail_table))
    h.append(f"<p><strong>Root cause:</strong> {esc(pp.root_cause)}</p>")
    quote = _ev_quote(pp.sources)
    if quote:
        h.append(quote)
    if pp.business_consequence:
        hi = _is_high(pp)
        sev_box = "high-box" if hi else "med-box"
        title_cls = "hb-title" if hi else "mb-title"
        text_cls = "hb-text" if hi else "mb-text"
        h.append(f"<div class='{sev_box}'><div class='{title_cls}'>Business impact</div>"
                 f"<div class='{text_cls}'>{esc(pp.business_consequence)}</div></div>")
    if pp.opportunity_signal:
        h.append("<div class='note-box'><div class='nb-title'>Addressed by</div>"
                 f"<div class='nb-text'>{esc(pp.opportunity_signal)} — see the Opportunity "
                 "Portfolio.</div></div>")
    h.append(f"<p class='prov'>Where this comes from: {_cite_links(pp.sources)}</p>")
    h.append("</div>")
    return "".join(h)


def _mini_stats(quantified) -> str:
    """A row of grounded mini-stats from a pain point's NumberRefs. Empty → ''."""
    cells = []
    for n in (quantified or [])[:4]:
        if n.unit == "eur":
            val, cls = _fmt_money(n.value), "red"
        elif n.unit == "percent":
            val, cls = f"{n.value:g}%", "amber"
        else:
            val = f"{int(n.value):,}" if float(n.value) == int(n.value) else f"{n.value:g}"
            cls = "blue"
        label = _clip((n.label or n.text or "").strip(), 34) or "figure"
        cells.append(f"<div class='mini'><div class='mval {cls}'>{esc(val)}</div>"
                     f"<div class='mlbl'>{esc(label)}</div></div>")
    return f"<div class='mini-row'>{''.join(cells)}</div>" if cells else ""


def _ev_quote(sources) -> str:
    """An attributed evidence quote — ONLY when a verified source quote exists. Attributed to the
    friendly document name (never a fabricated person/date). Empty → ''."""
    for r in sources or []:
        q = (getattr(r, "quote", "") or "").strip()
        if q:
            return ("<div class='ev-quote'>"
                    f"<div class='eq-text'>&ldquo;{esc(_clip(q, 240))}&rdquo;</div>"
                    f"<div class='eq-attr'>— {esc(docnames.friendly(r.doc_id))}</div></div>")
    return ""


def _seq_order(opportunities):
    """Stable order honouring dependencies: an opportunity never precedes one it depends on. Keeps
    declared order otherwise (deterministic)."""
    opps = list(opportunities)
    by_id = {o.id: o for o in opps}
    placed, order = set(), []

    def visit(o):
        if o.id in placed:
            return
        for d in o.dependencies:
            if d in by_id and d not in placed:
                visit(by_id[d])
        placed.add(o.id)
        order.append(o)
    for o in opps:
        visit(o)
    return order


def _rec_card(o, idx: int, s: SynthesisContent, titles: dict) -> str:
    pat = _PATTERN_LABEL.get(o.pattern.value, "")
    badges = []
    if o.value_rating:
        prio = ("b-crit" if o.value_rating == "high" else
                "b-med" if o.value_rating == "medium" else "b-low")
        lbl = {"high": "Critical Priority", "medium": "High Priority"}.get(
            o.value_rating, "Medium Priority")
        badges.append(f"<span class='badge {prio}'>{lbl}</span>")
    hz = _opp_horizon(o.id, s.roadmap)
    if hz:
        badges.append(f"<span class='badge {_HORIZON_CLASS.get(hz,'b-h1')}'>{esc(hz)}</span>")
    if o.pattern.value == "ai_agent":
        badges.append("<span class='badge b-ai'>AI Opportunity</span>")
    if pat:
        badges.append(f"<span class='badge b-pat'>{esc(pat)}</span>")
    pp = OPP_TO_PP_LABEL(o)
    trace = []
    if pp:
        trace.append(f"Addresses {esc(pp)}")
    trace.append(f"Delivers {esc(o.id)}")
    badges.append(f"<span class='trace'>{' &nbsp;|&nbsp; '.join(trace)}</span>")

    h = ["<div class='rec-card'><div class='rec-hdr'>",
         f"<div class='rec-id'>R<br>{idx:02d}</div>",
         f"<div><div class='rec-name'>{esc(o.title)}</div>"
         f"<div class='rec-badges'>{''.join(badges)}</div></div></div>",
         "<div class='rec-body'>",
         f"<p>{esc(o.overview)}</p>"]
    # phased actions: derive from before→after milestones placed on the opportunity's horizon
    actions = _rec_actions(o, hz)
    if actions:
        h.append("<h4>Phased actions</h4><ul class='action-list'>")
        for hzlbl, text in actions:
            cls = _HORIZON_CLASS.get(hzlbl, "al-h1")
            h.append(f"<li><span class='al-horizon {cls}'>{esc(hzlbl)}</span>"
                     f"<span>{esc(text)}</span></li>")
        h.append("</ul>")
    if o.success_metrics:
        h.append("<h4>Success criteria</h4><div class='kpi-row'>"
                 + "".join(f"<span class='kpi-pill'>{esc(m)}</span>" for m in o.success_metrics)
                 + "</div>")
    h.append("</div></div>")
    # dependency relationship as a strategy box (grounded in declared dependencies)
    rel = []
    if o.dependencies:
        rel.append("Requires " + ", ".join(str(titles.get(d, d)) for d in o.dependencies)
                   + " first.")
    if o.prerequisite_for:
        rel.append("Prerequisite for "
                   + ", ".join(str(titles.get(d, d)) for d in o.prerequisite_for) + ".")
    if rel:
        h.append("<div class='strat-box'><div class='sb-title'>Dependency</div>"
                 f"<div class='sb-text'>{esc(' '.join(rel))}</div></div>")
    return "".join(h)


def _rec_actions(o, hz: str) -> list[tuple[str, str]]:
    """Phased actions for a recommendation, grounded in the after-process steps (what the change
    actually does), each tagged to the opportunity's horizon. Falls back to the implementation
    approach as a single action if there are no after-steps."""
    out = []
    label = hz or "H1"
    for st in (o.after_process or [])[:4]:
        text = st.description or st.name
        if text:
            out.append((label, _clip(text, 220)))
    if not out and o.implementation_approach:
        out.append((label, _clip(o.implementation_approach, 220)))
    return out


def _opportunity_detail(o, s: SynthesisContent, opp_titles: dict) -> str:
    h = ["<div class='card'>",
         f"<h3>{esc(o.title)}<span class='pattern' style='margin-left:.5rem'>"
         f"{_PATTERN_LABEL.get(o.pattern.value,'')}</span></h3>",
         f"<p>{esc(o.overview)}</p>",
         "<div class='ba-grid'>",
         "<div class='col before'><div class='ba-tag'>Today</div>"
         + _steps(o.before_process) + "</div>",
         "<div class='ba-arrow' aria-hidden='true'><svg viewBox='0 0 28 28'>"
         "<path d='M4 14h16M15 8l6 6-6 6' fill='none' stroke='var(--blue)' stroke-width='2.4' "
         "stroke-linecap='round' stroke-linejoin='round'/></svg></div>",
         "<div class='col after'><div class='ba-tag after'>With the change</div>"
         + _steps(o.after_process) + "</div>",
         "</div>"]
    bi = o.business_impact
    impact = "<p><strong>Business impact.</strong> " + esc(bi.narrative)
    if bi.quantified:
        impact += " " + " &nbsp; ".join(_metric(n) for n in bi.quantified)
    impact += "</p>"
    h.append(impact)
    if bi.derivation:
        h.append(f"<p class='prov'>How we get there: {esc(bi.derivation)}</p>")
    h.append(f"<p><strong>How it's delivered.</strong> {esc(o.implementation_approach)}</p>")
    if o.personas or o.expected_behaviour or o.escalation:
        om = ["<div class='opmodel'>"]
        if o.personas:
            om.append("<p><strong>Who uses it.</strong> " + ", ".join(esc(x) for x in o.personas)
                      + "</p>")
        if o.expected_behaviour:
            om.append(f"<p><strong>Expected behaviour.</strong> {esc(o.expected_behaviour)}</p>")
        if o.escalation:
            om.append(f"<p><strong>Escalation &amp; human fallback.</strong> {esc(o.escalation)}</p>")
        if o.knowledge_sources or o.document_formats:
            bits = []
            if o.knowledge_sources:
                bits.append("<strong>Sources.</strong> "
                            + ", ".join(esc(x) for x in o.knowledge_sources))
            if o.document_formats:
                bits.append("<strong>Formats.</strong> "
                            + ", ".join(esc(x) for x in o.document_formats))
            om.append("<p>" + " &nbsp; ".join(bits) + "</p>")
        om.append("</div>")
        h.append("".join(om))
    if o.required_integrations:
        h.append("<p><strong>Connects:</strong> "
                 + ", ".join(esc(x) for x in o.required_integrations) + "</p>")
    if o.success_metrics:
        h.append("<p><strong>Success looks like:</strong></p><ul>"
                 + "".join(f"<li>{esc(x)}</li>" for x in o.success_metrics) + "</ul>")
    if o.dependencies:
        dep = "Requires " + ", ".join(str(opp_titles.get(d, d)) for d in o.dependencies) + " first."
    else:
        dep = "Independent — can start immediately."
    if o.prerequisite_for:
        dep += (" Prerequisite for "
                + ", ".join(str(opp_titles.get(d, d)) for d in o.prerequisite_for) + ".")
    h.append(f"<p><strong>Dependencies:</strong> {esc(dep)}</p>")
    if o.risks:
        h.append("<p><strong>Risks:</strong></p><ul>"
                 + "".join(f"<li>{esc(x)}</li>" for x in o.risks) + "</ul>")
    h.append(f"<p class='prov'>Where this comes from: {_cite_links(o.sources)}</p>")
    h.append("</div>")
    return "".join(h)


def OPP_TO_PP_LABEL(o) -> str:
    """The pain point an opportunity addresses, as a label (derived field set by build)."""
    return getattr(o, "addresses_pain_point", "") or ""


def _opp_horizon(opp_id: str, roadmap) -> str:
    """Which horizon an opportunity is scheduled in (from the roadmap placement). '' if unplaced."""
    for hz in roadmap or []:
        for it in hz.items:
            if it.opportunity_id == opp_id:
                return hz.horizon
    return ""


def _principles(s: SynthesisContent) -> list[tuple[str, str]]:
    """Guiding principles, DERIVED in code from grounded synthesis text (no invented principles).
    Built from the strategy posture + the sequencing/strategic-readiness narratives, split into
    short titled cards. Returns [] when there is nothing grounded to show."""
    out = []
    posture = (s.strategy_profile.get("posture") or "").replace("_", " ").strip()
    if posture:
        out.append(("Strategic direction", posture[:1].upper() + posture[1:]))
    for title, text in (("Sequencing", s.sequencing_rationale),
                        ("Readiness", s.strategic_readiness)):
        text = (text or "").strip()
        if text:
            out.append((title, _clip(_first_sentence(text), 180)))
    return out[:4]


def _first_sentence(text: str) -> str:
    m = re.search(r"^(.*?[.!?])(\s|$)", text)
    return m.group(1) if m else text


# ---------------------------------------------------------------------------
# infographics — pure inline SVG, offline-safe, grounded inputs only
# ---------------------------------------------------------------------------
_SVG_DEFS = (
    "<defs>"
    "<marker id='arr' markerWidth='10' markerHeight='10' refX='8' refY='3.2' orient='auto'>"
    "<path d='M0,0 L8,3.2 L0,6.4 Z' fill='#2563eb'/></marker>"
    "<marker id='arrg' markerWidth='10' markerHeight='10' refX='8' refY='3.2' orient='auto'>"
    "<path d='M0,0 L8,3.2 L0,6.4 Z' fill='#9aa7b6'/></marker>"
    "<filter id='sh' x='-20%' y='-20%' width='140%' height='150%'>"
    "<feDropShadow dx='0' dy='1.2' stdDeviation='2' flood-color='#1a2f50' flood-opacity='0.12'/>"
    "</filter></defs>"
)
# categorical palette in the navy/blue family
_SERIES = ["#1a2f50", "#2563eb", "#3665a8", "#60a5fa", "#a9c7f0"]


def _fig(cap: str, svg: str, foot: str = "") -> str:
    foot_html = f"<div class='fig-foot'>{esc(foot)}</div>" if foot else ""
    return f"<div class='fig'><div class='fig-cap'>{esc(cap)}</div>{svg}{foot_html}</div>"


def process_flow_svg(steps) -> str:
    """Report 01 hero: a wrapping chain of node cards (step number + name header band, actor +
    system lines), navy header, blue connecting arrows. Grounded from this run's steps. Empty → ''."""
    if not steps:
        return ""
    WRAP, NW, NH, GAP_X, GAP_Y, PAD, HDR = 3, 234, 104, 58, 52, 16, 30
    rows = [steps[i:i + WRAP] for i in range(0, len(steps), WRAP)]
    cols = min(WRAP, len(steps))
    width = PAD * 2 + cols * NW + (cols - 1) * GAP_X
    height = PAD * 2 + len(rows) * NH + (len(rows) - 1) * GAP_Y
    out = [f"<svg class='chart' viewBox='0 0 {width} {height}' width='100%' role='img' "
           f"aria-label='Process flow diagram' xmlns='http://www.w3.org/2000/svg'>", _SVG_DEFS]

    def node_xy(idx):
        r, c = idx // WRAP, idx % WRAP
        return PAD + c * (NW + GAP_X), PAD + r * (NH + GAP_Y)

    for i in range(len(steps) - 1):
        x1, y1 = node_xy(i)
        x2, y2 = node_xy(i + 1)
        if (i // WRAP) == ((i + 1) // WRAP):
            out.append(f"<line x1='{x1+NW}' y1='{y1+NH/2}' x2='{x2-3}' y2='{y2+NH/2}' "
                       f"stroke='#2563eb' stroke-width='2.2' marker-end='url(#arr)'/>")
        else:
            sx, sy = x1 + NW / 2, y1 + NH
            ex, ey = x2 + NW / 2, y2 - 3
            midy = sy + GAP_Y / 2
            out.append(f"<path d='M{sx},{sy} L{sx},{midy} L{ex},{midy} L{ex},{ey}' fill='none' "
                       f"stroke='#2563eb' stroke-width='2.2' marker-end='url(#arr)'/>")
    for i, st in enumerate(steps):
        x, y = node_xy(i)
        actor, system = getattr(st, "actor", ""), getattr(st, "system", "")
        out.append("<g filter='url(#sh)'>")
        out.append(f"<rect x='{x}' y='{y}' width='{NW}' height='{NH}' rx='10' fill='#fff' "
                   f"stroke='#d1d5db' stroke-width='1'/>")
        out.append(f"<path d='M{x},{y+10} a10,10 0 0 1 10,-10 h{NW-20} a10,10 0 0 1 10,10 "
                   f"v{HDR-10} h-{NW} z' fill='#1a2f50'/>")
        out.append(f"<text x='{x+13}' y='{y+20}' font-size='13' font-weight='700' fill='#fff'>"
                   f"{st.seq}. {esc(_clipw(st.name, 30))}</text>")
        if actor:
            out.append(f"<text x='{x+13}' y='{y+HDR+22}' font-size='11.5' fill='#111827'>"
                       f"<tspan font-weight='700'>Who </tspan>{esc(_clipw(actor, 26))}</text>")
        if system:
            out.append(f"<text x='{x+13}' y='{y+HDR+44}' font-size='11.5' fill='#6b7280'>"
                       f"<tspan font-weight='700' fill='#111827'>System </tspan>"
                       f"{esc(_clipw(system, 24))}</text>")
        out.append("</g>")
    out.append("</svg>")
    return _fig("How work moves, end to end", "".join(out))


def context_map_svg(steps, handoffs) -> str:
    """A context/handoff map: the process steps as boxes, with the grounded handoffs drawn as
    labelled arrows between them. Boxes = real steps; arrows = real handoffs (by mechanism). Pure
    SVG. Empty (no steps or no handoffs) → ''."""
    steps = list(steps or [])
    handoffs = list(handoffs or [])
    if len(steps) < 2 or not handoffs:
        return ""
    # lay steps out in a horizontal lane, wrapping; map step name -> index for handoff lookup
    WRAP = 4
    NW, NH, GAP_X, GAP_Y, PAD = 168, 56, 40, 60, 16
    cols = min(WRAP, len(steps))
    rows = [steps[i:i + WRAP] for i in range(0, len(steps), WRAP)]
    width = PAD * 2 + cols * NW + (cols - 1) * GAP_X
    height = PAD * 2 + len(rows) * NH + (len(rows) - 1) * GAP_Y
    name_idx = {(st.name or "").strip().lower(): i for i, st in enumerate(steps)}

    def cxy(idx):
        r, c = idx // WRAP, idx % WRAP
        return PAD + c * (NW + GAP_X), PAD + r * (NH + GAP_Y)

    out = [f"<svg class='chart' viewBox='0 0 {width} {height}' width='100%' role='img' "
           f"aria-label='Handoff map' xmlns='http://www.w3.org/2000/svg'>", _SVG_DEFS]
    # arrows for handoffs whose endpoints we can resolve to steps
    for ho in handoffs:
        a = name_idx.get((ho.from_step or "").strip().lower())
        b = name_idx.get((ho.to_step or "").strip().lower())
        if a is None or b is None or a == b:
            continue
        x1, y1 = cxy(a)
        x2, y2 = cxy(b)
        sx, sy = x1 + NW, y1 + NH / 2
        ex, ey = x2, y2 + NH / 2
        if y1 == y2 and b == a + 1:
            out.append(f"<line x1='{sx}' y1='{sy}' x2='{ex-3}' y2='{ey}' stroke='#3665a8' "
                       f"stroke-width='1.8' marker-end='url(#arr)'/>")
        else:
            my = min(y1, y2) - GAP_Y / 2 + 6
            cx1, cx2 = x1 + NW / 2, x2 + NW / 2
            out.append(f"<path d='M{cx1},{y1} C{cx1},{my} {cx2},{my} {cx2},{y2}' fill='none' "
                       f"stroke='#3665a8' stroke-width='1.6' stroke-dasharray='5 4' "
                       f"marker-end='url(#arr)'/>")
    for i, st in enumerate(steps):
        x, y = cxy(i)
        out.append(f"<g filter='url(#sh)'><rect x='{x}' y='{y}' width='{NW}' height='{NH}' rx='8' "
                   f"fill='#eff6ff' stroke='#2563eb' stroke-width='1.2'/>"
                   f"<text x='{x+NW/2}' y='{y+NH/2-2}' text-anchor='middle' font-size='12' "
                   f"font-weight='700' fill='#1a2f50'>{esc(_clipw(st.name, 20))}</text>"
                   f"<text x='{x+NW/2}' y='{y+NH/2+15}' text-anchor='middle' font-size='10' "
                   f"fill='#6b7280'>{esc(_clipw(getattr(st,'system','') or '', 22))}</text></g>")
    out.append("</svg>")
    return _fig("Where work crosses between steps and systems", "".join(out),
                "Boxes are process steps; arrows are the handoffs recorded between them.")


def root_cause_svg(pain_points, patterns) -> str:
    """A root-cause map: shared structural cause(s) on the left → the pain points they drive on the
    right, with arrows. Causes come from cross_process_patterns (grounded); if none are given, the
    pain points' own failure patterns are used as the cause nodes. Empty → ''."""
    pps = sorted(pain_points or [], key=lambda p: p.impact_rank)
    if not pps:
        return ""
    causes = [(c.get("pattern", "") or "").strip() for c in (patterns or [])]
    causes = [c for c in causes if c][:3]
    if not causes:
        # fall back to the distinct failure patterns across pain points
        seen = []
        for p in pps:
            fp = (p.failure_pattern or "").strip()
            if fp and fp.lower() not in [x.lower() for x in seen]:
                seen.append(fp)
        causes = seen[:3]
    if not causes:
        return ""
    LW, RW, NH, PAD, GAP = 188, 224, 50, 18, 16
    midgap = 96
    n_left, n_right = len(causes), len(pps)
    leftH = n_left * NH + (n_left - 1) * GAP
    rightH = n_right * NH + (n_right - 1) * GAP
    height = PAD * 2 + max(leftH, rightH)
    width = PAD * 2 + LW + midgap + RW
    lx = PAD
    rx = PAD + LW + midgap

    def ly(i):
        off = (height - leftH) / 2
        return off + i * (NH + GAP)

    def ry(i):
        off = (height - rightH) / 2
        return off + i * (NH + GAP)

    out = [f"<svg class='chart' viewBox='0 0 {width} {height}' width='100%' role='img' "
           f"aria-label='Root cause map' xmlns='http://www.w3.org/2000/svg'>", _SVG_DEFS]
    # edges: each pain point linked to its matching cause (by failure pattern), else to all causes
    for j, p in enumerate(pps):
        fp = (p.failure_pattern or "").strip().lower()
        match = [i for i, c in enumerate(causes) if c.lower() == fp]
        targets = match or list(range(len(causes)))
        for i in targets:
            y1 = ly(i) + NH / 2
            y2 = ry(j) + NH / 2
            out.append(f"<path d='M{lx+LW},{y1} C{lx+LW+midgap/2},{y1} {rx-midgap/2},{y2} "
                       f"{rx},{y2}' fill='none' stroke='#9aa7b6' stroke-width='1.4' "
                       f"marker-end='url(#arrg)'/>")
    for i, c in enumerate(causes):
        y = ly(i)
        out.append(f"<g filter='url(#sh)'><rect x='{lx}' y='{y}' width='{LW}' height='{NH}' rx='8' "
                   f"fill='#1a2f50'/><text x='{lx+LW/2}' y='{y+NH/2+4}' text-anchor='middle' "
                   f"font-size='11.5' font-weight='700' fill='#fff'>{esc(_clipw(c, 26))}</text></g>")
    for j, p in enumerate(pps):
        y = ry(j)
        sev_fill = "#fef2f2" if p.impact_rank <= 1 else "#fffbeb" if p.impact_rank == 2 else "#f9fafb"
        sev_bd = "#fca5a5" if p.impact_rank <= 1 else "#fcd34d" if p.impact_rank == 2 else "#d1d5db"
        out.append(f"<g filter='url(#sh)'><rect x='{rx}' y='{y}' width='{RW}' height='{NH}' rx='8' "
                   f"fill='{sev_fill}' stroke='{sev_bd}' stroke-width='1.2'/>"
                   f"<text x='{rx+12}' y='{y+22}' font-size='11.5' font-weight='700' fill='#1a2f50'>"
                   f"{esc(p.id)}  {esc(_clipw(p.title, 24))}</text>"
                   f"<text x='{rx+12}' y='{y+40}' font-size='10' fill='#6b7280'>"
                   f"{esc(_clip(p.failure_pattern or '', 32))}</text></g>")
    out.append("</svg>")
    return _fig("How the issues trace back to shared causes", "".join(out),
                "Left: structural causes. Right: the pain points each one drives.")


def value_matrix_svg(opportunities) -> str:
    """Value (y) vs feasibility (x) bubble plot using value_score/feasibility_score (1–5, grounded).
    Quadrant guides + soft 'do first' shade; deterministic collision spread; bubbles labelled with
    opportunity id. Empty (no scored opportunities) → ''."""
    opps = [o for o in opportunities if o.value_score and o.feasibility_score]
    if not opps:
        return ""
    W, H, PAD = 520, 420, 56
    plotW, plotH = W - PAD * 2, H - PAD * 2

    def px(score):
        return PAD + (score - 1) / 4 * plotW

    def py(score):
        return PAD + plotH - (score - 1) / 4 * plotH
    out = [f"<svg class='chart' viewBox='0 0 {W} {H}' width='100%' role='img' "
           f"aria-label='Value versus feasibility' xmlns='http://www.w3.org/2000/svg'>", _SVG_DEFS]
    midx, midy = px(3), py(3)
    out.append(f"<rect x='{midx}' y='{PAD}' width='{PAD+plotW-midx}' height='{midy-PAD}' "
               f"fill='#eff6ff'/>")
    out.append(f"<line x1='{midx}' y1='{PAD}' x2='{midx}' y2='{PAD+plotH}' stroke='#e3e8ee'/>")
    out.append(f"<line x1='{PAD}' y1='{midy}' x2='{PAD+plotW}' y2='{midy}' stroke='#e3e8ee'/>")
    out.append(f"<text x='{PAD+plotW/2}' y='{H-14}' text-anchor='middle' font-size='12' "
               f"fill='#6b7280' font-weight='700'>Feasibility →</text>")
    out.append(f"<text x='16' y='{PAD+plotH/2}' text-anchor='middle' font-size='12' fill='#6b7280' "
               f"font-weight='700' transform='rotate(-90 16 {PAD+plotH/2})'>Value →</text>")
    for qx, qy, anchor, label in [
            (PAD + plotW - 6, PAD + 16, "end", "Do first"),
            (PAD + 6, PAD + 16, "start", "Plan for"),
            (PAD + plotW - 6, PAD + plotH - 8, "end", "Quick wins"),
            (PAD + 6, PAD + plotH - 8, "start", "Reconsider")]:
        out.append(f"<text x='{qx}' y='{qy}' text-anchor='{anchor}' font-size='10' "
                   f"fill='#9aa7b6' font-weight='700'>{label}</text>")
    placed: dict[tuple, int] = {}
    for o in opps:
        key = (o.feasibility_score, o.value_score)
        k = placed.get(key, 0)
        placed[key] = k + 1
        ox = (k % 3 - 1) * 22 if k else 0
        oy = (k // 3) * 22 if k else 0
        cx, cy = px(o.feasibility_score) + ox, py(o.value_score) + oy
        out.append(f"<circle cx='{cx}' cy='{cy}' r='17' fill='#2563eb' fill-opacity='0.16' "
                   f"stroke='#2563eb'/>")
        out.append(f"<text x='{cx}' y='{cy+4}' text-anchor='middle' font-size='11' "
                   f"font-weight='700' fill='#1d4ed8'>{esc(o.id)}</text>")
    out.append("</svg>")
    return _fig("Where each opportunity sits on value versus feasibility", "".join(out))


def impact_bars_svg(pain_points) -> str:
    """Horizontal bars ranking pain points by impact_rank (1 = most material). The PP id + title sit
    in a LEFT label column (always fully readable); the bar to the right is a clean rank indicator
    (length encodes rank position, not a fabricated metric) with the rank number at its end.
    Empty → ''."""
    pts = sorted(pain_points or [], key=lambda p: p.impact_rank)
    if not pts:
        return ""
    rows = len(pts)
    BARH, GAP, PAD, LBLW = 30, 16, 12, 360
    W = 780
    innerW = W - PAD * 2 - LBLW - 40
    H = PAD * 2 + rows * BARH + (rows - 1) * GAP
    out = [f"<svg class='chart' viewBox='0 0 {W} {H}' width='100%' role='img' "
           f"aria-label='Pain points ranked by impact' xmlns='http://www.w3.org/2000/svg'>",
           _SVG_DEFS]
    for i, p in enumerate(pts):
        y = PAD + i * (BARH + GAP)
        frac = (rows - i) / rows
        w = max(2, int(innerW * frac))
        out.append(f"<text x='{PAD}' y='{y+BARH/2+1}' font-size='11' font-weight='700' "
                   f"fill='#2563eb'>{esc(p.id)}</text>")
        out.append(f"<text x='{PAD+34}' y='{y+BARH/2+1}' font-size='11.5' fill='#1a2f50'>"
                   f"{esc(_clipw(p.title, 50))}</text>")
        out.append(f"<rect x='{PAD+LBLW}' y='{y}' width='{w}' height='{BARH}' rx='5' fill='#1a2f50' "
                   f"filter='url(#sh)'/>")
        out.append(f"<text x='{PAD+LBLW+w-12}' y='{y+BARH/2+4}' text-anchor='end' font-size='11.5' "
                   f"font-weight='700' fill='#fff'>#{i+1}</text>")
    out.append("</svg>")
    return _fig("Issues ranked by business impact (most material first)", "".join(out))


def roadmap_timeline_svg(roadmap) -> str:
    """A horizon timeline: one column per horizon (H1/H2/H3) with a navy/blue header band (theme +
    window) and the horizon's items as stacked cards. A time arrow runs across the top (now →
    later); opportunity-backed items carry a dot. Positions encode horizon + item order only.
    Empty → ''."""
    horizons = list(roadmap or [])
    if not horizons:
        return ""
    cols = len(horizons)
    COLW, GAP, PAD, HDR, TOPBAR = 232, 26, 16, 56, 34
    ITEMH, ITEMGAP = 52, 10
    max_items = max((len(hz.items) for hz in horizons), default=0)
    bodyH = max_items * ITEMH + max(0, max_items - 1) * ITEMGAP
    W = PAD * 2 + cols * COLW + (cols - 1) * GAP
    H = PAD * 2 + TOPBAR + HDR + bodyH + 10
    out = [f"<svg class='chart' viewBox='0 0 {W} {H}' width='100%' role='img' "
           f"aria-label='Transformation roadmap timeline' xmlns='http://www.w3.org/2000/svg'>",
           _SVG_DEFS]
    ay = PAD + TOPBAR / 2
    out.append(f"<line x1='{PAD}' y1='{ay}' x2='{W-PAD-6}' y2='{ay}' stroke='#2563eb' "
               f"stroke-width='1.6' marker-end='url(#arr)'/>")
    out.append(f"<text x='{PAD+2}' y='{ay-8}' font-size='10' fill='#9aa7b6' "
               f"font-weight='700'>NOW</text>")
    out.append(f"<text x='{W-PAD-10}' y='{ay-8}' font-size='10' fill='#9aa7b6' text-anchor='end' "
               f"font-weight='700'>LATER</text>")
    shades = ["#1a2f50", "#2563eb", "#3665a8"]
    for ci, hz in enumerate(horizons):
        x = PAD + ci * (COLW + GAP)
        y = PAD + TOPBAR
        band = shades[ci % len(shades)]
        out.append(f"<path d='M{x},{y+10} a10,10 0 0 1 10,-10 h{COLW-20} a10,10 0 0 1 10,10 "
                   f"v{HDR-10} h-{COLW} z' fill='{band}'/>")
        out.append(f"<text x='{x+14}' y='{y+22}' font-size='12.5' font-weight='700' fill='#fff'>"
                   f"{esc(hz.horizon)} · {esc(_clipw(hz.theme, 26))}</text>")
        out.append(f"<text x='{x+14}' y='{y+40}' font-size='10.5' fill='#cfe0fb'>"
                   f"{esc(hz.window)}</text>")
        iy = y + HDR + 12
        for it in hz.items:
            out.append(f"<rect x='{x}' y='{iy}' width='{COLW}' height='{ITEMH}' rx='8' fill='#fff' "
                       f"stroke='#d1d5db'/>")
            if it.opportunity_id:
                out.append(f"<circle cx='{x+14}' cy='{iy+ITEMH/2}' r='4' fill='{band}'/>")
            tx = x + (26 if it.opportunity_id else 14)
            out.append(f"<text x='{tx}' y='{iy+ITEMH/2-3}' font-size='11.5' font-weight='700' "
                       f"fill='#1a2f50'>{esc(_clipw(it.title, 30))}</text>")
            out.append(f"<text x='{tx}' y='{iy+ITEMH/2+13}' font-size='10' fill='#6b7280'>"
                       f"{esc(_clipw(it.rationale, 36))}</text>")
            iy += ITEMH + ITEMGAP
    out.append("</svg>")
    return _fig("The plan across three horizons (now → later)", "".join(out))


def dependency_map_svg(opportunities) -> str:
    """A dependency map: opportunity nodes with directed 'enables' edges (from declared
    dependencies) flowing into an outcome node. Pure SVG. Empty (no edges) → ''."""
    opps = list(opportunities or [])
    edges = [(d, o.id) for o in opps for d in o.dependencies if d in {x.id for x in opps}]
    if not edges:
        return ""
    # rank nodes by dependency depth so prerequisites sit left of dependents
    by_id = {o.id: o for o in opps}
    depth: dict[str, int] = {}

    def dep_depth(oid, guard):
        if oid in depth:
            return depth[oid]
        if oid in guard:
            return 0
        ds = [d for d in by_id[oid].dependencies if d in by_id]
        depth[oid] = (1 + max((dep_depth(d, guard | {oid}) for d in ds), default=-1)) if ds else 0
        return depth[oid]
    for o in opps:
        dep_depth(o.id, set())
    max_d = max(depth.values(), default=0)
    cols: dict[int, list] = {}
    for o in opps:
        cols.setdefault(depth[o.id], []).append(o)
    NW, NH, COLGAP, ROWGAP, PAD = 168, 48, 70, 18, 18
    n_cols = max_d + 2                                   # + outcome column
    rowmax = max((len(v) for v in cols.values()), default=1)
    width = PAD * 2 + n_cols * NW + (n_cols - 1) * COLGAP
    height = PAD * 2 + rowmax * NH + (rowmax - 1) * ROWGAP
    pos: dict[str, tuple] = {}

    def colx(c):
        return PAD + c * (NW + COLGAP)
    out = [f"<svg class='chart' viewBox='0 0 {width} {height}' width='100%' role='img' "
           f"aria-label='Opportunity dependency map' xmlns='http://www.w3.org/2000/svg'>", _SVG_DEFS]
    for c in range(max_d + 1):
        group = cols.get(c, [])
        colH = len(group) * NH + max(0, len(group) - 1) * ROWGAP
        y0 = (height - colH) / 2
        for r, o in enumerate(group):
            y = y0 + r * (NH + ROWGAP)
            pos[o.id] = (colx(c), y)
    # outcome node centred in the last column
    ox = colx(n_cols - 1)
    oy = (height - NH) / 2
    # every opportunity is placed above (cols covers depths 0..max_d), so pos has all ids.
    for src, dst in edges:
        x1, y1 = pos[src]
        x2, y2 = pos[dst]
        out.append(f"<path d='M{x1+NW},{y1+NH/2} C{x1+NW+COLGAP/2},{y1+NH/2} "
                   f"{x2-COLGAP/2},{y2+NH/2} {x2},{y2+NH/2}' fill='none' stroke='#2563eb' "
                   f"stroke-width='1.6' marker-end='url(#arr)'/>")
    # leaf nodes (no dependents) flow into the outcome
    has_dependent = {src for src, _ in edges}
    for o in opps:
        if o.id not in has_dependent:
            x1, y1 = pos[o.id]
            out.append(f"<path d='M{x1+NW},{y1+NH/2} C{x1+NW+COLGAP/2},{y1+NH/2} "
                       f"{ox-COLGAP/2},{oy+NH/2} {ox},{oy+NH/2}' fill='none' stroke='#9aa7b6' "
                       f"stroke-width='1.4' stroke-dasharray='5 4' marker-end='url(#arrg)'/>")
    for o in opps:
        x, y = pos[o.id]
        out.append(f"<g filter='url(#sh)'><rect x='{x}' y='{y}' width='{NW}' height='{NH}' rx='8' "
                   f"fill='#eff6ff' stroke='#2563eb' stroke-width='1.2'/>"
                   f"<text x='{x+NW/2}' y='{y+NH/2-2}' text-anchor='middle' font-size='11' "
                   f"font-weight='700' fill='#1a2f50'>{esc(o.id)}</text>"
                   f"<text x='{x+NW/2}' y='{y+NH/2+14}' text-anchor='middle' font-size='9.5' "
                   f"fill='#6b7280'>{esc(_clipw(o.title, 22))}</text></g>")
    out.append(f"<g filter='url(#sh)'><rect x='{ox}' y='{oy}' width='{NW}' height='{NH}' rx='8' "
               f"fill='#1a2f50'/><text x='{ox+NW/2}' y='{oy+NH/2+4}' text-anchor='middle' "
               f"font-size='11' font-weight='700' fill='#fff'>Target state</text></g>")
    out.append("</svg>")
    return _fig("How the opportunities enable one another", "".join(out),
                "Arrows show enabling relationships; all paths lead to the target state.")


def data_flow_svg(steps) -> str:
    """Supporting-artefacts systems view: the distinct business systems the process touches, with
    dashed connecting arrows. Derived from systems named across the steps. <2 systems → ''."""
    systems, seen = [], set()
    for st in steps or []:
        sysname = (getattr(st, "system", "") or "").strip()
        for part in [p.strip() for p in sysname.replace(" / ", "/").split("/") if p.strip()]:
            if part.lower() not in seen:
                seen.add(part.lower())
                systems.append(part)
    if len(systems) < 2:
        return ""
    NW, NH, GAP_X, PAD = 196, 58, 64, 16
    cols = min(4, len(systems))
    rows = [systems[i:i + 4] for i in range(0, len(systems), 4)]
    width = PAD * 2 + cols * NW + (cols - 1) * GAP_X
    height = PAD * 2 + len(rows) * NH + (len(rows) - 1) * 44
    out = [f"<svg class='chart' viewBox='0 0 {width} {height}' width='100%' role='img' "
           f"aria-label='System and data-flow map' xmlns='http://www.w3.org/2000/svg'>", _SVG_DEFS]

    def sxy(idx):
        r, c = idx // 4, idx % 4
        return PAD + c * (NW + GAP_X), PAD + r * (NH + 44)
    for i in range(len(systems) - 1):
        x1, y1 = sxy(i)
        x2, y2 = sxy(i + 1)
        if (i // 4) == ((i + 1) // 4):
            out.append(f"<line x1='{x1+NW}' y1='{y1+NH/2}' x2='{x2-3}' y2='{y2+NH/2}' "
                       f"stroke='#3665a8' stroke-width='2' stroke-dasharray='5 4' "
                       f"marker-end='url(#arr)'/>")
    for i, name in enumerate(systems):
        x, y = sxy(i)
        out.append(f"<g filter='url(#sh)'><rect x='{x}' y='{y}' width='{NW}' height='{NH}' rx='9' "
                   f"fill='#eff6ff' stroke='#2563eb' stroke-width='1.2'/>"
                   f"<text x='{x+NW/2}' y='{y+NH/2+5}' text-anchor='middle' font-size='13' "
                   f"font-weight='700' fill='#1a2f50'>{esc(_clipw(name, 22))}</text></g>")
    out.append("</svg>")
    return _fig("Systems the process touches, and how data moves between them", "".join(out))


def donut_svg(segments, caption: str) -> str:
    """A donut from (label, value) pairs (grounded). Returns '' if nothing to show."""
    segs = [(l, float(v)) for l, v in segments if _to_number_safe(v) and float(v) > 0]
    total = sum(v for _, v in segs)
    if not segs or total <= 0:
        return ""
    import math
    cx, cy, r, rin = 90, 90, 78, 46
    out = [f"<svg class='chart donut' viewBox='0 0 380 184' width='100%' role='img' "
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
        legend.append(f"<rect x='208' y='{ly-10}' width='12' height='12' rx='2' fill='{col}'/>"
                      f"<text x='226' y='{ly}' font-size='12' fill='#111827'>"
                      f"{esc(_nice_label(_clip(label, 20)))} · {esc(_fmt_compact(v))} "
                      f"({frac*100:.0f}%)</text>")
        a0 = a1
    out += legend
    out.append("</svg>")
    return _fig(caption, "".join(out))


def value_bar_svg(segments, caption: str, unit: str = "") -> str:
    """A horizontal bar chart from (label, value) pairs — bar length proportional to value, the
    real figure labelled on each. Grounded breakdowns only. Empty → ''."""
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
        out.append(f"<text x='{PAD}' y='{y+BARH/2+4}' font-size='12.5' font-weight='700' "
                   f"fill='#1a2f50'>{esc(_clip(label, 18))}</text>")
        out.append(f"<rect x='{PAD+LBLW}' y='{y}' width='{w}' height='{BARH}' rx='5' fill='#2563eb' "
                   f"filter='url(#sh)'/>")
        val = _fmt_compact(v) if unit == "eur" else (f"{int(v):,}" if v == int(v) else f"{v:g}")
        out.append(f"<text x='{PAD+LBLW+w+10}' y='{y+BARH/2+4}' font-size='12' font-weight='700' "
                   f"fill='#1d4ed8'>{esc(val)}</text>")
    out.append("</svg>")
    return _fig(caption, "".join(out))


def render_charts(charts, kinds=None) -> str:
    out = []
    for c in charts or []:
        if kinds is not None and c.get("kind") not in kinds:
            continue
        segs = [(seg.get("label", ""), seg.get("value")) for seg in c.get("segments", [])]
        title = c.get("title", "")
        if c.get("kind") == "donut":
            out.append(donut_svg(segs, title))
        else:
            out.append(value_bar_svg(segs, title, unit=c.get("unit", "")))
    return "\n".join(x for x in out if x)


# ---------------------------------------------------------------------------
# stat tiles (exec summary + pain-points overview)
# ---------------------------------------------------------------------------
def stat_tiles(tiles) -> str:
    if not tiles:
        return ""
    cells = "".join(f"<div class='stat-box'>{_stat_icon(l)}<div class='sv {c}'>{esc(v)}</div>"
                    f"<div class='sl'>{esc(l)}</div></div>" for v, l, c in tiles[:4])
    return f"<div class='stat-row'>{cells}</div>"


def _data_table(t, show_title: bool = True) -> str:
    """Render a grounded factual DataTable: a titled table with a navy header, optional caption above
    and footnote below, and a source line. `show_title=False` omits the table's own heading when a
    section heading already names it (avoids a duplicate title). Empty rows → ''."""
    if not t or not getattr(t, "rows", None):
        return ""
    head = "".join(f"<th>{esc(c)}</th>" for c in t.columns)
    body = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>" for row in t.rows)
    title = f"<h4>{esc(t.title)}</h4>" if show_title else ""
    cap = f"<div class='dt-cap'>{esc(t.caption)}</div>" if t.caption else ""
    note = f"<p class='prov'>{esc(t.note)}</p>" if t.note else ""
    src = (f"<p class='prov'>Source: {_cite_links(t.sources)}</p>"
           if getattr(t, "sources", None) else "")
    return (f"<div class='dt'>{title}{cap}"
            f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>{note}{src}</div>")


def _exec_tiles(s: SynthesisContent):
    """Derived-in-code grounded tiles for the executive summary (counts + headline figures)."""
    tiles = [(str(len(s.pain_points)), "issues identified", "blue"),
             (str(len(s.opportunities)), "opportunities mapped", "blue"),
             (str(len(s.source_index)), "sources analysed", "blue")]
    money, pct = [], []
    for p in sorted(s.pain_points, key=lambda x: x.impact_rank):
        for n in p.quantified:
            label = (n.label or "").strip() or p.title
            if n.unit == "eur":
                money.append((float(n.value), _fmt_money(n.value), _clip(label, 30)))
            elif n.unit == "percent":
                pct.append((f"{n.value:g}%", _clip(label, 30)))
    headline = []
    if money:
        _, v, l = max(money, key=lambda m: m[0])
        headline.append((v, l, "red"))
    if pct:
        headline.append((pct[0][0], pct[0][1], "amber"))
    return (headline + tiles)[:4]


def _pp_tiles(s: SynthesisContent):
    """Severity-coloured tiles for the pain-points overview (counts by severity + opp count). Counts
    by the explicit grounded severity where set, else the impact rank."""
    def level(p):
        lvl = (p.severity or "").strip().lower()
        return lvl if lvl else ("high" if p.impact_rank <= 1 else
                                "medium" if p.impact_rank == 2 else "lower")
    levels = [level(p) for p in s.pain_points]
    high = sum(1 for x in levels if x == "high")
    med = sum(1 for x in levels if x == "medium")
    return [(str(len(s.pain_points)), "pain points", "blue"),
            (str(high), "high severity", "red"),
            (str(med), "medium severity", "amber"),
            (str(len(s.opportunities)), "opportunities", "green")]


_STAT_GLYPHS = {
    "value": "<circle cx='8' cy='8' r='6'/><path d='M8 5v6M6 7h3a1.3 1.3 0 010 2.6H6'/>",
    "share": "<circle cx='8' cy='8' r='6'/><path d='M8 2.2A5.8 5.8 0 0113.8 8H8z'/>",
    "issue": "<path d='M8 2l6 11H2z'/><path d='M8 7v3M8 11.5v.2'/>",
    "opportunity": "<path d='M5 9a3 3 0 116 0c0 1.5-1.2 2-1.2 3.2H6.2C6.2 11 5 10.5 5 9z'/>"
                   "<path d='M6.4 14h3.2'/>",
    "source": "<path d='M3.5 3.2h6l3 3v6.6h-9z'/><path d='M9.5 3.2v3h3'/>",
}


def _stat_icon(label: str) -> str:
    lo = label.lower()
    key = ("value" if "value" in lo or "€" in label or "divergence" in lo or "gap" in lo
           else "share" if "%" in label or "share" in lo or "percent" in lo or "severity" in lo
           else "issue" if "issue" in lo or "pain" in lo
           else "opportunity" if "opportun" in lo
           else "source" if "source" in lo
           else "value")
    return (f"<span class='stat-ico'><svg viewBox='0 0 16 16' fill='none' "
            f"stroke-linecap='round' stroke-linejoin='round'>{_STAT_GLYPHS[key]}</svg></span>")


# ---------------------------------------------------------------------------
# text + post-processing helpers
# ---------------------------------------------------------------------------
def _clip(t: str, n: int) -> str:
    t = str(t)
    return t if len(t) <= n else t[: n - 1] + "…"


def _clipw(t: str, n: int) -> str:
    """Word-boundary clip for diagram labels: trims to the last whole word that fits within n chars
    (rather than cutting mid-word), then appends an ellipsis. Falls back to a hard clip if even the
    first word overflows."""
    t = str(t)
    if len(t) <= n:
        return t
    cut = t[: n - 1]
    sp = cut.rfind(" ")
    return (cut[:sp] if sp > n // 2 else cut) + "…"


def _to_number_safe(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def _nice_label(s: str) -> str:
    s = str(s).strip()
    return "EDI" if s.lower() == "edi" else s


def _fmt_compact(v: float) -> str:
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


def _fmt_money(v: float) -> str:
    """A monetary figure with a currency mark at any magnitude: 600000 → '€600K', 30675000 →
    '€30.7M', 950 → '€950'."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    a = abs(f)
    if a >= 1_000_000:
        return f"€{f/1_000_000:.1f}M".replace(".0M", "M")
    if a >= 1_000:
        return f"€{int(f/1_000)}K" if f % 1_000 == 0 else f"€{f/1_000:.1f}K"
    return f"€{f:g}"


def _steps(steps) -> str:
    out = []
    for st in steps:
        who = " · ".join(x for x in [st.actor, st.system] if x)
        fp = "".join(f"<span class='failpoint'>{esc(p)}</span>" for p in st.failure_points)
        out.append(f"<div class='step'><strong>{st.seq}. {esc(st.name)}</strong>"
                   f"<div class='who'>{esc(who)}</div><div>{esc(st.description)}</div>{fp}</div>")
    return "\n".join(out)


def _metric(n) -> str:
    text = (n.text or n.label or "").strip()
    if not re.search(r"\d", text):
        figure = _fmt_money(n.value) if n.unit == "eur" else (
            f"{n.value:g}%" if n.unit == "percent" else
            (f"{int(n.value):,}" if float(n.value) == int(n.value) else f"{n.value:g}"))
        text = f"{figure} — {text}" if text else figure
    return f"<span class='metric'>{esc(text)}</span>"


def _rating_cell(raw: str) -> str:
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


def _secnum_chips(body: str) -> str:
    """Wrap the leading section number in a numbered heading with a designed chip. Section headings
    are <h2>'N. Title'</h2> (from _Doc.h1) and subsection headings are <h3>'N.M Title'</h3> (from
    _Doc.h2). Headings without a leading number (the report <h1>, opportunity/system card <h4>) are
    untouched."""
    def repl(m):
        tag, num, rest = m.group(1), m.group(2), m.group(3)
        return f"<{tag}><span class='secnum'>{num}</span>{rest}</{tag}>"
    return re.sub(r"<(h2|h3)>(\d+(?:\.\d+)?)\.?\s*(?:&nbsp;)?\s*(.*?)</\1>", repl, body)


def _scrub_names(body: str, suppress_names) -> str:
    for name in (suppress_names or []):
        if not name:
            continue
        body = re.sub(rf"\b{re.escape(name)}\b", "the organisation", body, flags=re.I)
    return body


def _cite(refs) -> str:
    return docnames.business_phrase_list([r.doc_id for r in refs]) or "—"


def _src_href(doc_id: str) -> str:
    from .. import docnames as dn
    return f"sources/{dn.stem(doc_id)}.html"


def _cite_links(refs) -> str:
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
    from .. import docnames as dn, tools
    sdir = outdir / "sources"
    sdir.mkdir(exist_ok=True)
    for d in s.source_index:
        sid = dn.stem(d.doc_id)
        disp = _scrub_names(dn.friendly(sid), suppress_names)
        body = [f"<h1>{esc(disp)}</h1>",
                f"<p class='lede'>{esc(d.doc_type)} — referenced by findings: "
                f"{esc(', '.join(d.supported_findings) or '—')}</p>",
                "<p><a href='../06-supporting-artefacts.html'>&larr; back to the source index</a></p>"]
        text = tools.DOC_TEXT.get(sid)
        if text is None:
            path = tools.FILE_REGISTRY.get(sid)
            if path:
                import csv as _csv
                with path.open(encoding="utf-8-sig", newline="") as fh:
                    rows = list(_csv.reader(fh))
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
    return re.sub(r"<[^>]+>", " ", htmlfrag)


# The AuroPro brand mark — inline SVG (offline-safe), navy/blue twin-triangle device.
_LOGO = ("<svg viewBox='0 0 32 32' xmlns='http://www.w3.org/2000/svg' aria-hidden='true'>"
         "<path d='M16 3 L27 26 H19 L16 18 L13 26 H5 Z' fill='#1a2f50'/>"
         "<path d='M16 3 L21 13 L16 13 Z' fill='#2563eb'/></svg>")


# ---------------------------------------------------------------------------
# per-report cover + standalone page assembly
# ---------------------------------------------------------------------------
def _cover(slug: str, title: str, meta: dict) -> str:
    """A branded per-report cover (print-only). Report tag, title, domain/client subtitle, and a
    meta grid. The report number is the slug's own prefix (00 = Executive Summary, 01–06 = the
    content reports), so it never drifts. Names route through scrub via meta (client blanked when
    suppressed)."""
    client = (meta.get("client") or "").strip()
    domain = esc(meta.get("domain_label", "Discovery"))
    num = slug.split("-")[0]
    is_exec = num == "00"
    tag = "Executive Summary" if is_exec else f"Report {num} of 06"
    sub = esc(client) if client else "Autonomous Discovery Assessment"
    meta_rows = [("Report reference", "Executive Summary" if is_exec else f"Report {num} of 06"),
                 ("Domain", meta.get("domain_label", "Discovery")),
                 ("Prepared by", "AuroPro · Autonomous Discovery Platform"),
                 ("Classification", "Confidential")]
    if client:
        meta_rows.insert(1, ("Client", client))
    grid = "".join(f"<div class='cml'>{esc(k)}</div><div class='cmv'>{esc(v)}</div>"
                   for k, v in meta_rows)
    return (f"<section class='cover'>"
            f"<div class='cv-top'></div>"
            f"<div class='cv-brand'><span class='brandmark'>{_LOGO}AuroPro</span>"
            f"<span class='cv-sub'>Autonomous Discovery Platform</span></div>"
            f"<div class='cv-accent'></div>"
            f"<div class='cv-body'>"
            f"<span class='cv-tag'>{esc(tag)}</span>"
            f"<div class='cv-title'>{esc(title)}</div>"
            f"<div class='cv-domain'>{domain} · {sub}</div>"
            f"<div class='cv-meta'>{grid}</div>"
            f"</div>"
            f"<div class='cv-bottom'><span class='cv-bot-txt'>{domain} Discovery</span>"
            f"<span class='cv-bot-badge'>Confidential</span></div>"
            f"</section>")


def _page(slug: str, title: str, body: str, meta: dict) -> str:
    """A standalone report document — like the reference: a slim top nav-bar to move between the
    seven reports (screen only), then the report's OWN cover, its OWN table of contents, and its
    numbered sections, as one centred scrolling document. Cover/TOC are visible on screen AND in
    print (where each report paginates from its own cover)."""
    nav = []
    for s_slug, label in REPORTS:
        num = s_slug.split("-")[0]
        cls = " active" if s_slug == slug else ""
        nav.append(f"<a class='{cls.strip()}' href='{s_slug}.html'>"
                   f"<span class='num'>{num}</span>{esc(label)}</a>")
    client = (meta.get("client") or "").strip()
    domain = esc(meta.get("domain_label", "Discovery"))
    page_title = f"{esc(title)} — {esc(client)}" if client else esc(title)
    cover = _cover(slug, title, meta)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<link rel="stylesheet" href="assets/report.css"></head><body>
<nav class="topnav">
  <span class="brandmark">{_LOGO}AuroPro</span>
  <span class="tn-links">{''.join(nav)}</span>
</nav>
{cover}
<main class="content">
{body}
</main></body></html>"""
