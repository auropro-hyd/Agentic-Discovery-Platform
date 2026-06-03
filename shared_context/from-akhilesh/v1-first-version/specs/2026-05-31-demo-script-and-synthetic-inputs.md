# Demo Script & Synthetic Input Artefacts — Opella Discovery Demo

**Date:** 2026-05-31
**Engagement:** AuroPro Autonomous Discovery Platform — Opella
**Audience:** Opella Head of Strategy
**Format:** 45-minute meeting (20 min demo + 25 min discussion)

**Visual references (HTML):**
- [`demo-script-v2.html`](html/demo-script-v2.html) — Primary demo script (Demand Planning)
- [`demo-script-o2c.html`](html/demo-script-o2c.html) — Secondary demo script (O2C)
- [`synthetic-inputs-demand-planning.html`](html/synthetic-inputs-demand-planning.html) — Demand Planning input set
- [`synthetic-inputs-o2c.html`](html/synthetic-inputs-o2c.html) — O2C input set

---

## 1. Context

Opella became an independent company in April 2025 following a carve-out from Sanofi. CD&R holds a 50% controlling stake; Sanofi retains 48.2%. The company inherited approximately 1,000+ applications across 38 direct countries, 13 manufacturing sites, and ~100 consumer health brands. The transformation programme must rationalise this landscape — at consumer-goods speed, using infrastructure built for pharma.

The demo shows how the AuroPro platform produces a discovery output (findings, operational map, transformation roadmap) that would take a traditional consulting engagement three months to deliver, in the time it takes to have a meeting.

---

## 2. Demo Structure

| Phase | Duration | What happens |
|---|---|---|
| Primary demo — Demand Planning & Distribution | 20 min | Live run on synthetic inputs; three findings; clarification flow; operational map; roadmap; hard close |
| Discussion & next steps | 25 min | Full report open; audience navigates; pilot scope discussed |
| Secondary demo — O2C | 30 min (separate) | Used only if: (a) audience is finance/commercial-led, or (b) audience asks to go deeper on order fulfilment during discussion phase |

**Narrative approach:** Discovery Journey (Approach 2). Central drama is time compression — the audience watches a three-month discovery happen in 12 minutes. Opening frame is the transformation cost ("1,000+ applications, 38 countries"), not a specific business failure. See `html/script-approaches.html` for the three-option evaluation; Approach 2 was selected on the basis that the strategy audience may not know the demand planning pain intimately, but speed is universally legible.

**Technical fallback (silent — not in the room):** If the live discovery run stalls during ingestion or analysis, switch to a pre-compiled output: *"Let me show you the complete picture from a run we prepared earlier — same documents, same process."* Jump directly to the operational map. The story is not sacrificed.

---

## 3. Language Guide

The platform is invisible. The business problem is the protagonist.

| Never say | Say instead |
|---|---|
| Block 1 / Block 2 / Block 3 | The platform is reading your landscape |
| Knowledge Graph | Your operational map |
| Evidence Synthesis Agent | Here's what it found |
| Pipeline is running | The discovery is running |
| High-severity gap detected | A finding that needs your input |
| Nodes and edges | How your processes connect |
| Parallel agents | It's working through everything at once |
| Discovery Copilot | A finding that needs a quick answer before we proceed |
| Gap resolution workflow | One targeted question, answered in 60 seconds |

---

## 4. Primary Demo Script — Demand Planning & Distribution

### 4.1 The Setup (0:00–2:00)

**Say:**
*"You have 1,000+ applications inherited from Sanofi, spread across 38 countries, touching every part of how Opella runs. Your transformation team needs to know what to keep, what to consolidate, what's at risk — and they need to build a credible plan for the board. Traditionally that discovery takes three months of your best people's time. We're going to show you what that picture looks like, and where the risks are, in the time it takes to have this conversation."*

**On screen:** Platform open. 12 business-readable document names visible — no technical labels. Nothing has run. Audience sees what went in.

