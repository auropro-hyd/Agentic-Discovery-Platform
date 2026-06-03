# Verified Golden Numbers — O2C (independently recomputed from raw data 2026-06-02)

Computed directly from `prototype/inputs/o2c/` with plain stdlib csv, not trusting any spec or
workflow report. These are the only numbers the demo may assert. Re-run the checks in
`tests/` (Gate A) to reconfirm before any demo.

## F2 — EDI channel share (order-flow-analysis-export-2025.csv, 8,420 rows)
- EDI:    5,667  (67.3% by count, 66.8% by value)   <- headline; count is canonical
- Manual: 1,802  (21.4%)
- Email:    767  (9.1%)
- Fax:      184  (2.2%)
- Distinct channels: {EDI, Email, Fax, Manual}  — there is NO "Phone" in order flow.
  ("Phone" appears only in the escalation log's channel column — a decoy.)

## F1 — Customer master conflict (ERP sap-s4 vs CRM sap-crm, key=customer_id)
- ERP rows 340 | CRM rows 318
- shared 318 | only in ERP 22 | only in CRM 0
- accounts with ANY difference: 307
- credit_limit mismatches: 267
- payment_terms mismatches: 228
- FR001 Carrefour France: ERP €1,800,000 / NET45  vs  CRM €2,400,000 / NET30  -> delta +€600,000
- FR001 provenance: ERP migration_source="Sanofi Legacy System";
  CRM source="manually updated by account manager post-carve-out"

### CAUTION — aggregate "total exposure" is FRAGILE, do not headline it
- sum of |credit-limit deltas| over the 267 mismatched accounts = €30,675,000 (my computed value).
- The design workflow reported €5,325,000, and an earlier draft said €78,550,000 — BOTH WRONG.
  The number swings wildly by definition (abs vs net vs only-higher-in-CRM).
- SAFE headline: "307 of 318 shared accounts disagree; largest single gap is Carrefour +€600,000."
- If a total is wanted, define it precisely first, then compute and label it exactly.

## F3 — EDI connection ownership (qualitative + one count)
- 6 of 14 active EDI connections still Sanofi-managed: Carrefour FR, Boots UK, dm, E.Leclerc,
  Lidl, Coop. (From EDI register prose + CS working notes — NOT from counting table rows.)
- Escalations with root_cause containing "EDI order not processed": 34 of 142.
  (root_cause string contains a U+2014 em-dash; match NFC-normalized + casefold.)
- Label the 34 precisely: "34 'EDI order not processed' escalations", never "34 EDI incidents"
  (channel==EDI in the escalation log is 61 — a different, larger number; the decoy).
