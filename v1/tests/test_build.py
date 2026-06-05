"""Coverage for build.py: the live-synthesis branch of build_synthesis, the _from_payload mapper
(incl. all the new depth fields), the NoFixtureForDomain refusal, source-index dedup, and _q.
All offline — the 'live' LLM is a scripted fake returning the depth payload.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery.llm import ToolTurn  # noqa: E402
from discovery.models import (  # noqa: E402
    BoundedContext, ContextRelationship, CurrentState, DataTable, MatrixQuadrant,
)
from discovery.reportsuite import build  # noqa: E402
from _payloads import depth_doc_keys, depth_synthesis_payload  # noqa: E402


class FakeSynthLLM:
    def __init__(self, payload):
        self._payload = payload

    def messages_with_tools(self, *, system, messages, tools, model=None, max_tokens=4096):
        return ToolTurn(content=[{"type": "tool_use", "id": "e1", "name": "emit_synthesis",
                                  "input": self._payload}], stop_reason="tool_use")


def _raw():
    return {
        "_tool_numbers": [267, 600000, 67, 5667, 8420, 1196, 12362493.74, 34, 2400000, 1800000,
                          340, 318, 22, 14, 320, 111, 40, 1100000, 1200000, 1000000, 950000,
                          850000, 800000, 750000, 1400000, 1550000, 1350000, 1150000],
        "findings": [
            {"id": "F1", "title": "Customer master conflict", "business_consequence": "Wrong limits.",
             "computed_values": [{"label": "a", "value": 267}, {"label": "b", "value": 600000}],
             "sources": [{"doc_id": "customer-master-erp"}, {"doc_id": "customer-master-crm"}]},
            {"id": "F2", "title": "EDI undocumented", "business_consequence": "Unowned.",
             "computed_values": [{"label": "c", "value": 67}],
             "sources": [{"doc_id": "order-flow"}]},
            {"id": "F3", "title": "EDI failures", "business_consequence": "Unfulfilled.",
             "computed_values": [{"label": "d", "value": 1196}, {"label": "e", "value": 34}],
             "sources": [{"doc_id": "order-flow"}]},
        ],
    }


def test_build_synthesis_live_maps_depth_fields():
    raw = _raw()
    llm = FakeSynthLLM(depth_synthesis_payload())
    content = build.build_synthesis(raw, domain="o2c", live=True, llm=llm,
                                    doc_keys=sorted(depth_doc_keys()))
    assert len(content.current_state.system_profiles) >= 3
    assert len(content.current_state.format_taxonomy) >= 2
    assert len(content.metrics_framework) >= 4
    for o in content.opportunities:
        assert o.personas and o.expected_behaviour and o.escalation
        assert o.data_readiness and o.technical_complexity and o.operational_readiness
    # derived links still applied on the live path
    opp1 = next(o for o in content.opportunities if o.id == "OPP1")
    assert "OPP3" in opp1.prerequisite_for


class _FanoutLLM:
    """A fake that emits a grounded payload per report tool (drives the deep fan-out path)."""
    _EMITS = {
        "emit_exec": {"executive_summary": {"headline": "h", "situation": "s", "opportunity": "o"}},
        "emit_current_state": {"current_state": {"domain_overview": "o", "process_summary": "s",
            "process_flow": [{"seq": 1, "name": "A", "description": "d"},
                             {"seq": 2, "name": "B", "description": "d"},
                             {"seq": 3, "name": "C", "description": "d"}]}},
        "emit_pain_points": {"pain_points": [{"id": "PP1", "title": "EDI fails", "impact_rank": 1,
                                              "description": "d", "root_cause": "rc",
                                              "severity": "high"}]},
        "emit_recommendation": {"transformation": {"sequencing_rationale": "seq",
                                                   "strategic_readiness": "sr"},
                                "metrics_framework": [{"name": "m1", "definition": "d", "target": "t"},
                                                      {"name": "m2", "definition": "d", "target": "t"},
                                                      {"name": "m3", "definition": "d", "target": "t"}]},
        "emit_roadmap": {"roadmap": [
            {"horizon": "H1", "window": "0-6 months", "theme": "t", "items": [{"title": "i",
                                                                              "rationale": "r"}]},
            {"horizon": "H2", "window": "6-18 months", "theme": "t", "items": [{"title": "i",
                                                                               "rationale": "r"}]},
            {"horizon": "H3", "window": "18+ months", "theme": "t", "items": [{"title": "i",
                                                                              "rationale": "r"}]}]},
        "emit_opportunity": {"id": "OPP1", "title": "Fix", "pattern": "automation", "overview": "o",
            "before_process": [{"seq": 1, "name": "b", "description": "d"},
                               {"seq": 2, "name": "b2", "description": "d"}],
            "after_process": [{"seq": 1, "name": "a", "description": "d"},
                              {"seq": 2, "name": "a2", "description": "d"}],
            "business_impact": {"narrative": "n"}},
    }

    def messages_with_tools(self, *, system, messages, tools, model=None, max_tokens=4096):
        name = tools[0]["name"]
        return ToolTurn(content=[{"type": "tool_use", "id": "e", "name": name,
                                  "input": self._EMITS.get(name, {})}], stop_reason="tool_use")


def test_build_synthesis_live_uses_fanout_when_reg_present():
    """With reg + live + fanout=True, build_synthesis routes through the deep per-report fan-out and
    attaches the fact-store, strategy, and planning assumptions."""
    reg = {"csv_ids": [], "doc_ids": [], "manifest": {"strategy_profile": {
        "direction_type": "consolidate", "horizon": "0-6 months"}}}
    content = build.build_synthesis(_raw(), domain="o2c", live=True, llm=_FanoutLLM(),
                                    doc_keys=[], reg=reg)
    assert content.fact_store is not None                       # fact-store attached
    assert content.strategy and content.strategy.direction_type == "consolidate"
    assert content.strategy_profile.get("direction_type") == "consolidate"  # merged in
    assert len(content.pain_points) == 1 and len(content.opportunities) == 1
    assert len(content.roadmap) == 3 and len(content.metrics_framework) == 3


def test_build_synthesis_live_falls_back_to_single_emit_without_reg():
    """No reg → legacy single-emit path (back-compat), even with fanout left at its default True."""
    llm = FakeSynthLLM(depth_synthesis_payload())
    content = build.build_synthesis(_raw(), domain="o2c", live=True, llm=llm,
                                    doc_keys=sorted(depth_doc_keys()))   # reg omitted, fanout default
    assert content.fact_store is None and content.current_state.system_profiles
    # and explicitly disabling fan-out takes the same legacy path
    content2 = build.build_synthesis(_raw(), domain="o2c", live=True, llm=llm,
                                     doc_keys=sorted(depth_doc_keys()), fanout=False, reg={"x": 1})
    assert content2.fact_store is None


def test_from_payload_tolerates_missing_optional_keys():
    """A minimal/partial emit must degrade, not crash (defensive mapper)."""
    minimal = {
        "current_state": {"domain_overview": "x", "process_summary": "y"},
        "pain_points": [], "opportunities": [],
        "transformation": {}, "roadmap": [], "strategy_profile": {},
    }
    content = build._from_payload(minimal)
    assert content.current_state.domain_overview == "x"
    assert content.current_state.system_profiles == []      # missing key -> empty
    assert content.metrics_framework == []
    assert content.opportunities == []


def test_strategy_profile_as_string_does_not_crash():
    """Regression: a live run once aborted the WHOLE suite with 'str object is not a mapping' when
    a section emitted strategy_profile as a bare string instead of an object — the {**profile}
    spread choked on it. _from_payload must coerce a non-dict strategy_profile to {} so neither the
    mapper nor the downstream spread crashes."""
    payload = {
        "current_state": {"domain_overview": "x"}, "pain_points": [], "opportunities": [],
        "transformation": {}, "roadmap": [],
        "strategy_profile": "Acme should prioritise PO compliance.",   # <- a STRING, not an object
    }
    content = build._from_payload(payload)
    assert content.strategy_profile == {}      # coerced, not the offending string
    # and the dict form still passes through untouched
    ok = build._from_payload({**payload, "strategy_profile": {"direction_type": "consolidate"}})
    assert ok.strategy_profile == {"direction_type": "consolidate"}


class _FanoutLLMStringProfile(_FanoutLLM):
    """A fan-out fake whose recommendation section emits strategy_profile as a bare STRING — the
    exact malformed shape that aborted a live p2p suite before the coercion fix."""
    _EMITS = {**_FanoutLLM._EMITS,
              "emit_recommendation": {**_FanoutLLM._EMITS["emit_recommendation"],
                                      "strategy_profile": "Acme should prioritise PO compliance."}}


def test_fanout_survives_string_strategy_profile():
    """End-to-end through the deep fan-out: even if a section emits strategy_profile as a string,
    build_synthesis completes (the live builder overlays the typed StrategyProfile)."""
    reg = {"csv_ids": [], "doc_ids": [], "manifest": {"strategy_profile": {
        "direction_type": "consolidate", "horizon": "0-6 months"}}}
    content = build.build_synthesis(_raw(), domain="o2c", live=True,
                                    llm=_FanoutLLMStringProfile(), doc_keys=[], reg=reg)
    assert content.strategy_profile.get("direction_type") == "consolidate"  # typed profile wins


def test_no_fixture_for_unknown_domain_refuses():
    with pytest.raises(build.NoFixtureForDomain, match="no grounded fixture"):
        build.build_synthesis(_raw(), domain="p2p", live=False)


def test_build_source_index_dedupes_and_lists_supported_findings():
    raw = _raw()
    # pass a doc list with a duplicate to exercise the seen-dedup branch
    idx = build.build_source_index(raw, ["order-flow", "order-flow", "customer-master-erp"])
    ids = [d.doc_id for d in idx]
    assert ids.count("order-flow") == 1                     # deduped
    of = next(d for d in idx if d.doc_id == "order-flow")
    assert set(of.supported_findings) == {"F2", "F3"}       # findings that cited it


def test_build_source_index_falls_back_to_cited_docs_when_no_list():
    idx = build.build_source_index(_raw(), None)
    assert {d.doc_id for d in idx} == {"customer-master-erp", "customer-master-crm", "order-flow"}


def test_q_helper_maps_quadrant():
    assert build._q("do_first") is MatrixQuadrant.DO_FIRST


def test_derive_charts_builds_grounded_series():
    raw = {"findings": [{"computed_values": [
        {"label": "Unfulfilled EDI orders (count)", "value": 1196},
        {"label": "Unfulfilled Manual orders (count)", "value": 320},
        {"label": "Unfulfilled Email orders (count)", "value": 111},
        {"label": "some non-numeric", "value": "n/a"}]}]}   # bad value -> skipped, no crash
    charts = build.derive_charts(raw)
    # emits BOTH a magnitude bar and a share donut over the same grounded segments
    kinds = {c["kind"] for c in charts}
    assert kinds == {"bar", "donut"}
    bar = next(c for c in charts if c["kind"] == "bar")
    assert bar["key"] == "unfulfilled_by_channel"
    assert [s["value"] for s in bar["segments"]] == [1196, 320, 111]   # sorted desc, EDI first
    donut = next(c for c in charts if c["kind"] == "donut")
    assert [s["value"] for s in donut["segments"]] == [1196, 320, 111]


def test_derive_charts_empty_when_no_breakdown():
    assert build.derive_charts({"findings": []}) == []
    # only one channel present -> not enough for a breakdown
    raw = {"findings": [{"computed_values": [{"label": "Unfulfilled EDI orders", "value": 5}]}]}
    assert build.derive_charts(raw) == []


def test_derive_charts_from_data_tables():
    cs = CurrentState(data_tables=[
        # a clean categorical + numeric table -> a donut (<=5 cats); values copied verbatim
        DataTable(title="Order channel mix", columns=["Channel", "Orders", "Value (EUR)"],
                  rows=[["EDI", "5,667", "59,711,399"], ["Fax", "184", "1,771,828"]]),
        # CRM vs ERP measures -> a bar (eur unit detected from the column name)
        DataTable(title="Credit CRM vs ERP", columns=["Measure", "Value (EUR)"],
                  rows=[["CRM total", "EUR 61,225,000"], ["ERP total", "EUR 58,975,000"],
                        ["Delta", "EUR 30,675,000"]]),
        # a date-led LOG must be REJECTED (no useful breakdown) — exercises the categorical guard
        DataTable(title="Escalation log", columns=["Date", "Resolution (hrs)"],
                  rows=[["2025-01-18", "6"], ["2025-01-25", "67"], ["2025-02-07", "54"]]),
        # too few rows -> skipped
        DataTable(title="One row", columns=["A", "N"], rows=[["x", "1"]]),
        # categorical labels but NO numeric column -> skipped (num_col is None)
        DataTable(title="All text", columns=["System", "Notes"],
                  rows=[["SAP", "core"], ["CRM", "supporting"], ["EDI", "external"]]),
        # numeric column found (col 1 has >=2 numeric cells), but the row loop drops a short row
        # (105) and two empty-label rows (108) — leaving only ONE valid segment (<2) -> skipped (112).
        DataTable(title="Ragged", columns=["Cat", "Count"],
                  rows=[["A", "5"], ["nine"], ["", "9"], ["", "8"]]),
        # a DUPLICATE title is skipped the second time (seen_titles guard)
        DataTable(title="Order channel mix", columns=["Channel", "Orders"],
                  rows=[["X", "1"], ["Y", "2"]]),
    ])
    charts = build.derive_charts({}, cs)
    titles = [c["title"] for c in charts]
    assert "Order channel mix" in titles and "Credit CRM vs ERP" in titles
    assert "Escalation log" not in titles                       # date-led log rejected
    assert "One row" not in titles and "All text" not in titles and "Ragged" not in titles
    mix = next(c for c in charts if c["title"] == "Order channel mix")
    assert mix["kind"] == "donut" and [s["value"] for s in mix["segments"]] == [5667.0, 184.0]
    crm = next(c for c in charts if c["title"] == "Credit CRM vs ERP")
    assert crm["unit"] == "eur" and crm["segments"][0]["value"] == 61225000.0   # sorted desc, verbatim


def test_derive_charts_helpers():
    assert build._num_cell("5,667") == 5667.0
    assert build._num_cell("EUR 61,225,000") == 61225000.0
    assert build._num_cell("67.3%") == 67.3
    assert build._num_cell("n/a") is None and build._num_cell(None) is None
    # categorical: a small repeated/fixed set is a category; dates / all-unique IDs are not
    assert build._is_categorical("Channel", ["EDI", "Fax", "EDI"]) is True
    assert build._is_categorical("Date", ["2025-01-01", "2025-02-01"]) is False   # date header
    assert build._is_categorical("When", ["2025-01-01", "2025-02-01", "2025-03-01"]) is False  # date VALUES
    assert build._is_categorical("Order ID", [f"ORD-{i}" for i in range(20)]) is False
    assert build._is_categorical("Measure", []) is False
    assert build._unit_from_col("Value (EUR)") == "eur" and build._unit_from_col("Share %") == "percent"
    assert build._unit_from_col("Orders") == ""


def test_bounded_context_to_dict_roundtrips():
    bc = BoundedContext(name="Order Mgmt", kind="core", owner="CS", responsibilities="Receipt",
                        is_shared_kernel=False,
                        relationships=[ContextRelationship(to="Credit", kind="customer_supplier",
                                                           label="U/D")])
    d = bc.to_dict()
    assert d["name"] == "Order Mgmt" and d["kind"] == "core" and d["is_shared_kernel"] is False
    assert d["relationships"][0] == {"to": "Credit", "kind": "customer_supplier", "label": "U/D"}
