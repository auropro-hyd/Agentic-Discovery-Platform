"""PR-A: the stakeholder report must not leak tool names/filenames/jargon, and the internal
JSON must retain the full tool-level trace for audit.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import docnames, report  # noqa: E402


def test_friendly_names_derive_cleanly_for_all_docs():
    """Generic: every doc derives a clean, acronym-aware name with no leftover separators."""
    import os
    files = [docnames.stem(f) for f in os.listdir(ROOT / "inputs" / "o2c")
             if f.endswith((".csv", ".pdf", ".txt")) and not f.startswith(("_", "."))]
    for f in files:
        name = docnames.friendly(f)
        assert name and "-" not in name and "_" not in name
    # acronyms render correctly
    assert docnames.friendly("sap-s4-customer-master-export") == "SAP S/4HANA Customer Master Export"
    assert docnames.friendly("o2c-process-raci-opella-europe").startswith("O2C Process RACI")


def test_unknown_doc_id_derives_not_crashes():
    """Generic: a never-seen doc must derive a clean name, NOT hard-fail (works on any domain)."""
    assert docnames.friendly("procurement-vendor-master-export.csv") == \
        "Procurement Vendor Master Export"
    assert docnames.friendly("p2p-approval-workflow-sop.pdf").startswith("P2P Approval Workflow")


def test_business_phrase_list_is_readable():
    s = docnames.business_phrase_list(
        ["sap-s4-customer-master-export", "sap-crm-customer-export"])
    assert "SAP S/4HANA" in s and "SAP CRM" in s and s.startswith("your ")


def test_assert_no_leaks_catches_tool_names():
    with pytest.raises(AssertionError):
        report.assert_no_leaks("the result (computed by join_diff) shows 5,667 orders")
    with pytest.raises(AssertionError):
        report.assert_no_leaks("see order-flow-analysis-export-2025.csv for detail")


def test_assert_no_leaks_suppresses_named_client_only_when_asked():
    # engine hardcodes NO client name. With no suppress list, a client name is allowed:
    report.assert_no_leaks("how Order-to-Cash runs today at Northwind Trading")  # must not raise
    # but a run can ask to suppress a specific (detected) name for a demo:
    with pytest.raises(AssertionError):
        report.assert_no_leaks("how it runs at Northwind Trading",
                               suppress_names=["Northwind Trading"])


def test_derived_names_strip_only_when_set_per_run():
    docnames.set_noise_words([])  # default: nothing stripped
    assert docnames.friendly("credit-management-policy-acme-europe") == \
        "Credit Management Policy Acme Europe"
    # a run can suppress the detected client (+ region) from citations:
    docnames.set_noise_words(["Acme", "Europe"])
    assert docnames.friendly("credit-management-policy-acme-europe") == "Credit Management Policy"
    docnames.set_noise_words([])  # reset so other tests are unaffected


def test_detect_client_infers_recurring_name():
    docs = ["Northwind Trading operates in the EU. Northwind Trading uses SAP.",
            "All Northwind Trading staff must comply. Northwind Trading policy applies."]
    assert docnames.detect_client(docs) == "Northwind Trading"


def test_detect_client_returns_none_when_not_confident():
    # a single mention in one doc must NOT be confidently named
    assert docnames.detect_client(["Acme makes things.", "Orders flow through the system."]) is None
    assert docnames.detect_client(["", ""]) is None


def test_assert_no_leaks_passes_clean_business_text():
    clean = ("Your ERP and CRM customer exports disagree on 267 of 318 accounts. "
             "The platform read your operational map and found this.")
    report.assert_no_leaks(clean)  # must not raise


def test_assert_no_leaks_allows_ordinary_english():
    # 'describe', 'aggregate', 'column', 'node' as ordinary words must NOT trip the guard
    report.assert_no_leaks("We aggregate the regional teams and describe each node of the org.")
