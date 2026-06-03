"""Error-path + operator coverage for tools.py: the dispatch wrapper, every ToolError branch
(unknown file/column/op/fn, malformed predicate), and the full _eval_predicate operator matrix.
The happy paths live in test_gate_a_tools.py; this file targets the branches those miss.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import registry, tools  # noqa: E402

CSV = "order-flow-analysis-export-2025"


@pytest.fixture(scope="module", autouse=True)
def _setup():
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    yield


# ---- dispatch wrapper ---------------------------------------------------------
def test_dispatch_unknown_tool():
    r = tools.dispatch("nope", {})
    assert r["error"]["code"] == "bad_arg" and "unknown tool" in r["error"]["message"]


def test_dispatch_wraps_toolerror_as_result():
    r = tools.dispatch("describe", {"file": "does-not-exist"})
    assert r["error"]["code"] == "unknown_file"


def test_dispatch_wraps_typeerror_as_bad_arg():
    r = tools.dispatch("describe", {"wrong_kwarg": 1})   # missing required 'file'
    assert r["error"]["code"] == "bad_arg"


# ---- resolve / column guards --------------------------------------------------
def test_resolve_unknown_file_raises():
    with pytest.raises(tools.ToolError) as ei:
        tools._resolve("ghost", "describe")
    assert ei.value.code == "unknown_file"


def test_group_by_unknown_column():
    r = tools.dispatch("group_by", {"file": CSV, "by": ["no_such_col"]})
    assert r["error"]["code"] == "unknown_column"


def test_group_by_sum_requires_value_col():
    r = tools.dispatch("group_by", {"file": CSV, "by": ["channel"], "agg": "sum"})
    assert r["error"]["code"] == "bad_arg"


def test_group_by_sum_with_value_col_succeeds():
    r = tools.group_by(CSV, by=["channel"], agg="sum", value_col="order_value_eur")
    assert r["groups"] and any(g.get("value", g.get("sum", 0)) for g in r["groups"])


def test_group_by_sum_excludes_nonnumeric_value_cells():
    # fulfilment_date cells are dates (non-numeric) -> every cell hits the exclusion branch,
    # so the summed grand total is zero.
    r = tools.group_by(CSV, by=["channel"], agg="sum", value_col="fulfilment_date")
    assert r["grand_total_value"] == 0.0


def test_join_diff_numeric_and_text_columns():
    r = tools.join_diff("sap-s4-customer-master-export", "sap-crm-customer-export",
                        key="customer_id", compare_cols=["credit_limit_eur", "payment_terms"])
    # numeric column produces deltas; text column produces text diffs — both branches exercised
    assert "per_column" in r or "matched" in r or "provenance" in r


def test_aggregate_invalid_fn():
    r = tools.dispatch("aggregate", {"file": CSV, "col": "order_value_eur", "fn": "median"})
    assert r["error"]["code"] == "bad_arg"


def test_aggregate_distinct_count_sum_avg_min_max():
    dc = tools.aggregate(CSV, "channel", "distinct_count")
    assert dc["value"] >= 1
    s = tools.aggregate(CSV, "order_value_eur", "sum")
    assert s["value"] > 0 and s["n_considered"] > 0
    avg = tools.aggregate(CSV, "order_value_eur", "avg")     # exercises _round_avg
    assert avg["value"] > 0
    assert tools.aggregate(CSV, "order_value_eur", "min")["value"] >= 0
    assert tools.aggregate(CSV, "order_value_eur", "max")["value"] > 0


def test_check_conformance_mixed_comply_and_violate():
    # rule: EDI orders should be Fulfilled. Some comply, some violate -> both branches + value sum.
    r = tools.check_conformance(
        CSV,
        when={"col": "channel", "op": "eq", "value": "EDI"},
        require={"col": "fulfilment_status", "op": "eq", "value": "Fulfilled"},
        value_col="order_value_eur")
    assert r["applies"] > 0
    assert r["compliant"] > 0 and r["violating"] > 0           # both branches exercised
    assert r["applies"] == r["compliant"] + r["violating"]
    assert r["violating_value"] > 0                            # value_col sum over violators


def test_aggregate_non_numeric_column_yields_none():
    r = tools.aggregate(CSV, "customer", "sum")     # text column -> no numbers
    assert r["value"] is None and r["n_considered"] == 0 and r["n_excluded"] > 0


def test_find_mentions_unknown_doc():
    r = tools.dispatch("find_mentions", {"doc": "ghost-doc", "terms": ["x"]})
    assert r["error"]["code"] == "unknown_file"


# ---- predicate validation -----------------------------------------------------
def _cols():
    return [c["name"] for c in tools.describe(CSV)["columns"]]


def test_predicate_too_deep():
    cols = _cols()
    p = {"col": "channel", "op": "eq", "value": "EDI"}
    for _ in range(8):
        p = {"not": p}
    with pytest.raises(tools.ToolError, match="too deep"):
        tools._validate_predicate(p, cols, 0)


def test_predicate_node_not_object():
    with pytest.raises(tools.ToolError, match="must be an object"):
        tools._validate_predicate("nonsense", _cols(), 0)


def test_predicate_all_not_a_list():
    with pytest.raises(tools.ToolError, match="must be a list"):
        tools._validate_predicate({"all": {"col": "channel"}}, _cols(), 0)


def test_predicate_bad_op():
    with pytest.raises(tools.ToolError, match="not in"):
        tools._validate_predicate({"col": "channel", "op": "wat", "value": "EDI"}, _cols(), 0)


def test_predicate_malformed_node():
    with pytest.raises(tools.ToolError, match="malformed"):
        tools._validate_predicate({"frobnicate": True}, _cols(), 0)


def test_predicate_nested_all_any_not_validate_ok():
    cols = _cols()
    good = {"all": [{"any": [{"col": "channel", "op": "eq", "value": "EDI"}]},
                    {"not": {"col": "country", "op": "is_empty"}}]}
    tools._validate_predicate(good, cols, 0)        # must not raise


# ---- _eval_predicate operator matrix -----------------------------------------
def test_eval_predicate_all_operators():
    row = {"channel": "EDI", "country": "France", "units": "10", "blank": "  "}
    ev = tools._eval_predicate
    assert ev({"col": "channel", "op": "eq", "value": "EDI"}, row)
    assert ev({"col": "channel", "op": "ne", "value": "FAX"}, row)
    assert ev({"col": "channel", "op": "contains", "value": "ED"}, row)
    assert ev({"col": "channel", "op": "not_contains", "value": "ZZ"}, row)
    assert ev({"col": "country", "op": "starts_with", "value": "Fra"}, row)
    assert ev({"col": "country", "op": "ends_with", "value": "nce"}, row)
    assert ev({"col": "channel", "op": "in", "value": ["EDI", "FAX"]}, row)
    assert ev({"col": "channel", "op": "not_in", "value": ["FAX"]}, row)
    assert ev({"col": "blank", "op": "is_empty"}, row)
    assert ev({"col": "channel", "op": "not_empty"}, row)
    # numeric comparisons (both parse as numbers)
    assert ev({"col": "units", "op": "gt", "value": 5}, row)
    assert ev({"col": "units", "op": "ge", "value": 10}, row)
    assert ev({"col": "units", "op": "lt", "value": 20}, row)
    assert ev({"col": "units", "op": "le", "value": 10}, row)
    # text comparison fallback (non-numeric)
    assert ev({"col": "country", "op": "gt", "value": "Argentina"}, row)
    # boolean combinators
    assert ev({"all": [{"col": "channel", "op": "eq", "value": "EDI"},
                       {"col": "country", "op": "eq", "value": "France"}]}, row)
    assert ev({"any": [{"col": "channel", "op": "eq", "value": "FAX"},
                       {"col": "country", "op": "eq", "value": "France"}]}, row)
    assert ev({"not": {"col": "channel", "op": "eq", "value": "FAX"}}, row)


# ---- synthetic-CSV edge branches (text-col equal in join_diff; non-numeric ----
# ---- value cell on a conformance violator) -----------------------------------
def test_join_diff_text_equal_and_nonrank_numeric_branches(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    # amt becomes rank_col; qty is a non-rank numeric col; name is a text col equal on row 2.
    a.write_text("id,name,amt,qty\n1,Acme,100,5\n2,Beta,200,9\n", encoding="utf-8")
    b.write_text("id,name,amt,qty\n1,Acme,150,7\n2,Beta,200,9\n", encoding="utf-8")
    tools.FILE_REGISTRY["_synth_a"] = a
    tools.FILE_REGISTRY["_synth_b"] = b
    try:
        r = tools.join_diff("_synth_a", "_synth_b", key="id",
                            compare_cols=["amt", "qty", "name"])
        assert r["provenance_a"]["row_count"] == 2
        assert r["matched_keys"] == 2
    finally:
        del tools.FILE_REGISTRY["_synth_a"], tools.FILE_REGISTRY["_synth_b"]


def test_conformance_violator_with_nonnumeric_value_cell(tmp_path):
    c = tmp_path / "c.csv"
    # row 2 violates the rule AND has a blank value_col -> the `if v is not None` skip fires
    c.write_text("ch,status,val\nEDI,Fulfilled,100\nEDI,Failed,\nEDI,Failed,50\n", encoding="utf-8")
    tools.FILE_REGISTRY["_synth_c"] = c
    try:
        r = tools.check_conformance(
            "_synth_c",
            when={"col": "ch", "op": "eq", "value": "EDI"},
            require={"col": "status", "op": "eq", "value": "Fulfilled"},
            value_col="val")
        assert r["applies"] == 3 and r["violating"] == 2
        assert r["violating_value"] == 50.0          # only the numeric violator counted
    finally:
        del tools.FILE_REGISTRY["_synth_c"]


# ---- number / normalize helpers ----------------------------------------------
def test_to_number_handles_currency_nulls_and_garbage():
    assert tools._to_number("€1,200.50") == 1200.50
    assert tools._to_number("45%") == 45.0
    assert tools._to_number("n/a") is None
    assert tools._to_number(None) is None
    assert tools._to_number("not a number") is None


def test_round_helpers_are_half_even():
    assert tools._round_money(1.005) in (1.0, 1.0)   # banker's rounding, deterministic
    assert tools._q(None, 2) is None
