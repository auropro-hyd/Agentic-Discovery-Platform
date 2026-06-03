# Demo Script & Synthetic Input Artefacts — Opella Discovery Demo

**Date:** 2026-05-31 (updated 2026-06-01)
**Engagement:** AuroPro Autonomous Discovery Platform — Opella
**Audience:** Opella Head of Strategy + Transformation team
**Format:** 60-minute meeting (20 min demo + 40 min discussion & Q&A)
**Domain:** Order-to-Cash (O2C only)

**Key references:**
- Demo script guide: [`html/demo-script-o2c-guide.md`](html/demo-script-o2c-guide.md) — full narration, beat notes, timing, fallback protocol, discussion prep
- Platform understanding: [`2026-06-01-autonomous-discovery-platform-understanding.md`](2026-06-01-autonomous-discovery-platform-understanding.md) — architecture, output suite, StrategyProfile, intervention taxonomy
- HTML demo script: [`html/demo-script-o2c.html`](html/demo-script-o2c.html)
- Synthetic inputs (HTML): [`html/synthetic-inputs-o2c.html`](html/synthetic-inputs-o2c.html)

---

## 1. Context

Opella became an independent company in April 2025 following a carve-out from Sanofi. CD&R holds a 50% controlling stake; Sanofi retains 48.2%. The company inherited approximately 1,000+ applications across 38 direct countries, 13 manufacturing sites, and ~100 consumer health brands. The O2C process was built for pharma distributors — 67% of actual order volume now arrives via retail EDI (Carrefour, Boots, dm, etc.). The process has not caught up with the distribution shift.

The demo shows how the AuroPro platform produces a full discovery output suite — findings, current state documentation, AI opportunity portfolio, and transformation roadmap — that would take a traditional engagement three months to deliver, in 20 minutes.

---

## 2. Demo Structure

| Phase | Duration | What happens |
|---|---|---|
| Session Configuration | Pre-demo | StrategyProfile confirmed with BU lead before the session. See [understanding doc §2](2026-06-01-autonomous-discovery-platform-understanding.md). |
| Demo — O2C | 20 min | Live run on 12 synthetic inputs; 3 findings surface; gap resolution via Discovery Copilot; full 6-report output suite walkthrough; hard close |
| Discussion & Q&A | 40 min | Full output suite open on screen; audience navigates; pilot scope discussed |

**Narrative approach:** The audience watches a three-month discovery complete in 12 minutes. Opening frame is the distribution shift mismatch — "your process was built for one business; 67% of your orders are running through another." Business problem leads; platform is invisible.

For full narration, beat notes, screen states, fallback protocol, and expected Q&A: → **[`html/demo-script-o2c-guide.md`](html/demo-script-o2c-guide.md)**

---

## 3. Language Guide

The platform is invisible. The business problem is the protagonist.

| Never say | Say instead |
|---|---|
| Block 1 / Block 2 / Block 3 | The platform is reading your landscape |
| Knowledge Graph | Your operational map |
| Evidence Synthesis Agent | Here's what it found |
| Pipeline is running | The discovery is running |
| High-severity gap detected | A finding that needs a quick answer before we proceed |
| Strategic tension | A conflict between where you're headed and what we found |
| Nodes and edges | How your processes connect |
| StrategyProfile / PipelineState | Your direction — what you've told us you're building toward |

---

## 4. The Three O2C Findings

| # | Severity | Tray | Finding | Business framing |
|---|---|---|---|---|
| F1 | 🔴 High | Blocking gap | **Customer Master: No Single Source of Truth** | Same retail accounts in SAP ERP and SAP CRM with conflicting credit limits and payment terms. €600K+ unhedged credit exposure. |
| F2 | 🔴 High | Blocking gap | **Undocumented EDI Order Flow** | 67% of order volume arrives via retail EDI. No SOP, no RACI owner, no documented process for this channel. |
| F3 | 🟡 Amber | Strategic tension | **TSA-Exposed EDI Integrations** | 6 of 14 EDI connections established by Sanofi Shared Services. Ownership at carve-out unconfirmed. CS team calls the Sanofi IT helpdesk for failures. Non-blocking — conflicts with Opella's stated consolidate + modernize direction; accepted tension under TSA constraints. |

**Cross-domain pattern** 🟢: Demand forecast underrun → O2C escalation spike 12–15 days later. CS escalation clusters (doc 06) align with EDI fulfilment drops (doc 10). Detectable only by reading signals together.

For resolution approach, demo narration, and Copilot two-tray model detail: → **[`html/demo-script-o2c-guide.md §Discovery Copilot`](html/demo-script-o2c-guide.md)**

---

## 5. Output Suite — 6 Deliverables