**Don't:** Explain what the platform does before it does it. Don't mention agents, AI, or architecture.

---

### 4.2 Discovery Runs (2:00–7:00)

**Say as it runs:**
*"It's reading everything simultaneously — the process documents, the system exports, the meeting transcripts. It's building a picture of who owns what, which systems are involved, and how the process actually moves between teams. Watch what it finds."*

**On screen:** Live discovery feed with business-language status messages:
*"Reading demand planning documentation… Mapping forecast system ownership… Cross-referencing documented process against system records… Comparing Commercial Planning records with Operations records…"*
Then a findings panel begins populating.

**As findings appear, say:**
*"There — it's already found something. Three of your systems all contain European demand forecasts, and they don't agree with each other. That's not a data quality issue — that's an ownership question your landscape hasn't answered."*

**Findings that surface:**

| # | Severity | Finding | Business framing |
|---|---|---|---|
| F1 | 🔴 High | **Demand Forecast Ownership** | 3 systems hold European demand forecast data for the same SKUs and time period. Numbers do not reconcile. No documented source of truth. |
| F2 | 🔴 High | **S&OP Governance Gap** | S&OP process states Commercial Planning approves the final forecast. System records show Operations overrode it in 34% of cycles last year — without documented sign-off. |
| F3 | 🟡 Amber | **DC Allocation Model: Unverified** | Distribution Operations Guide references a "DC Allocation Model" as the tool deciding inventory allocation. No system evidence found. Could be active, a spreadsheet, or still running under TSA. |

**Beat notes:**
- Let the audience react to each finding
- Don't rush past Finding 2 — the governance gap lands hardest
- Finding 3 explicitly flagged as amber: *"This one we flagged — we're not blocking on it"*

---

### 4.3 One Finding Needs Input (7:00–10:00)

**Say:**
*"Finding 1 — the three forecast systems — needs a quick call before we can finalise the analysis. Not a workshop. A 15-minute conversation with whoever owns demand planning. The platform has already done the work: it's ranked the evidence and given us three possible answers. We pick the most likely one and proceed."*

**On screen:** Finding 1 expanded. Three candidate answers, ranked by evidence weight:
1. SAP IBP is authoritative — other systems are shadow copies
2. Regional model runs in parallel by design for local adjustments
3. Integration failure — systems should sync but data pipeline is broken

AuroPro selects option 1. Finding updates: *"Resolved — SAP IBP confirmed as system of record. Regional model flagged for decommission review."*

**After resolution, say:**
*"That's it. One targeted question, answered in 60 seconds. Finding 2 — the governance gap — we've flagged for a quick call with the Commercial Planning lead. It won't hold up the rest of the analysis. It stays visible as something to resolve, but the discovery continues."*

---

### 4.4 Your Operational Map (10:00–15:00)

**Say:**
*"Now here's something your team has never seen as a single picture. This is how demand planning, distribution, and order fulfilment connect in your landscape — which teams hand off to which, which systems are involved at each step, and where the ownership boundaries are."*

**On screen:** Business-readable domain map. Three areas: *Demand Planning*, *Distribution Management*, *Order Fulfilment*. Arrows show plain-language handoff chains. Confidence indicators on each area.

**Say — O2C downstream link:**
*"And here's the part no one puts together manually. When your demand forecast undershoots by more than 15% in a European market, your customers feel it 12 to 15 days later — in delayed orders and stockouts. The platform found that by reading the distribution logs and the order fulfilment records together. It's not a coincidence. It's a systemic pattern that's been hiding in your data."*

| Pattern | Confidence | Detail |
|---|---|---|
| 🟢 Forecast miss → Customer impact | Verified | When European demand underruns by >15%, order fulfilment rate drops 12–15 days later. Detected across 8 SKUs in 2025. O2C audit trail confirms. Traceable, repeatable consequence. |

