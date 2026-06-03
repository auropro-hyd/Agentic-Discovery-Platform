"""The agent tool-use loop — the agent genuinely discovers the findings.

The agent is given generic data/text tools and asked to investigate an O2C document set and
emit exactly 3 findings. It is NOT told what the findings are. It calls describe/group_by/
join_diff/filter_count/aggregate/find_mentions, reasons over the results, and terminates by
calling emit_findings. Every quantitative claim is grounded against a real tool result.

Determinism notes: temp 0 + full-history cache key (in llm.py) make replays byte-identical.
canonical_args sorts list args so call dedup is stable. validate_and_ground rejects any number
the agent did not obtain from a tool (anti-fabrication).
"""
from __future__ import annotations

import json
import re

from . import tools
from .llm import LLMClient

MAX_TURNS = 24


class AgentBudgetExceeded(Exception):
    def __init__(self, messages):
        self.messages = messages
        super().__init__("agent exceeded MAX_TURNS without emitting findings")


class GroundingError(Exception):
    pass


EMIT_TOOL = {
    "name": "emit_findings",
    "description": ("Call EXACTLY ONCE when investigation is complete, then stop. Emit ALL the "
                    "material findings you discovered — as many as the evidence supports (typically "
                    "3-8; a thin document set may have fewer). Number them F1, F2, … and ORDER them "
                    "most-impactful first. Give each an impact_score (0-100) reflecting business "
                    "consequence (€ exposure, volume, frequency, risk) so the ranking is explicit. "
                    "Every number in computed_values MUST be a value you received from a prior "
                    "CSV-tool result; every number in narrative_values MUST be backed by a verbatim "
                    "quote from a find_mentions snippet. Do not introduce any number you did not get "
                    "from a tool."),
    "input_schema": {"type": "object", "properties": {"findings": {
        "type": "array", "minItems": 1, "maxItems": 10, "items": {"type": "object", "properties": {
            "id": {"type": "string", "pattern": r"^F\d+$"},
            "title": {"type": "string"},
            "severity": {"type": "string", "enum": ["high", "amber", "info"]},
            "confidence": {"type": "string", "enum": ["verified", "amber", "gap"]},
            "impact_score": {"type": "integer", "minimum": 0, "maximum": 100,
                             "description": "business consequence, higher = more material; used to rank"},
            "description": {"type": "string"},
            "business_consequence": {"type": "string"},
            "computed_values": {"type": "array", "items": {"type": "object", "properties": {
                "label": {"type": "string"}, "value": {"type": "number"},
                "from_tool": {"type": "string"}}, "required": ["label", "value", "from_tool"]}},
            "narrative_values": {"type": "array", "items": {"type": "object", "properties": {
                "label": {"type": "string"}, "value": {"type": ["number", "string"]},
                "doc_id": {"type": "string"}, "quote": {"type": "string"}},
                "required": ["label", "doc_id", "quote"]}},
            "sources": {"type": "array", "minItems": 2, "items": {"type": "object", "properties": {
                "doc_id": {"type": "string"}, "locator": {"type": "string"},
                "quote": {"type": "string"}}, "required": ["doc_id"]}}},
            "required": ["id", "title", "severity", "confidence", "impact_score", "description",
                         "business_consequence", "sources"]}},
        }, "required": ["findings"]},
}