Shown on screen from minute 8:00 onward. Full structure, content, and visual references in the understanding doc.

| # | Report | Demo slot | Primary reference |
|---|---|---|---|
| 01 | Current State Assessment | 8:00–9:30 | [`../html/o2c-report-suite-hl.html`](../html/o2c-report-suite-hl.html) |
| 02 | Pain Points & Opportunity Report | 9:30–11:00 | Understanding doc §5.2 |
| 03 | Transformation Recommendation | 11:00–12:00 | [`../html/value-feasibility-matrix.html`](../html/value-feasibility-matrix.html) |
| 04 | AI Opportunity Portfolio | 12:00–16:00 | Understanding doc §5.4 |
| 05 | Transformation Roadmap | 16:00–17:00 | [`../html/design-section1-timeline-v3.html`](../html/design-section1-timeline-v3.html) |
| 06 | Supporting Artefacts | 17:00–17:30 | Understanding doc §5.6 |

→ Full output suite specification: **[`2026-06-01-autonomous-discovery-platform-understanding.md §5`](2026-06-01-autonomous-discovery-platform-understanding.md)**

---

## 6. Synthetic Input Set — O2C (12 artefacts)

> **Design principle:** No single document reveals a finding. Every finding requires the platform to cross-reference at least two inputs from different categories. The most important documents are the informal ones — escalation logs, working notes. These carry evidence that never surfaces in formal documentation alone.

**Findings seeded:**
- 🔴 F1: Customer Master — No Single Source of Truth
- 🔴 F2: Undocumented EDI Order Flow
- 🟡 F3: TSA-Exposed EDI Integrations (strategic tension)
- 🟢 Cross-domain: Forecast miss → O2C escalation spike

### Structured (5 documents)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 01 | Order Management SOP — Opella Europe | PDF, ~6pp | F2 | A 6-page SOP that does not mention EDI at all — in a business where 67% of orders arrive via EDI. What's absent is the signal. |
| 02 | Credit Management Policy — Opella Europe | PDF, ~4pp | F1 | Refers to "the customer credit system" without naming it. When cross-referenced against docs 08 and 09 (two different credit systems, different limits), the ambiguity becomes the finding. |
| 03 | O2C Process RACI — Opella Europe | PDF, ~1pp | F2 | No RACI row for EDI order processing or EDI dispute resolution. 67% of order volume has no documented accountability. |
| 04 | EDI Integration Register — Opella Europe | PDF, ~3pp | F3 | 14 EDI connections. 8 marked "Opella Digital." 6 marked "Sanofi Shared Services / See TSA Schedule Annex C." No Annex C is provided — the reference is unresolvable from the input set alone. |
| 05 | Retail Customer Onboarding Guide — Opella Europe | PDF, ~4pp | F1, F2 | "Create the customer record in our systems" — no named system. Combined with docs 08 and 09, suggests customer setup creates parallel records by default, not by design. |

### Semi-Structured (2 documents)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 06 | Customer Service Escalation Log — Opella Europe 2025 | CSV, 142 rows | F2, Cross-domain | 34 entries flagged as EDI-related (root_cause: "EDI order not processed — manual intervention required"). 19 stockout complaints cluster in Apr–May and Oct–Nov 2025 — aligning with demand forecast underrun periods. Free text: "customer threatened to delist Doliprane," "third time this quarter for Carrefour FR." |
| 07 | Accounts Receivable Review Notes — Q4 2025 | Text, ~600w | F1 | Explicitly names two systems and two accounts: "Carrefour France is showing two different credit limits depending on which system you look at — CRM has €2.4M, ERP has €1.8M." Boots UK payment terms discrepancy also documented. |

### System Signals (3 documents)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 08 | SAP S/4HANA Customer Master Export | CSV, 340 rows | F1 | Top 10 retail accounts: credit limits €800K–€1.8M. 6 accounts flagged "migrated from Sanofi legacy system — 2024-05-01." These records were never reconciled with CRM post-migration. |
| 09 | SAP CRM Customer Export | CSV, 318 rows | F1 | 22 fewer records than ERP (customers created in one system, never synced). Credit limits uniformly higher than ERP for top accounts (Carrefour FR: €2.4M vs. €1.8M). Source: "manually updated by account manager post-carve-out." |
| 10 | Order Flow Analysis Export — Opella Europe 2025 | CSV, 8,420 rows | F2, Cross-domain | Channel split: EDI 67.3%, manual 21.4%, email 9.1%, fax 2.2%. EDI fulfilment rate drops to 61% during Apr–May and Oct–Nov clusters. Cross-domain signal: aligns with CS escalation clusters (doc 06). Business value derivation: 8,420 × 67.3% = 5,665 EDI orders/yr; 2-month cluster × 39% miss rate = ~370 orders miss SLA per cluster event. |