**Beat:** Pause here. Let it land. *"No one told it to look for this connection."* This is the moment the audience leans forward.

---

### 4.5 What To Do About It (15:00–18:30)

**Say:**
*"The platform doesn't just describe the problem — it tells you what to do next and in what order. Three priorities for your demand planning domain."*

**On screen — Transformation Roadmap (three priorities only):**

**Now (0–6 months)**
- Declare SAP IBP as demand forecast system of record
- Decommission or subordinate regional model
- Resolve DC Allocation Model ownership — is it on Sanofi TSA?

**Next (6–18 months)**
- Formalise S&OP override governance — documented escalation path, system-enforced sign-off
- Consolidate demand planning stack to one source of truth across regions

**Later (18+ months)**
- Agentic demand sensing — AI-assisted forecast adjustment for seasonal peaks (Allegra spring, cold/flu winter)
- Automated stockout early-warning tied to O2C fulfilment signals

**Don't** walk through the full report. Three priorities only. The rest lives in the report for the discussion.

---

### 4.6 The Offer (18:30–20:00)

**Say:**
*"Everything you just saw ran on synthetic data built to look like Opella's post-carve-out landscape. In the pilot, this runs on one real domain of your actual landscape — your documents, your system exports, your telemetry. Your transformation team's job is to review the findings and validate the roadmap. Not produce it. Two weeks. One domain. A plan your board can act on."*

**Stop talking after "act on."** Hand the floor back. Silence is fine.

Close signal to listen for: *"Can we run this on one of our real domains?"*

---

### 4.7 Discussion & Next Steps (20:00–45:00)

Full report open on screen. Navigate wherever the audience wants to go deeper.

**Expected questions:**
- "Is the DC Allocation Model finding real?" — Yes, it's exactly the kind of unresolved TSA dependency that appears in real carve-outs. In the pilot, we either find the system or flag it for decommission planning.
- "How long does the pilot take?" — Two weeks for one domain. You get a findings review and roadmap by end of week two.
- "What data do you need from us?" — Process documents, SOPs, RACIs, system exports (schemas only — no customer data), meeting notes if available.
- "Can we see the O2C section?" — Yes. [Switch to O2C discussion or offer secondary demo.]

---

## 5. Secondary Demo Script — Order-to-Cash

**When to use:** Audience is finance or commercial-led, or audience asks to go deeper on order fulfilment/customer service during the discussion phase. Runs as a standalone 30-minute session if needed.

> Full step-by-step script (including verbatim narration, screen states, beat notes, and discussion cues) is in [`demo-script-o2c.html`](html/demo-script-o2c.html). This section captures the structural decisions and key content for the spec record.

### 5.1 Findings

| # | Severity | Finding | Business framing |
|---|---|---|---|
| F1 | 🔴 High | **Customer Master: No Single Source of Truth** | Same retail and pharmacy accounts exist in SAP ERP and SAP CRM with conflicting credit limits and payment terms. Orders are being approved against informally inflated credit limits in CRM. |
| F2 | 🔴 High | **Undocumented EDI Order Flow** | 67% of Opella Europe's order volume arrives via retail EDI. There is no SOP, no RACI owner, and no documented process for this channel. |
| F3 | 🟡 Amber | **TSA-Exposed EDI Integrations** | 6 of 14 EDI connections were established by Sanofi Shared Services. Ownership at carve-out is unconfirmed. When these connections fail, customer service calls the Sanofi IT helpdesk. |

### 5.2 Cross-Domain Pattern

🟢 **Forecast Miss → O2C Escalation Spike:** When demand forecast underruns in the primary domain, customer service escalations spike 12–15 days later. This is the same pattern visible in the Demand Planning demo — confirmed from the O2C side.

### 5.3 When to Use vs. Primary

