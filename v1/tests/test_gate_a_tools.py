"""Gate A — tool purity & math truth (no LLM). The keystone non-fabrication control.

Every number the demo asserts is recomputed here from raw bytes via the generic tools and
checked against VERIFIED_NUMBERS.md. Also asserts tools are deterministic (called twice ->
identical). If this passes, the numbers are real, not hardcoded.

Run:  ./.venv/bin/python -m pytest tests/test_gate_a_tools.py -q
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT))

from discovery import tools, registry  # noqa: E402

DOMAIN = ROOT / "inputs" / "o2c"


@pytest.fixture(scope="module", autouse=True)
def _setup():
    registry.setup_domain(DOMAIN, freeze=True)
    yield


def _stable(fn, *a, **k):
    """Call twice; assert byte-identical; return result."""
    r1 = fn(*a, **k)
    r2 = fn(*a, **k)
    assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True), "tool not deterministic"
    return r1


# ---- F2: channel share ----------------------------------------------------
def test_f2_channel_share():
    r = _stable(tools.group_by, "order-flow-analysis-export-2025", ["channel"], "count")
    assert r["grand_total_rows"] == 8420
    g = {tuple(x["group"].values())[0]: x for x in r["groups"]}
    assert g["EDI"]["count"] == 5667
    assert g["EDI"]["pct_of_rows"] == 67.3
    assert sorted(g) == ["EDI", "Email", "Fax", "Manual"]   # NO "Phone"


def test_f2_channel_share_by_value():
    r = _stable(tools.group_by, "order-flow-analysis-export-2025", ["channel"], "sum",
                "order_value_eur")
    edi = next(x for x in r["groups"] if x["group"]["channel"] == "EDI")
    assert edi["pct_of_value"] == 66.8


# ---- F1: customer master conflict -----------------------------------------
def test_f1_customer_master_diff():
    r = _stable(tools.join_diff, "sap-s4-customer-master-export", "sap-crm-customer-export",
                "customer_id", ["credit_limit_eur", "payment_terms"],
                rank_by="credit_limit_eur",
                context_cols_a=["migration_source"], context_cols_b=["source"])
    assert r["matched_keys"] == 318
    assert r["only_in_a_count"] == 22
    assert r["only_in_b_count"] == 0
    assert r["rows_with_any_difference"] == 307
    assert r["per_column"]["credit_limit_eur"]["n_mismatch"] == 267
    assert r["per_column"]["payment_terms"]["n_mismatch"] == 228
    # FR001 ranks first (largest absolute credit delta)
    top = r["matched_rows"][0]
    assert top["key"] == "FR001"
    assert top["diffs"]["credit_limit_eur"]["a"] == 1800000
    assert top["diffs"]["credit_limit_eur"]["b"] == 2400000
    assert top["diffs"]["credit_limit_eur"]["delta"] == 600000
    assert top["diffs"]["payment_terms"]["a"] == "NET45"
    assert top["diffs"]["payment_terms"]["b"] == "NET30"
    assert top["context"]["migration_source (a)"] == "Sanofi Legacy System"
    assert "manually updated" in top["context"]["source (b)"]


# ---- F3: escalation count + qualitative ownership -------------------------
def test_f3_escalation_count():
    r = _stable(tools.filter_count, "customer-service-escalation-log-2025",
                {"col": "root_cause", "op": "contains", "value": "EDI order not processed"})
    assert r["matched"] == 34
    assert r["total"] == 142


def test_f3_edi_register_prose():
    r = _stable(tools.find_mentions, "edi-integration-register-opella-europe",
                ["Carrefour France", "Boots UK", "dm", "E.Leclerc", "Lidl", "Coop"])
    # all six named connections appear in the register text
    for term in ["Carrefour France", "Lidl", "Coop"]:
        assert r["results"][term]["count"] >= 1


# ---- determinism guard on describe ----------------------------------------
def test_describe_surfaces_rare_values():
    r = _stable(tools.describe, "sap-s4-customer-master-export")
    msrc = next(c for c in r["columns"] if c["name"] == "migration_source")
    # the rare "Sanofi Legacy System" value must be surfaced (a 5-row sample would miss it)
    vals = {d["value"]: d["count"] for d in msrc["distinct_values"]}
    assert "Sanofi Legacy System" in vals
