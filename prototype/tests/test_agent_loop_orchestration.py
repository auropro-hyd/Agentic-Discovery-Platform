"""Orchestration-level coverage of run_discovery: the activity callback, the no-tool-use reprompt,
the grounding-reject-then-retry path, the _tool_numbers attachment on success, and the
MAX_TURNS budget-exceeded raise. Uses scripted LLMs through the real ToolTurn contract; real
CSV/text tools run for real so the grounded numbers are genuine.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import agent_loop, registry  # noqa: E402
from discovery.llm import ToolTurn  # noqa: E402

DOMAIN = ROOT / "inputs" / "o2c"
CSV = ["order-flow-analysis-export-2025"]
DOC = ["edi-integration-register-opella-europe"]


@pytest.fixture(scope="module", autouse=True)
def _setup():
    registry.setup_domain(DOMAIN, freeze=True)
    yield


def _tu(name, inp, i):
    return {"type": "tool_use", "id": f"t{i}", "name": name, "input": inp}


def _grounded_payload():
    """Two findings, each with >=2 distinct sources; no computed/narrative numbers so it grounds
    without needing tool output (keeps these orchestration tests independent of tool math)."""
    return {"findings": [
        {"id": "F1", "title": "Customer master conflict", "severity": "high",
         "confidence": "verified", "impact_score": 90,
         "description": "ERP and CRM disagree.", "business_consequence": "Wrong limits.",
         "computed_values": [], "narrative_values": [],
         "sources": [{"doc_id": "sap-s4-customer-master-export"},
                     {"doc_id": "sap-crm-customer-export"}]},
        {"id": "F2", "title": "EDI undocumented", "severity": "high",
         "confidence": "verified", "impact_score": 70,
         "description": "EDI dominates volume but is undocumented.",
         "business_consequence": "Unowned channel.", "computed_values": [], "narrative_values": [],
         "sources": [{"doc_id": "order-flow-analysis-export-2025"},
                     {"doc_id": "o2c-process-raci-opella-europe"}]},
    ]}


class SeqLLM:
    """Returns a queued list of content-block lists, one per call."""

    def __init__(self, turns):
        self._turns = list(turns)

    def messages_with_tools(self, *, system, messages, tools, model=None, max_tokens=4096):
        content = self._turns.pop(0) if self._turns else [{"type": "text", "text": "done"}]
        stop = "tool_use" if any(b.get("type") == "tool_use" for b in content) else "end_turn"
        return ToolTurn(content=content, stop_reason=stop)


def test_run_discovery_success_invokes_activity_and_attaches_tool_numbers():
    seen = []
    llm = SeqLLM([
        [_tu("describe", {"file": "order-flow-analysis-export-2025"}, 0)],
        [_tu("emit_findings", _grounded_payload(), 1)],
    ])
    out = agent_loop.run_discovery(llm, CSV, DOC, "narrative", on_activity=seen.append)
    assert {f["id"] for f in out["findings"]} == {"F1", "F2"}
    assert "_tool_numbers" in out                 # the generic allow-list is attached
    assert any("Reading" in s for s in seen)      # narrate() ran via on_activity


def test_run_discovery_reprompts_when_no_tool_use():
    llm = SeqLLM([
        [{"type": "text", "text": "let me think"}],          # no tool_use -> reprompt branch
        [_tu("emit_findings", _grounded_payload(), 0)],
    ])
    out = agent_loop.run_discovery(llm, CSV, DOC, "narrative")
    assert {f["id"] for f in out["findings"]} == {"F1", "F2"}


def test_run_discovery_retries_after_grounding_rejection():
    bad = _grounded_payload()
    bad["findings"][0]["sources"] = [{"doc_id": "sap-s4-customer-master-export"}]  # only 1 source
    llm = SeqLLM([
        [_tu("emit_findings", bad, 0)],                       # rejected by grounding
        [_tu("emit_findings", _grounded_payload(), 1)],       # corrected
    ])
    out = agent_loop.run_discovery(llm, CSV, DOC, "narrative")
    assert {f["id"] for f in out["findings"]} == {"F1", "F2"}


def test_run_discovery_raises_budget_exceeded():
    # never emits findings -> loops MAX_TURNS times then raises
    llm = SeqLLM([[{"type": "text", "text": "still thinking"}] for _ in range(agent_loop.MAX_TURNS)])
    with pytest.raises(agent_loop.AgentBudgetExceeded) as ei:
        agent_loop.run_discovery(llm, CSV, DOC, "narrative")
    assert ei.value.messages                      # carries the transcript for debugging


def test_narrate_covers_every_tool_label():
    labels = {
        "describe": "Reading", "group_by": "Breaking down", "join_diff": "Cross-checking",
        "filter_count": "Counting", "check_conformance": "documented rule",
        "aggregate": "Totalling", "find_mentions": "Searching", "emit_findings": "findings together",
    }
    for name, expect in labels.items():
        assert expect in agent_loop.narrate({"name": name, "input": {}})
    assert "Working" in agent_loop.narrate({"name": "unknown_tool", "input": {}})


def test_canonical_args_sorts_list_args_for_stable_signature():
    a = agent_loop.canonical_args({"terms": ["b", "a"], "file": "x"})
    b = agent_loop.canonical_args({"file": "x", "terms": ["a", "b"]})
    assert a == b                                  # order-independent, key-independent


# ---- validate_and_ground: the remaining rejection branches -------------------
def test_ground_rejects_empty_findings():
    with pytest.raises(agent_loop.GroundingError, match="no findings"):
        agent_loop.validate_and_ground({"findings": []}, [])


def test_ground_rejects_bad_id_pattern():
    bad = _grounded_payload()
    bad["findings"][0]["id"] = "X1"                # not F<n>
    with pytest.raises(agent_loop.GroundingError, match="must match"):
        agent_loop.validate_and_ground(bad, [])


def test_ground_rejects_narrative_quote_not_in_snippets():
    import json as _json
    # a transcript whose tool_results include a find_mentions snippet AND a plain text block
    # (the text block exercises the non-tool_result branch of _collect_snippets/_tool_numbers)
    transcript = [{"role": "user", "content": [
        {"type": "text", "text": "context only, not a tool result"},
        {"type": "tool_result", "tool_use_id": "t0",
         "content": _json.dumps({"results": {"Carrefour": {"snippets": ["a real snippet here"]}}})},
    ]}]
    bad = _grounded_payload()
    bad["findings"][0]["narrative_values"] = [{"value": 1, "quote": "a quote nobody wrote"}]
    with pytest.raises(agent_loop.GroundingError, match="narrative quote not found"):
        agent_loop.validate_and_ground(bad, transcript)


def test_ground_accepts_narrative_quote_present_in_snippets():
    import json as _json
    transcript = [{"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "t0",
         "content": _json.dumps({"results": {"Carrefour": {"snippets": ["Carrefour France EDI"]}}})},
    ]}]
    ok = _grounded_payload()
    ok["findings"][0]["narrative_values"] = [{"value": 1, "quote": "Carrefour France EDI"}]
    agent_loop.validate_and_ground(ok, transcript)   # must not raise (quote found)


def test_harvest_numbers_skips_bools():
    acc: set = set()
    agent_loop._harvest_numbers({"flag": True, "n": 42, "rows": [1, False, 2.5]}, acc)
    assert acc == {42.0, 1.0, 2.5}                 # True/False are not harvested as 1/0
