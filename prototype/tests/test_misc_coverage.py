"""Coverage for the small active-pipeline modules: assemble.to_result (incl. derived-detail folding
and the verification-downgrade branch), verify's non-dict fallback, refresh.summary_line,
registry._frozen_text on a .txt source, and the model to_dict() serializers.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import assemble, refresh, registry, verify  # noqa: E402
from discovery import models as m  # noqa: E402


# ---- assemble.to_result -------------------------------------------------------
def _payload():
    return {"_process_summary": "summary", "findings": [{
        "id": "F1", "title": "Customer master conflict", "severity": "high",
        "confidence": "verified", "description": "ERP vs CRM.",
        "business_consequence": "Wrong limits.",
        "computed_values": [{"label": "accounts", "value": 267}, {"label": "amt", "value": 600000.0}],
        "narrative_values": [{"label": "FR gap", "value": 600000,
                              "doc_id": "credit-management-policy", "quote": "EUR 600,000"}],
        "sources": [{"doc_id": "sap-s4-customer-master-export"},
                    {"doc_id": "sap-crm-customer-export"}],
    }]}


def test_to_result_folds_derived_detail():
    res = assemble.to_result(_payload(), "o2c", "Order-to-Cash", documents=[],
                             effort_comparison={})
    f = res.findings[0]
    assert "What the data shows" in f.description
    assert "267" in f.description and "600,000" in f.description   # _fmt int + float
    assert res.raw_payload["_process_summary"] == "summary"


def test_to_result_finding_without_derived_detail():
    p = {"findings": [{"id": "F1", "title": "t", "severity": "high", "confidence": "verified",
                       "description": "plain", "business_consequence": "c",
                       "computed_values": [], "narrative_values": [],
                       "sources": [{"doc_id": "x"}]}]}
    res = assemble.to_result(p, "o2c", "Order-to-Cash", documents=[], effort_comparison={})
    assert res.findings[0].description == "plain"          # no "What the data shows" appended


def test_to_result_downgrades_challenged_finding():
    p = _payload()
    p["findings"][0]["verification"] = {"supported": False, "suggested_fix": "double-check the join"}
    res = assemble.to_result(p, "o2c", "Order-to-Cash", documents=[], effort_comparison={})
    f = res.findings[0]
    assert f.confidence is m.ConfidenceTier.AMBER
    assert "Flagged for review" in f.description and "double-check the join" in f.description


def test_to_result_handles_unknown_severity_and_confidence():
    p = _payload()
    p["findings"][0]["severity"] = "weird"
    p["findings"][0]["confidence"] = "weird"
    res = assemble.to_result(p, "o2c", "Order-to-Cash", documents=[], effort_comparison={})
    assert res.findings[0].severity is m.Severity.AMBER          # _sev fallback
    assert res.findings[0].confidence is m.ConfidenceTier.AMBER  # _conf fallback


def test_cite_renders_business_phrases():
    refs = [m.SourceRef(doc_id="sap-s4-customer-master-export"),
            m.SourceRef(doc_id="sap-crm-customer-export")]
    out = assemble.cite(refs)
    assert out and "export" in out.lower()


def test_fmt_handles_float_int_and_str():
    assert assemble._fmt(1000.0) == "1,000"
    assert assemble._fmt(2500) == "2,500"
    assert assemble._fmt("text") == "text"


# ---- verify non-dict fallback -------------------------------------------------
class _NonDictLLM:
    def complete_json(self, system, user, model=None):
        return ["not", "a", "dict"]


def test_verify_handles_non_dict_verdict():
    payload = {"findings": [{"id": "F1", "title": "t", "description": "d",
                             "business_consequence": "c"}]}
    out = verify.verify_findings(_NonDictLLM(), payload)
    v = out["findings"][0]["verification"]
    assert v["supported"] is None and "non-JSON" in v["reason"]


# ---- refresh.summary_line -----------------------------------------------------
def test_refresh_summary_line():
    prev = {"findings": [{"id": "F1", "title": "Gone issue", "computed_values": []}]}
    curr = {"findings": [{"id": "F1", "title": "New issue", "computed_values": []}]}
    d = refresh.diff_runs(prev, curr)
    line = refresh.summary_line(d)
    assert "new" in line and "resolved" in line and "changed" in line and "unchanged" in line


# ---- registry frozen-text on a .txt source -----------------------------------
def test_registry_frozen_text_reads_txt(tmp_path):
    src = tmp_path / "notes.txt"
    src.write_text("hello frozen text", encoding="utf-8")
    sidecar = tmp_path / "sidecar"
    sidecar.mkdir()
    text = registry._frozen_text(src, sidecar, freeze=True)
    assert text == "hello frozen text"
    assert (sidecar / "notes.txt").read_text(encoding="utf-8") == "hello frozen text"
    # non-freeze path reads the existing sidecar back
    text2 = registry._frozen_text(src, sidecar, freeze=False)
    assert text2 == "hello frozen text"


def test_frozen_text_determinism_guard_fires(tmp_path, monkeypatch):
    """The PDF determinism guard raises if two extractions of the same file disagree."""
    import pytest
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    calls = {"n": 0}

    def flaky(_path):
        calls["n"] += 1
        return f"extraction-{calls['n']}"        # different each call -> guard trips

    monkeypatch.setattr(registry, "_extract_pdf", flaky)
    with pytest.raises(RuntimeError, match="not stable"):
        registry._frozen_text(pdf, tmp_path, freeze=True)


def test_frozen_text_nonfreeze_without_sidecar_returns_fresh(tmp_path, monkeypatch):
    pdf = tmp_path / "doc2.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    monkeypatch.setattr(registry, "_extract_pdf", lambda _p: "fresh extraction")
    # freeze=False and no sidecar present -> returns the freshly extracted text
    text = registry._frozen_text(pdf, tmp_path, freeze=False)
    assert text == "fresh extraction"


# ---- model to_dict serializers ------------------------------------------------
def test_model_to_dicts():
    ref = m.SourceRef(doc_id="d1", locator="L", quote="q")
    doc = m.Document(doc_id="d1", path="/p", category=m.DocCategory.UNKNOWN, title="T", text="raw")
    dd = doc.to_dict()
    assert dd["category"] == m.DocCategory.UNKNOWN.value and "text" not in dd

    ent = m.Entity(name="SAP", kind="system", sources=[ref])
    assert ent.to_dict()["sources"][0]["doc_id"] == "d1"

    cand = m.CandidateResolution(id="c1", summary="s", sources=[ref])
    assert cand.to_dict()["sources"][0]["quote"] == "q"

    fnd = m.Finding(id="F1", title="t", severity=m.Severity.HIGH, description="d", sources=[ref],
                    candidates=[cand], confidence=m.ConfidenceTier.VERIFIED)
    fd = fnd.to_dict()
    assert fd["severity"] == m.Severity.HIGH.value and fd["candidates"][0]["id"] == "c1"

    rec = m.Recommendation(title="r", horizon="now", intervention="automate", sources=[ref])
    assert rec.to_dict()["sources"][0]["locator"] == "L"

    hz = m.RoadmapHorizon(horizon="H1", window="0-6 months", theme="x",
                          items=[m.RoadmapItem(title="i", rationale="r")])
    assert hz.to_dict()["items"][0]["title"] == "i"

    res = m.DiscoveryResult(domain="o2c", domain_label="Order-to-Cash", documents=[doc],
                            findings=[fnd], recommendations=[rec], effort_comparison={})
    rdict = res.to_dict()
    assert rdict["findings"][0]["id"] == "F1" and rdict["documents"][0]["doc_id"] == "d1"

    sd = m.SourceDoc(doc_id="d1", business_name="The Doc", doc_type="Report",
                     what_we_read="your doc", supported_findings=["F1"])
    assert sd.to_dict()["business_name"] == "The Doc"


# ---- registry.setup_domain over the real o2c dir (PDF extraction + loop skips) ----
def test_setup_domain_indexes_csv_and_docs_and_skips_noise():
    out = registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    # CSVs and narrative docs are indexed; the _generate.py and pdftext/ dir are skipped
    assert out["csv_ids"] and out["doc_ids"]
    assert all(not c.startswith("_") for c in out["csv_ids"])


def test_setup_domain_skips_hidden_dirs_and_unknown_suffixes(tmp_path):
    (tmp_path / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "_generate.py").write_text("# skipped (underscore)", encoding="utf-8")
    (tmp_path / ".hidden").write_text("skipped (dot)", encoding="utf-8")
    (tmp_path / "manifest.json").write_text("{}", encoding="utf-8")   # unknown suffix -> neither
    (tmp_path / "subdir").mkdir()                                     # dir -> skipped
    out = registry.setup_domain(tmp_path, freeze=True)
    assert out["csv_ids"] == ["data"]
    assert out["doc_ids"] == ["notes"]
