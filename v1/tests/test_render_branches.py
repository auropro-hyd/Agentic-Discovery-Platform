"""Branch coverage for render.py: the 'optional field absent' paths, the empty/edge SVG helpers,
the grounded component renderers (pain-point card, rec card, principle cards, mini-stats, evidence
quote), and the pure-function edge cases. Complements test_suite.py, which renders the full fixture
(all fields present) across both code paths.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import models as m  # noqa: E402
from discovery import registry  # noqa: E402
from discovery.reportsuite.render import (  # noqa: E402
    REPORTS, _Doc, _cite, _cite_links, _clipw, _data_table, _ev_quote, _first_sentence,
    _fmt_compact, _fmt_money, _level_badge, _mini_stats, _metric, _opp_horizon, _pain_point_card,
    _principles, _rating_cell, _rec_actions, _rec_card, _scrub_names, _secnum_chips, _seq_order,
    _severity, _stat_icon, _tables_titled, context_map_svg, data_flow_svg, dependency_map_svg,
    donut_svg, impact_bars_svg, process_flow_svg, render_charts, render_suite, roadmap_timeline_svg,
    root_cause_svg, stat_tiles, value_bar_svg, value_matrix_svg,
)


def _minimal_content() -> m.SynthesisContent:
    cs = m.CurrentState(
        domain_overview="overview", process_summary="summary",
        process_flow=[m.ProcessStep(seq=1, name="Step", actor="A", system="OneSystem",
                                    description="d")],
        process_inventory=[], ownership_map=[], system_inventory=[], handoff_catalogue=[],
        system_profiles=[], format_taxonomy=[])
    opp = m.Opportunity(
        id="OPP1", title="Opp", pattern=m.OppPattern.HITL, overview="o",
        before_process=[m.ProcessStep(seq=1, name="b", actor="A", description="d")],
        after_process=[m.ProcessStep(seq=1, name="a", actor="A", description="d")],
        business_impact=m.BusinessImpact(narrative="n", quantified=[]),
        matrix_quadrant=m.MatrixQuadrant.DO_FIRST)
    pp = m.PainPoint(id="PP1", title="Pain", impact_rank=1, from_finding="F1",
                     description="d", root_cause="rc", failure_pattern="fp",
                     quantified=[], sources=[])
    return m.SynthesisContent(
        current_state=cs, pain_points=[pp], opportunities=[opp],
        sequencing_rationale="seq", strategic_readiness="sr", roadmap=[],
        metrics_framework=[])


# ---- per-report structure: cover + own TOC + numbered sections, no doc-control ----
def test_render_suite_with_minimal_content(tmp_path):
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    out = tmp_path / "min"
    render_suite(_minimal_content(), {"client": "", "domain_label": "Process"}, out)
    for slug, _ in REPORTS:
        assert (out / f"{slug}.html").exists()
    r01 = (out / "01-current-state.html").read_text()
    # every report has its own cover + its own TOC
    assert "class='cover'" in r01 and "report-toc" in r01
    # numbered sections present (secnum chip applied to the section heading)
    assert "<span class='secnum'>1</span>Domain overview" in r01
    # no document-control / input-documents anywhere in the suite
    blob = "\n".join((out / f"{slug}.html").read_text() for slug, _ in REPORTS)
    low = blob.lower()
    assert "document control" not in low and "input document" not in low
    # depth sections ABSENT when their collections are empty
    assert "Systems and sources" not in r01 and "Information format" not in r01
    r06 = (out / "06-supporting-artefacts.html").read_text()
    assert "Success metrics framework" not in r06


def test_partial_profile_and_opmodel_fields(tmp_path):
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    cs = m.CurrentState(
        domain_overview="o", process_summary="s",
        process_flow=[m.ProcessStep(seq=1, name="S", actor="", system="", description="d")],
        system_profiles=[m.SystemProfile(name="BareSystem")],
        format_taxonomy=[m.FormatPattern(label="Type 1")])
    opp = m.Opportunity(
        id="OPP1", title="Opp", pattern=m.OppPattern.AUTOMATION, overview="o",
        before_process=[m.ProcessStep(seq=1, name="b", actor="A", description="d")],
        after_process=[m.ProcessStep(seq=1, name="a", actor="A", description="d")],
        business_impact=m.BusinessImpact(narrative="n", quantified=[]),
        escalation="hands to a human", matrix_quadrant=m.MatrixQuadrant.DO_FIRST)
    content = m.SynthesisContent(
        current_state=cs, pain_points=[], opportunities=[opp],
        sequencing_rationale="x", strategic_readiness="y", roadmap=[],
        metrics_framework=[m.MetricItem(name="M", definition="d", target="t")])
    out = tmp_path / "partial"
    render_suite(content, {"client": "", "domain_label": "Process"}, out)
    r01 = (out / "01-current-state.html").read_text()
    assert "BareSystem" in r01 and "How it's used" not in r01
    r04 = (out / "04-opportunity-portfolio.html").read_text()
    assert "Escalation" in r04 and "Who uses it" not in r04


def test_render_opmodel_without_escalation(tmp_path):
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    cs = m.CurrentState(domain_overview="o", process_summary="s",
                        process_flow=[m.ProcessStep(seq=1, name="S", actor="A", system="X",
                                                    description="d")])
    opp = m.Opportunity(
        id="OPP1", title="Opp", pattern=m.OppPattern.AI_AGENT, overview="o",
        before_process=[m.ProcessStep(seq=1, name="b", actor="A", description="d")],
        after_process=[m.ProcessStep(seq=1, name="a", actor="A", description="d")],
        business_impact=m.BusinessImpact(narrative="n", quantified=[]),
        personas=["Analyst"], expected_behaviour="does things",
        matrix_quadrant=m.MatrixQuadrant.DO_FIRST)
    content = m.SynthesisContent(current_state=cs, pain_points=[], opportunities=[opp],
                                 sequencing_rationale="x", strategic_readiness="y", roadmap=[])
    out = tmp_path / "noesc"
    render_suite(content, {"client": "", "domain_label": "Process"}, out)
    r04 = (out / "04-opportunity-portfolio.html").read_text()
    assert "Who uses it" in r04 and "Escalation" not in r04


# ---- _Doc section builder ----
def test_doc_toc_matches_sections_and_empty_toc():
    d = _Doc("Title", "lede")
    d.h1("One").p("para").h2("One-A").raw("<div>x</div>").p("")
    body = d.body()
    assert "<h1>Title</h1>" in body and "<p class='lede'>lede</p>" in body
    assert "<h2>1. One</h2>" in body and "<h3>1.1 &nbsp;One-A</h3>" in body
    toc = d.toc_html()
    assert "Contents" in toc and "One" in toc and "One-A" in toc
    # a doc with no sections produces no TOC; a doc with no lede omits the lede line
    empty = _Doc("Empty")
    assert empty.toc_html() == ""
    assert "lede" not in empty.body() and "<h1>Empty</h1>" in empty.body()


# ---- grounded component renderers ----
def test_severity_thresholds():
    # falls back to impact rank when no explicit severity
    assert _severity(1)[0] == "b-high"
    assert _severity(2)[0] == "b-med"
    assert _severity(3)[0] == "b-pat"        # neutral, not green (would clash in a pain context)
    # an explicit grounded severity overrides the rank
    assert _severity(3, "high")[0] == "b-high"
    assert _severity(1, "medium")[0] == "b-med"
    assert _severity(1, "lower")[0] == "b-pat"


def test_is_high():
    from discovery.reportsuite.render import _is_high
    assert _is_high(m.PainPoint(id="P", title="t", impact_rank=2, severity="high")) is True
    assert _is_high(m.PainPoint(id="P", title="t", impact_rank=2, severity="medium")) is False
    assert _is_high(m.PainPoint(id="P", title="t", impact_rank=1)) is True   # rank fallback
    assert _is_high(m.PainPoint(id="P", title="t", impact_rank=3)) is False


def test_mini_stats_units_and_empty():
    assert _mini_stats([]) == ""
    cells = _mini_stats([m.NumberRef(value=600000, unit="eur", label="gap"),
                         m.NumberRef(value=67.3, unit="percent", label="share"),
                         m.NumberRef(value=267, unit="accounts", label="accts"),
                         m.NumberRef(value=4.5, unit="count", text="avg")])
    assert "€600K" in cells and "67.3%" in cells and "267" in cells and "4.5" in cells
    # label falls back to 'figure' when both label and text are empty
    assert "figure" in _mini_stats([m.NumberRef(value=5, unit="count")])


def test_ev_quote_present_and_absent():
    assert _ev_quote([]) == ""
    assert _ev_quote([m.SourceRef(doc_id="order-management-sop")]) == ""   # no quote -> nothing
    q = _ev_quote([m.SourceRef(doc_id="order-management-sop", quote="a verbatim line")])
    assert "ev-quote" in q and "a verbatim line" in q and "Order Management SOP" in q


def test_data_table_empty_and_populated():
    assert _data_table(None) == ""
    assert _data_table(m.DataTable(title="T", rows=[])) == ""        # no rows -> ''
    t = m.DataTable(title="Channel mix", columns=["Channel", "Orders"],
                    rows=[["EDI", "5,667"], ["Email", "767"]],
                    caption="Counted from the order export.", note="A footnote.",
                    sources=[m.SourceRef(doc_id="order-flow-analysis-export-2025")])
    html = _data_table(t)
    assert "Channel mix" in html and "5,667" in html and "<th>Channel</th>" in html
    assert "Counted from the order export." in html and "A footnote." in html and "Source:" in html
    # a table with no caption/note/sources still renders the grid
    bare = _data_table(m.DataTable(title="Bare", columns=["A"], rows=[["1"]]))
    assert "<table>" in bare and "Source:" not in bare
    # show_title=False omits the table's own heading (a section heading already names it)
    no_title = _data_table(m.DataTable(title="Systems in scope", columns=["A"], rows=[["1"]]),
                           show_title=False)
    assert "<h4>" not in no_title and "<table>" in no_title


def test_tables_titled_filters():
    tabs = [m.DataTable(title="Order channel mix — 2025"),
            m.DataTable(title="EDI connection inventory"),
            m.DataTable(title="Top trading accounts")]
    assert len(_tables_titled(tabs, "channel mix")) == 1
    assert len(_tables_titled(tabs, "edi connection", "top trading")) == 2
    assert _tables_titled(None, "x") == []


def test_level_badge():
    assert "b-high" in _level_badge("High")
    assert "b-med" in _level_badge("Medium")
    assert "b-low" in _level_badge("Low")
    assert "b-pat" in _level_badge("Unknown")
    assert _level_badge("") == "—"


def test_pain_point_card_business_consequence_and_detail_table():
    # high-rank PP -> high-box business impact + detail table renders
    pp = m.PainPoint(id="PP1", title="t", impact_rank=1, category="Data Governance",
                     description="d", root_cause="rc", business_consequence="material exposure",
                     detail_table=m.DataTable(title="Register", columns=["A"], rows=[["x"]]))
    html = _pain_point_card(pp, 1)
    assert "Data Governance" in html and "high-box" in html and "material exposure" in html
    assert "Register" in html
    # medium-rank PP -> med-box; no detail table -> none rendered
    pp2 = m.PainPoint(id="PP2", title="t", impact_rank=2, description="d",
                      business_consequence="some impact")
    html2 = _pain_point_card(pp2, 2)
    assert "med-box" in html2 and "high-box" not in html2


def test_pain_point_card_with_quote_and_signal():
    pp = m.PainPoint(id="PP1", title="Two systems disagree", impact_rank=1,
                     description="d", root_cause="never reconciled", failure_pattern="data drift",
                     opportunity_signal="OPP1",
                     quantified=[m.NumberRef(value=267, unit="accounts", label="accounts")],
                     sources=[m.SourceRef(doc_id="accounts-receivable-review-notes",
                                          quote="operating against the CRM limit")])
    html = _pain_point_card(pp, 1)
    assert "pp-id" in html and "PP<br>01" in html
    assert "b-high" in html and "data drift" in html      # severity + category badges
    assert "267" in html                                  # grounded mini-stat
    assert "ev-quote" in html and "operating against the CRM limit" in html
    assert "Addressed by" in html and "OPP1" in html


def test_rec_card_full_and_bare_branches():
    s = m.SynthesisContent(
        current_state=m.CurrentState(domain_overview="o", process_summary="s"),
        opportunities=[], roadmap=[m.RoadmapHorizon(horizon="H2",
                                   items=[m.RoadmapItem(title="t", opportunity_id="OPP1")])])
    # full: high value, AI agent, on a horizon, addresses a PP, depends on / prerequisite-for
    o = m.Opportunity(id="OPP1", title="Credit reconciliation", pattern=m.OppPattern.AI_AGENT,
                      overview="ov", value_rating="high", addresses_pain_point="PP1",
                      after_process=[m.ProcessStep(seq=1, name="s", description="auto-resolve")],
                      success_metrics=["a single agreed limit"], prerequisite_for=["OPP3"])
    html = _rec_card(o, 1, s, {"OPP1": "Credit reconciliation", "OPP3": "Decisioning"})
    assert "rec-card" in html and "Critical Priority" in html and "AI Opportunity" in html
    assert "H2" in html and "Addresses PP1" in html and "Delivers OPP1" in html
    assert "Phased actions" in html and "Success criteria" in html and "kpi-pill" in html
    assert "strat-box" in html and "Prerequisite for" in html
    # bare: no value_rating (false arc), no pattern label (false arc), no horizon, no addresses
    import discovery.reportsuite.render as rndr
    o2 = m.Opportunity(id="OPP9", title="Bare", value_rating="", pattern=m.OppPattern.HITL)
    saved = rndr._PATTERN_LABEL.copy()
    rndr._PATTERN_LABEL["hitl_workflow"] = ""        # force the empty-pattern arc
    try:
        html2 = _rec_card(o2, 2, m.SynthesisContent(
            current_state=m.CurrentState(domain_overview="o", process_summary="s"), roadmap=[]),
            {"OPP9": "Bare"})
    finally:
        rndr._PATTERN_LABEL.clear()
        rndr._PATTERN_LABEL.update(saved)
    assert "Critical Priority" not in html2 and "High Priority" not in html2  # no priority badge
    assert "b-pat" not in html2                                              # no pattern badge
    assert "Delivers OPP9" in html2 and "Addresses" not in html2             # delivers only


def test_seq_order_respects_dependencies():
    a = m.Opportunity(id="OPP1", title="a")
    b = m.Opportunity(id="OPP2", title="b", dependencies=["OPP1"])
    order = [o.id for o in _seq_order([b, a])]
    assert order.index("OPP1") < order.index("OPP2")
    # an unknown dependency is ignored (no crash)
    c = m.Opportunity(id="OPP3", title="c", dependencies=["NOPE"])
    assert [o.id for o in _seq_order([c])] == ["OPP3"]


def test_r05_short_vs_long_posture():
    from discovery.reportsuite.render import r05
    cs = m.CurrentState(domain_overview="o", process_summary="s")
    rm = [m.RoadmapHorizon(horizon="H1", window="0-6 months", theme="Stabilise",
                           items=[m.RoadmapItem(title="t", rationale="r")])]
    # short posture -> spliced into the lede, no separate framing line
    short = m.SynthesisContent(current_state=cs, roadmap=rm,
                               strategy_profile={"posture": "consolidate then modernise"})
    h = r05(short, {})
    assert "aimed at a consolidate then modernise direction" in h
    assert "Strategic direction." not in h
    # long posture (a sentence) -> clean lede + a separate framing line (no garbled splice)
    longp = m.SynthesisContent(current_state=cs, roadmap=rm, strategy_profile={
        "posture": "establish a single trusted operating baseline then prevent failures at source"})
    h2 = r05(longp, {})
    assert "The recommended opportunities, sequenced across three horizons." in h2
    assert "Strategic direction." in h2 and "aimed at a establish" not in h2


def test_opp_horizon_lookup():
    rm = [m.RoadmapHorizon(horizon="H1", items=[m.RoadmapItem(title="t", opportunity_id="OPP1")]),
          m.RoadmapHorizon(horizon="H2", items=[m.RoadmapItem(title="u")])]
    assert _opp_horizon("OPP1", rm) == "H1"
    assert _opp_horizon("OPP9", rm) == ""        # unplaced
    assert _opp_horizon("OPP1", []) == ""        # empty roadmap


def test_rec_actions_fallback_to_implementation():
    o = m.Opportunity(id="OPP1", title="t", implementation_approach="do the thing")
    acts = _rec_actions(o, "H2")
    assert acts == [("H2", "do the thing")]
    # after-process present -> derived from steps; horizon defaults to H1 when none given.
    # a step with empty name+description is skipped (the `if text:` false arc).
    o2 = m.Opportunity(id="OPP2", title="t", after_process=[
        m.ProcessStep(seq=1, name="", description=""),
        m.ProcessStep(seq=2, name="s", description="auto-resolve")])
    assert _rec_actions(o2, "") == [("H1", "auto-resolve")]
    # nothing to say -> empty
    assert _rec_actions(m.Opportunity(id="OPP3", title="t"), "H1") == []


def test_principles_derivation_and_empty():
    cs = m.CurrentState(domain_overview="o", process_summary="s")
    s = m.SynthesisContent(current_state=cs, strategy_profile={"posture": "consolidate then modernise"},
                           sequencing_rationale="Do A first. Then B.", strategic_readiness="Ready now.")
    pr = _principles(s)
    titles = [t for t, _ in pr]
    assert "Strategic direction" in titles and "Sequencing" in titles and "Readiness" in titles
    # nothing grounded -> no principles
    s2 = m.SynthesisContent(current_state=cs, strategy_profile={}, sequencing_rationale="",
                            strategic_readiness="")
    assert _principles(s2) == []


def test_first_sentence():
    assert _first_sentence("One. Two.") == "One."
    assert _first_sentence("no terminator here") == "no terminator here"


def test_clipw_word_boundary():
    assert _clipw("short", 20) == "short"                      # fits -> unchanged
    # trims to a whole word, not mid-word
    out = _clipw("Customer account set-up and onboarding", 20)
    assert out.endswith("…") and " " in out and "account" in out and not out.endswith("acc…")
    # a single very long word (no space past the midpoint) falls back to a hard clip
    hard = _clipw("Supercalifragilisticexpialidocious", 10)
    assert hard.endswith("…") and len(hard) == 10


# ---- infographics: empty + populated + edges ----
def test_process_flow_svg_empty_and_populated():
    assert process_flow_svg([]) == ""
    steps = [m.ProcessStep(seq=i, name=f"S{i}", actor="A", system="X", description="d")
             for i in range(1, 6)]      # 5 steps -> wraps to a second row (cross-row connector arc)
    svg = process_flow_svg(steps)
    assert "<svg" in svg and "S1" in svg


def test_context_map_svg_empty_and_populated():
    assert context_map_svg([], []) == ""                       # no steps
    steps = [m.ProcessStep(seq=1, name="Receive", system="EDI", description="d"),
             m.ProcessStep(seq=2, name="Check", system="ERP", description="d")]
    assert context_map_svg(steps, []) == ""                    # no handoffs -> ''
    ho = [m.Handoff(from_step="Receive", to_step="Check", mechanism="auto"),
          m.Handoff(from_step="Nowhere", to_step="Check", mechanism="x"),   # unresolved -> skipped
          m.Handoff(from_step="Check", to_step="Check", mechanism="self")]  # self -> skipped
    svg = context_map_svg(steps, ho)
    assert "<svg" in svg and "Receive" in svg
    # a non-adjacent handoff (curved path arc) across many steps
    many = [m.ProcessStep(seq=i, name=f"N{i}", system="Y", description="d") for i in range(1, 7)]
    ho2 = [m.Handoff(from_step="N1", to_step="N6", mechanism="jump")]
    assert "<path" in context_map_svg(many, ho2)


def test_root_cause_svg_empty_patterns_and_fallback():
    assert root_cause_svg([], []) == ""
    pps = [m.PainPoint(id="PP1", title="A", impact_rank=1, failure_pattern="data drift"),
           m.PainPoint(id="PP2", title="B", impact_rank=2, failure_pattern="no governance"),
           m.PainPoint(id="PP3", title="C", impact_rank=3, failure_pattern="")]
    # explicit patterns supplied
    svg = root_cause_svg(pps, [{"pattern": "Carve-out debt", "description": "x"}])
    assert "<svg" in svg and "Carve-out debt" in svg
    # no patterns -> falls back to distinct failure_patterns as causes
    svg2 = root_cause_svg(pps, [])
    assert "<svg" in svg2 and "data drift" in svg2
    # pain points with no failure patterns at all and no patterns -> ''
    blank = [m.PainPoint(id="PP1", title="A", impact_rank=1, failure_pattern="")]
    assert root_cause_svg(blank, []) == ""


def test_value_matrix_empty_and_collision_spread():
    assert value_matrix_svg([m.Opportunity(id="OPP1", title="x", value_score=0,
                                           feasibility_score=0)]) == ""
    opps = [m.Opportunity(id="OPP1", title="x", value_score=5, feasibility_score=4),
            m.Opportunity(id="OPP2", title="y", value_score=3, feasibility_score=3),
            m.Opportunity(id="OPP3", title="z", value_score=3, feasibility_score=3)]
    svg = value_matrix_svg(opps)
    assert "<svg" in svg and svg.count("<circle") == 3        # collision-spread fires for the pair


def test_impact_bars_empty_and_populated():
    assert impact_bars_svg([]) == ""
    pts = [m.PainPoint(id="PP1", title="A", impact_rank=1),
           m.PainPoint(id="PP2", title="B", impact_rank=2)]
    svg = impact_bars_svg(pts)
    assert "<svg" in svg and "PP1" in svg and "PP2" in svg


def test_roadmap_timeline_empty_and_populated():
    assert roadmap_timeline_svg([]) == ""
    rm = [m.RoadmapHorizon(horizon="H1", window="0-6 months", theme="Stabilise",
                           items=[m.RoadmapItem(title="Reconcile", rationale="foundation",
                                                opportunity_id="OPP1"),
                                  m.RoadmapItem(title="Govern", rationale="no prereq")]),
          m.RoadmapHorizon(horizon="H2", window="6-18 months", theme="Prevent",
                           items=[m.RoadmapItem(title="Gate", rationale="needs OPP1",
                                                opportunity_id="OPP3")]),
          m.RoadmapHorizon(horizon="H3", window="18+ months", theme="Sustain", items=[])]
    svg = roadmap_timeline_svg(rm)
    assert "<svg" in svg and "H1" in svg and "H3" in svg and "NOW" in svg and "LATER" in svg
    assert "Reconcile" in svg and svg.count("<circle") >= 2


def test_dependency_map_empty_and_populated():
    # no edges -> ''
    assert dependency_map_svg([m.Opportunity(id="OPP1", title="a")]) == ""
    opps = [m.Opportunity(id="OPP1", title="Reconcile"),
            m.Opportunity(id="OPP2", title="Exceptions"),
            m.Opportunity(id="OPP3", title="Decisioning", dependencies=["OPP1"])]
    svg = dependency_map_svg(opps)
    assert "<svg" in svg and "OPP1" in svg and "Target state" in svg
    # a dependency on an opportunity not in the set is filtered (no edge -> '')
    assert dependency_map_svg([m.Opportunity(id="OPP1", title="x", dependencies=["GONE"])]) == ""
    # a dependency cycle (OPP1<->OPP2) exercises the depth-guard return arc without infinite loop
    cyc = [m.Opportunity(id="OPP1", title="a", dependencies=["OPP2"]),
           m.Opportunity(id="OPP2", title="b", dependencies=["OPP1"])]
    assert "<svg" in dependency_map_svg(cyc)


def test_data_flow_svg_too_few_and_wrap():
    one = [m.ProcessStep(seq=1, name="s", actor="a", system="OnlyOne", description="d")]
    assert data_flow_svg(one) == ""                            # <2 systems -> ''
    six = [m.ProcessStep(seq=i, name=f"S{i}", actor="A", system=f"Sys{i}", description="d")
           for i in range(1, 7)]
    assert "<svg" in data_flow_svg(six)                        # wraps rows; cross-row skip arc
    # a step with empty system still parses
    mixed = [m.ProcessStep(seq=1, name="A", actor="", system="Sys1", description="d"),
             m.ProcessStep(seq=2, name="B", actor="Owner", system="Sys2", description="d")]
    assert "<svg" in data_flow_svg(mixed)


def test_donut_svg_empty_and_populated():
    assert donut_svg([], "cap") == ""
    assert donut_svg([("X", 0), ("Y", "bad")], "cap") == ""
    svg = donut_svg([("EDI", 6_000_000), ("Manual", 2_000_000)], "Value by channel")
    assert "<svg" in svg and "EDI" in svg and "%" in svg


def test_value_bar_svg_empty_and_populated():
    assert value_bar_svg([], "cap") == ""
    svg = value_bar_svg([("EDI", 1196), ("Manual", 320)], "By channel", unit="orders")
    assert "<svg" in svg and "EDI" in svg and "1,196" in svg
    assert "€12.4M" in value_bar_svg([("A", 12362493.74)], "Value", unit="eur")


def test_render_charts_bar_and_donut_and_kinds():
    bar = render_charts([{"kind": "bar", "unit": "orders", "title": "By channel",
                          "segments": [{"label": "EDI", "value": 1196},
                                       {"label": "Manual", "value": 320}]}])
    assert "<svg" in bar and "EDI" in bar
    donut = render_charts([{"kind": "donut", "unit": "eur", "title": "Value share",
                            "segments": [{"label": "EDI", "value": 6_000_000},
                                         {"label": "Other", "value": 2_000_000}]}])
    assert "<svg" in donut and "%" in donut
    assert render_charts([]) == ""
    both = [{"kind": "bar", "unit": "orders", "title": "B",
             "segments": [{"label": "A", "value": 5}, {"label": "C", "value": 2}]},
            {"kind": "donut", "unit": "orders", "title": "D",
             "segments": [{"label": "A", "value": 5}, {"label": "C", "value": 2}]}]
    assert "donut" not in render_charts(both, kinds={"bar"})
    assert render_charts(both, kinds={"donut"}).count("<svg") == 1


# ---- stat tiles + icons ----
def test_stat_tiles_empty_and_icons():
    assert stat_tiles([]) == ""
    html = stat_tiles([("3", "issues identified", "blue")])
    assert "stat-box" in html and "issues identified" in html
    for lbl in ["aggregate divergence", "channel share by count", "high severity",
                "opportunities mapped", "sources analysed", "pain points", "something else"]:
        assert "stat-ico" in _stat_icon(lbl)


def test_exec_and_pp_tiles_via_render(tmp_path):
    """Exercise _exec_tiles (money + percent headline figures) and _pp_tiles (severity counts)."""
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    cs = m.CurrentState(domain_overview="o", process_summary="s",
                        process_flow=[m.ProcessStep(seq=1, name="S", actor="A", system="X",
                                                    description="d")])
    pp = m.PainPoint(id="PP1", title="Money issue", impact_rank=1,
                     quantified=[m.NumberRef(value=600000, unit="eur", label="small gap"),
                                 m.NumberRef(value=30675000, unit="eur", label="big divergence"),
                                 m.NumberRef(value=67, unit="percent", label="EDI share")])
    pp2 = m.PainPoint(id="PP2", title="Other", impact_rank=2)
    s = m.SynthesisContent(current_state=cs, pain_points=[pp, pp2],
                           opportunities=[m.Opportunity(id="OPP1", title="o")],
                           source_index=[m.SourceDoc(doc_id="d", business_name="D", doc_type="x")])
    s.executive_summary = m.ExecutiveSummary(headline="H", situation="sit", opportunity="opp")
    out = tmp_path / "tiles"
    render_suite(s, {"client": "", "domain_label": "Process"}, out)
    exec_pg = (out / "00-executive-summary.html").read_text()
    assert "€30.7M" in exec_pg and "67%" in exec_pg          # largest money + first percent
    r02 = (out / "02-pain-points.html").read_text()
    assert "high severity" in r02 and "medium severity" in r02


def test_exec_tiles_no_money(tmp_path):
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    cs = m.CurrentState(domain_overview="o", process_summary="s",
                        process_flow=[m.ProcessStep(seq=1, name="S", actor="A", system="X",
                                                    description="d")])
    s = m.SynthesisContent(current_state=cs,
                           pain_points=[m.PainPoint(id="PP1", title="t", impact_rank=1)],
                           opportunities=[], source_index=[])
    s.executive_summary = m.ExecutiveSummary(headline="H")
    out = tmp_path / "nomoney"
    render_suite(s, {"client": "", "domain_label": "Process"}, out)
    assert "issues identified" in (out / "00-executive-summary.html").read_text()


# ---- formatting + text helpers ----
def test_fmt_compact():
    assert _fmt_compact(30_675_000) == "€30.7M"
    assert _fmt_compact(2_000_000) == "€2M"
    assert _fmt_compact(1196) == "1,196"
    assert _fmt_compact(5) == "5"
    assert _fmt_compact("not-a-number") == "not-a-number"


def test_fmt_money():
    assert _fmt_money(30_675_000) == "€30.7M"
    assert _fmt_money(600000) == "€600K"
    assert _fmt_money(1500) == "€1.5K"
    assert _fmt_money(950) == "€950"
    assert _fmt_money("x") == "x"


def test_metric_prepends_figure_when_text_has_no_number():
    nr = m.NumberRef(value=30675000, unit="eur", label="x", text="aggregate divergence addressed")
    out = _metric(nr)
    assert "€30.7M" in out and "aggregate divergence addressed" in out
    nr2 = m.NumberRef(value=267, unit="accounts", label="x", text="267 accounts reconciled")
    assert _metric(nr2).count("267") == 1
    assert "67.3%" in _metric(m.NumberRef(value=67.3, unit="percent", text="share"))
    assert "1,196" in _metric(m.NumberRef(value=1196, unit="orders", text="orders affected"))
    # eur with no number in text -> money figure prepended
    assert "€600K" in _metric(m.NumberRef(value=600000, unit="eur", text="single largest gap"))


def test_secnum_chips_wraps_numbered_headings_only():
    out = _secnum_chips("<h2>1. Domain overview</h2><h3>1.1 &nbsp;Context and scope</h3>"
                        "<h2>Where to start</h2><h1>Current State</h1><h4>A card</h4>")
    assert "<h2><span class='secnum'>1</span>Domain overview</h2>" in out
    assert "<h3><span class='secnum'>1.1</span>Context and scope</h3>" in out
    assert "<h2>Where to start</h2>" in out          # no number -> untouched
    assert "<h1>Current State</h1>" in out            # h1 untouched
    assert "<h4>A card</h4>" in out                   # h4 untouched


def test_rating_cell_variants():
    assert _rating_cell("") == "—"
    assert "rate-high" in _rating_cell("high — solid reason")
    assert "rate-medium" in _rating_cell("medium - hyphen sep")
    assert "rate-low" in _rating_cell("low: colon sep")
    assert "rate-na" in _rating_cell("unknown rating phrase")
    assert _rating_cell("high").strip().endswith("</span>")
    # an all-caps (shouting) reason is down-cased for readability, preserving acronyms
    cell = _rating_cell("high — BOTH VALUES EXIST IN THE ERP AND CRM TODAY")
    assert "Both values exist in the ERP and CRM today" in cell


def test_deshout():
    from discovery.reportsuite.render import _deshout
    # shouting → sentence-cased, acronyms preserved
    assert _deshout("BOTH VALUES IN ERP AND SAP S/4HANA") == "Both values in ERP and SAP S/4HANA"
    # normal text is left untouched
    assert _deshout("Both values already exist") == "Both values already exist"
    # no letters → unchanged (no crash)
    assert _deshout("267 / 318") == "267 / 318"
    assert _deshout("") == ""
    # a raw SHOUTY_SNAKE enum embedded in normal prose is humanised
    assert _deshout("1,196 orders in a NOT_FULFILLED state") == "1,196 orders in a not fulfilled state"


def test_humanize_enums_preserves_acronyms():
    from discovery.reportsuite.render import _humanize_enums, esc
    # multi-segment SHOUTY_SNAKE enum → plain words
    assert _humanize_enums("status NOT_FULFILLED today") == "status not fulfilled today"
    assert _humanize_enums("ON_HOLD and PARTIALLY_SHIPPED") == "on hold and partially shipped"
    # single-token acronyms are NOT touched (no underscore → no match)
    assert _humanize_enums("EDI via SAP S/4HANA and CRM") == "EDI via SAP S/4HANA and CRM"
    # esc() humanises before escaping (visible text only)
    assert "not fulfilled" in esc("orders NOT_FULFILLED")
    assert "EDI" in esc("an EDI connection")


def test_cite_and_cite_links():
    assert _cite([]) == "—"

    class R:
        def __init__(self, d):
            self.doc_id = d
    assert _cite_links([]) == "—"
    one = _cite_links([R("order-management-sop")])
    assert one.startswith("<a ") and "Order Management SOP" in one
    dup = _cite_links([R("order-management-sop"), R("order-management-sop")])
    assert dup.count("<a ") == 1
    multi = _cite_links([R("order-management-sop"), R("credit-management-policy")])
    assert " and " in multi


def test_scrub_names_skips_empty_names():
    out = _scrub_names("Acme did things", ["", "Acme"])
    assert "the organisation" in out and "Acme" not in out


# ---- source pages (CSV preview + frozen text + unregistered) ----
def test_source_pages_render_csv_and_narrative(tmp_path):
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    cs = m.CurrentState(domain_overview="o", process_summary="s",
                        process_flow=[m.ProcessStep(seq=1, name="S", actor="A", system="X",
                                                    description="d")])
    content = m.SynthesisContent(current_state=cs, pain_points=[], opportunities=[],
                                 sequencing_rationale="x", strategic_readiness="y", roadmap=[])
    content.source_index = [
        m.SourceDoc(doc_id="order-flow-analysis-export-2025", business_name="Order Flow",
                    doc_type="Data export", what_we_read="orders", supported_findings=["F1"]),
        m.SourceDoc(doc_id="edi-integration-register-opella-europe", business_name="EDI Register",
                    doc_type="Register", what_we_read="edi", supported_findings=[]),
    ]
    out = tmp_path / "srcpages"
    render_suite(content, {"client": "", "domain_label": "Process"}, out)
    csv_page = (out / "sources" / "order-flow-analysis-export-2025.html").read_text()
    assert "rows · columns" in csv_page and "more rows" in csv_page
    doc_page = (out / "sources" / "edi-integration-register-opella-europe.html").read_text()
    assert "srcdoc" in doc_page


def test_source_page_csv_small_and_unregistered(tmp_path):
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    from discovery import tools
    small = tmp_path / "small.csv"
    small.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    tools.FILE_REGISTRY["small-src"] = small
    cs = m.CurrentState(domain_overview="o", process_summary="s",
                        process_flow=[m.ProcessStep(seq=1, name="S", actor="A", system="X",
                                                    description="d")])
    content = m.SynthesisContent(current_state=cs, pain_points=[], opportunities=[],
                                 sequencing_rationale="x", strategic_readiness="y", roadmap=[])
    content.source_index = [
        m.SourceDoc(doc_id="small-src", business_name="Small", doc_type="CSV"),
        m.SourceDoc(doc_id="phantom-src", business_name="Phantom", doc_type="Unknown"),
    ]
    out = tmp_path / "pages"
    try:
        render_suite(content, {"client": "", "domain_label": "Process"}, out)
    finally:
        del tools.FILE_REGISTRY["small-src"]
    small_page = (out / "sources" / "small-src.html").read_text()
    assert "rows · columns" in small_page and "more rows" not in small_page
    assert (out / "sources" / "phantom-src.html").exists()


def test_exec_summary_partial_panels():
    from discovery.reportsuite.render import r00
    cs = m.CurrentState(domain_overview="o", process_summary="s")
    s = m.SynthesisContent(current_state=cs, pain_points=[], opportunities=[], source_index=[])
    s.executive_summary = m.ExecutiveSummary(headline="H", situation="just the situation")
    html = r00(s, {"domain_label": "Process"})
    assert "The situation" in html and "The opportunity" not in html
    s.executive_summary = m.ExecutiveSummary(headline="H", opportunity="just the opportunity")
    html2 = r00(s, {"domain_label": "Process"})
    assert "The opportunity" in html2 and "The situation" not in html2


def test_opp_partial_sources_formats():
    from discovery.reportsuite.render import r04
    cs = m.CurrentState(domain_overview="o", process_summary="s")
    o = m.Opportunity(id="OPP1", title="t", overview="o",
                      before_process=[m.ProcessStep(seq=1, name="b", actor="A", description="d")],
                      after_process=[m.ProcessStep(seq=1, name="a", actor="A", description="d")],
                      business_impact=m.BusinessImpact(narrative="n"),
                      personas=["Analyst"], knowledge_sources=["ERP"],
                      matrix_quadrant=m.MatrixQuadrant.DO_FIRST)
    html = r04(m.SynthesisContent(current_state=cs, opportunities=[o]), {})
    assert "Sources." in html and "Formats." not in html
    o2 = m.Opportunity(id="OPP1", title="t", overview="o",
                       before_process=[m.ProcessStep(seq=1, name="b", actor="A", description="d")],
                       after_process=[m.ProcessStep(seq=1, name="a", actor="A", description="d")],
                       business_impact=m.BusinessImpact(narrative="n"),
                       personas=["Analyst"], document_formats=["CSV export"],
                       matrix_quadrant=m.MatrixQuadrant.DO_FIRST)
    html2 = r04(m.SynthesisContent(current_state=cs, opportunities=[o2]), {})
    assert "Formats." in html2 and "Sources." not in html2
