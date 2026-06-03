"""Deterministic fallback — the "tell" to the agent loop's "show".

Runs the SAME generic tools as the agent would, in a fixed trajectory with fixed args, then makes
ONE tool-free LLM call to write the 3 findings from the pre-computed facts. Because it calls the
identical tool functions on identical bytes, every number (€600K, 307, 67.3%, 5667, 34, 6/14) is
byte-identical to the agent path. This is NOT fabrication: the numbers are still computed from the
data by the same tools; only the orchestration is fixed instead of model-chosen.

Used when --scripted is passed, or automatically when the agent loop fails (budget/LLM/grounding).
"""
from __future__ import annotations

import json
import textwrap

from . import tools
from .llm import LLMClient


def gather_facts() -> dict:
    """Run the pinned tool trajectory. Pure tool calls — no LLM, fully deterministic."""
    facts = {}
    # F1 — customer master conflict
    facts["customer_master_diff"] = tools.join_diff(
        "sap-s4-customer-master-export", "sap-crm-customer-export", "customer_id",
        ["credit_limit_eur", "payment_terms"], rank_by="credit_limit_eur",
        context_cols_a=["migration_source"], context_cols_b=["source"], top_n=5,
    )
    # F2 — channel share + RACI exclusion quote
    facts["channel_share"] = tools.group_by(
        "order-flow-analysis-export-2025", ["channel"], "count")
    facts["channel_share_by_value"] = tools.group_by(
        "order-flow-analysis-export-2025", ["channel"], "sum", "order_value_eur")
    facts["raci_edi_mentions"] = tools.find_mentions(
        "o2c-process-raci-opella-europe",
        ["EDI", "EDI channel process steps are not included", "EDI-related rows excluded",
         "Manual", "Email"])
    # F3 — Sanofi-managed EDI connections + escalation count
    facts["edi_register_mentions"] = tools.find_mentions(
        "edi-integration-register-opella-europe",
        ["All 14 active", "Carrefour France", "Boots UK", "dm", "E.Leclerc", "Lidl", "Coop",
         "Sanofi", "6 remaining", "connections 9-14"])
    facts["cs_notes_mentions"] = tools.find_mentions(
        "edi-dispute-resolution-cs-working-notes",
        ["Carrefour France", "Boots UK", "dm", "E.Leclerc", "Lidl", "Coop", "Sanofi", "TSA"])
    facts["edi_escalations"] = tools.filter_count(
        "customer-service-escalation-log-2025",
        {"col": "root_cause", "op": "contains", "value": "EDI order not processed"})
    return facts


SYNTH_SYSTEM = textwrap.dedent("""\
    You are an enterprise process-discovery analyst. You are given FACTS already computed by
    deterministic tools over a company's Order-to-Cash documents (system exports + policies). Write
    exactly 3 findings. Use ONLY the numbers present in the facts — do not invent or recompute any
    number. Each finding needs >=2 distinct source documents. Output strictly valid JSON matching
    the schema. No prose outside the JSON.
""")


def scripted_plan(llm: LLMClient, narrative_text: str, model: str | None = None) -> dict:
    facts = gather_facts()
    schema_hint = textwrap.dedent("""\
        JSON schema (exactly 3 findings, ids F1/F2/F3):
        {"findings":[{"id","title","severity":high|amber|info,"confidence":verified|amber|gap,
          "description","business_consequence",
          "computed_values":[{"label","value":number,"from_tool"}],
          "narrative_values":[{"label","value","doc_id","quote"}],
          "sources":[{"doc_id","locator","quote"}]}]}
    """)
    prompt = (
        f"{schema_hint}\n\nFACTS (computed by tools — use these numbers verbatim):\n"
        f"{json.dumps(facts, indent=2, ensure_ascii=False)}\n\n"
        "Guidance: F1 = customer master ERP-vs-CRM conflict (cite matched/differ counts and the "
        "largest single delta, FR001). F2 = EDI share of order volume vs the RACI excluding EDI "
        "(cite pct_of_rows for EDI). F3 = the six Sanofi-managed EDI connections (strategic tension, "
        "non-blocking) plus the count of 'EDI order not processed' escalations. Label the escalation "
        "count precisely as 'EDI order not processed escalations', not 'EDI incidents'."
    )
    result = llm.complete_json(SYNTH_SYSTEM, prompt, model=model)
    payload: dict = result if isinstance(result, dict) else {}
    # attach the raw facts so the report/citation layer and a grounding check can use them
    payload["_facts"] = facts
    return payload
