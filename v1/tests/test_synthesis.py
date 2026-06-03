"""Live-path coverage for synthesis without spending credits.

Drives run_synthesis() against a scripted fake LLM that returns a real ToolTurn through the actual
messages_with_tools contract, so the live wiring (prompt build -> tool emit -> grounding ->
retry-on-rejection -> validated payload) is exercised end to end. Also covers the emit-tool schema
builder, allowed_numbers, and every rejection branch of validate_synthesis.

The depth payload is built from fixture_o2c() (see tests/_payloads.py), so this test proves the
SAME consultant-grade depth the renderer expects survives the live grounding gate.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import synthesis  # noqa: E402
from discovery.agent_loop import GroundingError  # noqa: E402
from discovery.llm import ToolTurn  # noqa: E402
from _payloads import depth_doc_keys, depth_synthesis_payload, o2c_allow  # noqa: E402


# ---- a minimal raw_payload whose allow-list covers the fixture's numbers ----
def _raw_payload() -> dict:
    return {
        "_tool_numbers": [267, 600000, 67, 5667, 8420, 1196, 12362493.74, 34, 2400000, 1800000,
                          340, 318, 22, 14, 320, 111, 40, 1100000, 1200000, 1000000, 950000,
                          850000, 800000, 750000, 1400000, 1550000, 1350000, 1150000],
        "findings": [
            {"id": "F1", "title": "Customer master conflict",
             "business_consequence": "Wrong limits applied.",
             "computed_values": [{"label": "accounts differ", "value": 267},
                                 {"label": "FR gap", "value": 600000}],
             # narrative_values + source quotes exercise the quote-number extraction in allowed_numbers
             "narrative_values": [{"value": 2.4, "quote": "CRM shows 2,400,000 EUR"}],
             "sources": [{"doc_id": "customer-master-erp", "quote": "ERP shows 1,800,000 EUR"},
                         {"doc_id": "customer-master-crm"}]},
            {"id": "F2", "title": "EDI undocumented",
             "business_consequence": "No owner.",
             "computed_values": [{"label": "edi share", "value": 67}],
             "sources": [{"doc_id": "order-flow"}]},
            {"id": "F3", "title": "EDI failures",
             "business_consequence": "Unfulfilled orders.",
             "computed_values": [{"label": "edi unfulfilled", "value": 1196},
                                 {"label": "escalations", "value": 34}],
             "sources": [{"doc_id": "order-flow"}]},
        ],
    }


class ScriptedSynthLLM:
    """Returns a queued sequence of emit payloads (or empty turns) through the real ToolTurn."""

    def __init__(self, turns):
        self._turns = list(turns)
        self.calls = 0
        self.last_messages: list = []

    def messages_with_tools(self, *, system, messages, tools, model=None, max_tokens=4096):
        self.calls += 1
        self.last_messages = messages
        item = self._turns.pop(0) if self._turns else None
        if item is None:                       # an empty turn (no tool_use)
            return ToolTurn(content=[{"type": "text", "text": "thinking..."}],
                            stop_reason="end_turn")
        return ToolTurn(content=[{"type": "tool_use", "id": "e1", "name": "emit_synthesis",
                                  "input": item}], stop_reason="tool_use")


def test_run_synthesis_happy_path_returns_grounded_depth():
    raw = _raw_payload()
    payload = depth_synthesis_payload()
    doc_keys = sorted(depth_doc_keys())
    llm = ScriptedSynthLLM([payload])
    out = synthesis.run_synthesis(llm, raw, doc_keys)
    assert llm.calls == 1
    # the depth survives the live grounding gate and is returned intact
    assert out["current_state"]["system_profiles"]
    assert out["current_state"]["format_taxonomy"]
    assert out["metrics_framework"]
    for o in out["opportunities"]:
        assert o["personas"] and o["expected_behaviour"] and o["escalation"]
        assert o["data_readiness"] and o["technical_complexity"] and o["operational_readiness"]


def test_run_synthesis_reprompts_when_no_emit():
    raw = _raw_payload()
    llm = ScriptedSynthLLM([None, depth_synthesis_payload()])  # first turn emits nothing
    out = synthesis.run_synthesis(llm, raw, sorted(depth_doc_keys()))
    assert llm.calls == 2
    assert out["opportunities"]


def test_run_synthesis_retries_after_grounding_rejection():
    raw = _raw_payload()
    bad = depth_synthesis_payload()
    # inject a fabricated number into report-04 narrative -> first emit is rejected
    bad["opportunities"][0]["business_impact"]["narrative"] += " saving 999999 euros."
    good = depth_synthesis_payload()
    llm = ScriptedSynthLLM([bad, good])
    out = synthesis.run_synthesis(llm, raw, sorted(depth_doc_keys()))
    assert llm.calls == 2
    # the rejection was fed back as a tool_result before the retry
    assert any(isinstance(m.get("content"), list)
               and any(isinstance(b, dict) and b.get("type") == "tool_result"
                       for b in m["content"])
               for m in llm.last_messages)
    assert out["opportunities"]


def test_run_synthesis_gives_up_after_retries():
    raw = _raw_payload()
    bad = depth_synthesis_payload()
    bad["opportunities"][0]["business_impact"]["narrative"] += " saving 999999 euros."
    llm = ScriptedSynthLLM([bad, bad, bad])   # never fixes it (3 attempts)
    with pytest.raises(GroundingError, match="failed validation after retries"):
        synthesis.run_synthesis(llm, raw, sorted(depth_doc_keys()))
    assert llm.calls == 3                     # three attempts before giving up


def test_run_synthesis_recovers_on_third_attempt():
    raw = _raw_payload()
    bad = depth_synthesis_payload()
    bad["opportunities"][0]["business_impact"]["narrative"] += " saving 999999 euros."
    good = depth_synthesis_payload()
    llm = ScriptedSynthLLM([bad, bad, good])  # fixes it on the 3rd
    out = synthesis.run_synthesis(llm, raw, sorted(depth_doc_keys()))
    assert llm.calls == 3 and out["opportunities"]


def test_fix_hint_is_targeted_per_error_kind():
    from discovery.agent_loop import GroundingError as GE
    assert "FACTUAL" in synthesis._fix_hint(GE("Report-01 prose contains diagnostic language: ['exposure']"))
    assert "VERIFIED NUMBERS" in synthesis._fix_hint(GE("prose has untraceable number '999'"))
    assert "DOCUMENT KEYS" in synthesis._fix_hint(GE("unknown doc_key 'x'"))
    assert synthesis._fix_hint(GE("some other failure"))   # generic fallback non-empty


def test_run_synthesis_with_suppress_names_adds_avoid_clause():
    raw = _raw_payload()
    llm = ScriptedSynthLLM([depth_synthesis_payload()])
    synthesis.run_synthesis(llm, raw, sorted(depth_doc_keys()), suppress_names=["Acme Holdings"])
    user_msg = llm.last_messages[0]["content"]
    assert "Acme Holdings" in user_msg and "DO NOT name these organisations" in user_msg


# ---- emit-tool schema builder -------------------------------------------------
def test_emit_tool_schema_carries_all_depth_fields():
    tool = synthesis.synthesis_emit_tool(["order-flow", "customer-master-erp"])
    props = tool["input_schema"]["properties"]
    cs = props["current_state"]["properties"]
    opp = props["opportunities"]["items"]["properties"]
    assert "system_profiles" in cs and "format_taxonomy" in cs
    assert "metrics_framework" in props
    for f in ("personas", "expected_behaviour", "escalation", "data_readiness",
              "technical_complexity", "operational_readiness"):
        assert f in opp
    # doc-key enum is the sorted set of provided keys
    assert props["pain_points"]["items"]["properties"]["sources"]["items"][
        "properties"]["doc_key"]["enum"] == ["customer-master-erp", "order-flow"]


# ---- schema <-> model enum sync (regression: 'modernisation' crashed the live run) ----
def test_opp_pattern_schema_enum_matches_model_enum():
    """Every `pattern` value the emit schema allows MUST be a valid OppPattern, or the live model
    can emit a schema-valid value the dataclass rejects (the bug that fell back to the fixture)."""
    from discovery.models import OppPattern
    tool = synthesis.synthesis_emit_tool(["d"])
    schema_patterns = set(
        tool["input_schema"]["properties"]["opportunities"]["items"]["properties"]["pattern"]["enum"])
    model_patterns = {p.value for p in OppPattern}
    assert schema_patterns <= model_patterns, \
        f"schema offers patterns the model can't parse: {schema_patterns - model_patterns}"


def test_build_opp_accepts_modernisation_pattern():
    from discovery.reportsuite.build import _opp
    o = _opp({"id": "OPP1", "title": "Modernise", "pattern": "modernisation",
              "business_impact": {"narrative": "n", "quantified": []},
              "before_process": [], "after_process": [], "sources": []})
    assert o.pattern.value == "modernisation"


# ---- allowed_numbers ----------------------------------------------------------
def test_allowed_numbers_includes_tool_numbers_ratios_and_eur_scaling():
    raw = _raw_payload()
    allow = synthesis.allowed_numbers(raw)
    assert 267.0 in allow and 1196.0 in allow            # tool numbers + computed values
    assert 12362493.74 in allow                          # large EUR
    assert 12.362494 in allow or round(12362493.74 / 1_000_000, 4) in allow  # /1e6 scaling
    assert round(5667 / 8420 * 100, 1) in allow          # a derived ratio
    # a junk value is rejected by add()'s float guard (no crash, just absent)
    raw["_tool_numbers"].append("not-a-number")
    synthesis.allowed_numbers(raw)                        # must not raise


# ---- validate_synthesis: every rejection branch ------------------------------
def _valid():
    return depth_synthesis_payload(), o2c_allow(), depth_doc_keys()


def test_validate_passes_clean():
    p, a, d = _valid()
    synthesis.validate_synthesis(p, a, d)                 # must not raise


def test_validate_rejects_untraceable_prose_number():
    p, a, d = _valid()
    p["transformation"]["strategic_readiness"] += " worth 424242 today."
    with pytest.raises(GroundingError, match="untraceable number"):
        synthesis.validate_synthesis(p, a, d)


def test_validate_rejects_untraceable_numberref():
    p, a, d = _valid()
    p["opportunities"][0]["business_impact"]["quantified"].append(
        {"value": 555555, "unit": "eur", "text": "fabricated"})
    with pytest.raises(GroundingError, match="not traceable"):
        synthesis.validate_synthesis(p, a, d)


def test_validate_rejects_unknown_doc_key():
    p, a, d = _valid()
    p["opportunities"][0]["sources"].append({"doc_key": "totally-unknown-doc"})
    with pytest.raises(GroundingError, match="unknown doc_key"):
        synthesis.validate_synthesis(p, a, d)


def test_validate_rejects_diagnostic_language_in_report01():
    p, a, d = _valid()
    p["current_state"]["domain_overview"] += " There is a critical conflict here."
    with pytest.raises(GroundingError, match="diagnostic language"):
        synthesis.validate_synthesis(p, a, d)


def test_validate_rejects_no_pain_points():
    p, a, d = _valid()
    p["pain_points"] = []
    with pytest.raises(GroundingError, match="no pain points"):
        synthesis.validate_synthesis(p, a, d)


def test_validate_rejects_no_opportunities():
    p, a, d = _valid()
    p["opportunities"] = []
    with pytest.raises(GroundingError, match="no opportunities"):
        synthesis.validate_synthesis(p, a, d)


def test_validate_rejects_fewer_opps_than_pps():
    p, a, d = _valid()
    p["opportunities"] = p["opportunities"][:1]
    with pytest.raises(GroundingError, match="opportunity per pain point"):
        synthesis.validate_synthesis(p, a, d)


def test_validate_rejects_dependency_on_unknown_opp():
    p, a, d = _valid()
    p["opportunities"][0]["dependencies"] = ["OPP99"]   # OPP99 is not in the payload
    with pytest.raises(GroundingError, match="unknown opportunity"):
        synthesis.validate_synthesis(p, a, d)


def test_validate_rejects_self_dependency():
    p, a, d = _valid()
    p["opportunities"][0]["dependencies"] = [p["opportunities"][0]["id"]]
    with pytest.raises(GroundingError, match="cannot depend on itself"):
        synthesis.validate_synthesis(p, a, d)


def test_validate_rejects_dependency_cycle():
    p, a, d = _valid()
    o = p["opportunities"]
    o[0]["dependencies"] = [o[1]["id"]]
    o[1]["dependencies"] = [o[0]["id"]]
    with pytest.raises(GroundingError, match="cycle"):
        synthesis.validate_synthesis(p, a, d)


def test_validate_rejects_roadmap_scheduling_dep_too_late():
    p, a, d = _valid()
    # OPP3 depends on OPP1; move OPP1 into a LATER horizon than OPP3
    for hz in p["roadmap"]:
        hz["items"] = [it for it in hz["items"] if it.get("opportunity_id") not in ("OPP1", "OPP3")]
    p["roadmap"][0]["items"].append({"title": "AI Credit Decisioning", "rationale": "x",
                                     "opportunity_id": "OPP3"})
    p["roadmap"][1]["items"].append({"title": "Customer Master Reconciliation", "rationale": "x",
                                     "opportunity_id": "OPP1"})
    with pytest.raises(GroundingError, match="scheduled before its dependency"):
        synthesis.validate_synthesis(p, a, d)


# ---- cycle detector unit (incl. dangling-edge branch) ------------------------
def test_has_cycle_detects_and_ignores_dangling_edges():
    assert synthesis._has_cycle({"A": ["B"], "B": ["A"]}) is True
    # an edge to a node not in the graph is skipped, not a cycle (covers the `continue`)
    assert synthesis._has_cycle({"A": ["GHOST"], "B": []}) is False
    assert synthesis._has_cycle({"A": ["B"], "B": ["C"], "C": []}) is False


# ---- briefs -------------------------------------------------------------------
def test_findings_and_numbers_briefs_render():
    raw = _raw_payload()
    fb = synthesis._findings_brief(raw)
    nb = synthesis._numbers_brief(raw)
    assert "F1" in fb and "Customer master conflict" in fb
    assert "edi share = 67" in nb
