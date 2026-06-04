"""Phase 1 — the synthesis fan-out skeleton (discovery/fanout.py).

Drives the per-section / per-opportunity orchestration with a fake LLM through the real ToolTurn
contract: asserts sections assemble, the per-section grounding gate rejects an ungrounded measured
number (retry path), planning content lands in the labelled channel, a failing section omits without
aborting, opportunities expand individually, and the same inputs replay to the same output.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import fanout  # noqa: E402
from discovery import models as m  # noqa: E402
from discovery.agent_loop import GroundingError  # noqa: E402
from discovery.llm import ToolTurn  # noqa: E402
from discovery.fanout import (  # noqa: E402
    collect_planning, run_synthesis_fanout, synth_section, validate_section,
)


class FakeLLM:
    """Returns a queued emit per call, tagged with the tool the caller offered (so a section's tool
    name flows through). A None queues an empty (no-tool) turn; a callable is invoked with the
    messages to vary by attempt (for the retry path)."""

    def __init__(self, script):
        self._script = list(script)
        self.calls = 0

    def messages_with_tools(self, *, system, messages, tools, model=None, max_tokens=4096):
        self.calls += 1
        tool_name = tools[0]["name"]
        item = self._script.pop(0) if self._script else None
        if callable(item):
            item = item(messages)
        if item is None:
            return ToolTurn(content=[{"type": "text", "text": "…"}], stop_reason="end_turn")
        return ToolTurn(content=[{"type": "tool_use", "id": "e", "name": tool_name, "input": item}],
                        stop_reason="tool_use")


def _fs():
    return m.FactStore(quant=[m.QuantFact("Unfulfilled EDI orders", 1196, "orders", ["flow"]),
                              m.QuantFact("EDI share", 67.3, "percent", ["flow"])],
                       quotes=[m.DocQuote("manual re-entry required", "notes")],
                       entities=[m.EntityFact("account", "Carrefour France",
                                              {"erp_limit": "1800000"}, ["erp"])])


# ── validate_section (the per-section gate) ──────────────────────────────────────────────────────
def test_validate_section_passes_grounded_and_rejects_ungrounded():
    allow = {1196.0, 67.3}
    ok = {"prose": "1,196 EDI orders, 67.3% of volume",
          "numbers": [{"value": 1196, "unit": "orders", "text": "1,196 orders"}]}
    assert validate_section(ok, allow, {"flow"}) is ok
    import pytest
    with pytest.raises(GroundingError, match="untraceable number"):
        validate_section({"prose": "9999 orders affected"}, allow, {"flow"})
    with pytest.raises(GroundingError, match="not traceable"):
        validate_section({"numbers": [{"value": 42, "unit": "x", "text": "42"}]}, allow, {"flow"})
    with pytest.raises(GroundingError, match="unknown doc_key"):
        validate_section({"sources": [{"doc_key": "ghost"}]}, allow, {"flow"})


def test_validate_section_sourced_tables_and_planning_exempt():
    allow = {1196.0}            # 340/318 are NOT in allow, but live in a sourced table → exempt
    section = {"data_tables": [{"rows": [["ERP", "340"], ["CRM", "318"]]}],
               "planning_assumptions": [{"statement": "Go live week 6", "kind": "date"}]}
    assert validate_section(section, allow, set()) is section   # no raise


def test_validate_section_factual_lint():
    import pytest
    allow: set[float] = set()
    # the diagnostic word is nested inside a LIST and a nested DICT (exercises the recursion arcs)
    with pytest.raises(GroundingError, match="diagnostic language"):
        validate_section({"sections": [{"body": "this is a critical risk and a breach"}],
                          "title": "Current state"}, allow, set(), factual=True)
    # a clean factual section with lists + nested dicts + non-string leaves (int/None/bool) passes
    # (the non-string leaf exercises the lint's else/fall-through arc)
    assert validate_section({"rows": [{"step": "Order receipt", "count": 3, "active": True}],
                             "title": "Process", "note": None}, allow, set(), factual=True)
    # structural numbers (years, 0-6) are always allowed
    assert validate_section({"prose": "in 2025 there were 3 steps"}, allow, set())


# ── synth_section (one bounded call + gate + retry + omit) ───────────────────────────────────────
_SCHEMA = {"type": "object", "properties": {"prose": {"type": "string"}}}


def test_synth_section_happy():
    llm = FakeLLM([{"prose": "1,196 EDI orders", "title": "Impact"}])
    out = synth_section(llm, tool_name="emit_x", schema=_SCHEMA, fact_store=_fs(),
                        strategy=None, instruction="do it", doc_keys={"flow"})
    assert out["title"] == "Impact" and llm.calls == 1


def test_synth_section_retries_then_succeeds():
    # first emit has an ungrounded number → rejected; second is clean → accepted
    llm = FakeLLM([{"prose": "9999 orders"}, {"prose": "1,196 orders"}])
    out = synth_section(llm, tool_name="emit_x", schema=_SCHEMA, fact_store=_fs(),
                        strategy=None, instruction="x", doc_keys={"flow"})
    assert out["prose"] == "1,196 orders" and llm.calls == 2


def test_synth_section_omits_when_ungroundable():
    llm = FakeLLM([{"prose": "9999 orders"}, {"prose": "8888 orders"}])   # both bad
    assert synth_section(llm, tool_name="emit_x", schema=_SCHEMA, fact_store=_fs(),
                         strategy=None, instruction="x", doc_keys={"flow"}) is None


def test_synth_section_reprompts_on_empty_turn():
    llm = FakeLLM([None, {"prose": "67.3% via EDI"}])     # no-tool turn, then a clean emit
    out = synth_section(llm, tool_name="emit_x", schema=_SCHEMA, fact_store=_fs(),
                        strategy=None, instruction="x", doc_keys={"flow"})
    assert out["prose"] == "67.3% via EDI" and llm.calls == 2


def test_synth_section_passes_strategy_brief():
    seen = {}

    def capture(messages):
        seen["user"] = messages[0]["content"]
        return {"prose": "ok"}
    llm = FakeLLM([capture])
    synth_section(llm, tool_name="emit_x", schema=_SCHEMA, fact_store=_fs(),
                  strategy=m.StrategyProfile(direction_type="consolidate"),
                  instruction="x", doc_keys={"flow"})
    assert "consolidate" in seen["user"]      # strategy brief reaches the prompt


def test_facts_brief_includes_relations_and_quotes():
    """The prompt brief lists relations + quotes (exercises those loops in _facts_brief)."""
    seen = {}

    def capture(messages):
        seen["user"] = messages[0]["content"]
        return {"prose": "ok"}
    fs = m.FactStore(quotes=[m.DocQuote("manual re-entry", "notes")],
                     relations=[m.Relation("F1", "conflict", "credit systems disagree", ["a"])])
    synth_section(FakeLLM([capture]), tool_name="emit_x", schema=_SCHEMA, fact_store=fs,
                  strategy=None, instruction="x", doc_keys={"notes"})
    assert "[rel] F1 conflict" in seen["user"] and "[quote]" in seen["user"]


# ── collect_planning ─────────────────────────────────────────────────────────────────────────────
def test_collect_planning_typed_and_filtered():
    section = {"planning_assumptions": [
        {"statement": "Migrate Carrefour in Q4", "kind": "date", "basis": "register"},
        {"statement": "Owner: Credit Controller", "kind": "weird"},   # unknown kind -> sequence
        {"statement": "", "kind": "date"},                            # empty -> dropped
        "A bare-string assumption from the model",                    # str item -> treated as statement
        12345]}                                                       # non-str/dict -> skipped
    pas = collect_planning(section)
    assert len(pas) == 3
    assert pas[0].kind == "date" and pas[1].kind == "sequence"
    assert pas[2].statement == "A bare-string assumption from the model" and pas[2].kind == "sequence"
    assert collect_planning(None) == []


# ── run_synthesis_fanout (the orchestrator) ──────────────────────────────────────────────────────
def _specs():
    sch = {"type": "object", "properties": {"pain_points": {"type": "array"}}}
    return {
        "02-pain-points": {"tool": "emit_r02", "schema": sch, "instruction": "pps",
                           "slice": ["edi"],
                           # emitted content for this report (a list field + planning)
                           },
        "03-recommendation": {"tool": "emit_r03",
                              "schema": {"type": "object", "properties": {}}, "instruction": "rec"},
    }


def test_fanout_assembles_reports_opportunities_and_planning():
    fs = _fs()
    # script: r02 emit (with a list field + planning), r03 emit, then one opportunity emit
    script = [
        {"pain_points": [{"id": "PP1", "title": "EDI fails"}],
         "planning_assumptions": [{"statement": "target H1", "kind": "date"}]},
        {"sequencing_rationale": "OPP1 first"},
        {"id": "OPP1", "title": "Exception handling", "overview": "auto-triage",
         "planning_assumptions": [{"statement": "owner: CS Lead", "kind": "owner"}]},
    ]
    llm = FakeLLM(script)
    merged, planning = run_synthesis_fanout(
        llm, fs, m.StrategyProfile(), doc_keys={"flow"},
        report_specs=_specs(), opp_seeds=[{"id": "OPP1", "title": "Exception handling",
                                           "topic": "edi"}])
    assert merged["pain_points"][0]["id"] == "PP1"            # report field merged
    assert merged["sequencing_rationale"] == "OPP1 first"     # scalar field set
    assert merged["opportunities"][0]["id"] == "OPP1"         # per-opp expansion merged in
    kinds = {p.kind for p in planning}
    assert "date" in kinds and "owner" in kinds              # planning collected from both


def test_fanout_skips_report_with_no_spec_and_omits_failed_opp():
    fs = _fs()
    # opp emit is ungroundable twice -> omitted; r02 omitted (no spec for it here)
    llm = FakeLLM([{"id": "OPP9", "title": "t", "overview": "o",
                    "business_impact": {"quantified": [{"value": 5, "unit": "x", "text": "5"}]}},
                   {"id": "OPP9", "title": "t", "overview": "o",
                    "business_impact": {"quantified": [{"value": 5, "unit": "x", "text": "5"}]}}])
    merged, planning = run_synthesis_fanout(
        llm, fs, m.StrategyProfile(), doc_keys={"flow"},
        report_specs={"04-opportunity-portfolio": {}},
        opp_seeds=[{"id": "OPP9", "title": "t", "topic": ""}])
    assert "opportunities" not in merged                     # the single opp failed grounding -> omitted
    assert planning == []


def test_fanout_omits_a_report_that_raises(monkeypatch):
    """A malformed emit that makes section assembly raise must omit ONLY that report, not abort the
    suite (resilience over all-or-nothing)."""
    fs = _fs()
    calls = {"n": 0}
    real = fanout.synth_section

    def flaky(*a, **k):
        calls["n"] += 1
        if k.get("tool_name") == "emit_r02":
            raise TypeError("simulated malformed emit shape")   # report 02 blows up
        return real(*a, **k)
    monkeypatch.setattr(fanout, "synth_section", flaky)
    specs = {
        "02-pain-points": {"tool": "emit_r02", "schema": {"type": "object", "properties": {}},
                           "instruction": "x"},
        "03-recommendation": {"tool": "emit_r03", "schema": {"type": "object", "properties": {}},
                              "instruction": "y"},
    }
    llm = FakeLLM([{"sequencing_rationale": "OPP1 first"}])    # only r03 will reach the LLM
    merged, planning = run_synthesis_fanout(llm, fs, m.StrategyProfile(), doc_keys={"flow"},
                                            report_specs=specs)
    assert "pain_points" not in merged                        # r02 omitted (raised), suite survived
    assert merged.get("sequencing_rationale") == "OPP1 first"  # r03 still assembled


def test_fanout_omits_an_opportunity_that_raises(monkeypatch):
    fs = _fs()
    real = fanout.synth_section

    def flaky(*a, **k):
        if k.get("tool_name") == "emit_opportunity":
            raise ValueError("bad opp shape")
        return real(*a, **k)
    monkeypatch.setattr(fanout, "synth_section", flaky)
    merged, _ = run_synthesis_fanout(FakeLLM([]), fs, m.StrategyProfile(), doc_keys={"flow"},
                                     report_specs={"04-opportunity-portfolio": {}},
                                     opp_seeds=[{"id": "OPP1", "title": "t", "topic": ""}])
    assert "opportunities" not in merged                      # the raising opp omitted, no crash


def test_fanout_merge_concats_lists_and_keeps_first_scalar():
    into: dict = {}
    fanout._merge(into, {"xs": [1], "name": "a"})
    fanout._merge(into, {"xs": [2], "name": "b"})       # list concats; scalar keeps first
    fanout._merge(into, None)                           # None is a no-op
    assert into == {"xs": [1, 2], "name": "a"}


def test_fanout_determinism_same_inputs_same_output():
    fs = _fs()
    specs = {"03-recommendation": {"tool": "emit_r03", "schema": {"type": "object", "properties": {}},
                                   "instruction": "rec"}}
    out1, _ = run_synthesis_fanout(FakeLLM([{"sequencing_rationale": "x"}]), fs,
                                   m.StrategyProfile(), doc_keys={"flow"}, report_specs=specs)
    out2, _ = run_synthesis_fanout(FakeLLM([{"sequencing_rationale": "x"}]), fs,
                                   m.StrategyProfile(), doc_keys={"flow"}, report_specs=specs)
    assert out1 == out2