| Primary (Demand Planning) | Secondary (O2C) |
|---|---|
| Supply chain transformation programme | Commercial / finance transformation programme |
| Audience: Strategy, Supply Chain, Digital | Audience: CFO, Sales Operations, Commercial lead |
| Entry point: "We don't know what we have" | Entry point: "Our customers keep hitting problems" |
| Cross-domain link: demand miss → customer impact (foreshadows O2C) | Cross-domain link: CS escalation spike ← demand miss (completes the picture) |

---

## 6. Synthetic Input Sets

### 6.1 Design Principle

> No single document reveals a finding. Every finding requires the platform to cross-reference at least two inputs from different categories.

The most important documents in each set are the informal ones — meeting transcripts, escalation logs, working notes. These carry the evidence that would never surface in formal documentation alone.

---

### 6.2 Demand Planning & Distribution — Input Set (12 artefacts)

**Findings to surface:**
- 🔴 F1: Demand Forecast Ownership Conflict — 3 systems, same SKUs, same period, no reconciliation
- 🔴 F2: S&OP Governance Gap — documented process contradicts system behaviour (34% override rate)
- 🟡 F3: DC Allocation Model Unverified — referenced in docs, no system evidence, possible TSA dependency
- 🟢 Cross-domain: Demand underrun >15% → fulfilment drops 12–15 days later (via WMS + O2C signals)

#### Structured (5 documents)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 01 | Demand Planning Policy — Opella Europe | PDF, ~5pp | F1, F2 | States SAP IBP as single system (contradicted by docs 08/09). States Commercial accountability (contradicted by doc 08's 34% override rate). |
| 02 | S&OP Process Document — Opella Europe | PDF, ~7pp | F2 | Explicitly documents Commercial as final approval authority with no Operations override path. Direct contradiction with system audit trail. |
| 03 | S&OP RACI Matrix — Opella Europe | PDF, ~1pp | F2 | No "Forecast Override" row — the absence of a RACI entry for an action that occurs 34% of the time is the signal. |
| 04 | Distribution Operations Runbook — Opella Europe | PDF, ~6pp | F3 | Section 4.2 references "DC Allocation Model" by name. No system name, vendor, or access details. No system export for this tool will be provided. |
| 05 | Supply Chain Application Landscape Overview | PDF, ~3pp | F1, F3 | Lists SAP IBP only — no regional model or local tool. Omission detected when cross-referenced against docs 09 and 10. |

#### Semi-Structured (2 documents)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 06 | S&OP Monthly Review Transcript — March 2026 | Text, ~2,400w | F1, F2 | "The regional model is showing 18% above what IBP has" — regional model surfaces in casual conversation, not formal documentation. Override happens verbally, no sign-off visible. |
| 07 | Regional Demand Review Notes — Q1 2026 | Text, ~800w | F1 | Notes from a regional market review. References a "local market tool" used by the France and Germany teams. Never named in any formal document. |

#### System Signals (3 documents)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 08 | SAP IBP Audit Log | CSV, 847 rows | F2 | 34% of forecast cycles show an Operations-sourced adjustment without a corresponding Commercial approval event. Pattern is consistent across all 12 months. |
| 09 | Regional Forecast Export | CSV, 203 rows | F1 | Forecast data from a system other than IBP, covering the same SKUs and periods. Numbers do not reconcile with IBP. System identifier in the export: "RegionalFC" — not listed in the application landscape (doc 05). |
| 10 | WMS Event Log | CSV, ~1,200 events | F3, Cross-domain | Fulfilment rate drops visible in Apr–May 2025 and Oct–Nov 2025. 12–15 day lag from forecast underrun events. DC Allocation Model is not referenced in any WMS event. Cross-domain link: aligns with O2C escalation clusters (O2C doc 06). |

#### Unstructured (1 document)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 11 | S&OP Exception & Escalation Log | Text, 38 entries | F2 | 76% of exceptions have no documented Commercial Planning notification. Free-text notes include: "adjusted based on Operations recommendation," "IBP number overridden ahead of executive S&OP." |

