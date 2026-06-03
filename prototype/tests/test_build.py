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
from discovery.models import MatrixQuadrant  # noqa: E402
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
        "_tool_numbers": [267, 600000, 67, 5667, 8420, 1196, 12362493.74, 34, 2400000, 1800000],
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
    assert len(charts) == 1
    c = charts[0]
    assert c["key"] == "unfulfilled_by_channel" and c["kind"] == "bar"
    # sorted descending, EDI first
    assert [s["value"] for s in c["segments"]] == [1196, 320, 111]


def test_derive_charts_empty_when_no_breakdown():
    assert build.derive_charts({"findings": []}) == []
    # only one channel present -> not enough for a breakdown
    raw = {"findings": [{"computed_values": [{"label": "Unfulfilled EDI orders", "value": 5}]}]}
    assert build.derive_charts(raw) == []
