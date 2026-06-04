"""Build a grounded FactStore (the KG-lite) from a discovery run + the registered sources.

This is the Block-1+2 output the per-report synthesis fan-out expands from — it replaces the flat
"~3 findings" waist with a structured, sourced collection of measured numbers, verbatim document
quotes, typed entities (accounts / systems / connections with field-level attributes), and
relations. Everything carries its source(s) + confidence tier.

GENERIC by construction: facts are derived from whatever findings + CSV columns + narrative text a
domain provides. No domain constants — a thinner domain simply yields fewer facts. Deterministic:
ordering is stable and row harvesting is capped + sorted, so a golden replay is byte-stable.
"""
from __future__ import annotations

from . import docnames, tools
from .models import DocQuote, EntityFact, FactStore, QuantFact, Relation, StrategyProfile

# how many entity rows to harvest per CSV (deterministic cap — the reports surface the top accounts,
# not every row; full data lives in the source pages / provenance).
_ENTITY_CAP = 12
# relation keywords a finding/handoff may carry (generic, not domain-specific)
_REL_KINDS = ("handoff", "conflict", "owns", "runs on", "triggers", "depends")


def build_fact_store(raw_payload: dict, reg: dict) -> FactStore:
    """Assemble the grounded fact-store from the run's findings + the registered sources."""
    fs = FactStore()
    _harvest_quants_and_quotes(raw_payload, fs)
    _harvest_entities(reg, fs)
    _harvest_relations(raw_payload, fs)
    return fs


# ── measured numbers + verbatim quotes (from the findings the tools already grounded) ───────────
def _harvest_quants_and_quotes(raw_payload: dict, fs: FactStore) -> None:
    seen_q: set[tuple] = set()
    seen_quote: set[tuple] = set()
    for f in raw_payload.get("findings", []):
        tier = _tier(f)
        srcs = sorted({docnames.stem(s.get("doc_id", "")) for s in f.get("sources", [])
                       if s.get("doc_id")})
        for cv in f.get("computed_values", []):
            label, val = str(cv.get("label", "")).strip(), cv.get("value")
            num = _num(val)
            if num is None or not label:
                continue
            key = (label.lower(), round(num, 4))
            if key in seen_q:
                continue
            seen_q.add(key)
            fs.quant.append(QuantFact(label=label, value=num, unit=_unit_of(label),
                                      sources=srcs, tier=tier))
        for nv in f.get("narrative_values", []):
            quote, doc = str(nv.get("quote", "")).strip(), docnames.stem(nv.get("doc_id", ""))
            if not quote or not doc:
                continue
            key = (doc, quote[:60].lower())
            if key in seen_quote:
                continue
            seen_quote.add(key)
            fs.quotes.append(DocQuote(text=quote, doc_id=doc,
                                      locator=str(nv.get("label", "")), tier=tier))
        for s in f.get("sources", []):
            quote, doc = str(s.get("quote", "")).strip(), docnames.stem(s.get("doc_id", ""))
            if not quote or not doc:
                continue
            key = (doc, quote[:60].lower())
            if key in seen_quote:
                continue
            seen_quote.add(key)
            fs.quotes.append(DocQuote(text=quote, doc_id=doc,
                                      locator=str(s.get("locator", "")), tier=tier))


# ── typed entities (one per CSV row, generic name + attributes derived from the columns) ─────────
def _harvest_entities(reg: dict, fs: FactStore) -> None:
    for csv_id in sorted(reg.get("csv_ids", [])):
        path = tools.FILE_REGISTRY.get(csv_id)
        if path is None:
            continue
        try:
            cols, rows = tools._read_rows(path)
        except (OSError, ValueError):
            continue
        if not cols or not rows:
            continue
        kind = _entity_kind(csv_id)
        name_col = _name_column(cols)
        # keep a deterministic, capped slice (rows are already in file order)
        for r in rows[:_ENTITY_CAP]:
            name = str(r.get(name_col, "")).strip() if name_col else ""
            if not name:
                continue
            attrs = {c: str(r.get(c, "")).strip() for c in cols
                     if c != name_col and str(r.get(c, "")).strip()}
            fs.entities.append(EntityFact(kind=kind, name=name, attributes=attrs,
                                          sources=[csv_id], tier="verified"))


