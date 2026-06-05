"""Per-report emit schemas + prompts for the synthesis fan-out (feature 003, Phase 2).

Each report owns a slice of SynthesisContent (see reportsuite.render field map). This module defines,
per report, the bounded emit-tool schema it produces and the instruction that drives it from the
grounded fact-store slice. The orchestrator (`run_report_fanout`) runs them, merges the slices into
one payload, and reconstructs a reference-depth SynthesisContent via build._from_payload.

Schemas are scoped (a report emits only its fields) so each call stays within its own token budget —
this is what removes the single-16K ceiling. Reusable JSON-schema fragments mirror the report
dataclasses; planning content rides a `planning_assumptions` array (never a measured fact).
"""
from __future__ import annotations

from . import factstore
from .fanout import run_synthesis_fanout
from .models import StrategyProfile

# ── reusable JSON-schema fragments ──────────────────────────────────────────────────────────────
_STR = {"type": "string"}
_STRS = {"type": "array", "items": _STR}


def _source(doc_keys):
    return {"type": "object", "properties": {"doc_key": {"type": "string", "enum": sorted(doc_keys)}},
            "required": ["doc_key"]}


_NUMBER_REF = {"type": "object", "properties": {
    "value": {"type": "number"},
    "unit": {"type": "string",
             "enum": ["count", "eur", "percent", "ratio", "accounts", "orders", "escalations"]},
    "label": _STR, "text": _STR}, "required": ["value", "unit", "text"]}

_PLANNING = {"type": "array", "description":
             "forward-looking content the data cannot compute (a date, future owner, SLA, target "
             "threshold, cadence, cost, or sequence decision) — NEVER a measured fact",
             "items": {"type": "object", "properties": {
                 "statement": _STR,
                 "kind": {"type": "string",
                          "enum": ["date", "owner", "sla", "threshold", "cadence", "cost",
                                   "sequence"]},
                 "basis": {"type": "string",
                           "description": "the grounded fact this assumption is anchored to"}},
                 "required": ["statement"]}}


def _data_table(doc_keys):
    return {"type": "object", "properties": {
        "title": _STR,
        "columns": _STRS,
        "rows": {"type": "array", "items": {"type": "array", "items": _STR}},
        "caption": _STR, "note": _STR,
        "sources": {"type": "array", "items": _source(doc_keys)}},
        "required": ["title", "columns", "rows"]}


def _key_stat():
    return {"type": "object", "properties": {"value": _STR, "label": _STR, "sublabel": _STR},
            "required": ["value", "label"]}


def _process_detail(doc_keys):
    return {"type": "object", "properties": {
        "title": _STR, "body": _STR, "actor": _STR, "system": _STR,
        "sources": {"type": "array", "items": _source(doc_keys)}},
        "required": ["title", "body"]}


def _step(doc_keys):
    return {"type": "object", "properties": {
        "seq": {"type": "integer", "minimum": 1}, "name": _STR, "actor": _STR, "system": _STR,
        "description": _STR, "failure_points": _STRS,
        "sources": {"type": "array", "items": _source(doc_keys)}},
        "required": ["seq", "name", "description"]}


