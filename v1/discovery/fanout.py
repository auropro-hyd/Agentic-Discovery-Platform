"""Per-report / per-opportunity synthesis fan-out (feature 003).

Replaces the single 16K `emit_synthesis` (which had to produce all six reports at once and so thinned
every field) with MANY bounded generations — one per report, plus one per opportunity for the
centrepiece portfolio. Each call:
  - is fed only the RELEVANT grounded slice of the fact-store (numbers + verbatim quotes + entities)
    plus the StrategyProfile brief for the strategic reports;
  - has its own token budget (no shared 16K ceiling);
  - is routed through the EXISTING LLMClient, so the on-disk cache / golden replay / determinism are
    unchanged (each sub-call is cache-keyed on its own inputs);
  - is passed through a per-section grounding gate (`validate_section`) that rejects ungrounded
    MEASURED numbers (retry once), keeps Report-01 factual, and treats sourced factual tables as
    document facts — identical rules to the monolithic gate, applied per section;
  - emits forward-looking PLANNING content into a separate, clearly-labelled channel
    (PlanningAssumption) — never as a measured fact.

Plain-code (no framework — see specs/003-deep-live-pipeline/decision.md). One failed section omits
rather than aborting the suite.
"""
from __future__ import annotations

import re

from .agent_loop import GroundingError, _close
from .models import FactStore, PlanningAssumption, StrategyProfile
from .synthesis import _STRUCTURAL, _SOURCED_TABLE_KEYS, assert_factual

# the seven report keys, in suite order (matches reportsuite.render.REPORTS)
REPORT_KEYS = ["00-executive-summary", "01-current-state", "02-pain-points", "03-recommendation",
               "04-opportunity-portfolio", "05-roadmap", "06-supporting-artefacts"]
# the strategic reports the StrategyProfile shapes (tactical 04/06 stay direction-agnostic)
_STRATEGIC = {"03-recommendation", "05-roadmap"}
# report keys whose prose is held to the factual lint (no diagnostic language)
_FACTUAL = {"01-current-state"}

PLANNING_KINDS = {"date", "owner", "sla", "threshold", "cadence", "cost", "sequence"}


# ── per-section grounding gate (same rules as the monolith, applied to one section) ─────────────
def validate_section(section: dict, allow: set[float], doc_keys: set[str], *,
                     factual: bool = False) -> dict:
    """Raise GroundingError if this report section violates a grounding/factual invariant. Sourced
    factual tables (baseline_stats/data_tables/…) restate cited document facts and are exempt from
    the findings-allow-list; every other measured number must trace to `allow`."""
    def prose_ok(s: str):
        for tok in re.findall(r"\d[\d,]*\.?\d*", s or ""):
            v = float(tok.replace(",", ""))
            if round(v, 4) in _STRUCTURAL:
                continue
            if not _close(v, allow):
                raise GroundingError(f"section has untraceable number {tok!r}")

    def walk(o, sourced=False):
        if isinstance(o, dict):
            if {"value", "unit", "text"} <= set(o):
                if not (round(float(o["value"]), 4) in _STRUCTURAL or _close(o["value"], allow)):
                    raise GroundingError(f"section number {o['value']} not traceable")
            if "doc_key" in o and o["doc_key"] not in doc_keys:
                raise GroundingError(f"unknown doc_key {o['doc_key']!r}")
            for k, v in o.items():
                # planning assumptions are explicitly NON-facts → not number-gated
                walk(v, sourced or k in _SOURCED_TABLE_KEYS or k == "planning_assumptions")
        elif isinstance(o, list):
            for x in o:
                walk(x, sourced)
        elif isinstance(o, str):
            if not sourced:
                prose_ok(o)

    walk(section)
    if factual:
        _lint_factual(section)
    return section


def _lint_factual(o) -> None:
    if isinstance(o, dict):
        for v in o.values():
            _lint_factual(v)
    elif isinstance(o, list):
        for x in o:
            _lint_factual(x)
    elif isinstance(o, str):
        assert_factual(o)


# ── one bounded generation (a report section or an opportunity) ─────────────────────────────────
def _emit_tool(name: str, schema: dict) -> dict:
    return {"name": name,
            "description": ("Emit this report section as structured grounded content. Call EXACTLY "
                            "once. Every measured number must equal a VERIFIED FACT value; put any "
                            "forward-looking planning content (dates, owners, SLAs, thresholds, "
                            "cadence, cost, sequence) in `planning_assumptions`, never as a fact."),
            "input_schema": schema}


