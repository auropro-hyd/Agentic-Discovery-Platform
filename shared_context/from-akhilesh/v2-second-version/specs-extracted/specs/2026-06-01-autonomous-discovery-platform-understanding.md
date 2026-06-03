# AuroPro Autonomous Discovery Platform — Understanding Document

**Date:** 2026-06-01
**Status:** Working Document
**Author:** Akhilesh / AuroPro
**Context:** Opella Engagement — O2C Domain Demo

---

## 1. Vision & Purpose

The AuroPro Autonomous Discovery Platform is a consulting accelerator used by AuroPro as part of enterprise transformation initiatives. It is not a standalone product sold independently — it is the tooling and methodology that powers how AuroPro runs discovery engagements faster, more rigorously, and with far less demand on client stakeholder time than traditional consulting approaches.

### The Problem It Solves

Traditional enterprise discovery takes 2–3 months of business stakeholder time: interviews, workshops, manual documentation review. For clients like Opella — in the middle of a post-carve-out transformation, with time pressure, operational disruption risk, and limited stakeholder availability — that timeline is not viable.

The platform compresses discovery to **days** by:

- Ingesting all available organisational knowledge across every input type (documents, system logs, interview transcripts, process SOPs, email threads)
- Automatically detecting patterns, contradictions, and gaps across sources
- Surfacing only high-confidence, high-severity findings for AuroPro SME review
- Resolving ambiguities through a structured Discovery Copilot interface — without requiring repeated client involvement
- Generating a full suite of clean tactical and strategic outputs once all critical gaps are resolved

### Who It Is For

| Role | Interaction |
|---|---|
| **AuroPro SME (Discovery Specialist)** | Operates the platform. Reviews high-severity gaps in the Discovery Copilot. Resolves findings and triggers report generation. |
| **Client Stakeholders** (e.g., Head of Strategy, Transformation Team) | Receive the output reports. Do not interact with the platform directly. |

---

## 2. Platform Architecture

The platform runs as a pre-pipeline configuration step followed by a four-block agentic pipeline:

```
Session Config (Pre-Pipeline)
──────────────────────────────
StrategyProfile per BU
→ confirmed by client BU lead
→ locked into PipelineState
              ↓
Block 1           Block 2                Block 3               Block 4
──────────────    ──────────────────     ─────────────────     ──────────────────
Ingest &     →   Analysis Pipeline  →   Domain Analysis   →   Report Generation
Knowledge         (merged strategy       (per-BU profile        (tactical: constant;
Construction      signal; tensions       applied per            strategic: shaped
(priority-        detected here)         domain sub-agent)      by StrategyProfile)
weighted by
merged signal)
```

### Session Configuration (Pre-Block 1)

A dedicated step that runs before Block 1. Produces confirmed **StrategyProfiles** — one per business unit — locked into PipelineState before any ingestion begins. This is what ensures strategic outputs are aimed at something specific rather than generating generic recommendations.

**StrategyProfile fields:**

| Field | Type | Purpose |
|---|---|---|
| `direction_type` | Enum | Primary strategic move: `consolidate` / `modernize` / `divest` / `stabilize` / `acquire` / `exit` |
| `horizon` | Enum | Execution window: `0–6 months` / `6–18 months` / `18+ months` |
| `strategic_constraints` | Free text | What cannot be recommended (budget caps, TSA obligations, regulatory, political) |
| `stakeholder_priorities` | List | What the BU lead cares most about from this engagement |
| `out_of_scope` | Free text | Explicit exclusions (e.g., "do not recommend greenfield builds") |
| `success_definition` | Free text | How the BU lead defines a successful engagement outcome |

**Confirmation flow:**
1. AuroPro SME populates the StrategyProfile per BU from intake materials (pre-engagement conversations, existing documents, prior context)
2. The Discovery Copilot generates a structured confirmation document for the client BU lead to review
3. BU lead reviews, edits if needed, and confirms
4. Confirmed profiles are locked into PipelineState — profiles cannot change mid-pipeline; changes require a new session