# ── per-report emit schemas (each scoped to the fields that report owns) ────────────────────────
def _r01_schema(doc_keys):
    return {"type": "object", "properties": {"current_state": {"type": "object", "properties": {
        "domain_overview": _STR, "process_summary": _STR,
        "process_flow": {"type": "array", "minItems": 3, "items": _step(doc_keys)},
        "baseline_stats": {"type": "array", "items": _key_stat()},
        "data_tables": {"type": "array", "items": _data_table(doc_keys),
                        "description": "the grounded factual tables (channel mix, lead times, credit "
                                       "bands, collections ladder, connection inventory, top "
                                       "accounts, systems) — restate values VERBATIM from sources"},
        "process_detail": {"type": "array", "items": _process_detail(doc_keys),
                           "description": "one entry per process stage — how it runs today"},
        "process_inventory": {"type": "array", "items": {"type": "object", "properties": {
            "name": _STR, "purpose": _STR}, "required": ["name"]}},
        "ownership_map": {"type": "array", "items": {"type": "object", "properties": {
            "activity": _STR, "responsible": _STR, "accountable": _STR}, "required": ["activity"]}},
        "system_inventory": {"type": "array", "items": {"type": "object", "properties": {
            "name": _STR, "role": _STR, "system_of_record_for": _STR}, "required": ["name"]}},
        "system_profiles": {"type": "array", "items": {"type": "object", "properties": {
            "name": _STR, "role": _STR, "how_used": _STR, "owners": _STR, "limitations": _STR},
            "required": ["name"]}},
        "format_taxonomy": {"type": "array", "items": {"type": "object", "properties": {
            "label": _STR, "description": _STR, "examples": _STR}, "required": ["label"]}},
        "handoff_catalogue": {"type": "array", "items": {"type": "object", "properties": {
            "from_step": _STR, "to_step": _STR, "mechanism": _STR},
            "required": ["from_step", "to_step"]}},
        "bounded_contexts": {"type": "array", "description": "a Domain-Driven-Design view of the "
            "domain: each subdomain as a bounded context, classified and owned, with its "
            "relationships to other contexts. Derive ONLY from the documents — name the real "
            "subdomains, owners and systems; do not invent. Omit if the documents don't support it.",
            "items": {"type": "object", "properties": {
                "name": _STR,
                "kind": {"type": "string", "enum": ["core", "supporting", "generic", "external"],
                         "description": "core = differentiating; supporting = enabling; generic = "
                                        "commodity; external = outside the org / a TSA / a partner"},
                "owner": _STR,
                "responsibilities": _STR,
                "is_shared_kernel": {"type": "boolean", "description": "true only for the single "
                                     "authoritative system-of-record shared across contexts"},
                "relationships": {"type": "array", "items": {"type": "object", "properties": {
                    "to": _STR,
                    "kind": {"type": "string", "enum": [
                        "customer_supplier", "conformist", "anti_corruption_layer",
                        "open_host_service", "shared_kernel", "partnership"]},
                    "label": _STR}, "required": ["to", "kind"]}}},
                "required": ["name", "kind"]}}},
        "required": ["domain_overview", "process_summary", "process_flow"]},
        "planning_assumptions": _PLANNING}}


def _r02_schema(doc_keys):
    src = _source(doc_keys)
    pp = {"type": "object", "properties": {
        "id": {"type": "string", "pattern": r"^PP\d+$"}, "title": _STR,
        "impact_rank": {"type": "integer", "minimum": 1, "maximum": 8},
        "from_finding": _STR, "description": _STR, "root_cause": _STR, "failure_pattern": _STR,
        "business_consequence": _STR, "category": _STR,
        "severity": {"type": "string", "enum": ["high", "medium", "lower"]},
        "quantified": {"type": "array", "items": _NUMBER_REF},
        "detail_table": _data_table(doc_keys),
        "sources": {"type": "array", "minItems": 1, "items": src}},
        "required": ["id", "title", "impact_rank", "description", "root_cause"]}
    return {"type": "object", "properties": {
        "pain_points": {"type": "array", "minItems": 1, "maxItems": 8, "items": pp},
        "cross_process_patterns": {"type": "array", "items": {"type": "object", "properties": {
            "pattern": _STR, "description": _STR}, "required": ["pattern", "description"]}},
        "evidence_register": {"type": "array", "items": {"type": "object", "properties": {
            "finding": _STR, "source": _STR, "evidence_type": _STR, "data_point": _STR,
            "confidence": {"type": "string", "enum": ["Verified", "Amber", "Gap"]}},
            "required": ["finding", "source"]}},
        "planning_assumptions": _PLANNING}, "required": ["pain_points"]}


def _r03_schema(doc_keys):
    return {"type": "object", "properties": {
        "transformation": {"type": "object", "properties": {
            "sequencing_rationale": _STR, "strategic_readiness": _STR, "dependency_notes": _STR},
            "required": ["sequencing_rationale", "strategic_readiness"]},
        "target_state": _STR,
        "metrics_framework": {"type": "array", "minItems": 3, "items": {"type": "object",
            "properties": {"name": _STR, "definition": _STR, "target": _STR},
            "required": ["name", "definition", "target"]}},
        "risk_register": {"type": "array", "items": {"type": "object", "properties": {
            "risk": _STR, "likelihood": {"type": "string", "enum": ["High", "Medium", "Low"]},
            "impact": {"type": "string", "enum": ["High", "Medium", "Low"]},
            "mitigation": _STR, "owner": _STR}, "required": ["risk"]}},
        "traceability": {"type": "array", "items": {"type": "object", "properties": {
            "pain_point": _STR, "summary": _STR, "severity": _STR, "recommendation": _STR,
            "opportunity": _STR, "expected_outcome": _STR, "horizon": _STR},
            "required": ["pain_point"]}},
        "planning_assumptions": _PLANNING},
        "required": ["transformation", "metrics_framework"]}


