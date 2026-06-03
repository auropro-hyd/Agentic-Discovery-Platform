# Input Document Contract

This is the shape the prototype expects for the synthetic input documents. It is
deliberately loose — real client documents are messy — but following it lets the
pipeline cross-reference reliably and lets Akhilesh's docs drop in without code changes.

## Where docs go

```
prototype/inputs/<domain>/        e.g. inputs/o2c/  or  inputs/demand_planning/
```

Each file is one document. Supported formats: `.md`, `.txt`, `.csv`, `.pdf` (text-based),
`.json`. Filenames should be readable, e.g. `01-order-management-sop.md`.

## Document categories (matches the discovery design)

The classifier assigns each doc one of these `doc_type`s. You do not need to label them —
classification is by content — but the input set should span several categories so that
findings require cross-referencing (no single doc reveals a finding).

| category        | examples                                              |
|-----------------|-------------------------------------------------------|
| `structured`    | SOPs, policies, RACI matrices, integration registers  |
| `semi_structured` | meeting transcripts, review notes                   |
| `system_signal` | CSV exports, audit logs, event logs                   |
| `unstructured`  | working notes, escalation logs, "how we actually do it"|
| `comparative`   | inherited/legacy SOPs from the parent org (pre-carve) |

## Design principle (important)

> **No single document should reveal a finding.** Each engineered finding should require
> cross-referencing at least two documents from different categories.

This is what makes the platform look like it is *connecting dots a human would miss*,
and it is the honest, demonstrable version of the capability.

## Optional sidecar: `_manifest.json`

If present in a domain folder, it lets us pin the demo to specific engineered findings
(useful for a consistent live run). Entirely optional — the pipeline works without it.

```json
{
  "domain": "o2c",
  "domain_label": "Order-to-Cash",
  "expected_findings": [
    {
      "id": "F1",
      "title": "Customer Master: no single source of truth",
      "severity": "high",
      "source_docs": ["07-ar-review-notes.txt", "08-erp-customer-export.csv", "09-crm-customer-export.csv"],
      "business_consequence": "Orders approved against inflated CRM credit limits."
    }
  ],
  "effort_comparison": {
    "traditional": { "duration": "8-12 weeks", "stakeholders": "15-20", "hours_each": "4-8" },
    "platform":    { "duration": "2-3 weeks", "touchpoints": "2 SME review sessions" }
  }
}
```

## Sidecar: `_resolutions.json` (for consistent / non-interactive runs)

Maps each flagged finding to the SME's chosen resolution, so the live demo is consistent
and the `--auto-resolve` mode works. Generated/edited after a first run.

```json
{
  "F1": { "chosen": "candidate_1", "note": "ERP confirmed as system of record." }
}
```