SECTION_SYSTEM = (
    "You write ONE section of a grounded, client-ready discovery report. BUSINESS LANGUAGE ONLY. "
    "Every measured figure must equal one of the VERIFIED FACTS you are given — never invent, sum, "
    "or round a number. Forward-looking planning content (a date, a future owner, an SLA, a target "
    "threshold, a cadence, a cost, a sequence decision) is NOT a measured fact: put it in "
    "`planning_assumptions` with its kind and the grounded basis it rests on. Emit by calling the "
    "tool exactly once.")


def synth_section(llm, *, tool_name: str, schema: dict, fact_store: FactStore,
                  strategy: StrategyProfile | None, instruction: str, doc_keys: set[str],
                  factual: bool = False, max_tokens: int = 6000, model=None,
                  attempts: int = 2, allow: set[float] | None = None) -> dict | None:
    """Generate one report section via a bounded, cache-keyed LLM call, then gate it. Returns the
    section dict, or None if it cannot be grounded after `attempts` (the suite omits it rather than
    aborting). `fact_store` is the SLICE shown in the prompt; `allow` (when given) is the grounding
    allow-list to gate against — pass the FULL run's allow-list here so a focused prompt slice never
    starves the gate of a legitimately-grounded number. Determinism inherited from
    llm.messages_with_tools."""
    if allow is None:
        allow = fact_store.numbers_allow()
    brief = strategy.brief() if strategy else ""
    user = (f"VERIFIED FACTS (use ONLY these numbers):\n{_facts_brief(fact_store)}\n\n"
            + (f"STRATEGY (shape this section to this direction):\n{brief}\n\n" if brief else "")
            + f"DOCUMENT KEYS you may cite: {sorted(doc_keys)}\n\n"
            + f"TASK:\n{instruction}\nCall {tool_name} exactly once.")
    messages: list[dict] = [{"role": "user", "content": user}]
    tool = _emit_tool(tool_name, schema)
    last_err = None
    for _ in range(attempts):
        turn = llm.messages_with_tools(system=SECTION_SYSTEM, messages=messages, tools=[tool],
                                       model=model, max_tokens=max_tokens)
        emits = [b for b in turn.tool_uses if b["name"] == tool_name]
        if not emits:
            messages.append({"role": "assistant", "content": turn.content})
            messages.append({"role": "user", "content": f"Call {tool_name} exactly once now."})
            continue
        try:
            return validate_section(emits[0]["input"], allow, doc_keys, factual=factual)
        except GroundingError as e:
            last_err = e
            messages.append({"role": "assistant", "content": turn.content})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": emits[0]["id"],
                 "content": f"REJECTED: {e}\n\nUse only the verified facts for measured numbers; move "
                            f"any planning content into planning_assumptions. Re-emit {tool_name}."}]})
    return None  # could not ground this section — omit it (one section never aborts the suite)


def collect_planning(section: dict | None) -> list[PlanningAssumption]:
    """Pull a section's labelled planning assumptions into typed objects (kept out of the measured
    grounding gate). Unknown kinds default to 'sequence'."""
    out = []
    for pa in (section or {}).get("planning_assumptions", []) or []:
        stmt = str(pa.get("statement", "")).strip()
        if not stmt:
            continue
        kind = str(pa.get("kind", "sequence")).strip().lower()
        out.append(PlanningAssumption(statement=stmt,
                                      kind=kind if kind in PLANNING_KINDS else "sequence",
                                      basis=str(pa.get("basis", "")).strip()))
    return out


def _facts_brief(fs: FactStore) -> str:
    lines = []
    for q in fs.quant:
        lines.append(f"  [num] {q.label} = {q.value} {q.unit} ({q.tier}; {', '.join(q.sources)})")
    for e in fs.entities[:24]:
        attrs = "; ".join(f"{k}={v}" for k, v in list(e.attributes.items())[:6])
        lines.append(f"  [{e.kind}] {e.name} — {attrs} ({', '.join(e.sources)})")
    for d in fs.quotes[:16]:
        lines.append(f"  [quote] \"{d.text}\" — {d.doc_id}")
    for r in fs.relations:
        lines.append(f"  [rel] {r.src} {r.kind} {r.dst}")
    return "\n".join(lines)


