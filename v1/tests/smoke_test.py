#!/usr/bin/env python3
"""Offline smoke test: exercises loader -> stages -> resolve -> report with a fake LLM.

No API key required. Proves the wiring is sound before real docs/creds arrive.
Run:  ./.venv/bin/python tests/smoke_test.py   (from the v1/ root)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # v1/ (this file lives in v1/tests/)
sys.path.insert(0, str(ROOT))

from discovery import loader, report, resolve, stages  # noqa: E402
from discovery.models import DiscoveryResult, Severity  # noqa: E402


class FakeLLM:
    """Returns canned JSON per stage by sniffing the prompt. Deterministic."""

    def complete_json(self, system: str, prompt: str, **kw):
        if "Classify each document" in prompt:
            return [
                {"doc_id": "01-order-management-sop.md", "category": "structured",
                 "title": "Order Management SOP", "summary": "Manual order channel only."},
                {"doc_id": "02-edi-working-notes.txt", "category": "unstructured",
                 "title": "EDI Working Notes", "summary": "Informal EDI how-to; names Sanofi dependency."},
                {"doc_id": "03-order-flow-export.csv", "category": "system_signal",
                 "title": "Order Flow Export", "summary": "Channel split; EDI is 67%."},
            ]
        if "Extract the key elements" in prompt:
            return [
                {"name": "EDI order channel", "kind": "process",
                 "sources": [{"doc_id": "02-edi-working-notes.txt", "locator": "para 2", "quote": ""},
                             {"doc_id": "03-order-flow-export.csv", "locator": "row EDI", "quote": "67.3"}],
                 "attributes": {"volume_pct": 67.3}},
            ]
        if "find CONTRADICTIONS and GAPS" in prompt:
            return [
                {"id": "F1", "title": "Undocumented EDI order flow", "severity": "high",
                 "description": "67% of orders arrive via EDI but the SOP covers only the manual channel and there is no EDI owner.",
                 "business_consequence": "Majority of order volume has no documented accountability.",
                 "confidence": "verified",
                 "sources": [{"doc_id": "01-order-management-sop.md", "locator": "whole doc", "quote": ""},
                             {"doc_id": "03-order-flow-export.csv", "locator": "EDI 67.3%", "quote": ""}],
                 "candidates": [
                     {"id": "candidate_1", "summary": "EDI is the de-facto primary channel; assign an owner and write the SOP.",
                      "rationale": "67% volume with no SOP.", "evidence_strength": "strong",
                      "sources": [{"doc_id": "03-order-flow-export.csv", "locator": "EDI 67.3%", "quote": ""}]},
                     {"id": "candidate_2", "summary": "EDI handled ad hoc by CS; formalise the existing practice.",
                      "rationale": "Working notes show informal handling.", "evidence_strength": "moderate",
                      "sources": [{"doc_id": "02-edi-working-notes.txt", "locator": "para 1", "quote": ""}]},
                 ]},
            ]
        if "roadmap of recommendations" in prompt:
            return {
                "process_summary": "Orders enter mainly via retail EDI (67%) yet the formal SOP only documents the manual channel; six EDI links still depend on Sanofi IT.",
                "recommendations": [
                    {"title": "Assign an owner and SOP for the EDI order channel", "horizon": "now",
                     "intervention": "hitl", "justification": "Finding F1: 67% of volume is undocumented.",
                     "sources": [{"doc_id": "03-order-flow-export.csv", "locator": "EDI 67.3%", "quote": ""}]},
                    {"title": "Migrate the 6 Sanofi-managed EDI connections off TSA", "horizon": "next",
                     "intervention": "modernize", "justification": "Working notes confirm live Sanofi dependency.",
                     "sources": [{"doc_id": "02-edi-working-notes.txt", "locator": "para 2", "quote": ""}]},
                ],
            }
        raise AssertionError("unexpected prompt in FakeLLM")


def main() -> int:
    domain_dir = ROOT / "inputs" / "o2c"
    docs = loader.load_domain(domain_dir)
    assert docs, "no docs loaded"
    manifest = loader.load_manifest(domain_dir) or {}

    llm = FakeLLM()
    docs = stages.classify(llm, docs)
    entities = stages.extract(llm, docs)
    findings = stages.cross_reference(llm, docs, entities)
    assert findings and findings[0].severity == Severity.HIGH

    # auto-resolve using a canned choice (no interactive prompt in the test)
    resolve.resolve_auto(findings, {"F1": {"chosen": "candidate_1"}})
    assert findings[0].resolved and findings[0].chosen_candidate_id == "candidate_1"

    summary, recs = stages.synthesize(llm, "Order-to-Cash", docs, entities, findings)
    result = DiscoveryResult(
        domain="o2c", domain_label="Order-to-Cash", documents=docs, entities=entities,
        findings=findings, recommendations=recs,
        effort_comparison=manifest.get("effort_comparison", {}), process_summary=summary,
    )

    md = report.render_markdown(result)
    html_doc = report.render_html(md, "Discovery Report — Order-to-Cash")
    assert "Undocumented EDI order flow" in md
    assert "SME selected" in md          # resolution shows up
    assert "Effort comparison" in md     # 80% story shows up
    assert "<table>" in html_doc and "<h1>" in html_doc

    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    (out / "report-o2c.md").write_text(md, encoding="utf-8")
    (out / "report-o2c.html").write_text(html_doc, encoding="utf-8")
    print("SMOKE TEST PASSED")
    print(f"  wrote {out/'report-o2c.md'}")
    print(f"  wrote {out/'report-o2c.html'}")
    print("\n--- markdown preview (first 40 lines) ---")
    print("\n".join(md.splitlines()[:40]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
