"""Second agent turn: turn the verified findings into client-facing content for reports 01-05.

Two things live here:
  - validate_synthesis(): the grounding gate. Every client-facing number must trace to the
    findings' allow-list; Report 01 must be factual (no diagnostic words); the opportunity
    dependency invariant must hold (OPP3 depends on exactly OPP1). No new fabricated numbers.
  - run_synthesis(): the live synthesis turn (schema-enforced, one re-prompt, fixture fallback).
    Gated behind --live-synth; the demo default uses the hand-grounded fixture.

PP<->OPP mapping is fixed in code (never model-set):
  PP1 (F1 customer master) -> OPP1 (reconciliation)
  PP2 (F2 67% EDI undocumented) -> OPP3 (AI credit decisioning)
  PP3 (F3 EDI fulfilment failures) -> OPP2 (EDI exception handling)
"""
from __future__ import annotations

import json
import re

from . import docnames, tools
from .agent_loop import GroundingError, _close

PP_TO_OPP = {"PP1": "OPP1", "PP2": "OPP3", "PP3": "OPP2"}
OPP_TO_PP = {v: k for k, v in PP_TO_OPP.items()}

# numbers that are structural (report/horizon indices, 2x2 scores, opp count, calendar years,
# roadmap windows) — not data claims, so exempt from the findings-traceability check
_STRUCTURAL = {0, 1, 2, 3, 4, 5, 6, 18} | set(range(2020, 2031))
_DIAGNOSTIC = re.compile(
    r"\b(breach|violation|uncontrolled|critical|severe|urgent|red flag|amber|broken|"
    r"failure risk|conflict|gap|problem|risky|exposure|unhedged|blind spot)\b", re.I)


# ---------------------------------------------------------------------------
# allow-list of legitimate numbers, derived from the findings payload
# ---------------------------------------------------------------------------
def allowed_numbers(raw_payload: dict) -> set[float]:
    """Generic, run-specific allow-list. Sources, in order of authority:
      1. every number the tools actually returned this run (raw_payload['_tool_numbers']) — the
         real denominators/totals/counts, computed from THIS engagement's data;
      2. findings' computed_values + numbers in verified quotes;
      3. legitimate derived ratios n/m*100 over allow-list pairs + dual EUR scaling.
    No domain constants — works for any document set."""
    nums: set[float] = set()

    def add(v):
        try:
            f = float(v)
        except (TypeError, ValueError):
            return
        nums.add(round(f, 4))
        if 0 < f < 1000:
            nums.add(round(f * 1_000_000, 4))   # 12.36 <-> 12,360,000
        if f >= 1_000_000:
            nums.add(round(f / 1_000_000, 4))

    for tn in raw_payload.get("_tool_numbers", []):
        add(tn)
    for f in raw_payload.get("findings", []):
        for cv in f.get("computed_values", []):
            add(cv.get("value"))
        for nv in f.get("narrative_values", []):
            add(nv.get("value"))
            for tok in re.findall(r"\d[\d,]*\.?\d*", str(nv.get("quote", ""))):
                add(tok.replace(",", ""))
        for s in f.get("sources", []):
            for tok in re.findall(r"\d[\d,]*\.?\d*", str(s.get("quote", ""))):
                add(tok.replace(",", ""))
    # legitimate ratios n/m*100 over allow-list pairs (e.g. 267/318*100, 5667/8420*100)
    base = sorted(n for n in nums if n >= 1)
    for a in base:
        for b in base:
            if b and a < b:
                add(round(a / b * 100, 1))
    return nums


def _num_ok(value, allow: set[float]) -> bool:
    return round(float(value), 4) in _STRUCTURAL or _close(value, allow)


def assert_factual(text: str) -> None:
    hits = _DIAGNOSTIC.findall(text or "")
    if hits:
        raise GroundingError(f"Report-01 prose contains diagnostic language: {hits[:3]}")