def build_system_prompt(csv_ids: list[str], doc_ids: list[str], narrative_text: str,
                        domain_label: str = "business process") -> str:
    files = "\n".join(f"  - {i}" for i in csv_ids)
    docs = "\n".join(f"  - {i}" for i in doc_ids)
    return f"""You are an enterprise process-discovery analyst examining a {domain_label} document \
set for a company. You have generic data tools and a text-search tool. Discover what is wrong, \
undocumented, or inconsistent — findings that no single document states outright. You surface them \
by COMPUTING over data and CROSS-REFERENCING files.

Documentation says how things are SUPPOSED to work; system exports show how they ACTUALLY work. \
The findings live in the GAP between the two. You do not know the findings in advance — derive them.

PROTOCOL (in order):
1. ORIENT. For every data file, call describe() before computing on it. Never reference a column or
   category value you have not seen in a describe() result. Category/channel value SETS come from
   group_by or describe's full-distinct list — NEVER from a sample row or from prose.
2. FORM QUESTIONS from what describe reveals:
   - Two files describing the SAME entities by the SAME key (e.g. customer_id) — do they AGREE on
     commercial terms/limits? Use join_diff. Disagreement is a finding. Report the SCALE (how many
     accounts differ) and the LARGEST single discrepancy.
   - A categorical column (channel, status, root_cause) — how does it DISTRIBUTE? Use group_by. A
     dominant category (large share by COUNT) that the SOP/RACI do not document or assign an owner
     to is a finding. Confirm the documentation gap by QUOTING the relevant document line via
     find_mentions.
   - A categorical value naming a specific failure — how OFTEN? Use filter_count.
   - A documented RULE (a policy/SOP says "X must Y", e.g. "orders over a threshold need a second
     approval", "a PO must exist before an order") — does the DATA obey it? Use check_conformance
     with `when` = the rows the rule covers and `require` = what they must satisfy. The violating
     count and value-at-risk is a finding. This is the SOP-as-to-be-model conformance check.
   - Named entities/ownership in the narrative docs — locate and COUNT them with find_mentions over
     the exact terms; quote the lines.
3. GROUND. Every quantitative claim MUST come from a tool result, cited by tool: a CSV number from
   group_by/join_diff/filter_count/aggregate (put it in computed_values), or a narrative-stated
   number backed by a verbatim find_mentions quote (put it in narrative_values). NEVER estimate a
   number from a sample or from prose you summarized. Each finding needs >=2 distinct source docs.
4. STOP. When you have investigated every data file and cross-referenced the narrative docs, call
   emit_findings with ALL the material findings the evidence supports (typically 3-8). Give each an
   impact_score and ORDER them most-impactful first. Do not pad with weak findings, and do not drop
   a material one to hit a number. Do not call any tool afterward.

RULES:
- Code does the math; you do the reasoning. Get every number from a tool; never compute or round one
  yourself.
- Prefer the most specific tool. Do not repeat a call with identical args; the result won't change.
- Join only files that share the SAME key column — check describe first.
- On a tool error, read it, fix the argument (usually a column typo from describe), retry once.
- Work files in the listed order for reproducibility.

DATA FILES (use the CSV tools):
{files}

NARRATIVE DOCS (use find_mentions; full frozen text also below):
{docs}

NARRATIVE TEXT (verbatim, for reference — still cite via find_mentions):
{narrative_text}
"""


def canonical_args(args: dict) -> str:
    """Stable signature for dedup — sort list args so order can't fork the cache."""
    norm = {}
    for k, v in args.items():
        norm[k] = sorted(v) if isinstance(v, list) and all(isinstance(x, str) for x in v) else v
    return json.dumps(norm, sort_keys=True, ensure_ascii=False)


def narrate(tu: dict) -> str:
    """Business-readable, demo-safe description of a tool call (no agent/tool jargon)."""
    name, a = tu["name"], tu.get("input", {})
    if name == "describe":
        return f"Reading {a.get('file','a data source')}…"
    if name == "group_by":
        return f"Breaking down {a.get('file','the records')} by {', '.join(a.get('by', []))}…"
    if name == "join_diff":
        return (f"Cross-checking {a.get('file_a','one system')} against "
                f"{a.get('file_b','another')} on {a.get('key','the shared key')}…")
    if name == "filter_count":
        return f"Counting how often a condition occurs in {a.get('file','the records')}…"
    if name == "check_conformance":
        return f"Checking {a.get('file','the records')} against the documented rule…"
    if name == "aggregate":
        return f"Totalling {a.get('col','a field')} in {a.get('file','the records')}…"
    if name == "find_mentions":
        return f"Searching {a.get('doc','a document')} for: {', '.join(a.get('terms', [])[:4])}…"
    if name == "emit_findings":
        return "Pulling the findings together…"
    return f"Working ({name})…"