# ── orchestrator: build the fact-store, fan out per report (+ per opportunity), assemble ────────
# Each report owns a slice of SynthesisContent fields; the orchestrator merges the per-report emits.
# (Phase 1 wires the control flow + gate + planning channel; Phase 2 fills the per-report schemas to
# reference depth.) The seed names a small number of opportunities to expand individually for r04.
def run_synthesis_fanout(llm, fact_store: FactStore, strategy: StrategyProfile, doc_keys, *,
                         report_specs=None, opp_seeds=None, model=None):
    """Run the fan-out and return (merged_payload: dict, planning: list[PlanningAssumption]).

    `report_specs`: {report_key: {"tool", "schema", "instruction", "slice"(terms)}} — what each
    report generates. `opp_seeds`: [{"id","title","topic"}] — opportunities expanded individually for
    report 04. Both are injected (Phase 2 supplies the real specs); this keeps Phase 1 testable and
    the orchestration logic independent of the schema detail."""
    report_specs = report_specs or {}
    opp_seeds = opp_seeds or []
    merged: dict = {}
    planning: list[PlanningAssumption] = []
    # numbers are grounded RUN-WIDE; the per-section slice only shapes the prompt, so always gate
    # against the full store's allow-list (a focused slice must never starve the gate).
    allow = fact_store.numbers_allow()

    for key in REPORT_KEYS:
        spec = report_specs.get(key)
        if not spec:
            continue
        fs = fact_store.slice_for(*spec.get("slice", [])) if spec.get("slice") else fact_store
        section = synth_section(
            llm, tool_name=spec["tool"], schema=spec["schema"], fact_store=fs, allow=allow,
            strategy=strategy if key in _STRATEGIC else None,
            instruction=spec["instruction"], doc_keys=doc_keys,
            factual=key in _FACTUAL, max_tokens=spec.get("max_tokens", 6000), model=model)
        planning += collect_planning(section)
        _merge(merged, section)

    # per-opportunity deep generation for the centrepiece portfolio (report 04)
    opps = []
    for seed in opp_seeds:
        spec = report_specs.get("04-opportunity-portfolio", {})
        opp = synth_section(
            llm, tool_name="emit_opportunity", schema=spec.get("opp_schema", _MIN_OPP_SCHEMA),
            fact_store=fact_store.slice_for(*([seed.get("topic")] if seed.get("topic") else [])),
            allow=allow, strategy=None, instruction=_opp_instruction(seed), doc_keys=doc_keys,
            max_tokens=spec.get("opp_max_tokens", 6000), model=model)
        if opp is not None:
            planning += collect_planning(opp)
            opps.append(opp)
    if opps:
        merged.setdefault("opportunities", [])
        merged["opportunities"] = opps + merged.get("opportunities", [])
    return merged, planning


def _merge(into: dict, section: dict | None) -> None:
    """Merge one report's emitted fields into the suite payload. List fields concatenate; scalar/
    object fields are set if absent (earlier reports own the shared fields). `planning_assumptions`
    is consumed by collect_planning, not merged into the payload."""
    if not section:
        return
    for k, v in section.items():
        if k == "planning_assumptions":
            continue
        if isinstance(v, list):
            into.setdefault(k, [])
            into[k].extend(v)
        else:
            into.setdefault(k, v)


def _opp_instruction(seed: dict) -> str:
    return (f"Write the FULL working documentation for opportunity {seed.get('id','')} — "
            f"\"{seed.get('title','')}\": overview, before/after process, quantified business impact "
            f"(verified numbers only, with derivation), implementation approach, success metrics, "
            f"dependencies and risks. Put any dates/owners/SLAs/thresholds in planning_assumptions. "
            f"Emit emit_opportunity once.")


# a minimal opportunity schema so Phase 1 is runnable; Phase 2 supplies the full reference schema.
_MIN_OPP_SCHEMA = {"type": "object", "properties": {
    "id": {"type": "string"}, "title": {"type": "string"}, "overview": {"type": "string"},
    "business_impact": {"type": "object", "properties": {
        "narrative": {"type": "string"},
        "quantified": {"type": "array", "items": {"type": "object", "properties": {
            "value": {"type": "number"}, "unit": {"type": "string"}, "text": {"type": "string"}},
            "required": ["value", "unit", "text"]}}}},
    "planning_assumptions": {"type": "array", "items": {"type": "object", "properties": {
        "statement": {"type": "string"}, "kind": {"type": "string"}, "basis": {"type": "string"}},
        "required": ["statement"]}}},
    "required": ["id", "title", "overview"]}
