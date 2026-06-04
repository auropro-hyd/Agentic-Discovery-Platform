"""Phase 0 — the grounded fact-store (discovery/factstore.py).

Drives the deterministic builders on the real o2c golden payload and on synthetic edge payloads, so
every branch (unit/kind classification, dedup, empty-source, relation detection, manifest strategy)
is covered without an LLM or live spend.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import factstore, registry  # noqa: E402
from discovery import models as m  # noqa: E402
from discovery.factstore import _clean_quote, _entity_kind, _name_column, _unit_of  # noqa: E402


@pytest.fixture(scope="module")
def raw_o2c():
    p = ROOT / "out" / "discovery-o2c.json"
    if not p.exists():
        pytest.skip("run `python run.py --domain o2c --golden` first")
    return json.load(open(p))["internal_trace"]


@pytest.fixture(scope="module")
def reg_o2c():
    return registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)


def test_fact_store_grounds_the_expected_facts(raw_o2c, reg_o2c):
    fs = factstore.build_fact_store(raw_o2c, reg_o2c)
    # measured numbers harvested from findings' computed_values. 267 (account mismatch count) and
    # 30,675,000 (aggregate EUR divergence) are the core join_diff facts that survive every bake;
    # we assert on those durable values, not bake-specific magic numbers.
    vals = {round(q.value, 4) for q in fs.quant}
    assert 267.0 in vals and 30675000.0 in vals
    # the account-count label is classified as accounts, not eur, despite naming 'credit_limit_eur'
    q267 = next(q for q in fs.quant if q.value == 267)
    assert q267.unit == "accounts"
    # verbatim quotes harvested
    assert fs.quotes and any("authoritative" in d.text.lower() for d in fs.quotes)
    # and NO raw tool-output jargon leaks into any harvested quote (the _clean_quote guard)
    assert not any("n_mismatch" in d.text or "sum_delta" in d.text or "from_tool" in d.text
                   for d in fs.quotes)
    # typed entities with field-level attributes; the escalation log is an incident, not an account
    kinds = {e.kind for e in fs.entities}
    assert "account" in kinds and "incident" in kinds
    acct = next(e for e in fs.entities if e.kind == "account")
    assert acct.name and acct.attributes        # has a name + attributes
    # allow-list and slicing
    assert fs.numbers_allow() >= {267.0, 30675000.0}
    credit = fs.slice_for("credit", "limit")
    assert credit.quant and all("credit" in q.label.lower() or "limit" in q.label.lower()
                                for q in credit.quant)
    # the full to_dict round-trips
    d = fs.to_dict()
    assert set(d) == {"quant", "quotes", "entities", "relations"}


def test_slice_for_empty_terms_returns_whole_store():
    fs = m.FactStore(quant=[m.QuantFact("x", 1)], quotes=[m.DocQuote("q", "d")])
    assert fs.slice_for() is fs                  # no terms -> identity
    assert fs.slice_for("nomatch").quant == []   # no hit -> empty


def test_relations_from_handoff_or_conflict_findings():
    raw = {"findings": [
        {"id": "F1", "title": "Two systems conflict on credit", "description": "x",
         "sources": [{"doc_id": "a.csv"}], "computed_values": [], "narrative_values": []},
        {"id": "F2", "title": "Order handoff to fulfilment", "description": "y",
         "sources": [], "computed_values": [], "narrative_values": []},
        {"id": "F3", "title": "Nothing relational here", "description": "z",
         "sources": [], "computed_values": [], "narrative_values": []}]}
    fs = factstore.build_fact_store(raw, {"csv_ids": []})
    kinds = {r.kind for r in fs.relations}
    assert "conflict" in kinds and "handoff" in kinds   # F1, F2 detected; F3 not
    assert all(r.kind != "" for r in fs.relations)


def test_dedup_quants_and_quotes():
    raw = {"findings": [
        {"id": "F1", "title": "t", "description": "d", "sources": [
            {"doc_id": "x.csv", "quote": "same quote here", "locator": "L1"}],
         "computed_values": [{"label": "A count", "value": 5},
                             {"label": "A count", "value": 5}],   # duplicate -> 1
         "narrative_values": [{"doc_id": "x.csv", "quote": "same quote here", "label": "n"}]}]}
    fs = factstore.build_fact_store(raw, {"csv_ids": []})
    assert len([q for q in fs.quant if q.value == 5]) == 1        # quant dedup
    assert len([d for d in fs.quotes if d.text == "same quote here"]) == 1  # quote dedup across nv+src


def test_tier_downgrades_challenged_finding():
    raw = {"findings": [
        {"id": "F1", "title": "t", "description": "d", "sources": [{"doc_id": "x.csv"}],
         "computed_values": [{"label": "n", "value": 9}], "narrative_values": [],
         "verification": {"supported": False}}]}
    fs = factstore.build_fact_store(raw, {"csv_ids": []})
    assert fs.quant[0].tier == "amber"           # challenged -> at most amber
    # explicit confidence wins
    raw["findings"][0]["confidence"] = "gap"
    assert factstore.build_fact_store(raw, {"csv_ids": []}).quant[0].tier == "gap"


def test_entities_skip_unreadable_or_empty(tmp_path):
    from discovery import tools
    # an empty CSV (header only) yields no entities; a phantom id is skipped
    empty = tmp_path / "empty-account-export.csv"
    empty.write_text("customer_name,country\n", encoding="utf-8")
    tools.FILE_REGISTRY["empty-account-export"] = empty
    try:
        fs = factstore.build_fact_store({"findings": []},
                                        {"csv_ids": ["empty-account-export", "phantom-id"]})
    finally:
        del tools.FILE_REGISTRY["empty-account-export"]
    assert fs.entities == []                      # empty file + missing path both skip cleanly


def test_unit_classification():
    assert _unit_of("Accounts with mismatched credit_limit_eur") == "accounts"
    assert _unit_of("EDI share of orders (pct)") == "percent"
    assert _unit_of("EDI-not-processed escalations") == "escalations"
    assert _unit_of("Aggregate divergence (EUR)") == "eur"
    assert _unit_of("active account count") == "accounts"
    assert _unit_of("number of widgets") == "count"


def test_entity_kind_classification():
    assert _entity_kind("customer-service-escalation-log-2025") == "incident"
    assert _entity_kind("edi-connection-register") == "connection"
    assert _entity_kind("order-flow-analysis-export-2025") == "transaction"
    assert _entity_kind("sap-s4-customer-master-export") == "account"
    assert _entity_kind("misc-reference-sheet") == "record"


def test_name_column_pick():
    assert _name_column(["customer_name", "country"]) == "customer_name"
    assert _name_column(["region", "customer_id", "x"]) == "customer_id"
    assert _name_column(["alpha", "beta"]) == "alpha"
    assert _name_column([]) == ""


def test_clean_quote_strips_tool_jargon():
    # a quote that is ONLY raw tool-output keys + numbers is dropped (no prose meaning of its own)
    assert _clean_quote("n_mismatch 267; sum_delta 30675000.0") == ""
    # a real prose quote is left exactly as-is (no jargon token present -> early return)
    prose = "EDI is the sole authoritative system of record for credit limits."
    assert _clean_quote(prose) == prose
    # jargon embedded in prose: the token is removed, the human words survive
    assert _clean_quote("from_tool join_diff produced 267 mismatches") == "produced 267 mismatches"
    # a JSON-ish dump loses braces/quotes and orphaned separators collapse (no "': :'")
    assert _clean_quote('{"col": {"n_mismatch": 267, "sum_delta": 5.0}}') == "col: 267: 5.0"
    # empty / whitespace-only -> empty
    assert _clean_quote("   ") == ""


def test_harvest_drops_quote_that_is_only_tool_jargon():
    """End-to-end: a finding whose narrative quote is a raw tool-output dump yields NO DocQuote, so
    internal field names (n_mismatch / sum_delta) can never reach a client-facing brief."""
    raw = {"findings": [{
        "id": "F1", "confidence": "verified",
        "sources": [{"doc_id": "sap-s4-customer-master-export"}],
        "narrative_values": [
            {"quote": "n_mismatch 267; sum_delta 30675000.0", "doc_id": "sap-s4-customer-master-export"},
            {"quote": "EDI is the sole authoritative system of record.",
             "doc_id": "credit-management-policy-opella-europe"},
        ],
    }]}
    fs = factstore.build_fact_store(raw, {"csv_ids": []})
    texts = [q.text for q in fs.quotes]
    assert "EDI is the sole authoritative system of record." in texts
    assert not any("n_mismatch" in t or "sum_delta" in t for t in texts)


def test_strategy_from_manifest():
    neutral = factstore.strategy_from_manifest(None)
    assert neutral.brief() == "" and neutral.direction_type == ""
    s = factstore.strategy_from_manifest({"strategy_profile": {
        "direction_type": "consolidate", "horizon": "0-6 months",
        "strategic_constraints": "TSA obligations", "stakeholder_priorities": ["time-to-value"],
        "out_of_scope": "no greenfield", "success_definition": "AI live in H1"}})
    assert "consolidate" in s.brief() and "time-to-value" in s.brief() and "greenfield" in s.brief()


def test_strategy_profile_brief_partial():
    assert m.StrategyProfile(direction_type="modernize").brief() == "Direction: modernize"
    assert m.StrategyProfile().brief() == ""


def test_harvest_skips_malformed_values_and_quotes():
    """Non-numeric computed value, empty label, and empty quotes/docs all skip cleanly."""
    raw = {"findings": [{
        "id": "F1", "title": "t", "description": "d",
        "sources": [{"doc_id": "", "quote": "orphan-no-doc"},      # empty doc -> skip
                    {"doc_id": "x.csv", "quote": ""}],              # empty quote -> skip
        "computed_values": [{"label": "Good", "value": 7},
                            {"label": "", "value": 3},             # empty label -> skip
                            {"label": "Bad", "value": "not-a-number"}],  # non-numeric -> skip
        "narrative_values": [{"doc_id": "", "quote": "nv-no-doc"},  # empty doc -> skip
                             {"doc_id": "y.csv", "quote": ""}]}]}   # empty quote -> skip
    fs = factstore.build_fact_store(raw, {"csv_ids": []})
    assert [q.value for q in fs.quant] == [7]                       # only the good one
    assert fs.quotes == []                                          # all quote arms skipped


def test_entity_row_with_blank_name_is_skipped(tmp_path):
    from discovery import tools
    csv = tmp_path / "acct-master.csv"
    csv.write_text("customer_name,country\n,FR\nReal Co,UK\n", encoding="utf-8")  # 1st row blank name
    tools.FILE_REGISTRY["acct-master"] = csv
    try:
        fs = factstore.build_fact_store({"findings": []}, {"csv_ids": ["acct-master"]})
    finally:
        del tools.FILE_REGISTRY["acct-master"]
    assert [e.name for e in fs.entities] == ["Real Co"]             # blank-name row skipped


def test_entity_unreadable_file_is_skipped(tmp_path):
    from discovery import tools
    # register a path that is a directory → _read_rows raises OSError → that csv is skipped
    bad = tmp_path / "a-dir-account"
    bad.mkdir()
    tools.FILE_REGISTRY["a-dir-account"] = bad
    try:
        fs = factstore.build_fact_store({"findings": []}, {"csv_ids": ["a-dir-account"]})
    finally:
        del tools.FILE_REGISTRY["a-dir-account"]
    assert fs.entities == []


def test_factstore_model_to_dict_and_allow_branches():
    fs = m.FactStore(
        quant=[m.QuantFact("a", 5), m.QuantFact("bad", float("nan"))],
        quotes=[m.DocQuote("q", "d", "loc")],
        entities=[m.EntityFact("account", "N", {"k": "v"}, ["s"])],
        relations=[m.Relation("x", "handoff_to", "y", ["s"])])
    # numbers_allow tolerates a NaN/odd value without crashing
    allow = fs.numbers_allow()
    assert 5.0 in allow
    # every member's to_dict round-trips
    d = fs.to_dict()
    assert d["entities"][0]["attributes"] == {"k": "v"}
    assert d["relations"][0]["kind"] == "handoff_to"
    assert d["quotes"][0]["locator"] == "loc"


def test_numbers_allow_skips_non_floatable():
    class Weird:
        def __float__(self):
            raise ValueError("nope")
    fs = m.FactStore(quant=[m.QuantFact("w", Weird()), m.QuantFact("ok", 12)])  # type: ignore[arg-type]
    assert fs.numbers_allow() == {12.0}


def test_narrative_quote_dedup_and_relation_dedup():
    # two narrative_values with the same quote -> deduped (the nv-vs-nv dedup arc);
    # two findings with the same id+relation-kind -> one relation (the relation dedup arc).
    raw = {"findings": [
        {"id": "F1", "title": "systems conflict", "description": "d", "sources": [],
         "computed_values": [],
         "narrative_values": [{"doc_id": "x.csv", "quote": "dup line"},
                              {"doc_id": "x.csv", "quote": "dup line"}]},
        {"id": "F1", "title": "systems conflict again", "description": "d2", "sources": [],
         "computed_values": [], "narrative_values": []}]}
    fs = factstore.build_fact_store(raw, {"csv_ids": []})
    assert len([d for d in fs.quotes if d.text == "dup line"]) == 1
    assert len([r for r in fs.relations if r.src == "F1" and r.kind == "conflict"]) == 1


def test_strategy_and_planning_to_dict():
    assert m.StrategyProfile(direction_type="consolidate").to_dict()["direction_type"] == "consolidate"
    pa = m.PlanningAssumption(statement="Migrate Carrefour first", kind="sequence", basis="register")
    assert pa.to_dict() == {"statement": "Migrate Carrefour first", "kind": "sequence",
                            "basis": "register"}