def run_discovery(llm: LLMClient, csv_ids: list[str], doc_ids: list[str],
                  narrative_text: str, model: str | None = None, on_activity=None,
                  domain_label: str = "business process") -> dict:
    system = build_system_prompt(csv_ids, doc_ids, narrative_text, domain_label)
    schemas = tools.schemas() + [EMIT_TOOL]
    messages: list[dict] = [{"role": "user", "content":
                             f"Investigate this {domain_label} landscape and emit exactly 3 "
                             "findings. Begin by orienting on each data file per the protocol."}]
    seen, findings = set(), None
    for _ in range(MAX_TURNS):
        turn = llm.messages_with_tools(system=system, messages=messages, tools=schemas, model=model)
        messages.append({"role": "assistant", "content": turn.content})
        tool_uses = turn.tool_uses
        if on_activity:
            for tu in tool_uses:
                on_activity(narrate(tu))
        if turn.stop_reason != "tool_use" or not tool_uses:
            messages.append({"role": "user", "content":
                             "You must finish by calling emit_findings exactly once. Do that now."})
            continue
        # Append a tool_result for EVERY tool_use first (API requires 1:1), then act on it.
        # Grounding is evaluated AFTER results are recorded so a grounding failure can be
        # surfaced back to the agent as a tool_result instead of desyncing the message list.
        results, emit_payload, ground_err = [], None, None
        for tu in tool_uses:
            if tu["name"] == "emit_findings":
                try:
                    emit_payload = validate_and_ground(tu["input"], messages)
                    results.append(_tr(tu["id"], {"status": "received"}))
                except GroundingError as e:
                    ground_err = str(e)
                    results.append(_tr(tu["id"], {"status": "rejected", "reason": ground_err,
                                                  "fix": "Re-emit using only numbers from tool "
                                                         "results; ensure >=2 distinct source docs "
                                                         "per finding."}))
                continue
            sig = (tu["name"], canonical_args(tu["input"]))
            seen.add(sig)
            results.append(_tr(tu["id"], tools.dispatch(tu["name"], tu["input"])))
        messages.append({"role": "user", "content": results})
        if emit_payload is not None:
            # attach every number the tools actually returned this run — the generic, run-specific
            # allow-list the synthesis stage grounds against (no domain constants needed)
            emit_payload["_tool_numbers"] = sorted(_collect_tool_numbers(messages))
            return emit_payload
        # if grounding rejected, loop continues so the agent can correct
    raise AgentBudgetExceeded(messages)


def _tr(tool_use_id: str, content: dict) -> dict:
    return {"type": "tool_result", "tool_use_id": tool_use_id,
            "content": json.dumps(content, sort_keys=True, ensure_ascii=False)}


def validate_and_ground(payload: dict, transcript: list) -> dict:
    """Anti-fabrication gate. Pure Python, post-emit.

    Findings are variable in number and ranked by impact (most material first). We check: at least
    one finding; unique sequential F-ids; impact-descending order; and the grounding rules (>=2
    source docs, every computed value from a tool, every narrative number backed by a real quote).
    """
    findings = payload.get("findings", [])
    if not findings:
        raise GroundingError("no findings emitted")
    ids = [f["id"] for f in findings]
    if len(set(ids)) != len(ids):
        raise GroundingError(f"finding ids must be unique; got {ids}")
    if not all(re.fullmatch(r"F\d+", i) for i in ids):
        raise GroundingError(f"finding ids must match F<n>; got {ids}")
    # ranked most-impactful first
    scores = [f.get("impact_score", 0) for f in findings]
    if scores != sorted(scores, reverse=True):
        raise GroundingError(f"findings must be ordered by impact_score descending; got {scores}")

    tool_numbers = _collect_tool_numbers(transcript)
    snippets = _collect_snippets(transcript)
    for f in findings:
        if len({s["doc_id"] for s in f["sources"]}) < 2:
            raise GroundingError(f"{f['id']}: needs >=2 distinct source docs")
        for cv in f.get("computed_values", []):
            if not _close(cv["value"], tool_numbers):
                raise GroundingError(f"{f['id']}: computed value {cv['value']} not from any tool result")
        for nv in f.get("narrative_values", []):
            q = tools._norm(nv["quote"])
            if not any(q in s for s in snippets):
                raise GroundingError(f"{f['id']}: narrative quote not found in any find_mentions snippet")
    return payload


def _collect_tool_numbers(transcript: list) -> set:
    nums = set()
    for m in transcript:
        if m["role"] != "user":
            continue
        content = m["content"]
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                _harvest_numbers(json.loads(block["content"]), nums)
    return nums


def _harvest_numbers(obj, acc: set):
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        acc.add(round(float(obj), 4))
    elif isinstance(obj, dict):
        for v in obj.values():
            _harvest_numbers(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _harvest_numbers(v, acc)


def _collect_snippets(transcript: list) -> set:
    out = set()
    for m in transcript:
        if m["role"] != "user" or not isinstance(m["content"], list):
            continue
        for block in m["content"]:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                data = json.loads(block["content"])
                if isinstance(data, dict) and "results" in data:
                    for term in data["results"].values():
                        for sn in term.get("snippets", []):
                            out.add(tools._norm(sn))
    return out


def _close(value, tool_numbers: set, tol: float = 0.5) -> bool:
    v = round(float(value), 4)
    return any(abs(v - t) <= tol for t in tool_numbers)