**Why this matters:** The confirmation document is the **first formal alignment artefact** of the engagement. It forces explicit articulation of strategic direction before discovery begins — and frequently surfaces misalignment between stakeholders before the platform has run a single analysis.

**Tactical vs. strategic split:**
- Tactical outputs (automation candidates, agent workflows, process redesign) are generated consistently regardless of strategic direction — the opportunity is the opportunity
- Strategic outputs (transformation roadmap, app rationalization, build-vs-buy recommendations) are fully shaped by the StrategyProfile

**O2C Demo (Opella) StrategyProfile:**

| Field | Value |
|---|---|
| `direction_type` | `consolidate` + `modernize` — rationalizing the inherited O2C landscape while modernizing for retail EDI reality |
| `horizon` | H1 (0–6 months) for tactical AI opportunities; H3 (18+ months) for app rationalization |
| `strategic_constraints` | TSA obligations with Sanofi; FMCH regulatory requirements; limited change capacity during stabilization |
| `stakeholder_priorities` | Time-to-value; reduced operational disruption; retail SLA protection (Carrefour delisting risk) |
| `out_of_scope` | No greenfield ERP replacement in engagement scope |
| `success_definition` | AI opportunities live in H1; agreed app rationalization roadmap and pilot commitment by end of engagement |

---

### Block 1 — Ingestion & Knowledge Construction

- Accepts all five input categories (see Section 4)
- Classifies each document by content type (SOP, org chart, transcript, log, etc.) — not by filename or metadata
- Extracts entities, events, actors, systems, decision points, and handoffs
- Constructs the **Knowledge Graph** — the shared data plane accessed by all downstream agents
- **Strategy relevance tagging:** Each extracted KG node receives a `strategy_relevance` attribute based on the merged StrategyProfile signal — prioritises document types most relevant to the stated directions (e.g., `consolidate` → tech assessments, integration docs, system-of-record references)

**Knowledge Graph node types:** Process, System/Application, Actor (team/role), Domain Event, Decision Point, Domain Boundary

**Edge types:** `handoff_to`, `triggers`, `owned_by`, `runs_on`, `conflicts_with`, `belongs_to_domain`

**Confidence tiers (first-class attributes on every node and edge):**
- 🟢 **Verified** — supported by document evidence AND non-prod app crawl
- 🟡 **Amber** — document evidence only, or low-severity gap carried forward
- 🔴 **Gap** — mentioned but unverifiable, contradicted, or missing system-of-record

---

### Block 2 — Analysis Pipeline + Gap Gate

