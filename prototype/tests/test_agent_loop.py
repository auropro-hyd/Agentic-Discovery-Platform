"""Structural test of the agent loop with a scripted FakeLLM (no API key).

Drives a realistic tool-calling trajectory: describe -> group_by/join_diff/filter_count/
find_mentions -> emit_findings. Proves the loop threads messages correctly, dispatches tools to
the real functions (so numbers are real), and the grounding gate passes for honest output and
fails for fabricated output.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import agent_loop, registry, tools  # noqa: E402
from discovery.llm import ToolTurn  # noqa: E402

DOMAIN = ROOT / "inputs" / "o2c"


@pytest.fixture(scope="module", autouse=True)
def _setup():
    registry.setup_domain(DOMAIN, freeze=True)
    yield


def _tu(name, inp, i):
    return {"type": "tool_use", "id": f"t{i}", "name": name, "input": inp}


class ScriptedLLM:
    """Emits a fixed sequence of tool-use turns, then emit_findings. Real tools run for real."""

    def __init__(self, emit_payload):
        self.emit_payload = emit_payload
        self.step = 0
        self.plan = [
            [_tu("group_by", {"file": "order-flow-analysis-export-2025", "by": ["channel"]}, 0)],
            [_tu("join_diff", {"file_a": "sap-s4-customer-master-export",
                               "file_b": "sap-crm-customer-export", "key": "customer_id",
                               "compare_cols": ["credit_limit_eur", "payment_terms"]}, 1)],
            [_tu("filter_count", {"file": "customer-service-escalation-log-2025",
                                  "predicate": {"col": "root_cause", "op": "contains",
                                                "value": "EDI order not processed"}}, 2)],
            [_tu("find_mentions", {"doc": "edi-integration-register-opella-europe",
                                   "terms": ["Carrefour France", "Lidl", "Coop"]}, 3)],
            [_tu("emit_findings", self.emit_payload, 4)],
        ]

    def messages_with_tools(self, *, system, messages, tools, model=None, max_tokens=4096):
        content = self.plan[self.step]
        self.step += 1
        return ToolTurn(content=content, stop_reason="tool_use")


def _honest_payload():
    return {"findings": [
        {"id": "F1", "title": "Customer master conflict", "severity": "high", "confidence": "verified",
         "description": "ERP and CRM disagree on credit limits/terms for shared accounts.",
         "business_consequence": "Wrong credit limits applied.",
         "computed_values": [{"label": "FR001 delta", "value": 600000, "from_tool": "join_diff"},
                             {"label": "accounts differ", "value": 307, "from_tool": "join_diff"}],
         "sources": [{"doc_id": "sap-s4-customer-master-export"},
                     {"doc_id": "sap-crm-customer-export"}]},
        {"id": "F2", "title": "67% orders via EDI undocumented", "severity": "high", "confidence": "verified",
         "description": "EDI dominates volume but is undocumented.",
         "business_consequence": "Majority of orders unowned.",
         "computed_values": [{"label": "EDI pct", "value": 67.3, "from_tool": "group_by"}],
         "sources": [{"doc_id": "order-flow-analysis-export-2025"},
                     {"doc_id": "o2c-process-raci-opella-europe"}]},
        {"id": "F3", "title": "6 of 14 EDI connections Sanofi-managed", "severity": "amber", "confidence": "verified",
         "description": "Six connections remain under Sanofi TSA.",
         "business_consequence": "Operational dependency on parent.",
         "computed_values": [{"label": "EDI-not-processed escalations", "value": 34, "from_tool": "filter_count"}],
         "sources": [{"doc_id": "edi-integration-register-opella-europe"},
                     {"doc_id": "edi-dispute-resolution-cs-working-notes"}]},
    ]}


def test_loop_runs_and_grounds_honest_output():
    llm = ScriptedLLM(_honest_payload())
    out = agent_loop.run_discovery(llm, ["order-flow-analysis-export-2025"],
                                   ["edi-integration-register-opella-europe"], "narrative")
    assert {f["id"] for f in out["findings"]} == {"F1", "F2", "F3"}


def _transcript_with_real_tool_results():
    """Run the honest plan once to get a transcript whose tool_results hold the real numbers,
    so validate_and_ground can be tested directly against genuine tool output."""
    captured = {}

    class Capture(ScriptedLLM):
        def messages_with_tools(self, *, system, messages, tools, model=None, max_tokens=4096):
            captured["messages"] = messages  # latest history (grows each call)
            return super().messages_with_tools(system=system, messages=messages, tools=tools)

    llm = Capture(_honest_payload())
    agent_loop.run_discovery(llm, ["order-flow-analysis-export-2025"],
                             ["edi-integration-register-opella-europe"], "narrative")
    return captured["messages"]


def test_grounding_rejects_fabricated_number():
    transcript = _transcript_with_real_tool_results()
    bad = _honest_payload()
    bad["findings"][0]["computed_values"][0]["value"] = 999999  # never produced by any tool
    with pytest.raises(agent_loop.GroundingError):
        agent_loop.validate_and_ground(bad, transcript)


def test_grounding_rejects_too_few_sources():
    transcript = _transcript_with_real_tool_results()
    bad = _honest_payload()
    bad["findings"][1]["sources"] = [{"doc_id": "order-flow-analysis-export-2025"}]  # only 1
    with pytest.raises(agent_loop.GroundingError):
        agent_loop.validate_and_ground(bad, transcript)
