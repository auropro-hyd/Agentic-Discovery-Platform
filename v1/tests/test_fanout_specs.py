"""Phase 2 — per-report fan-out specs + assembly (discovery/fanout_specs.py) + planning render.

Drives the full per-report / per-opportunity fan-out with a fake LLM through the real ToolTurn
contract, asserts the merged payload reconstructs a reference-depth SynthesisContent, the strategy
brief reaches the strategic reports, planning content lands in the labelled channel and renders as a
marked panel, and replay is byte-stable.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import fanout_specs as fspec  # noqa: E402
from discovery import models as m  # noqa: E402
from discovery.llm import ToolTurn  # noqa: E402
from discovery.reportsuite.build import _from_payload  # noqa: E402
from discovery.reportsuite.render import _planning_panel, render_suite  # noqa: E402

# a grounded minimal emit per report tool (every number below is in the fact-store allow-list)
_EMITS = {
    "emit_exec": {"executive_summary": {"headline": "h", "situation": "s", "opportunity": "o"},
                  "planning_assumptions": [{"statement": "Pilot kicks off in week 1", "kind": "date",
                                            "basis": "roadmap H1"}]},
    "emit_current_state": {"current_state": {
        "domain_overview": "o", "process_summary": "s",
        "process_flow": [{"seq": 1, "name": "Receipt", "description": "d"},
                         {"seq": 2, "name": "Check", "description": "d"},
                         {"seq": 3, "name": "Ship", "description": "d"}],
        "baseline_stats": [{"value": "1,196", "label": "unfulfilled"}],
        "data_tables": [{"title": "Channel mix", "columns": ["Ch", "N"], "rows": [["EDI", "1196"]],
                         "sources": [{"doc_key": "flow"}]}],
        "process_detail": [{"title": "Receipt", "body": "orders arrive", "actor": "CS"}]}},
    "emit_pain_points": {
        "pain_points": [{"id": "PP1", "title": "EDI fails", "impact_rank": 1, "description": "d",
                         "root_cause": "rc", "severity": "high",
                         "quantified": [{"value": 1196, "unit": "orders", "text": "1,196 orders"}],
                         "detail_table": {"title": "By channel", "columns": ["Ch"],
                                          "rows": [["EDI"]]}}],
        "evidence_register": [{"finding": "PP1", "source": "flow", "confidence": "Verified"}]},
    "emit_recommendation": {
        "transformation": {"sequencing_rationale": "seq", "strategic_readiness": "sr"},
        "metrics_framework": [{"name": "m1", "definition": "d", "target": "t"},
                              {"name": "m2", "definition": "d", "target": "t"},
                              {"name": "m3", "definition": "d", "target": "t"}],
        "risk_register": [{"risk": "r", "likelihood": "High", "impact": "High", "owner": "CC"}],
        "target_state": "ts",
        "planning_assumptions": [{"statement": "Owner: Credit Controller", "kind": "owner"}]},
    "emit_roadmap": {"roadmap": [
        {"horizon": "H1", "window": "0-6 months", "theme": "t",
         "items": [{"title": "i", "rationale": "r", "opportunity_id": "OPP1"}]},
        {"horizon": "H2", "window": "6-18 months", "theme": "t", "items": [{"title": "i",
                                                                            "rationale": "r"}]},
        {"horizon": "H3", "window": "18+ months", "theme": "t", "items": [{"title": "i",
                                                                           "rationale": "r"}]}],
        "strategy_profile": {"posture": "consolidate"},
        "planning_assumptions": [{"statement": "Migrate first connection by Q4", "kind": "date",
                                  "basis": "register targets"}]},
    "emit_opportunity": {
        "id": "OPP1", "title": "Fix EDI", "pattern": "automation", "overview": "o",
        "before_process": [{"seq": 1, "name": "b", "description": "d"},
                           {"seq": 2, "name": "b2", "description": "d"}],
        "after_process": [{"seq": 1, "name": "a", "description": "d"},
                          {"seq": 2, "name": "a2", "description": "d"}],
        "business_impact": {"narrative": "n", "quantified": [{"value": 1196, "unit": "orders",
                                                              "text": "1,196 orders"}]}},
}


class Fake:
    def __init__(self):
        self.seen_strategy = []

    def messages_with_tools(self, *, system, messages, tools, model=None, max_tokens=4096):
        name = tools[0]["name"]
        if "STRATEGY" in messages[0]["content"]:
            self.seen_strategy.append(name)
        return ToolTurn(content=[{"type": "tool_use", "id": "e", "name": name,
                                  "input": _EMITS.get(name, {})}], stop_reason="tool_use")


def _fs():
    return m.FactStore(quant=[m.QuantFact("Unfulfilled EDI orders", 1196, "orders", ["flow"])],
                       entities=[m.EntityFact("account", "Carrefour", {"erp_limit": "1800000"},
                                              ["flow"])])


def test_report_specs_cover_all_reports():
    specs = fspec.report_specs(["flow"])
    assert set(specs) >= {"00-executive-summary", "01-current-state", "02-pain-points",
                          "03-recommendation", "04-opportunity-portfolio", "05-roadmap"}
    # each spec carries a tool + schema + instruction (04 carries an opp schema)
    assert "opp_schema" in specs["04-opportunity-portfolio"]


def test_fanout_assembles_reference_depth_synthesis_content(monkeypatch):
    # build a fact-store directly (no live discovery); run the report fan-out with the fake LLM
    monkeypatch.setattr(fspec.factstore, "build_fact_store", lambda raw, reg: _fs())
    llm = Fake()
    reg = {"csv_ids": ["flow"], "doc_ids": [], "manifest": {}}
    merged, planning, fs, strat = fspec.run_report_fanout(
        llm, {"findings": []}, reg, strategy=m.StrategyProfile(direction_type="consolidate"),
        doc_keys={"flow"})
    c = _from_payload(merged)
    assert len(c.pain_points) == 1 and c.pain_points[0].severity == "high"
    assert len(c.opportunities) == 1 and c.opportunities[0].id == "OPP1"
    assert len(c.roadmap) == 3
    assert c.current_state.data_tables and c.current_state.baseline_stats
    assert len(c.metrics_framework) == 3 and c.risk_register and c.evidence_register
    assert c.executive_summary.headline == "h"
    assert c.strategy_profile.get("posture") == "consolidate"
    # planning content collected across reports (exec date, rec owner, roadmap date)
    kinds = {p.kind for p in planning}
    assert "date" in kinds and "owner" in kinds
    # the strategy brief reached the STRATEGIC reports (03 recommendation, 05 roadmap), not r01/r02
    assert "emit_recommendation" in llm.seen_strategy and "emit_roadmap" in llm.seen_strategy
    assert "emit_current_state" not in llm.seen_strategy


def test_opp_seeds_one_per_pain_point():
    seeds = fspec.opp_seeds_from_pain_points({"pain_points": [
        {"title": "Two systems disagree on credit limits"}, {"title": "EDI undocumented"}]})
    assert [s["id"] for s in seeds] == ["OPP1", "OPP2"]
    assert seeds[0]["topic"]                         # a non-empty topic derived from the title


def test_planning_panel_renders_and_empty():
    assert _planning_panel([]) == ""
    panel = _planning_panel([
        m.PlanningAssumption("Migrate Carrefour by Q4", "date", "register targets"),
        m.PlanningAssumption("Owner: Credit Controller", "owner", "")])
    assert "Planning assumption" in panel and "b-plan" in panel
    assert "Migrate Carrefour by Q4" in panel and "Timing" in panel and "Ownership" in panel
    # an unknown kind falls back to the generic "Planning" label
    p2 = _planning_panel([m.PlanningAssumption("x", "weirdkind", "")])
    assert "Planning</span>" in p2


def test_planning_panel_renders_in_suite(tmp_path):
    from discovery import registry
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    cs = m.CurrentState(domain_overview="o", process_summary="s",
                        process_flow=[m.ProcessStep(seq=1, name="S", actor="A", system="X",
                                                    description="d")])
    s = m.SynthesisContent(current_state=cs,
                           roadmap=[m.RoadmapHorizon(horizon="H1", window="0-6 months", theme="t",
                                                     items=[m.RoadmapItem(title="i",
                                                                          rationale="r")])],
                           planning_assumptions=[m.PlanningAssumption("Go live week 6", "date",
                                                                      "H1")])
    out = tmp_path / "o2c"
    render_suite(s, {"client": "", "domain_label": "Order-to-Cash"}, out)
    r05 = (out / "05-roadmap.html").read_text()
    assert "Planning assumptions" in r05 and "Go live week 6" in r05 and "b-plan" in r05


def test_fanout_determinism(monkeypatch):
    monkeypatch.setattr(fspec.factstore, "build_fact_store", lambda raw, reg: _fs())
    reg = {"csv_ids": ["flow"], "doc_ids": [], "manifest": {}}
    a, _, _, _ = fspec.run_report_fanout(Fake(), {"findings": []}, reg, doc_keys={"flow"})
    b, _, _, _ = fspec.run_report_fanout(Fake(), {"findings": []}, reg, doc_keys={"flow"})
    assert a == b