Two agents run in parallel, both operating on the **merged strategy signal** (union of all BUs' confirmed StrategyProfiles):

- **Evidence Synthesis Agent** — detects cross-source patterns, sequences process events, maps handoff chains, surfaces workarounds and exceptions, flags contradictions. Actively sequences patterns that confirm or challenge the stated direction — not just patterns in general.
- **Technology Landscape Assessment Agent** — constructs the application inventory, maps functional surface area, identifies integration topology and system-to-process bindings, detects overlap and redundancy. Evaluates the app landscape against the direction (e.g., `consolidate` triggers identification of survivability candidates and dependency chains that would block consolidation).

**Gap handling — severity-split model:**

| Severity | Classification | Action |
|---|---|---|
| **High-severity** | Missing system-of-record for a critical process; unresolvable contradictions | Blocks Block 3. Surfaced to SME via Discovery Copilot. Must be resolved before pipeline continues. |
| **Low-severity** | Ambiguous ownership; minor inconsistencies | Carries forward automatically as amber-tiered nodes. Block 3 runs against them at reduced confidence. |

**Strategic tensions (new event class):** Where discovered evidence conflicts with the stated direction (e.g., direction is `consolidate` but evidence shows 4 active vendor negotiations for new point solutions). Strategic tensions are **non-blocking** — they are findings, not missing data. They route to a separate SME tray in the Discovery Copilot. The SME chooses one of three interpretations: (1) the direction needs revisiting, (2) the finding needs verification, or (3) the tension is known and accepted. Tensions never reach the client without SME review.

Once all high-severity gaps are cleared, Block 2 produces a **Verified Cohort** — a confidence-tiered snapshot of the Knowledge Graph — and passes it to Block 3.

---

### Block 3 — Domain Analysis

DDD-motivated multi-agent framework. **Handoff topology is the primary signal for domain boundary discovery** — where a process crosses a team or system boundary, that is a candidate domain boundary.

At this block, the per-BU split fully activates. Each domain sub-agent set is initialized with its BU's specific StrategyProfile — not the merged signal. This is what makes strategic outputs per-domain rather than averaged across the engagement.

| Sub-Agent | Responsibility |
|---|---|
| Bounded Context Mapper | Proposes domain boundaries from handoff chains |
| Context Map Builder | Maps relationships between domains (upstream/downstream, shared kernel, ACL) |
| Domain Event Cataloguer | Catalogs every discrete event per domain, tagged by trigger, actor, system, outcome |
| Automation Opportunity Ranker | Scores automation and agent workflow candidates by effort-to-impact ratio — direction-agnostic |
| App Rationalization Scorer | Scores consolidation candidates per domain, **shaped by `direction_type`** — `consolidate` scores by survivability; `modernize` scores by technical debt; `divest` scores by operational separability |
| Transformation Roadmap Planner | Sequences initiatives across three horizons, **constrained by `horizon` and `direction_type`** from the StrategyProfile |

**New output per domain:** Strategic Alignment Score — how well the current state positions this BU to execute its stated direction. Key input to Block 4.

---

### Block 4 — Report Generation

A single Report Generation Agent synthesises all block outputs into the full deliverable suite (see Section 5). No further human gates — generation is automatic once the Verified Cohort is available.

---

## 3. Discovery Copilot — SME Interface

The Discovery Copilot is the **only human-in-the-loop surface** in the pipeline. It sits inside Block 2's Gap Gate and is used exclusively by the AuroPro SME — not the client.

**What it handles:**
- Only high-severity gaps that are actively blocking Block 3
- For each gap, the agent proposes 2–3 candidate resolutions based on available evidence
- The SME selects one, provides a free-text override, or resolves via any available channel (email, chat, app crawl, targeted stakeholder clarification)
- The Copilot records the outcome; the Knowledge Graph updates; the pipeline continues

**Resolution model — B now, C later:**

| Model | Description |
|---|---|
| **Current (B)** | Guided resolution — agent proposes candidates, SME selects or overrides |
| **Upgrade (C)** | Action-triggered resolution — "run app crawl on System X", "send clarification to [contact]", "mark as out of scope" — each action has a defined outcome that feeds directly back into the Knowledge Graph |

**Key principle:** The Copilot is a communication hub, not a meeting scheduler. Once all high-severity gaps are resolved, generation continues automatically. There are no further human approval gates until the output reports are handed to the client.

**What this means for the output:** All six reports reflect a clean, verified state. The Current State Assessment contains no conflict flags, no red/amber status indicators, no diagnostic language. Every finding was resolved before the reports were generated.

---

## 4. Input Types

The platform accepts five input categories:

| Category | Examples |
|---|---|
| **Structured** | Process SOPs, org charts, system inventories, contracts, credit policies |
| **Semi-structured** | Email threads, meeting notes, Confluence pages, ticket logs |
| **System Signals** | ERP exception logs, EDI error reports, audit trails, integration failure dumps |
| **Unstructured / Conversational** | Interview transcripts, workshop recordings, Slack exports |
| **Comparative** | Same process described across multiple sources or teams — used to detect contradictions and workarounds |

**O2C Demo (Opella):** 12 synthetic inputs across all five categories. All business value for the three portfolio opportunities is derivable from these 12 inputs alone — no additional documents required.

---

## 5. Output Suite — The 6 Deliverables

The output suite is **6 separate standalone reports** — not one combined document. Each is a clean, client-ready deliverable. They are generated in sequence from the same Block 4 synthesis pass.

### Classification

| # | Report | Classification | Purpose |
|---|---|---|---|
| 01 | Current State Assessment | **Foundational** | Documents what exists today — factual, no diagnostic language |
| 02 | Pain Points & Opportunity Report | **Tactical** | Evidence layer — why the opportunities exist |
| 03 | Transformation Recommendation | **Strategic** | Prioritisation — which opportunities to pursue and in what order |
| 04 | AI Opportunity Portfolio | **Tactical (Primary)** | Detailed per-opportunity documentation — the centrepiece |
| 05 | Transformation Roadmap | **Strategic** | Long-term sequencing — AI opportunities + app rationalization |
| 06 | Supporting Artefacts | **Reference** | Diagrams, maps, catalogues, and source index |

> 📎 **Visual reference:** [`html/o2c-report-suite-hl.html`](html/o2c-report-suite-hl.html) — High-level suite overview showing all 6 report cards with section listings

---

### 5.1 Current State Assessment (Foundational)

**Purpose:** Establishes a factual, verified baseline of how the process works today. This is not a gap analysis — it is documentation of the as-is state after all findings have been resolved.

**Key sections:**

| Section | Content |
|---|---|
| Domain Overview | Scope, volume, ownership summary |
| Process Inventory | End-to-end process steps, actors, systems involved |
| Process Flow | Visual chain from order receipt through to collections |
| Ownership Map | Who owns each step — role, team, system |
| System Inventory | All systems connected to the domain, function, integration type |
| Handoff Catalogue | Where processes cross team or system boundaries |

**What it is NOT:** No conflict flags. No red/amber/green status. No "gaps identified" language. The copilot has resolved everything — this document is clean documentation of the verified state.

**O2C Example:**
- Process chain: EDI order receipt → credit check → fulfilment → invoicing → AR collections
- Key actors: Customer Service team, Finance/Credit, Warehouse, Accounts Receivable
- Systems: SAP S/4HANA (ERP), EDI middleware, CRM, AR module
- Notable fact: 67% of orders now arrive via retail EDI (Carrefour, Boots, dm) — a structural shift from the pharma-distributor model the O2C process was originally designed for

> 📎 **Visual reference:** [`html/o2c-report-suite-hl.html`](html/o2c-report-suite-hl.html) (scroll to Report 01 section) — sidebar nav, domain overview stats, process flow chain, 2-column process layout, RACI table, system inventory

---

### 5.2 Pain Points & Opportunity Report (Tactical)

**Purpose:** Documents every confirmed pain point from the discovery process, ranked by business impact. This is the evidence layer — it explains *why* the opportunities in Report 04 exist. Derived from Block 2 Evidence Synthesis output.

**Key sections:**

- **Pain Point Register** — ranked by severity and business impact
- **Root Cause Analysis** — what is causing each pain point at a process and system level
- **Process Failure Patterns** — recurring failure modes across the domain (not one-off incidents)
- **Opportunity Signal** — each pain point mapped to its candidate opportunity in Report 04
- **Cross-domain Patterns** — where the pain in one domain causes downstream consequences elsewhere

**O2C Example:**

| Pain Point | Root Cause | Business Impact |
|---|---|---|
| Customer master fragmentation | 3 conflicting CRM/ERP records for the same retail accounts post-carve-out | €600K+ credit exposure; wrong credit limits applied to orders |
| EDI order exception handling | No automated triage — every exception lands in CS queue | 34 manual CS incidents/year; SLA breach risk; potential retail delisting |
| Credit coverage gap | O2C credit check process designed for pharma distributors, not retail EDI | 67% of EDI orders (5,665/year) proceed without credit assessment |
| TSA EDI dependency | 6 EDI connections for retail accounts still managed by Sanofi post-carve-out | Pipeline cannot operate fully autonomously while connections are outside Opella's control |

**Cross-domain pattern (O2C):** Demand forecast miss → O2C escalation spike 12–15 days later. Excess orders hit credit holds and exception queues simultaneously, compounding the manual load.

---

### 5.3 Transformation Recommendation (Strategic)

**Purpose:** Recommends which opportunities to pursue and in what order, using a value vs. feasibility framework. This is the sequencing and prioritisation document — it answers the question "what do we do first and why?" Shaped by the BU's StrategyProfile: the `direction_type` and `strategic_constraints` directly influence which opportunities are foregrounded and how trade-offs are framed.

**Key sections:**

- **Value vs. Feasibility Matrix** (2×2: High/Low Value × High/Low Feasibility) — each opportunity plotted by business impact and delivery complexity
- **Opportunity Ratings Table** — score bars, rationale, intervention type, and quadrant placement per opportunity
- **Sequencing Rationale** — why certain opportunities must precede others; which can run in parallel
- **Dependencies** — what must be true before each opportunity can begin
- **Strategic Readiness Assessment** — the gap between the current state and what the stated strategic direction requires to execute (informed by the Strategic Alignment Score from Block 3 and by resolved strategic tensions)

**O2C Quadrant Placement:**

| Quadrant | Opportunity | Rationale |
|---|---|---|
| **Do First** (High Value · High Feasibility) | Opp 1 — Customer Master Reconciliation | €600K+ exposure resolved in one structured session. No new technology required. |
| **Do First** (High Value · High Feasibility) | Opp 2 — EDI Order Exception Pipeline | Deterministic automation. Eliminates 34 incidents/year. Runs in parallel with Opp 1. |
| **Plan For** (High Value · Low Feasibility) | Opp 3 — AI Credit Decisioning Agent | Highest long-term value. Requires Opp 1 complete as prerequisite. Multi-month build. |
| **Consider** (Medium Value · Medium Feasibility) | TSA Connection Ownership Transfer | Risk mitigation. No tech build — legal and contractual action. Enables Opp 2 to run fully autonomously. |
| **Deprioritise** | — | No opportunities in this quadrant for O2C. |

> 📎 **Visual reference:** [`html/value-feasibility-matrix.html`](html/value-feasibility-matrix.html) — Full 2×2 matrix with detail table, score bars, intervention type badges, and quadrant placement

---

### 5.4 AI Opportunity Portfolio (Tactical — Primary Deliverable)

**Purpose:** The centrepiece of the output suite. Detailed documentation of each identified AI and automation opportunity — not summary cards, but full working documentation: what the problem is, how the intervention works, what changes in the process, what it delivers, and everything required to implement it.

**Important:** The portfolio is **direction-agnostic** — it captures every opportunity the platform identifies regardless of the BU's stated strategic direction. Tactical opportunities (automation, AI agents, HITL workflows) are equally valid whether the BU is consolidating, modernising, or stabilizing. The StrategyProfile does not filter the portfolio — it shapes the Roadmap (Report 05) where those opportunities get sequenced.

**Scale:** In an actual engagement, the portfolio may contain 5–15 opportunities across a domain. The O2C demo uses three opportunities as representative examples. The structure and depth of documentation is identical regardless of how many opportunities are identified — each gets the full treatment below.

**Per-opportunity structure:**

| Section | Content |
|---|---|
| **Opportunity Overview** | What the problem is, why it matters, intervention type |
| **Before Process** | Current state process steps, actors, systems, failure points — elaborated in full, not summarised |
| **After Process** | Redesigned process with the intervention in place — step by step |
| **Business Impact** | Quantified: cost savings, time reduction, risk mitigation, revenue protection — with derivation |
| **Implementation Approach** | High-level technical approach for delivering the intervention |
| **Required System Integrations** | Which systems connect, what data flows between them |
| **Success Metrics** | How success is measured post-implementation |
| **Dependencies** | What must be resolved before this opportunity can start |
| **Risks** | Delivery risks, adoption risks, data quality risks |

**O2C Portfolio (3 reference opportunities for demo):**

---

**Opportunity 1 — Customer Master Reconciliation**
*Intervention type: HITL Workflow*

- **Problem:** Three conflicting CRM and ERP records exist for the same retail accounts (Carrefour, Boots, dm). Post-carve-out from Sanofi, records were migrated inconsistently. Credit limits are applied against the wrong record — resulting in €600K+ of unhedged credit exposure.
- **Before:** CS team manually identifies the correct record at point of order. Credit check runs against whichever record the system resolves first. Errors propagate into AR collections.
- **After:** One structured reconciliation session with Credit and CS teams, assisted by an AI deduplication agent that surfaces conflicts and proposes the canonical record. Ongoing: a sync rule between CRM and ERP prevents re-fragmentation.
- **Business impact:** €600K+ credit exposure resolved. Prerequisite for Opp 3 — the AI Credit Agent requires a clean customer master to function.
- **Integration:** CRM ↔ ERP customer master sync
- **Success metric:** Zero duplicate customer records for active retail accounts; credit limit accuracy rate > 99%
- **Dependency:** None. Can start immediately.
- **Risks:** Business adoption — Credit team must agree on canonical record rules; data migration errors if reconciliation is done without validation gates

---

**Opportunity 2 — EDI Order Exception Pipeline**
*Intervention type: Automation Pipeline*

- **Problem:** Every EDI order exception (wrong quantity, missing PO reference, format error) lands in the CS queue for manual triage. 34 incidents per year resolved manually. No classification, no auto-routing, no SLA tracking. Retail partners (Carrefour) have delisting thresholds if fulfilment SLAs are missed.
- **Before:** EDI middleware flags error → CS agent receives it → manually classifies → manually routes to correct team → manually resolves → manually closes
- **After:** Deterministic rule engine classifies exception by type → auto-routes to the correct resolution path (resubmit, escalate to partner, flag to finance) → only genuine ambiguities reach CS
- **Business impact:** Eliminates ~34 manual CS incidents/year. Removes SLA breach risk. Reduces delisting exposure. Runs independently — does not require Opp 1 to be complete.
- **Integration:** EDI middleware → ERP order management module
- **Success metric:** < 5 manual CS interventions per year for EDI exceptions; SLA compliance rate > 98%
- **Dependency:** None. Can run in parallel with Opp 1.
- **Risks:** Rule completeness — edge cases not covered by initial rule set will still hit CS; EDI format changes from retail partners may break rules without versioning

---

**Opportunity 3 — AI Credit Decisioning Agent**
*Intervention type: AI Agent*

- **Problem:** 67% of EDI orders (approximately 5,665/year) proceed through fulfilment without a credit assessment. The credit check process was designed for pharma distributor relationships — it does not scale to retail EDI volumes. Result: significant unhedged credit exposure across the retail order book.
- **Before:** Credit team manually reviews select accounts. Retail EDI orders bypass the check by default. No system-level credit gate on the EDI channel.
- **After:** An AI agent sits on the EDI order stream and assesses credit risk per order in real time. It uses the clean customer master (from Opp 1), order history, and credit policy rules to approve, flag, or hold each order. Flagged orders route to a credit analyst for human review. Approved orders proceed automatically.
- **Business impact:** Closes the 67% credit coverage gap across ~5,665 EDI orders per year. Reduces unhedged exposure across the full retail order book.
- **Integration:** ERP customer master + credit module + EDI order stream (real-time)
- **Success metric:** Credit assessment coverage > 95% of EDI orders; < 2% false positive hold rate (orders incorrectly blocked)
- **Dependency:** **Opp 1 must be complete.** The agent requires a clean, deduplicated customer master to assign the correct credit limit at order assessment time. Running this on fragmented data produces unreliable decisions.
- **Risks:** Model confidence calibration — agent must be tuned to avoid over-blocking legitimate orders; change management — credit analysts must trust and act on agent flags consistently

---

### 5.5 Transformation Roadmap (Strategic)

**Purpose:** Sequences all initiatives — tactical (AI/automation) and strategic (application rationalization, modernization, consolidation) — across three time horizons. This is the long-game document. It shows how the immediate AI opportunities connect to the client's broader transformation objectives: which applications consolidate, which migrate, which are decommissioned, and on what timeline. This report is **fully shaped by the StrategyProfile** — the `direction_type` and `horizon` determine how initiatives are sequenced, the App Rationalization Scorer's output determines which applications survive vs. consolidate, and the `strategic_constraints` bound what can be recommended.

**Key sections:**

- **Three-horizon view:** 0–6 months, 6–18 months, 18+ months
- **Initiative sequencing** — with dependency lines showing what unblocks what
- **Application rationalization pathway** — which systems consolidate, which migrate, which are decommissioned, and which are replaced with build/buy/configure decisions
- **Build vs. Buy vs. Configure recommendations** — per domain
- **Governance model** — how the agentic layer is owned, maintained, and monitored post-deployment (drift and hallucination management)
- **Strategic KPI framework** — baseline → target state → leading indicators per initiative

**What makes this different from Report 03 (Transformation Recommendation):**
- Report 03 answers: *"Which opportunities should we prioritise and why?"* (near-term focus)
- Report 05 answers: *"How do all the initiatives — immediate and long-term — fit together into a transformation programme?"* (full-horizon view, including application consolidation goals)

**O2C Horizon view:**

| Horizon | Initiatives |
|---|---|
| **H1 (0–6 months)** | Opp 1 — Customer Master Reconciliation; Opp 2 — EDI Exception Pipeline; TSA Connection Ownership Transfer |
| **H2 (6–18 months)** | Opp 3 — AI Credit Decisioning Agent; EDI middleware assessment |
| **H3 (18+ months)** | Application rationalization — CRM consolidation, EDI middleware modernisation, ERP credit module upgrade |

> 📎 **Visual reference:** [`html/design-section1-timeline-v3.html`](html/design-section1-timeline-v3.html) — Transformation Roadmap timeline mockup (three-horizon Gantt-style view)

---

### 5.6 Supporting Artefacts (Reference)

**Purpose:** All generated artefacts that support the five primary reports. These are auto-generated from Block 3 Domain Analysis output and the Knowledge Graph. They are shared as a reference pack alongside the primary reports — not standalone documents, but companion material that clients and implementation teams will refer back to.

**Contents:**

| Artefact | Description |
|---|---|
| **Process diagrams** | Auto-generated from Block 3 — one per key process |
| **Context maps** | DDD-style domain relationship maps (upstream/downstream, shared kernel, ACL boundaries) |
| **Data flow diagrams** | Customer master data flow; EDI integration topology |
| **Ownership maps** | Role/team/system responsibility per process step |
| **Domain event catalogue** | Every discrete event, trigger, actor, system, and outcome — tagged by domain |
| **Exception and workaround register** | Block 2 Evidence Synthesis output — all confirmed workarounds and exception patterns |
| **Source document index** | The input documents with annotation showing how each contributed to findings |
| **Technical specs** | System integration specs for opportunities requiring new connections |

---

## 6. Intervention Type Taxonomy

Every opportunity in the AI Opportunity Portfolio is classified by intervention type. The type determines the implementation approach, required tooling, and the human-in-the-loop profile.

| Type | Description | Human Involvement | O2C Example |
|---|---|---|---|
| **Modernisation** | Structural changes — migration, consolidation, ownership transfer. No AI. | High initially; zero ongoing | TSA Connection Ownership Transfer |
| **Automation Pipeline** | Deterministic rule-based automation. No AI judgement required. Rules are explicit and auditable. | Minimal — exception escalations only | EDI Order Exception Pipeline |
| **AI Agent** | LLM or ML-powered agent making decisions within defined parameters. Escalates to human on exceptions or low-confidence cases. | Review of flagged exceptions | AI Credit Decisioning Agent |
| **HITL Workflow** | Human-in-the-loop process with structured AI assistance. AI surfaces options and evidence; human makes the final call. | High — human is the decision-maker | Customer Master Reconciliation |

---

## 7. Deployment Strategy

The platform ships in two architectural forms depending on engagement phase:

| Phase | Approach | Description |
|---|---|---|
| **Demo** | Approach A — Linear Pipeline | AuroPro-hosted. Synthetic FMCH data. One domain end-to-end. Explicit phase gates — simple, predictable, easy to demo. |
| **Pilot** | Approach A | AuroPro-hosted. One real Opella domain under NDA. Same linear model. |
| **Engagement** | A → B | Full domain-by-domain sprints. Hierarchical Orchestrator introduced as volume and complexity scale. |
| **Platform** | Approach B — Hierarchical Orchestrator | Multi-engagement, multi-client. Orchestrator as control plane — owns pipeline state, gap routing, and audit trail. Agents promoted to stateless workers. |

**Upgrade path:** Approach A → B is a control model upgrade, not a rewrite. The same agents run in both — what changes is the orchestration layer. This means the demo is built on the same components that will power the production platform.

---

## 8. O2C Demo — Opella Context

**Client:** Opella — global FMCH (fast-moving consumer healthcare), post-carve-out from Sanofi in 2024
**Domain in scope:** Order-to-Cash (O2C)
**Core challenge:** The O2C process was designed for pharma distributor relationships. 67% of actual orders now arrive via retail EDI (Carrefour, Boots, dm, etc.). The process has not caught up with the distribution shift — resulting in credit exposure, manual exception handling, and SLA risk.

**Demo format:** 20 minutes within a 60-minute session
- 0:00–3:30 — Synthetic inputs briefing + upload
- 3:30–7:00 — Discovery process walkthrough (analysis + copilot gap resolution)
- 7:00–17:30 — Full output suite walkthrough (all 6 reports)
- 17:30–20:00 — Next steps + pilot framing

**Audience:** Head of Strategy + Transformation team. They care about business impact, sequencing rationale, and how quickly they can move to a pilot.

### Portfolio Summary

| # | Opportunity | Type | Quadrant | Key Impact |
|---|---|---|---|---|
| 1 | Customer Master Reconciliation | HITL Workflow | Do First | Resolves €600K+ credit exposure. Prerequisite for Opp 3. |
| 2 | EDI Order Exception Pipeline | Automation | Do First | Eliminates 34 CS incidents/year. Removes SLA breach risk. |
| 3 | AI Credit Decisioning Agent | AI Agent | Plan For | Closes 67% credit coverage gap across 5,665 EDI orders/year. |
| T | TSA Connection Ownership Transfer | Modernisation | Consider | Resolves Sanofi-managed EDI dependency. Enables Opp 2 autonomy. |

### Business Value Derivation (all from 12 existing synthetic inputs)

| Figure | Source |
|---|---|
| €600K+ credit exposure | Docs 07 (customer master extract) + 08 (credit limit report) + 09 (AR ageing analysis) |
| 34 CS incidents/year | Doc 06 (EDI exception log) |
| ~370 orders miss SLA per cluster event | Doc 10 (EDI volume analysis + demand forecast miss pattern): 5,665 ÷ 12 months × 2-month cluster window × 39% miss rate |
| 5,665 EDI orders/year | Doc 10 (order volume breakdown by channel) |

---

## 9. Open Items

The following areas are not yet fully resolved:

| Item | Status |
|---|---|
| Report 04 detailed HTML per opportunity (before/after process, integration view, success metrics) | Not yet built |
| Report 02 (Pain Points & Opportunity) — full standalone HTML | Not yet built |
| Report 05 (Transformation Roadmap) — full standalone HTML with app rationalization section | Not yet built |
| Report 06 (Supporting Artefacts) — format and layout | Not yet designed |
| Demo narration script (minutes 7:00–17:30) | Explicitly deferred |
| Context map and ownership map visuals | Marked "to be designed" |
| Knowledge Graph demo representation | Open question from platform design doc |
| Demo — what does the Discovery Copilot surface look like in the 20-min walkthrough? | Not specified |

---

*References:*
- Platform architecture: [`2026-05-30-autonomous-discovery-platform-design.md`](./2026-05-30-autonomous-discovery-platform-design.md)
- Discovery Session Configuration: [`2026-05-31-discovery-session-configuration-design.md`](./2026-05-31-discovery-session-configuration-design.md)
- Opella engagement design: [`../../Agentic Discovery Platform/Opella - Autonomous Discovery Platform.md`](../../Agentic%20Discovery%20Platform/Opella%20-%20Autonomous%20Discovery%20Platform.md)
- Visual HTML files: [`html/`](html/)