# ── relations (from handoff/conflict-flavoured findings) ─────────────────────────────────────────
def _harvest_relations(raw_payload: dict, fs: FactStore) -> None:
    seen: set[tuple] = set()
    for f in raw_payload.get("findings", []):
        blob = (str(f.get("title", "")) + " " + str(f.get("description", ""))).lower()
        kind = next((k.replace(" ", "_") for k in _REL_KINDS if k in blob), "")
        if not kind:
            continue
        srcs = sorted({docnames.stem(s.get("doc_id", "")) for s in f.get("sources", [])
                       if s.get("doc_id")})
        rel = Relation(src=str(f.get("id", "")), kind=kind, dst=str(f.get("title", ""))[:60],
                       sources=srcs)
        key = (rel.src, rel.kind)
        if key in seen:
            continue
        seen.add(key)
        fs.relations.append(rel)


# ── StrategyProfile from the domain manifest (neutral default when none declared) ────────────────
def strategy_from_manifest(manifest: dict | None) -> StrategyProfile:
    s = (manifest or {}).get("strategy_profile") or {}
    return StrategyProfile(
        direction_type=str(s.get("direction_type", "")),
        horizon=str(s.get("horizon", "")),
        strategic_constraints=str(s.get("strategic_constraints", "")),
        stakeholder_priorities=list(s.get("stakeholder_priorities", []) or []),
        out_of_scope=str(s.get("out_of_scope", "")),
        success_definition=str(s.get("success_definition", "")))


# ── helpers ──────────────────────────────────────────────────────────────────────────────────────
def _num(v) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _tier(f: dict) -> str:
    c = str(f.get("confidence", "")).lower()
    if c in ("verified", "amber", "gap"):
        return c
    # an adversarially-challenged finding is at most amber
    if f.get("verification", {}).get("supported") is False:
        return "amber"
    return "verified"


def _unit_of(label: str) -> str:
    lo = label.lower()
    # a COUNT-of-things label wins over the field name it counts ("Accounts with mismatched
    # credit_limit_eur" is a count of accounts, not a EUR amount).
    if lo.startswith("account") or "accounts with" in lo or "number of account" in lo:
        return "accounts"
    if "pct" in lo or "percent" in lo or "%" in label or " rate" in lo or "share" in lo:
        return "percent"
    if "escalation" in lo or "incident" in lo or "case" in lo:
        return "escalations"
    if "eur" in lo or "€" in label or "overstatement" in lo or "limit" in lo or "value" in lo:
        return "eur"
    if "account" in lo:
        return "accounts"
    return "count"


def _entity_kind(csv_id: str) -> str:
    """Derive a generic entity kind from the filename (no domain constants). Check the more specific
    signals (escalation/incident log, connection register) before the broad 'customer/master' one,
    so a 'customer-service-escalation-log' is an incident, not an account."""
    lo = csv_id.lower()
    if "escalation" in lo or "incident" in lo or "ticket" in lo or "log" in lo:
        return "incident"
    if "connection" in lo or "integration" in lo or "edi" in lo:
        return "connection"
    if "order" in lo or "flow" in lo or "transaction" in lo:
        return "transaction"
    if "customer" in lo or "account" in lo or "master" in lo or "crm" in lo:
        return "account"
    return "record"


def _name_column(cols: list[str]) -> str:
    """Pick the most name-like column generically: prefer a 'name', else an 'id', else the first."""
    lowered = [(c, c.lower()) for c in cols]
    for c, lo in lowered:
        if lo.endswith("name") or lo == "name" or "customer_name" in lo:
            return c
    for c, lo in lowered:
        if lo.endswith("_id") or lo == "id":
            return c
    return cols[0] if cols else ""
