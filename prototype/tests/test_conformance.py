"""Validates the SOP-conformance tool (the 'to-be model vs. actual data' diff) against the P2P
purchase-order data ground truth. No LLM — pure tool math, like Gate A."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import tools, registry  # noqa: E402

DOMAIN = ROOT / "inputs" / "p2p"


@pytest.fixture(scope="module", autouse=True)
def _setup():
    registry.setup_domain(DOMAIN, freeze=False)
    yield


def test_conformance_dual_approval_rule():
    """Policy: orders above EUR 50,000 must be dual-approved. 7 violate, EUR 557,000 at risk."""
    r = tools.check_conformance(
        "purchase-order-export",
        when={"col": "amount_eur", "op": "gt", "value": 50000},
        require={"col": "approval_status", "op": "eq", "value": "approved"},
        value_col="amount_eur")
    assert r["violating"] == 7
    assert r["violating_value"] == 557000
    assert r["compliant"] == 6          # the legitimately-large, properly-approved decoys
    assert 0 < r["compliance_rate_pct"] < 100


def test_conformance_po_first_rule():
    """Policy: every order must have a PO raised first. 3 violate (maverick), EUR 216,000."""
    r = tools.check_conformance(
        "purchase-order-export",
        when={"col": "po_id", "op": "not_empty"},
        require={"col": "po_before_order", "op": "eq", "value": "yes"},
        value_col="amount_eur")
    assert r["violating"] == 3
    assert r["violating_value"] == 216000


def test_conformance_deterministic():
    a = tools.check_conformance("purchase-order-export",
                                when={"col": "amount_eur", "op": "gt", "value": 50000},
                                require={"col": "approval_status", "op": "eq", "value": "approved"})
    b = tools.check_conformance("purchase-order-export",
                                when={"col": "amount_eur", "op": "gt", "value": 50000},
                                require={"col": "approval_status", "op": "eq", "value": "approved"})
    assert a == b


def test_conformance_in_schemas():
    assert "check_conformance" in [s["name"] for s in tools.schemas()]