def _r05_schema(doc_keys):
    roaditem = {"type": "object", "properties": {
        "title": _STR, "rationale": _STR, "opportunity_id": _STR, "depends_on": _STRS},
        "required": ["title", "rationale"]}
    return {"type": "object", "properties": {
        "roadmap": {"type": "array", "minItems": 3, "maxItems": 3, "items": {"type": "object",
            "properties": {
                "horizon": {"type": "string", "enum": ["H1", "H2", "H3"]},
                "window": _STR, "theme": _STR,
                "items": {"type": "array", "minItems": 1, "items": roaditem}},
            "required": ["horizon", "window", "theme", "items"]}},
        "strategy_profile": {"type": "object", "properties": {"posture": _STR, "notes": _STR}},
        "planning_assumptions": _PLANNING},
        "required": ["roadmap"]}


def _r00_schema(doc_keys):
    return {"type": "object", "properties": {
        "executive_summary": {"type": "object", "properties": {
            "headline": _STR, "situation": _STR, "opportunity": _STR},
            "required": ["headline", "situation", "opportunity"]},
        "planning_assumptions": _PLANNING},
        "required": ["executive_summary"]}


def _opp_schema(doc_keys):
    src = _source(doc_keys)
    return {"type": "object", "properties": {
        "id": {"type": "string", "pattern": r"^OPP\d+$"}, "title": _STR,
        "pattern": {"type": "string", "enum": ["hitl_workflow", "automation", "ai_agent",
                                               "modernisation"]},
        "overview": _STR,
        "before_process": {"type": "array", "minItems": 2, "items": _step(doc_keys)},
        "after_process": {"type": "array", "minItems": 2, "items": _step(doc_keys)},
        "business_impact": {"type": "object", "properties": {
            "narrative": _STR, "quantified": {"type": "array", "items": _NUMBER_REF},
            "derivation": _STR}, "required": ["narrative"]},
        "implementation_approach": _STR, "personas": _STRS, "expected_behaviour": _STR,
        "escalation": _STR, "knowledge_sources": _STRS, "document_formats": _STRS,
        "data_readiness": _STR, "technical_complexity": _STR, "operational_readiness": _STR,
        "required_integrations": _STRS, "success_metrics": _STRS,
        "dependencies": {"type": "array", "items": {"type": "string", "pattern": r"^OPP\d+$"}},
        "risks": _STRS,
        "value_rating": {"type": "string", "enum": ["high", "medium", "low"]},
        "feasibility_rating": {"type": "string", "enum": ["high", "medium", "low"]},
        "value_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "feasibility_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "matrix_quadrant": {"type": "string",
                            "enum": ["do_first", "plan_for", "consider", "deprioritise"]},
        "sources": {"type": "array", "minItems": 1, "items": src},
        "planning_assumptions": _PLANNING},
        "required": ["id", "title", "pattern", "overview", "before_process", "after_process",
                     "business_impact"]}


