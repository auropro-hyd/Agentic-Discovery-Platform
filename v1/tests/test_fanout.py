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
    merged, planning, _ = run_synthesis_fanout(
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
    merged, planning, _ = run_synthesis_fanout(
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
    merged, planning, _ = run_synthesis_fanout(llm, fs, m.StrategyProfile(), doc_keys={"flow"},
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
    merged, _, _ = run_synthesis_fanout(FakeLLM([]), fs, m.StrategyProfile(), doc_keys={"flow"},
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
    out1, _, _ = run_synthesis_fanout(FakeLLM([{"sequencing_rationale": "x"}]), fs,
                                      m.StrategyProfile(), doc_keys={"flow"}, report_specs=specs)
    out2, _, _ = run_synthesis_fanout(FakeLLM([{"sequencing_rationale": "x"}]), fs,
                                      m.StrategyProfile(), doc_keys={"flow"}, report_specs=specs)
    assert out1 == out2


# ── parallelization: order-independence, omission signal, worker count ────────────────────────────
import threading  # noqa: E402


class _ConcurrentLLM:
    """Thread-safe fake: returns a fixed emit keyed by the offered tool name (no mutable per-call
    state), and records how many calls were IN FLIGHT simultaneously so we can prove the pool really
    ran sections concurrently (not silently serialized)."""

    def __init__(self, by_tool, barrier_n=0):
        self._by_tool = by_tool
        self._lock = threading.Lock()
        self.max_inflight = 0
        self._inflight = 0
        # an optional barrier forces N calls to overlap, proving real concurrency
        self._barrier = threading.Barrier(barrier_n) if barrier_n else None

    def messages_with_tools(self, *, system, messages, tools, model=None, max_tokens=4096):
        with self._lock:
            self._inflight += 1
            self.max_inflight = max(self.max_inflight, self._inflight)
        if self._barrier:
            try:
                self._barrier.wait(timeout=5)
            except threading.BrokenBarrierError:
                pass
        try:
            name = tools[0]["name"]
            return ToolTurn(content=[{"type": "tool_use", "id": "e", "name": name,
                                      "input": self._by_tool.get(name, {})}], stop_reason="tool_use")
        finally:
            with self._lock:
                self._inflight -= 1


_MULTI_SPECS = {
    "00-executive-summary": {"tool": "emit_r00", "schema": {"type": "object", "properties": {}},
                             "instruction": "exec"},
    "03-recommendation": {"tool": "emit_r03", "schema": {"type": "object", "properties": {}},
                          "instruction": "rec"},
    "05-roadmap": {"tool": "emit_r05", "schema": {"type": "object", "properties": {}},
                   "instruction": "road"},
}
_MULTI_EMITS = {
    "emit_r00": {"target_state": "t"},
    "emit_r03": {"sequencing_rationale": "seq"},
    "emit_r05": {"strategic_readiness": "ready"},
    "emit_opportunity": {"id": "OPPx", "title": "t", "overview": "o"},
}


def test_max_workers_env_parsing(monkeypatch):
    monkeypatch.setenv("DISCOVERY_MAX_WORKERS", "3"); assert fanout._max_workers() == 3
    monkeypatch.setenv("DISCOVERY_MAX_WORKERS", "0"); assert fanout._max_workers() == 1   # floored
    monkeypatch.setenv("DISCOVERY_MAX_WORKERS", "nonsense"); assert fanout._max_workers() == 4  # fallback
    monkeypatch.delenv("DISCOVERY_MAX_WORKERS", raising=False); assert fanout._max_workers() == 4


def test_fanout_output_identical_at_workers_1_and_4(monkeypatch):
    """The whole point: byte-identical merged/planning regardless of worker count (submission-order
    consume). Same fixed emits, run serial then parallel — outputs must be equal."""
    def run(n):
        monkeypatch.setenv("DISCOVERY_MAX_WORKERS", str(n))
        return run_synthesis_fanout(_ConcurrentLLM(_MULTI_EMITS), _fs(), m.StrategyProfile(),
                                    doc_keys={"flow"}, report_specs=_MULTI_SPECS,
                                    opp_seeds=[{"id": "OPPx", "title": "t", "topic": ""}])
    m1, p1, o1 = run(1)
    m4, p4, o4 = run(4)
    assert m1 == m4 and o1 == o4 == []
    assert [str(x.statement) for x in p1] == [str(x.statement) for x in p4]


def test_fanout_actually_runs_concurrently():
    """Prove the pool overlaps calls (not silently serialized): 3 sections + a 3-way barrier; if any
    call ran alone the barrier would time out, so reaching max_inflight==3 proves real concurrency."""
    llm = _ConcurrentLLM(_MULTI_EMITS, barrier_n=3)
    run_synthesis_fanout(llm, _fs(), m.StrategyProfile(), doc_keys={"flow"},
                         report_specs=_MULTI_SPECS)
    assert llm.max_inflight == 3


def test_fanout_reports_omitted_sections():
    """A section that fails grounding twice is omitted AND reported in the third return value, so
    run.py can warn / refuse --save-golden."""
    fs = _fs()
    # opp grounds-fails (a measured number not in allow) on both attempts -> omitted
    bad_opp = {"id": "OPP9", "title": "t", "overview": "o",
               "business_impact": {"quantified": [{"value": 999, "unit": "x", "text": "999"}]}}
    llm = _ConcurrentLLM({**_MULTI_EMITS, "emit_opportunity": bad_opp})
    _, _, omitted = run_synthesis_fanout(llm, fs, m.StrategyProfile(), doc_keys={"flow"},
                                         report_specs={"04-opportunity-portfolio": {}},
                                         opp_seeds=[{"id": "OPP9", "title": "t", "topic": ""}])
    assert omitted == ["OPP9"]   # labelled by the seed id, surfaced for the operator


def test_fanout_placeholder_report_not_flagged_omitted():
    """A report spec with an EMPTY instruction is a structural placeholder (the 04 portfolio's
    content comes from opp seeds). Its None return must NOT be reported as a missing section —
    otherwise the operator gets a false-positive warning and --save-golden is wrongly blocked."""
    fs = _fs()
    # report 04 has an empty instruction AND its emit grounds-empty -> returns None, but it's a
    # placeholder so it must NOT appear in `omitted`. A substantive report (03) succeeds normally.
    specs = {
        "03-recommendation": {"tool": "emit_r03", "schema": {"type": "object", "properties": {}},
                              "instruction": "rec"},
        "04-opportunity-portfolio": {"tool": "emit_portfolio",
                                     "schema": {"type": "object", "properties": {}},
                                     "instruction": ""},   # <- placeholder
    }
    # emit_portfolio grounds-fails (a measured number not in `allow`) on both attempts -> the worker
    # returns None for it. Because its instruction is empty (placeholder), that None must NOT be
    # tracked. The opp seed still produces the real portfolio content.
    bad_portfolio = {"numbers": [{"value": 12345, "unit": "x", "text": "12,345 widgets"}]}
    llm = _ConcurrentLLM({**_MULTI_EMITS, "emit_portfolio": bad_portfolio})
    merged, _, omitted = run_synthesis_fanout(
        llm, fs, m.StrategyProfile(), doc_keys={"flow"}, report_specs=specs,
        opp_seeds=[{"id": "OPPx", "title": "t", "topic": ""}])
    assert "04-opportunity-portfolio" not in omitted   # placeholder None is expected, not flagged
    assert merged["opportunities"][0]["id"] == "OPPx"  # portfolio content came from the opp seed
