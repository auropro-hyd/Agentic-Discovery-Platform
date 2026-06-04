"""Coverage for docnames.py: overrides (friendly/kind/phrase), noise-word mutation, the
two-document phrase-collapse, and the empty-list guard. Pure functions, no IO.

These tests mutate module-level OVERRIDES/_NOISE_WORDS, so each restores state in a finally.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import docnames as dn  # noqa: E402


def test_overrides_take_precedence_for_friendly_kind_phrase():
    saved = dict(dn.OVERRIDES)
    try:
        dn.load_overrides({"my-doc": {"friendly": "The Big Report", "kind": "Report",
                                      "phrase": "the headline report"}})
        assert dn.friendly("my-doc") == "The Big Report"
        assert dn.kind("my-doc") == "Report"
        assert dn.phrase("my-doc") == "the headline report"
    finally:
        dn.OVERRIDES.clear()
        dn.OVERRIDES.update(saved)


def test_derives_when_no_override():
    saved = dict(dn.OVERRIDES)
    try:
        dn.load_overrides({})
        assert dn.friendly("order-management-sop") != ""        # falls through to _derive_friendly
        assert dn.phrase("order-management-sop").startswith("your ")
    finally:
        dn.OVERRIDES.clear()
        dn.OVERRIDES.update(saved)


def test_add_noise_words_mutates_set():
    before = set(dn._NOISE_WORDS)
    try:
        dn.add_noise_words(["Zephyr", "Quux"])
        assert "zephyr" in dn._NOISE_WORDS and "quux" in dn._NOISE_WORDS
    finally:
        dn.set_noise_words(before)


def test_business_phrase_list_empty_is_blank():
    assert dn.business_phrase_list([]) == ""


def test_business_phrase_list_single_and_multi():
    one = dn.business_phrase_list(["order-management-sop"])
    assert one.startswith("your ")
    multi = dn.business_phrase_list(["order-management-sop", "credit-management-policy"])
    assert " and " in multi


def test_phrase_collapse_pairs_two_docs_sharing_trailing_noun():
    # two ids ending in the same collapsible noun phrase ("customer export") collapse into one
    out = dn.business_phrase_list(["sap-s4-customer-export", "sap-crm-customer-export"])
    assert "customer exports" in out.lower()                    # collapsed plural form
    assert " and " in out


def test_business_phrase_list_dedupes_repeated_doc_ids():
    # a repeated id must be deduped (exercises the `s not in ids` skip)
    out = dn.business_phrase_list(["order-management-sop", "order-management-sop"])
    assert out.startswith("your ") and out.count("Order Management SOP") == 1


def test_phrase_collapse_skips_already_used_peer():
    # three ids: two collapse into a pair; iterating reaches the second peer which is `used`
    out = dn.business_phrase_list(["sap-s4-customer-export", "sap-crm-customer-export",
                                   "order-management-sop"])
    assert "customer exports" in out.lower() and "and" in out.lower()


def test_phrase_collapse_leaves_unpaired_docs_alone():
    out = dn.business_phrase_list(["sap-s4-customer-export", "order-management-sop"]).lower()
    # no shared trailing noun -> not collapsed; both phrases present, joined by "and"
    assert "export" in out and "order" in out and " and " in out


# ── expand_suppress_names: full phrase + significant tokens (confidentiality-critical) ──────────
def test_expand_suppress_names_empty_and_blank():
    assert dn.expand_suppress_names("") == []
    assert dn.expand_suppress_names("   ") == []


def test_expand_suppress_names_single_word_unchanged():
    # a single-word name is not expanded — only the phrase is returned
    assert dn.expand_suppress_names("Opella") == ["Opella"]


def test_expand_suppress_names_multiword_adds_significant_tokens():
    # full phrase ALWAYS first, then each significant token; region/legal qualifier dropped
    assert dn.expand_suppress_names("Opella Europe") == ["Opella Europe", "Opella"]
    assert dn.expand_suppress_names("Acme Manufacturing") == ["Acme Manufacturing", "Acme"]
    assert dn.expand_suppress_names("Northwind Trading Group") == [
        "Northwind Trading Group", "Northwind", "Trading"]


def test_expand_suppress_names_skips_short_and_stopword_tokens():
    # a <3-char token and a generic stopword are not added as standalone scrub tokens
    out = dn.expand_suppress_names("BP Customer Co")
    assert out[0] == "BP Customer Co"                    # phrase always kept
    assert "BP" not in out[1:] and "Co" not in out[1:]   # 2-char tokens skipped
    assert "Customer" not in out[1:]                     # generic stopword skipped


def test_expand_suppress_names_dedupes_repeated_token():
    # a token equal (case-insensitively) to one already present is not duplicated
    assert dn.expand_suppress_names("Acme acme") == ["Acme acme", "Acme"]
