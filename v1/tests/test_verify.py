"""Offline tests for the adversarial verifier (fake LLM playing skeptic — no API)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import verify  # noqa: E402
from discovery.llm import LLMError  # noqa: E402


def _payload():
    return {"findings": [
        {"id": "F1", "title": "Credit conflict", "description": "ERP vs CRM disagree.",
         "business_consequence": "x", "computed_values": [{"label": "delta", "value": 600000}],
         "sources": [{"doc_id": "a"}, {"doc_id": "b"}]},
        {"id": "F2", "title": "Causal lag claim",
         "description": "A forecast miss CAUSES a fulfilment drop 12 days later.",
         "business_consequence": "y", "computed_values": [{"label": "lag", "value": 12}],
         "sources": [{"doc_id": "c"}, {"doc_id": "d"}]},
    ]}


class SkepticLLM:
    """Supports F1 (well-grounded), challenges F2 (causal over-reach)."""
    def complete_json(self, system, prompt, **kw):
        if "CAUSES" in prompt or "Causal" in prompt:
            return {"supported": False, "reason": "causal claim from correlational data",
                    "suggested_fix": "describe as a co-occurring pattern, not a cause"}
        return {"supported": True, "reason": "numbers cited and consistent", "suggested_fix": ""}


class OfflineLLM:
    def complete_json(self, system, prompt, **kw):
        raise LLMError("offline: no cached response")


def test_verifier_supports_and_challenges():
    p = verify.verify_findings(SkepticLLM(), _payload())
    by = {f["id"]: f["verification"] for f in p["findings"]}
    assert by["F1"]["supported"] is True
    assert by["F2"]["supported"] is False
    assert "co-occurring" in by["F2"]["suggested_fix"]
    s = verify.verification_summary(p)
    assert s == {"total": 2, "supported": 1, "challenged": 1, "unverified": 0}


def test_verifier_degrades_gracefully_offline():
    """Offline / errored verification must NOT raise — findings pass through marked 'unverified'."""
    p = verify.verify_findings(OfflineLLM(), _payload())
    assert all(f["verification"]["supported"] is None for f in p["findings"])
    assert verify.verification_summary(p)["unverified"] == 2


def test_challenged_finding_downgrades_confidence_in_report():
    """A challenged finding is rendered as amber/needs-review, not silently dropped."""
    from discovery import assemble, registry
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=False)
    p = verify.verify_findings(SkepticLLM(), _payload())
    # give the findings real O2C doc_ids so cite() works
    for f in p["findings"]:
        f["sources"] = [{"doc_id": "sap-s4-customer-master-export"},
                        {"doc_id": "sap-crm-customer-export"}]
    res = assemble.to_result(p, "o2c", "Order-to-Cash", [], {})
    f2 = next(f for f in res.findings if f.id == "F2")
    assert "Flagged for review" in f2.description
