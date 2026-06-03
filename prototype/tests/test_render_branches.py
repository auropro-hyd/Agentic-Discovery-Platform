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
    REPORTS, _cite_links, _rating_cell, data_flow_svg, process_flow_svg, render_suite,
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