### Unstructured (1 document)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 11 | EDI Dispute Resolution — Customer Service Working Notes | Text, ~1,100w | F2, F3 | **Most important document in the set.** Informal "how we actually do it" guide written by the CS team lead for new team members. Contains: *"For the 6 older connections (Carrefour FR, Boots UK, dm, Leclerc, Lidl, Coop) — if there's an outage, contact Sanofi IT helpdesk on [number]. Opella Digital doesn't manage these yet."* No formal document contains this. The CS team lead wrote it down; no one escalated it. |

### Comparative (1 document)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 12 | Inherited Sanofi Consumer Healthcare O2C SOP (2023) | PDF, ~9pp | F1, F2, F3, Context | Pre-carve-out. Pharma distributor model: low-volume, high-value, Sanofi-managed MDM, EDI as "optional for strategic accounts." Cross-referencing shows Opella's current O2C SOP is a light adaptation of this document — the inherited architecture explains all three findings. |

### Cross-Reference Map

| Docs | Finding |
|---|---|
| 01 + 03 + 10 | 🔴 F2: SOP covers manual flow only (01) · RACI has no EDI row (03) · 67% of orders are EDI (10). Three-source confirmation that majority order volume is undocumented. |
| 07 + 08 + 09 | 🔴 F1: AR notes name the discrepancy (07) · ERP shows lower limits / Net 45 (08) · CRM shows higher limits / Net 30 (09). Named accounts, quantified conflict, two-system evidence. |
| 04 + 11 | 🟡 F3: EDI register names 6 Sanofi-established connections with unresolved TSA status (04) · CS working notes confirm "contact Sanofi IT" for those same connections (11). Operational evidence that the dependency is live, not theoretical. |
| 06 + 10 | 🟢 Cross-domain: Escalation log clusters (06) align with EDI fulfilment drops (10). 12–15 day lag consistent with demand forecast underrun pattern. |

### Business Value Derivation

| Figure | Source |
|---|---|
| €600K+ credit exposure | Doc 07 (AR notes naming discrepancy) + Doc 08 (ERP: €1.8M) + Doc 09 (CRM: €2.4M) |
| 34 CS incidents/year | Doc 06 (escalation log: 34 EDI-flagged entries) |
| 5,665 EDI orders/year | Doc 10: 8,420 total × 67.3% EDI |
| ~370 orders miss SLA per cluster | Doc 10: 5,665 ÷ 12 × 2-month window × 39% miss rate |

---

## 7. Open Items

| Item | Status |
|---|---|
| Synthetic input files (PDFs, CSVs) — generate or keep as spec? | Open |
| Demo output format — HTML, PDF, or both? | Open |
| Discovery Copilot surface — what does it look like in the 20-min walkthrough? | Not yet specified |
| Report 04 (AI Opportunity Portfolio) — detailed standalone HTML | Not yet built |
| Report 02 (Pain Points) — standalone HTML | Not yet built |
| Report 05 (Transformation Roadmap) — standalone HTML with app rationalization | Not yet built |
| Report 06 (Supporting Artefacts) — format and layout | Not yet designed |
| Demo narration script (minutes 8:00–17:30) | Explicitly deferred |
| Pilot domain scope for Opella — proposed framing | Open |

---

## 8. Related Files

| File | Purpose |
|---|---|
| [`html/demo-script-o2c-guide.md`](html/demo-script-o2c-guide.md) | Full demo narration, beat notes, timing, fallback protocol, Q&A prep |
| [`html/demo-script-o2c.html`](html/demo-script-o2c.html) | HTML demo script |
| [`html/synthetic-inputs-o2c.html`](html/synthetic-inputs-o2c.html) | 12 synthetic input artefacts (HTML) |
| [`2026-06-01-autonomous-discovery-platform-understanding.md`](2026-06-01-autonomous-discovery-platform-understanding.md) | Platform understanding — architecture, output suite, StrategyProfile |
| [`2026-05-30-autonomous-discovery-platform-design.md`](2026-05-30-autonomous-discovery-platform-design.md) | Platform architecture spec |
| [`2026-05-31-discovery-session-configuration-design.md`](2026-05-31-discovery-session-configuration-design.md) | StrategyProfile and session configuration design |
| [`../html/o2c-report-suite-hl.html`](../html/o2c-report-suite-hl.html) | Report 01 + suite overview mockup |
| [`../html/value-feasibility-matrix.html`](../html/value-feasibility-matrix.html) | Report 03 — Value vs. Feasibility matrix |
| [`../html/design-section1-timeline-v3.html`](../html/design-section1-timeline-v3.html) | Report 05 — Transformation Roadmap mockup |