#### Comparative (1 document)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 12 | Inherited Sanofi Demand Planning SOP (2023) | PDF, ~8pp | F1, F2, F3, Context | Pre-carve-out document. Shows a centralised, pharma-grade planning model with no regional tool, strict governance, Sanofi-managed demand systems. Cross-referencing with Opella's current docs reveals the inherited model explains all three findings. |

#### Cross-Reference Map

| Docs | Finding |
|---|---|
| 01 + 02 + 03 + 08 | 🔴 F2: Policy, SOP, and RACI all assert Commercial authority. System audit log shows 34% Operations override. Three-source process-vs-reality conflict. |
| 01 + 05 + 09 | 🔴 F1: Policy and landscape both claim IBP is the only system. Regional forecast export (doc 09) shows a second system with conflicting numbers. |
| 04 + 10 | 🟡 F3: Runbook names DC Allocation Model. WMS log has no trace of it. Tool is either invisible to WMS or running outside Opella's infrastructure. |
| 10 + O2C:06 + O2C:10 | 🟢 Cross-domain: WMS fulfilment drops (doc 10) align with CS escalation clusters (O2C doc 06) and EDI fulfilment drops (O2C doc 10). Three-source cross-domain pattern. |

---

### 6.3 Order-to-Cash — Input Set (12 artefacts)

**Findings to surface:**
- 🔴 F1: Customer Master Data — No Single Source of Truth (same accounts in ERP and CRM with conflicting credit limits and payment terms)
- 🔴 F2: Undocumented EDI Order Flow (67% of orders run through retail EDI with no SOP, no RACI, no owner)
- 🟡 F3: TSA-Exposed EDI Integrations (6 of 14 EDI connections still managed by Sanofi Shared Services)
- 🟢 Cross-domain: Forecast miss → O2C escalation spike (links back to Demand Planning input set)

#### Structured (5 documents)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 01 | Order Management SOP — Opella Europe | PDF, ~6pp | F2 | A 6-page SOP that does not mention EDI at all — in a business where 67% of orders arrive via EDI. What's absent is the signal. |
| 02 | Credit Management Policy — Opella Europe | PDF, ~4pp | F1 | Refers to "the customer credit system" without naming it. When cross-referenced against docs 08 and 09 (two different credit systems, different limits), the ambiguity becomes the finding. |
| 03 | O2C Process RACI — Opella Europe | PDF, ~1pp | F2 | No RACI row for EDI order processing or EDI dispute resolution. 67% of order volume has no documented accountability. |
| 04 | EDI Integration Register — Opella Europe | PDF, ~3pp | F3 | 14 EDI connections. 8 marked "Opella Digital." 6 marked "Sanofi Shared Services / See TSA Schedule Annex C." No Annex C is provided — the reference is unresolvable from the input set alone. |
| 05 | Retail Customer Onboarding Guide — Opella Europe | PDF, ~4pp | F1, F2 | "Create the customer record in our systems" — no named system. Combined with docs 08 and 09, suggests customer setup creates parallel records by default, not by design. |

#### Semi-Structured (2 documents)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 06 | Customer Service Escalation Log — Opella Europe 2025 | CSV, 142 rows | F2, Cross-domain | 34 entries flagged as EDI-related (root_cause: "EDI order not processed — manual intervention required"). 19 stockout complaints cluster in Apr–May and Oct–Nov 2025 — aligning with demand forecast underrun periods. Free text: "customer threatened to delist Doliprane," "third time this quarter for Carrefour FR." |
| 07 | Accounts Receivable Review Notes — Q4 2025 | Text, ~600w | F1 | Explicitly names two systems and two accounts: "Carrefour France is showing two different credit limits depending on which system you look at — CRM has €2.4M, ERP has €1.8M." Boots UK payment terms discrepancy also documented. |

