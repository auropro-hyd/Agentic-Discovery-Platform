"""Branch coverage for render.py: the 'optional field absent' paths (empty system_profiles,
format_taxonomy, metrics_framework, personas, quantified, etc.), the empty/edge SVG helpers,
and the _rating_cell / _cite_links pure-function edge cases. Complements test_suite.py, which
renders the full fixture (all fields present).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import models as m  # noqa: E402
from discovery import registry  # noqa: E402
from discovery.reportsuite import render  # noqa: E402
from discovery.reportsuite.render import (  # noqa: E402
    REPORTS, _cite_links, _fmt_compact, _kpi_icon, _metric, _rating_cell, _secnum_chips,
    data_flow_svg, donut_svg, impact_bars_svg, kpi_tiles, process_flow_svg, render_charts,
    render_suite, roadmap_timeline_svg, value_bar_svg, value_feasibility_svg,
)


def _minimal_content() -> m.SynthesisContent:
    """A valid-but-sparse content: every optional collection empty, one bare opportunity and
    pain point with no quantified numbers, one-system process flow (too few for a data map)."""
    cs = m.CurrentState(
        domain_overview="overview", process_summary="summary",
        process_flow=[m.ProcessStep(seq=1, name="Step", actor="A", system="OneSystem",
                                    description="d")],
        process_inventory=[], ownership_map=[], system_inventory=[], handoff_catalogue=[],
        system_profiles=[], format_taxonomy=[])           # both depth collections empty
    opp = m.Opportunity(
        id="OPP1", title="Opp", pattern=m.OppPattern.HITL, overview="o",
        before_process=[m.ProcessStep(seq=1, name="b", actor="A", description="d")],
        after_process=[m.ProcessStep(seq=1, name="a", actor="A", description="d")],
        business_impact=m.BusinessImpact(narrative="n", quantified=[]),
        matrix_quadrant=m.MatrixQuadrant.DO_FIRST)        # no personas/readiness/quantified
    pp = m.PainPoint(id="PP1", title="Pain", impact_rank=1, from_finding="F1",
                     description="d", root_cause="rc", failure_pattern="fp",
                     quantified=[], sources=[])           # no quantified, no opportunity_signal
    return m.SynthesisContent(
        current_state=cs, pain_points=[pp], opportunities=[opp],
        sequencing_rationale="seq", strategic_readiness="sr", roadmap=[],
        metrics_framework=[])                             # empty framework


def test_render_suite_with_minimal_content(tmp_path):
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    content = _minimal_content()
    out = tmp_path / "min"
    render_suite(content, {"client": "", "domain_label": "Process"}, out)
    for slug, _ in REPORTS:
        assert (out / f"{slug}.html").exists()
    r01 = (out / "01-current-state.html").read_text()
    # depth sections are ABSENT when their collections are empty
    assert "Systems &amp; sources" not in r01
    assert "Information format" not in r01
    r06 = (out / "06-supporting-artefacts.html").read_text()
    assert "Success metrics framework" not in r06


def test_render_partial_profile_and_opmodel_fields(tmp_path):
    """A system profile with only a name, and an opportunity with only escalation set, exercise
    the per-subfield 'present?' conditionals (role/how_used/owners/limitations, personas/behaviour)."""
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    cs = m.CurrentState(
        domain_overview="o", process_summary="s",
        process_flow=[m.ProcessStep(seq=1, name="S", actor="", system="", description="d")],
        system_profiles=[m.SystemProfile(name="BareSystem")],          # all sub-fields empty
        format_taxonomy=[m.FormatPattern(label="Type 1")])
    opp = m.Opportunity(
        id="OPP1", title="Opp", pattern=m.OppPattern.AUTOMATION, overview="o",
        before_process=[m.ProcessStep(seq=1, name="b", actor="A", description="d")],
        after_process=[m.ProcessStep(seq=1, name="a", actor="A", description="d")],
        business_impact=m.BusinessImpact(narrative="n", quantified=[]),
        escalation="hands to a human", matrix_quadrant=m.MatrixQuadrant.DO_FIRST)  # only escalation
    content = m.SynthesisContent(
        current_state=cs, pain_points=[], opportunities=[opp],
        sequencing_rationale="x", strategic_readiness="y", roadmap=[],
        metrics_framework=[m.MetricItem(name="M", definition="d", target="t")])
    out = tmp_path / "partial"
    render_suite(content, {"client": "", "domain_label": "Process"}, out)
    r01 = (out / "01-current-state.html").read_text()
    assert "BareSystem" in r01 and "How it's used" not in r01      # name shown, empty subfields not
    r04 = (out / "04-opportunity-portfolio.html").read_text()
    assert "Escalation" in r04 and "Who uses it" not in r04        # only escalation rendered


def test_cite_empty_returns_dash():
    from discovery.reportsuite.render import _cite
    assert _cite([]) == "—"


def test_source_pages_render_csv_preview_and_narrative(tmp_path):
    """A source index with a large CSV (>20 rows -> truncation note) and a narrative doc exercises
    both arms of _render_source_pages (CSV preview vs frozen-text block)."""
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    cs = m.CurrentState(domain_overview="o", process_summary="s",
                        process_flow=[m.ProcessStep(seq=1, name="S", actor="A", system="X",
                                                    description="d")])
    content = m.SynthesisContent(
        current_state=cs, pain_points=[], opportunities=[],
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
    assert "rows · columns" in csv_page and "more rows" in csv_page   # CSV preview + truncation
    doc_page = (out / "sources" / "edi-integration-register-opella-europe.html").read_text()
    assert "srcdoc" in doc_page                                       # frozen-text block


def test_render_opmodel_without_escalation(tmp_path):
    """An opportunity with personas + behaviour but NO escalation hits the escalation-absent arc."""
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    cs = m.CurrentState(domain_overview="o", process_summary="s",
                        process_flow=[m.ProcessStep(seq=1, name="S", actor="A", system="X",
                                                    description="d")])
    opp = m.Opportunity(
        id="OPP1", title="Opp", pattern=m.OppPattern.AI_AGENT, overview="o",
        before_process=[m.ProcessStep(seq=1, name="b", actor="A", description="d")],
        after_process=[m.ProcessStep(seq=1, name="a", actor="A", description="d")],
        business_impact=m.BusinessImpact(narrative="n", quantified=[]),
        personas=["Analyst"], expected_behaviour="does things",  # no escalation
        matrix_quadrant=m.MatrixQuadrant.DO_FIRST)
    content = m.SynthesisContent(current_state=cs, pain_points=[], opportunities=[opp],
                                 sequencing_rationale="x", strategic_readiness="y", roadmap=[])
    out = tmp_path / "noesc"
    render_suite(content, {"client": "", "domain_label": "Process"}, out)
    r04 = (out / "04-opportunity-portfolio.html").read_text()
    assert "Who uses it" in r04 and "Escalation" not in r04


def test_data_flow_svg_step_missing_actor_or_system():
    steps = [m.ProcessStep(seq=1, name="A", actor="", system="Sys1", description="d"),
             m.ProcessStep(seq=2, name="B", actor="Owner", system="Sys2", description="d")]
    svg = data_flow_svg(steps)
    assert "<svg" in svg                       # renders; the missing-actor arc is exercised


def test_cite_links_dedup_collapses_to_one_link():
    class R:
        def __init__(self, d):
            self.doc_id = d
    out = _cite_links([R("order-management-sop"), R("order-management-sop"),
                       R("order-management-sop")])
    assert out.count("<a ") == 1               # three identical -> one link (continue arc)


def test_data_flow_svg_wraps_rows_with_many_systems():
    # 6 distinct systems force a row wrap; the cross-row connector-skip arc fires
    steps = [m.ProcessStep(seq=i, name=f"S{i}", actor="A", system=f"Sys{i}", description="d")
             for i in range(1, 7)]
    assert "<svg" in data_flow_svg(steps)


def test_scrub_names_skips_empty_names():
    from discovery.reportsuite.render import _scrub_names
    out = _scrub_names("Acme did things", ["", "Acme"])      # empty entry -> continue arc
    assert "the organisation" in out and "Acme" not in out


def test_source_page_csv_small_and_unregistered(tmp_path):
    """A small CSV (<=20 rows, no truncation note) and a source whose id is registered nowhere
    (neither frozen text nor file) exercise the remaining source-page arcs."""
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
        m.SourceDoc(doc_id="phantom-src", business_name="Phantom", doc_type="Unknown"),  # nowhere
    ]
    out = tmp_path / "pages"
    try:
        render_suite(content, {"client": "", "domain_label": "Process"}, out)
    finally:
        del tools.FILE_REGISTRY["small-src"]
    small_page = (out / "sources" / "small-src.html").read_text()
    assert "rows · columns" in small_page and "more rows" not in small_page
    assert (out / "sources" / "phantom-src.html").exists()       # rendered with no body block


def test_process_flow_svg_empty():
    assert "No process flow available" in process_flow_svg([])


# ---- data-viz helpers --------------------------------------------------------
def test_impact_bars_empty_and_populated():
    assert impact_bars_svg([]) == ""
    pts = [m.PainPoint(id="PP1", title="A", impact_rank=1),
           m.PainPoint(id="PP2", title="B", impact_rank=2)]
    svg = impact_bars_svg(pts)
    assert "<svg" in svg and "PP1" in svg and "PP2" in svg


def test_value_feasibility_empty_and_collision_spread():
    assert value_feasibility_svg([]) == ""
    # three opps, two sharing the exact same coordinate -> collision-spread branch fires
    opps = [m.Opportunity(id="OPP1", title="x", value_score=5, feasibility_score=4),
            m.Opportunity(id="OPP2", title="y", value_score=3, feasibility_score=3),
            m.Opportunity(id="OPP3", title="z", value_score=3, feasibility_score=3)]
    svg = value_feasibility_svg(opps)
    assert "<svg" in svg and svg.count("<circle") == 3


def test_donut_svg_empty_and_populated():
    assert donut_svg([], "cap") == ""
    assert donut_svg([("X", 0), ("Y", "bad")], "cap") == ""     # no positive numeric segments
    svg = donut_svg([("EDI", 6_000_000), ("Manual", 2_000_000)], "Value by channel")
    assert "<svg" in svg and "EDI" in svg and "%" in svg


def test_fmt_compact():
    assert _fmt_compact(30_675_000) == "€30.7M"
    assert _fmt_compact(2_000_000) == "€2M"
    assert _fmt_compact(1196) == "1,196"
    assert _fmt_compact(5) == "5"                  # small number -> %g fallback
    assert _fmt_compact("not-a-number") == "not-a-number"


def test_roadmap_timeline_empty_and_populated():
    assert roadmap_timeline_svg([]) == ""
    rm = [m.RoadmapHorizon(horizon="H1", window="0-6 months", theme="Stabilise",
                           items=[m.RoadmapItem(title="Reconcile master", rationale="foundation",
                                                opportunity_id="OPP1"),
                                  m.RoadmapItem(title="Govern channel", rationale="no prereq")]),
          m.RoadmapHorizon(horizon="H2", window="6-18 months", theme="Prevent",
                           items=[m.RoadmapItem(title="Credit gate", rationale="needs OPP1",
                                                opportunity_id="OPP3")]),
          m.RoadmapHorizon(horizon="H3", window="18+ months", theme="Sustain", items=[])]
    svg = roadmap_timeline_svg(rm)
    assert "<svg" in svg and "H1" in svg and "H2" in svg and "H3" in svg
    assert "NOW" in svg and "LATER" in svg
    assert "Reconcile master" in svg                # item title appears
    assert svg.count("<circle") >= 2                # opportunity-backed items get a dot


def test_secnum_chips_wraps_numbered_headings_only():
    # numbered h2 (N.M and N.) get a teal chip; unnumbered h2 untouched; h1 untouched
    out = _secnum_chips("<h2>1.3 Systems &amp; sources</h2><h2>2. Scope</h2>"
                        "<h2>Where to start</h2><h1>1. Current State</h1>")
    assert "<span class='secnum'>1.3</span>Systems &amp; sources" in out
    assert "<span class='secnum'>2</span>Scope" in out
    assert "<h2>Where to start</h2>" in out                 # no leading number -> unchanged
    assert "<h1>1. Current State</h1>" in out                # h1 untouched


def test_kpi_icon_picks_glyph_by_label():
    assert "<svg" in _kpi_icon("issues identified")
    # each category resolves to a glyph without error
    for lbl in ["aggregate divergence", "channel share by count", "opportunities mapped",
                "sources analysed", "something else"]:
        assert "kpi-ico" in _kpi_icon(lbl)


def test_value_bar_svg_empty_and_populated():
    assert value_bar_svg([], "cap") == ""
    svg = value_bar_svg([("EDI", 1196), ("Manual", 320)], "Unfulfilled by channel", unit="orders")
    assert "<svg" in svg and "EDI" in svg and "1,196" in svg
    # eur unit formats compactly
    svg2 = value_bar_svg([("A", 12362493.74)], "Value", unit="eur")
    assert "€12.4M" in svg2


def test_render_charts_bar_and_donut():
    bar = render_charts([{"kind": "bar", "unit": "orders", "title": "By channel",
                          "segments": [{"label": "EDI", "value": 1196},
                                       {"label": "Manual", "value": 320}]}])
    assert "<svg" in bar and "EDI" in bar
    donut = render_charts([{"kind": "donut", "unit": "eur", "title": "Value share",
                            "segments": [{"label": "EDI", "value": 6_000_000},
                                         {"label": "Other", "value": 2_000_000}]}])
    assert "<svg" in donut and "%" in donut
    assert render_charts([]) == ""


def test_metric_prepends_figure_when_text_has_no_number():
    # NumberRef-like with text that lacks a digit -> figure prepended
    nr = m.NumberRef(value=30675000, unit="eur", label="x", text="aggregate divergence addressed")
    out = _metric(nr)
    assert "€30.7M" in out and "aggregate divergence addressed" in out
    # text already carries a number -> shown as-is, no double-prefix
    nr2 = m.NumberRef(value=267, unit="accounts", label="x", text="267 accounts reconciled")
    assert _metric(nr2).count("267") == 1
    # percent + bare-count fallbacks
    assert "67.3%" in _metric(m.NumberRef(value=67.3, unit="percent", text="share"))
    assert "1,196" in _metric(m.NumberRef(value=1196, unit="orders", text="orders affected"))


def test_exec_summary_partial_panels(tmp_path):
    """An executive summary with only 'situation' (no 'opportunity') hits the absent-panel arc."""
    from discovery.reportsuite.render import r00
    cs = m.CurrentState(domain_overview="o", process_summary="s")
    s = m.SynthesisContent(current_state=cs, pain_points=[], opportunities=[], source_index=[])
    s.executive_summary = m.ExecutiveSummary(headline="H", situation="just the situation")
    html = r00(s, {"domain_label": "Process"})
    assert "The situation" in html and "The opportunity" not in html
    # mirror: only 'opportunity' set (covers the situation-absent arc)
    s.executive_summary = m.ExecutiveSummary(headline="H", opportunity="just the opportunity")
    html2 = r00(s, {"domain_label": "Process"})
    assert "The opportunity" in html2 and "The situation" not in html2


def test_opp_partial_sources_formats(tmp_path):
    """An opportunity with knowledge_sources but no document_formats hits that absent arc."""
    from discovery.reportsuite.render import r04
    o = m.Opportunity(id="OPP1", title="t", overview="o",
                      before_process=[m.ProcessStep(seq=1, name="b", actor="A", description="d")],
                      after_process=[m.ProcessStep(seq=1, name="a", actor="A", description="d")],
                      business_impact=m.BusinessImpact(narrative="n"),
                      personas=["Analyst"], knowledge_sources=["ERP"], matrix_quadrant=m.MatrixQuadrant.DO_FIRST)
    cs = m.CurrentState(domain_overview="o", process_summary="s")
    s = m.SynthesisContent(current_state=cs, opportunities=[o])
    html = r04(s, {})
    assert "Sources." in html and "Formats." not in html
    # mirror: only document_formats (covers the knowledge_sources-absent arc)
    o2 = m.Opportunity(id="OPP1", title="t", overview="o",
                       before_process=[m.ProcessStep(seq=1, name="b", actor="A", description="d")],
                       after_process=[m.ProcessStep(seq=1, name="a", actor="A", description="d")],
                       business_impact=m.BusinessImpact(narrative="n"),
                       personas=["Analyst"], document_formats=["CSV export"],
                       matrix_quadrant=m.MatrixQuadrant.DO_FIRST)
    html2 = r04(m.SynthesisContent(current_state=cs, opportunities=[o2]), {})
    assert "Formats." in html2 and "Sources." not in html2


def test_kpi_tiles_derives_from_grounded_content():
    cs = m.CurrentState(domain_overview="o", process_summary="s")
    pp = m.PainPoint(id="PP1", title="Money issue", impact_rank=1,
                     quantified=[m.NumberRef(value=600000, unit="eur", label="small gap"),
                                 m.NumberRef(value=30675000, unit="eur", label="big divergence"),
                                 m.NumberRef(value=67, unit="percent", label="EDI share")])
    s = m.SynthesisContent(current_state=cs, pain_points=[pp],
                           opportunities=[m.Opportunity(id="OPP1", title="o")],
                           source_index=[m.SourceDoc(doc_id="d", business_name="D", doc_type="x")])
    tiles = kpi_tiles(s)
    assert "€30.7M" in tiles and "€600" not in tiles            # leads with the LARGEST money figure
    assert "67%" in tiles                                       # first percentage
    assert "issues identified" in tiles and "opportunities mapped" in tiles


def test_kpi_tiles_no_money_figures():
    cs = m.CurrentState(domain_overview="o", process_summary="s")
    s = m.SynthesisContent(current_state=cs,
                           pain_points=[m.PainPoint(id="PP1", title="t", impact_rank=1)],
                           opportunities=[], source_index=[])
    tiles = kpi_tiles(s)
    assert "issues identified" in tiles                        # counts always present


def test_data_flow_svg_too_few_systems():
    one = [m.ProcessStep(seq=1, name="s", actor="a", system="OnlyOne", description="d")]
    assert "too few named systems" in data_flow_svg(one)


def test_rating_cell_variants():
    assert _rating_cell("") == "—"
    assert "rate-high" in _rating_cell("high — solid reason")
    assert "rate-medium" in _rating_cell("medium - hyphen sep")     # ' - ' separator
    assert "rate-low" in _rating_cell("low: colon sep")             # ':' separator
    assert "rate-na" in _rating_cell("unknown rating phrase")       # unrecognised level
    assert _rating_cell("high").strip().endswith("</span>")         # bare rating, no reason


def test_cite_links_dedup_single_and_empty():
    class R:
        def __init__(self, d):
            self.doc_id = d
    assert _cite_links([]) == "—"
    one = _cite_links([R("order-management-sop")])
    assert one.startswith("<a ") and "Order Management SOP" in one      # friendly display text
    # duplicate doc_id collapses to a single link
    dup = _cite_links([R("order-management-sop"), R("order-management-sop")])
    assert dup.count("<a ") == 1
    multi = _cite_links([R("order-management-sop"), R("credit-management-policy")])
    assert " and " in multi