def validate_synthesis(payload: dict, allow: set[float], doc_keys: set[str]) -> dict:
    """Raise GroundingError if the synthesis violates any grounding/quality invariant."""
    def prose_ok(s: str):
        for tok in re.findall(r"\d[\d,]*\.?\d*", s or ""):
            v = float(tok.replace(",", ""))
            if round(v, 4) in _STRUCTURAL:
                continue
            if not _close(v, allow):
                raise GroundingError(f"prose has untraceable number {tok!r}")

    def walk(o):
        if isinstance(o, dict):
            if {"value", "unit", "text"} <= set(o):
                if not _num_ok(o["value"], allow):
                    raise GroundingError(f"synthesis number {o['value']} not traceable to findings")
            if "doc_key" in o and o["doc_key"] not in doc_keys:
                raise GroundingError(f"unknown doc_key {o['doc_key']!r}")
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
        elif isinstance(o, str):
            prose_ok(o)

    walk(payload)

    # Report 01 must be factual
    def lint01(o):
        if isinstance(o, dict):
            for v in o.values():
                lint01(v)
        elif isinstance(o, list):
            for x in o:
                lint01(x)
        elif isinstance(o, str):
            assert_factual(o)
    lint01(payload.get("current_state", {}))

    # completeness: the suite is useless without pain points AND opportunities (Report 04 is the
    # centrepiece). One opportunity per pain point.
    pps = payload.get("pain_points", [])
    opps = payload.get("opportunities", [])
    if not pps:
        raise GroundingError("synthesis produced no pain points")
    if not opps:
        raise GroundingError("synthesis produced no opportunities (Report 04 would be empty)")
    if len(opps) < len(pps):
        raise GroundingError(f"need an opportunity per pain point: {len(pps)} pain points but "
                             f"only {len(opps)} opportunities")

    # dependency soundness (generic — not tied to specific opportunity ids):
    opp_ids = {o["id"] for o in payload.get("opportunities", [])}
    deps = {o["id"]: list(o.get("dependencies", [])) for o in payload.get("opportunities", [])}
    for oid, ds in deps.items():
        for d in ds:
            if d not in opp_ids:
                raise GroundingError(f"{oid} depends on unknown opportunity {d!r}")
            if d == oid:
                raise GroundingError(f"{oid} cannot depend on itself")
    if _has_cycle(deps):
        raise GroundingError("opportunity dependencies contain a cycle")

    # roadmap must respect declared dependencies: a dependency cannot appear in a LATER horizon
    # than the opportunity that needs it
    order = {hz["horizon"]: i for i, hz in enumerate(payload.get("roadmap", []))}
    placement = {it.get("opportunity_id"): order.get(hz["horizon"], 0)
                 for hz in payload.get("roadmap", []) for it in hz["items"]
                 if it.get("opportunity_id")}
    for oid, ds in deps.items():
        for d in ds:
            if oid in placement and d in placement and placement[d] > placement[oid]:
                raise GroundingError(f"{oid} is scheduled before its dependency {d}")
    return payload


def _has_cycle(deps: dict) -> bool:
    WHITE, GREY, BLACK = 0, 1, 2
    color = {k: WHITE for k in deps}

    def visit(n):
        color[n] = GREY
        for m in deps.get(n, []):
            if m not in color:
                continue
            if color[m] == GREY or (color[m] == WHITE and visit(m)):
                return True
        color[n] = BLACK
        return False

    return any(color[n] == WHITE and visit(n) for n in deps)