#### System Signals (3 documents)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 08 | SAP S/4HANA Customer Master Export | CSV, 340 rows | F1 | Top 10 retail accounts: credit limits €800K–€1.8M. 6 accounts flagged "migrated from Sanofi legacy system — 2024-05-01." These records were never reconciled with CRM post-migration. |
| 09 | SAP CRM Customer Export | CSV, 318 rows | F1 | 22 fewer records than ERP (customers created in one system, never synced). Credit limits uniformly higher than ERP for top accounts (Carrefour FR: €2.4M vs. €1.8M). Source: "manually updated by account manager post-carve-out." |
| 10 | Order Flow Analysis Export — Opella Europe 2025 | CSV, 8,420 rows | F2, Cross-domain | Channel split: EDI 67.3%, manual 21.4%, email 9.1%, fax 2.2%. EDI fulfilment rate drops to 61% during Apr–May and Oct–Nov clusters. Aligns with WMS event log in Demand Planning input set. |

#### Unstructured (1 document)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 11 | EDI Dispute Resolution — Customer Service Working Notes | Text, ~1,100w | F2, F3 | **Most important document in the set.** Informal "how we actually do it" guide written by the CS team lead for new team members. Contains: *"For the 6 older connections (Carrefour FR, Boots UK, dm, Leclerc, Lidl, Coop) — if there's an outage, contact Sanofi IT helpdesk on [number]. Opella Digital doesn't manage these yet."* No formal document contains this. The CS team lead wrote it down; no one escalated it. |

#### Comparative (1 document)

| # | Name | Format | Seeds | Engineering note |
|---|---|---|---|---|
| 12 | Inherited Sanofi Consumer Healthcare O2C SOP (2023) | PDF, ~9pp | F1, F2, F3, Context | Pre-carve-out. Pharma distributor model: low-volume, high-value, Sanofi-managed MDM, EDI as "optional for strategic accounts." Cross-referencing shows Opella's current O2C SOP is a light adaptation of this document — the inherited architecture explains all three findings. |

#### Cross-Reference Map

| Docs | Finding |
|---|---|
| 01 + 03 + 10 | 🔴 F2: SOP covers manual flow only (01) · RACI has no EDI row (03) · 67% of orders are EDI (10). Three-source confirmation that majority order volume is undocumented. |
| 07 + 08 + 09 | 🔴 F1: AR notes name the discrepancy (07) · ERP shows lower limits / Net 45 (08) · CRM shows higher limits / Net 30 (09). Named accounts, quantified conflict, two-system evidence. |
| 04 + 11 | 🟡 F3: EDI register names 6 Sanofi-established connections with unresolved TSA status (04) · CS working notes confirm "contact Sanofi IT" for those same connections (11). Operational evidence that the dependency is live, not theoretical. |
| 06 + 10 + DP:10 | 🟢 Cross-domain: Escalation log clusters (06) align with EDI fulfilment drops (10) align with WMS drops in Demand Planning set (DP:10). Only detectable by reading both input sets together. |

---

## 7. Open Questions

| Question | Status |
|---|---|
| Which systems actually need to be built to run the demo (ingestion engine, KG writer, report generator)? | → Platform architecture spec: `2026-05-30-autonomous-discovery-platform-design.md` |
| Do the synthetic input files (PDFs, CSVs) need to be generated, or is the spec sufficient for demo prep? | Open — to be confirmed |
| What report format does the demo output? (PDF, HTML, both?) | Open |
| Pilot domain for Opella — shortlist and proposed framing? | Open |

---

## 8. Related Specs

- [Autonomous Discovery Platform — High Level Design](2026-05-30-autonomous-discovery-platform-design.md)
- [Approach A — Linear Pipeline Design](2026-05-30-approach-a-linear-pipeline-design.md)
- [Approach B — Hierarchical Orchestrator Design](2026-05-30-approach-b-orchestrator-design.md)