# ── the per-report spec registry the orchestrator consumes ──────────────────────────────────────
def report_specs(doc_keys) -> dict:
    dk = list(doc_keys)
    return {
        "00-executive-summary": {
            "tool": "emit_exec", "schema": _r00_schema(dk),
            "instruction": "Write the executive summary: a headline (the single most important "
                           "finding), the situation in a nutshell, and where the value is / what to "
                           "do first. Business language; only verified numbers."},
        "01-current-state": {
            "tool": "emit_current_state", "schema": _r01_schema(dk), "max_tokens": 12000,
            "instruction": "Document the FACTUAL current state at reference depth: domain overview + "
                           "process summary; the end-to-end process_flow (≥3 steps, actor+system "
                           "each); baseline_stats tiles; the grounded data_tables you can build from "
                           "the facts (channel mix, lead times, credit bands, collections ladder, "
                           "connection inventory, top accounts, systems — restate values VERBATIM "
                           "from the sources, cite each); process_detail per stage; ownership_map "
                           "(RACI); system_inventory; system_profiles; format_taxonomy; "
                           "handoff_catalogue. STATE FACTS ONLY — no diagnostic words (risk, gap, "
                           "breach, conflict, critical). Omit a table/section the facts cannot fill."},
        "02-pain-points": {
            "tool": "emit_pain_points", "schema": _r02_schema(dk), "max_tokens": 10000,
            "instruction": "Document the pain points found, ranked by impact: each with id (PP1…), "
                           "title, severity (high|medium|lower), category, description, root_cause, "
                           "failure_pattern, business_consequence, quantified figures (verified "
                           "numbers only), and a grounded detail_table where the facts support one "
                           "(e.g. a discrepancy register). Add cross_process_patterns and an "
                           "evidence_register (finding → source → data point/quote → confidence)."},
        "03-recommendation": {
            "tool": "emit_recommendation", "schema": _r03_schema(dk), "max_tokens": 9000,
            "instruction": "Write the transformation recommendation shaped by the STRATEGY: "
                           "sequencing_rationale, strategic_readiness, dependency_notes; a "
                           "target_state narrative; a metrics_framework (name/definition/directional "
                           "target — no invented numbers); a risk_register (risk, likelihood, "
                           "impact, mitigation, owner-by-ROLE — ratings/owners are planning "
                           "assumptions); and a traceability matrix (pain point → recommendation → "
                           "opportunity → outcome → horizon)."},
        "04-opportunity-portfolio": {
            "tool": "emit_portfolio", "opp_schema": _opp_schema(dk), "opp_max_tokens": 8000,
            "schema": {"type": "object", "properties": {}},          # opportunities come per-seed
            "instruction": ""},
        "05-roadmap": {
            "tool": "emit_roadmap", "schema": _r05_schema(dk), "max_tokens": 7000,
            "instruction": "Sequence the opportunities across three horizons (H1 0-6 / H2 6-18 / "
                           "H3 18+), shaped by the STRATEGY direction and horizon. Each horizon: "
                           "window, theme, items (title, rationale, opportunity_id where it maps a "
                           "portfolio item, depends_on). Specific dates/durations are planning "
                           "assumptions. Set strategy_profile.posture."},
    }


def opp_seeds_from_pain_points(payload: dict) -> list[dict]:
    """One opportunity to expand per pain point (the portfolio addresses each PP). Derives a topic
    from the PP title so each opportunity is fed its relevant fact slice."""
    seeds = []
    for i, pp in enumerate(payload.get("pain_points", []), start=1):
        title = pp.get("title", "")
        topic = " ".join(w for w in title.split() if len(w) > 4)[:40]
        seeds.append({"id": f"OPP{i}", "title": f"Address: {title}", "topic": topic})
    return seeds


def run_report_fanout(llm, raw_payload: dict, reg: dict, strategy: StrategyProfile | None = None,
                      doc_keys=None, model=None):
    """Top-level live deep synthesis: build the grounded fact-store, fan out per report, expand one
    opportunity per pain point, and return (merged_payload, planning, fact_store, strategy, omitted).
    `omitted` lists the section labels that could not be produced (transient/grounding failures) so
    the caller can warn or, on --save-golden, refuse a short deliverable. The caller maps
    merged_payload via build._from_payload and attaches fact_store/strategy/planning."""
    from .synthesis import allowed_numbers
    fs = factstore.build_fact_store(raw_payload, reg)
    strat = strategy or factstore.strategy_from_manifest(reg.get("manifest"))
    dk = set(doc_keys or (reg.get("csv_ids", []) + reg.get("doc_ids", [])))
    specs = report_specs(dk)
    # the AUTHORITATIVE grounding allow-list for this run (tool numbers + finding values + derived
    # ratios) — same source the monolith gate uses; the fact-store slice only shapes the prompt.
    allow = allowed_numbers(raw_payload)
    # first pass for the pain points (report 02) so we can seed one opportunity per pain point.
    # This MUST precede seed derivation — it is the one hard barrier in the fan-out (the full pass
    # below parallelises everything after it). The pre-pass's own omissions don't matter (02 is
    # re-run in the full pass and folded with first-write-wins below), so we ignore them here.
    pp_only, _, _ = run_synthesis_fanout(llm, fs, strat, dk, allow=allow,
                                         report_specs={"02-pain-points": specs["02-pain-points"]})
    seeds = opp_seeds_from_pain_points(pp_only)
    merged, planning, omitted = run_synthesis_fanout(
        llm, fs, strat, dk, allow=allow, report_specs=specs, opp_seeds=seeds)
    # fold the first-pass pain points in (report_specs ran them again in the full pass too; merge
    # keeps the first, so they are consistent)
    for k, v in pp_only.items():
        merged.setdefault(k, v)
    return merged, planning, fs, strat, omitted