# ---------------------------------------------------------------------------
# live synthesis turn (gated behind --live-synth; demo default uses the fixture)
# ---------------------------------------------------------------------------
def synthesis_emit_tool(doc_keys: list[str]) -> dict:
    DOC_ENUM = {"type": "string", "enum": sorted(doc_keys)}
    NUMBER_REF = {"type": "object", "properties": {
        "value": {"type": "number"},
        "unit": {"type": "string",
                 "enum": ["count", "eur", "percent", "ratio", "accounts", "orders", "escalations"]},
        "label": {"type": "string"}, "text": {"type": "string"}},
        "required": ["value", "unit", "text"]}
    SOURCE = {"type": "object", "properties": {
        "doc_key": DOC_ENUM, "as_business_phrase": {"type": "string"}}, "required": ["doc_key"]}
    STEP = {"type": "object", "properties": {
        "seq": {"type": "integer", "minimum": 1}, "name": {"type": "string"},
        "actor": {"type": "string"}, "system": {"type": "string"},
        "description": {"type": "string"},
        "failure_points": {"type": "array", "items": {"type": "string"}},
        "sources": {"type": "array", "items": SOURCE}},
        "required": ["seq", "name", "actor", "description"]}
    READINESS = {"type": "string", "description":
                 "one of high|medium|low, an em-dash, then a one-line reason, e.g. "
                 "'high — both values already exist as structured fields'"}
    OPP = {"type": "object", "properties": {
        "id": {"type": "string", "pattern": r"^OPP\d+$"}, "title": {"type": "string"},
        "pattern": {"type": "string", "enum": ["hitl_workflow", "automation", "ai_agent",
                                               "modernisation"]},
        "overview": {"type": "string"},
        "before_process": {"type": "array", "minItems": 2, "items": STEP},
        "after_process": {"type": "array", "minItems": 2, "items": STEP},
        "business_impact": {"type": "object", "properties": {
            "narrative": {"type": "string"},
            "quantified": {"type": "array", "items": NUMBER_REF},
            "derivation": {"type": "string"}}, "required": ["narrative", "quantified"]},
        "implementation_approach": {"type": "string"},
        "personas": {"type": "array", "items": {"type": "string"},
                     "description": "the business roles who use this once live"},
        "expected_behaviour": {"type": "string",
                               "description": "how the solution behaves day to day, in business "
                                              "terms (what it does, what it never does on its own)"},
        "escalation": {"type": "string",
                       "description": "what happens when it cannot resolve — when and to whom it "
                                      "hands back to a human"},
        "knowledge_sources": {"type": "array", "items": {"type": "string"},
                              "description": "the business systems/sources this draws on (named "
                                             "generically, e.g. 'the ERP credit master')"},
        "document_formats": {"type": "array", "items": {"type": "string"},
                             "description": "the data/document formats it consumes (e.g. "
                                            "'structured transactional export')"},
        "data_readiness": READINESS,
        "technical_complexity": READINESS,
        "operational_readiness": READINESS,
        "required_integrations": {"type": "array", "items": {"type": "string"}},
        "success_metrics": {"type": "array", "items": {"type": "string"}},
        "dependencies": {"type": "array", "items": {"type": "string", "pattern": r"^OPP\d+$"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "value_rating": {"type": "string", "enum": ["high", "medium", "low"]},
        "feasibility_rating": {"type": "string", "enum": ["high", "medium", "low"]},
        "value_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "feasibility_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "matrix_quadrant": {"type": "string",
                            "enum": ["do_first", "plan_for", "consider", "deprioritise"]},
        "sources": {"type": "array", "minItems": 1, "items": SOURCE}},
        "required": ["id", "title", "pattern", "overview", "before_process", "after_process",
                     "business_impact", "implementation_approach", "value_rating",
                     "feasibility_rating", "value_score", "feasibility_score", "matrix_quadrant",
                     "dependencies", "sources", "personas", "expected_behaviour", "escalation",
                     "data_readiness", "technical_complexity", "operational_readiness"]}
    PP = {"type": "object", "properties": {
        "id": {"type": "string", "pattern": r"^PP\d+$"}, "title": {"type": "string"},
        "impact_rank": {"type": "integer", "minimum": 1, "maximum": 3},
        "from_finding": {"type": "string", "pattern": r"^F\d+$"},
        "description": {"type": "string"}, "root_cause": {"type": "string"},
        "failure_pattern": {"type": "string"},
        "quantified": {"type": "array", "items": NUMBER_REF},
        "sources": {"type": "array", "minItems": 2, "items": SOURCE}},
        "required": ["id", "title", "impact_rank", "from_finding", "description",
                     "root_cause", "failure_pattern", "sources"]}
    ROADITEM = {"type": "object", "properties": {
        "title": {"type": "string"}, "rationale": {"type": "string"},
        "opportunity_id": {"type": "string", "enum": ["OPP1", "OPP2", "OPP3"]},
        "depends_on": {"type": "array", "items": {"type": "string"}}},
        "required": ["title", "rationale"]}
    return {"name": "emit_synthesis",
            "description": ("Call EXACTLY ONCE. Client-facing content for reports 01-05 for a "
                            "non-technical Head of Strategy. BUSINESS LANGUAGE ONLY. Every number "
                            "lives in a NumberRef.value matching a verified finding number. Cite "
                            "source documents by key; never write a filename, column, or tool name."),
            "input_schema": {"type": "object", "properties": {
                "current_state": {"type": "object", "properties": {
                    "domain_overview": {"type": "string"}, "process_summary": {"type": "string"},
                    "process_flow": {"type": "array", "minItems": 3, "items": STEP},
                    "process_inventory": {"type": "array", "items": {"type": "object", "properties": {
                        "name": {"type": "string"}, "purpose": {"type": "string"}},
                        "required": ["name", "purpose"]}},
                    "ownership_map": {"type": "array", "items": {"type": "object", "properties": {
                        "activity": {"type": "string"}, "responsible": {"type": "string"},
                        "accountable": {"type": "string"}, "consulted": {"type": "string"},
                        "informed": {"type": "string"}}, "required": ["activity", "accountable"]}},
                    "system_inventory": {"type": "array", "items": {"type": "object", "properties": {
                        "name": {"type": "string"}, "role": {"type": "string"},
                        "system_of_record_for": {"type": "string"}}, "required": ["name", "role"]}},
                    "handoff_catalogue": {"type": "array", "items": {"type": "object", "properties": {
                        "from_step": {"type": "string"}, "to_step": {"type": "string"},
                        "mechanism": {"type": "string"}}, "required": ["from_step", "to_step"]}},
                    "system_profiles": {"type": "array", "items": {"type": "object", "properties": {
                        "name": {"type": "string"},
                        "role": {"type": "string", "description": "what it is / what it's for"},
                        "how_used": {"type": "string",
                                     "description": "how the business actually uses it day to day"},
                        "owners": {"type": "string",
                                   "description": "who owns it and who has access"},
                        "limitations": {"type": "string",
                                        "description": "observed constraints stated as plain fact, "
                                                       "NOT as a judgement (no 'gap'/'conflict'/"
                                                       "'risk' wording — that belongs in pain "
                                                       "points)"}},
                        "required": ["name", "role"]}},
                    "format_taxonomy": {"type": "array", "items": {"type": "object", "properties": {
                        "label": {"type": "string",
                                  "description": "e.g. 'Type 1 — Structured transactional export'"},
                        "description": {"type": "string"},
                        "examples": {"type": "string",
                                     "description": "which sources follow this pattern"}},
                        "required": ["label", "description"]}}},
                    "required": ["domain_overview", "process_summary", "process_flow",
                                 "process_inventory", "ownership_map", "system_inventory",
                                 "handoff_catalogue", "system_profiles", "format_taxonomy"]},
                "pain_points": {"type": "array", "minItems": 2, "maxItems": 8, "items": PP},
                "cross_process_patterns": {"type": "array", "items": {"type": "object", "properties": {
                    "pattern": {"type": "string"}, "description": {"type": "string"}},
                    "required": ["pattern", "description"]}},
                "opportunities": {"type": "array", "minItems": 2, "maxItems": 8, "items": OPP},
                "transformation": {"type": "object", "properties": {
                    "sequencing_rationale": {"type": "string"},
                    "strategic_readiness": {"type": "string"},
                    "dependency_notes": {"type": "string"}},
                    "required": ["sequencing_rationale", "strategic_readiness"]},
                "roadmap": {"type": "array", "minItems": 3, "maxItems": 3, "items": {
                    "type": "object", "properties": {
                        "horizon": {"type": "string", "enum": ["H1", "H2", "H3"]},
                        "window": {"type": "string",
                                   "enum": ["0-6 months", "6-18 months", "18+ months"]},
                        "theme": {"type": "string"},
                        "items": {"type": "array", "minItems": 1, "items": ROADITEM}},
                    "required": ["horizon", "window", "theme", "items"]}},
                "strategy_profile": {"type": "object", "properties": {
                    "posture": {"type": "string"},
                    "notes": {"type": "string"}}, "required": ["posture"]},
                "metrics_framework": {"type": "array", "minItems": 3, "items": {
                    "type": "object", "properties": {
                        "name": {"type": "string"},
                        "definition": {"type": "string",
                                       "description": "what the metric measures, in business terms"},
                        "target": {"type": "string",
                                   "description": "the target to hold delivery to; a forward-looking "
                                                  "goal phrase, e.g. 'at least 70% at go-live, "
                                                  "improving to 90% within 3 months'"}},
                    "required": ["name", "definition", "target"]}},
                "executive_summary": {"type": "object", "properties": {
                    "headline": {"type": "string",
                                 "description": "1-2 sentences framing the engagement and the "
                                                "single most important thing found"},
                    "situation": {"type": "string",
                                  "description": "2-3 sentences: the current state in a nutshell"},
                    "opportunity": {"type": "string",
                                    "description": "2-3 sentences: where the value is and what to "
                                                   "do first"}},
                    "required": ["headline", "situation", "opportunity"]},
                "target_state": {"type": "string",
                                 "description": "a forward-looking 'where this should converge' "
                                                "narrative (3-5 sentences): the to-be picture once "
                                                "the opportunities land. Business language; no new "
                                                "numbers."}},
                "required": ["current_state", "pain_points", "opportunities", "transformation",
                             "roadmap", "strategy_profile", "metrics_framework",
                             "executive_summary", "target_state"]}}


SYNTH_SYSTEM = """You are a transformation strategist writing a briefing for a non-technical Head of \
Strategy. You are turning a set of already-verified discovery findings into client-facing content \
for a business-process assessment.

ABSOLUTE RULES (checked automatically — violations are rejected):
1. BUSINESS LANGUAGE ONLY. NEVER use: pipeline, agent (except the named pattern "AI Agent"), block,
   knowledge graph, evidence synthesis, gap detected/resolved, node, edge, join, diff, group_by,
   aggregate, filter, query, tool, CSV, column, row, locator. Never write a raw column name or a
   filename. Refer to inputs as business documents (e.g. "your system exports", "the policy"). Cite
   a source by choosing its key in `sources`.
2. NO NEW NUMBERS. Every figure goes in a NumberRef.value and must equal one of the VERIFIED NUMBERS
   you are given. Never invent, estimate, sum, average, or round a new number. Do NOT state ROI, FTE,
   hours-saved, or time-to-resolve figures — keep those impacts qualitative. This applies EVERYWHERE,
   including metric targets and readiness reasons: NEVER write a target like "70% at go-live" or
   "within 3 months" — those are unverifiable. State targets as DIRECTIONAL goals against the
   verified baseline (e.g. "a material reduction against the 1,196 baseline", "near-complete
   coverage", "improving through tuning"). The ONLY numbers allowed anywhere are the VERIFIED NUMBERS.
3. FACTUAL CURRENT STATE (report 01). Describe how the process runs. State facts only — NO evaluative
   words (breach, risk, violation, gap, conflict, uncontrolled, critical, broken, exposure). Where a
   step has no documented owner, write "Not assigned". Judgement belongs in pain points and
   opportunities, never report 01.
4. Pain points and opportunities cite the source documents their evidence rests on (by key).
5. DEPENDENCIES & SEQUENCING. Give each opportunity an id (OPP1, OPP2, …). If one opportunity
   genuinely requires another to be done first (e.g. it relies on the output of the other), list
   that in its `dependencies`. Do NOT invent dependencies — only declare one where the evidence
   shows a real prerequisite. The roadmap must never schedule an opportunity before something it
   depends on. Dependencies must form no cycle.
6. Output ONLY by calling emit_synthesis exactly once.
You are not discovering anything new. Explain the settled findings and chart what to do."""


def run_synthesis(llm, raw_payload: dict, doc_keys: list[str], model=None,
                  suppress_names=None) -> dict:
    """Live synthesis turn. Returns the emit_synthesis payload (validated). Raises on failure.

    suppress_names: organisation names the run chose NOT to show on screen — the synthesis must
    never write them into any field (they'd be blocked by the leak guard otherwise)."""
    allow = allowed_numbers(raw_payload)
    findings_brief = _findings_brief(raw_payload)
    numbers_brief = _numbers_brief(raw_payload)
    tool = synthesis_emit_tool(doc_keys)
    n = len(raw_payload.get("findings", []))
    avoid = ""
    if suppress_names:
        avoid = ("\nDO NOT name these organisations anywhere in your output (refer to them only "
                 "generically, e.g. 'the organisation', 'the parent company', or by role): "
                 + ", ".join(suppress_names) + ".\n")
    user = (f"VERIFIED FINDINGS (settled — restate, don't re-derive):\n{findings_brief}\n\n"
            f"VERIFIED NUMBERS you may use (and ONLY these):\n{numbers_brief}\n\n"
            f"DOCUMENT KEYS you may cite: {sorted(doc_keys)}\n{avoid}\n"
            f"Produce, in business language, a DEEP consultant-grade assessment (not a thin "
            f"summary — break things down, explain, and use the structured fields fully):\n"
            f"- current_state: a factual baseline of how this process runs today (no judgements). "
            f"Include system_profiles — a narrative profile per system/source (role, how it's used, "
            f"who owns it, observed constraints stated as plain fact) — and format_taxonomy, the "
            f"2-4 patterns the source information follows (e.g. 'Type 1 — structured transactional "
            f"export').\n"
            f"- pain_points: one per finding ({n} total), each PP ranked by business impact, with "
            f"root cause and failure pattern, citing its source documents.\n"
            f"- opportunities: one recommended intervention per pain point. Give each an id (OPP1, "
            f"OPP2, …), a client-friendly title (avoid the words 'pipeline'/'agent' in titles), an "
            f"intervention pattern (hitl_workflow | automation | ai_agent | modernisation), a full "
            f"BEFORE process and AFTER process, quantified business impact (verified numbers only), "
            f"implementation approach, integrations, success metrics, dependencies (only real "
            f"prerequisites), and risks. ALSO give each: personas (the roles who use it once live), "
            f"expected_behaviour (how it behaves day to day and what it never does on its own), "
            f"escalation (when and to whom it hands back to a human), knowledge_sources (the "
            f"systems/sources it draws on, named generically), document_formats (the data/document "
            f"formats it consumes), and the three readiness ratings (data_readiness, "
            f"technical_complexity, operational_readiness) — each written as 'high|medium|low — "
            f"reason'. Place each on the value/feasibility matrix.\n"
            f"- transformation: sequencing rationale + strategic readiness, honouring dependencies.\n"
            f"- roadmap: three horizons (H1 0-6 / H2 6-18 / H3 18+ months); never schedule an "
            f"opportunity before something it depends on.\n"
            f"- metrics_framework: 4-5 metrics for measuring success once live — name, definition "
            f"(tie to the verified baseline where relevant), and a DIRECTIONAL target (no invented "
            f"numbers; reference the verified baseline, e.g. 'a material reduction against the "
            f"1,196 baseline').\n"
            f"- strategy_profile.posture: a short phrase for the client's strategic direction.\n"
            f"- executive_summary: a headline (1-2 sentences framing the engagement and the single "
            f"most important finding), a situation (the current state in a nutshell), and an "
            f"opportunity (where the value is and what to do first) — for the landing page.\n"
            f"- target_state: a short forward-looking 'where this should converge' narrative (the "
            f"to-be picture once the opportunities land). Business language, no new numbers.\n"
            f"Call emit_synthesis once.")
    messages: list[dict] = [{"role": "user", "content": user}]
    last_err = None
    for attempt in range(2):
        # the full 6-report emit (3+ opportunities with before/after) is large — give it room so
        # opportunities aren't truncated mid-emit
        turn = llm.messages_with_tools(system=SYNTH_SYSTEM, messages=messages, tools=[tool],
                                       model=model, max_tokens=16000)
        messages.append({"role": "assistant", "content": turn.content})
        emits = [b for b in turn.tool_uses if b["name"] == "emit_synthesis"]
        if not emits:
            messages.append({"role": "user", "content": "Call emit_synthesis exactly once now."})
            continue
        try:
            return validate_synthesis(emits[0]["input"], allow, set(doc_keys))
        except GroundingError as e:
            last_err = e
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": emits[0]["id"],
                 "content": f"REJECTED: {e}. Re-emit, fixing this. Use only verified numbers; "
                            f"keep report 01 factual."}]})
    raise GroundingError(f"synthesis failed validation after retries: {last_err}")


def _findings_brief(raw_payload: dict) -> str:
    out = []
    for f in raw_payload.get("findings", []):
        docs = docnames.business_phrase_list([s.get("doc_id", "") for s in f.get("sources", [])])
        out.append(f"[{f['id']}] {f['title']}\n   {f.get('business_consequence','')}\n   "
                   f"(evidence: {docs})")
    return "\n".join(out)


def _numbers_brief(raw_payload: dict) -> str:
    rows = []
    for f in raw_payload.get("findings", []):
        for cv in f.get("computed_values", []):
            rows.append(f"  {cv['label']} = {cv['value']}")
    return "\n".join(rows)
