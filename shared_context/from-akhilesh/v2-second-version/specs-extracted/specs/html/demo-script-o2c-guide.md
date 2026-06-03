# Demo Script Guide — Order-to-Cash

**Last updated:** 2026-06-01
**HTML script:** `docs/superpowers/specs/html/demo-script-o2c.html`
**Design spec:** `docs/superpowers/specs/2026-06-01-o2c-tactical-output-design.md`
**Synthetic inputs:** `docs/superpowers/specs/html/synthetic-inputs-o2c.html`

---

## What this script is for

This is the O2C secondary demo script for the Opella engagement. Use it when the primary Demand Planning demo is not running, when the audience is finance or CFO-led, or when the meeting pivots to Order-to-Cash.

The session structure:
- **0–20 min:** Demo (this script)
- **20–45 min:** Discussion and Q&A

The demo is 20 minutes. It does not describe how the platform is implemented. It shows what the platform produces and why it matters.

---

## Session Configuration — Before the Demo Runs

Before discovery starts, the platform requires a confirmed StrategyProfile. This is not a live demo step — it happens in the pre-engagement setup, before the 20-minute clock starts. The presenter should be aware of it because (a) the Setup section (0:00–1:30) can reference that Opella has already confirmed their direction, and (b) every strategic output the audience sees is shaped by it.

**What a StrategyProfile is (reference only — do not use this language on screen):**

| Field | Opella O2C Value |
|-------|-----------------|
| `direction_type` | Consolidate + Modernize — rationalizing the inherited O2C landscape while modernizing for retail EDI reality |
| `horizon` | H1 (0–6 months) for AI opportunities; H3 (18+ months) for app rationalization |
| `strategic_constraints` | TSA obligations with Sanofi; FMCH regulatory requirements; limited change capacity during stabilization |
| `stakeholder_priorities` | Time-to-value; reduced operational disruption; retail SLA protection (Carrefour delisting risk) |
| `out_of_scope` | No greenfield ERP replacement in engagement scope |
| `success_definition` | AI opportunities live in H1; agreed app rationalization roadmap and pilot commitment by end of engagement |

**Why this matters for the demo:**
The StrategyProfile confirmation document is the first formal alignment artefact of the engagement — produced before any analysis runs. It forces explicit articulation of strategic direction and frequently surfaces stakeholder misalignment before the platform has run a single analysis. In the demo setup (0:00–1:30), the presenter can note that this document already exists — Opella has stated their direction, and every strategic recommendation the audience is about to see is aimed at that direction specifically.

**Tactical vs. strategic split — key for the output walkthrough:**
- Tactical outputs (AI Opportunity Portfolio — Report 04) are direction-agnostic. The platform identifies every opportunity regardless of stated direction. The portfolio the audience sees would look the same whether Opella said "consolidate," "modernize," or "stabilize."
- Strategic outputs (Transformation Roadmap — Report 05) are fully shaped by the StrategyProfile. The sequencing, app rationalization decisions, and horizon placement are specific to Opella's confirmed consolidate + modernize direction and TSA constraints. Use this to explain why the roadmap looks the way it does.

---

## 20-Minute Structure

| Time | Section | Purpose |
|------|---------|---------|
| 0:00–1:30 | Setup | Name the business mismatch — not the technology. Note that Opella's strategic direction has already been confirmed — every strategic output is aimed at that direction. |
| 1:30–5:00 | Discovery Runs | Let the three findings surface |
| 5:00–8:00 | Gap Resolution | Resolve Finding 1, route Findings 2 and 3. Two resolution trays: blocking gaps (Findings 1 and 2) and strategic tensions (Finding 3). |
| — | *Output Suite begins* | — |
| 8:00–9:30 | Current State Assessment | Domain map, system context, ownership map |
| 9:30–11:00 | Pain Points & Opportunity Report | 4 findings quantified with business impact |
| 11:00–12:00 | Transformation Recommendation | Value/feasibility matrix + sequencing rationale + Strategic Readiness Assessment (bridge to portfolio) |
| 12:00–16:00 | **AI Opportunity Portfolio** | **Primary output — 3 full opportunities with before/after** |
| 16:00–17:00 | Transformation Roadmap | Horizon sequencing shaped by Opella's stated direction — consolidate + modernize. Note: roadmap is direction-specific; portfolio was direction-agnostic. |
| 17:00–17:30 | Supporting Artefacts | Navigation — name them, don't walk through |
| 17:30–20:00 | The Offer | Hard close |

**The portfolio is the centrepiece.** Everything before 12:00 is setup. Everything after 16:00 is close. Give the portfolio its 4 minutes.

---

## The Three O2C Findings

### Finding 1 — Customer Master: No Single Source of Truth 🔴
**What it is:** Same retail/pharmacy customers exist in SAP ERP, SAP CRM, and the AR system with conflicting credit limits and payment terms.
**Key example:** Carrefour FR — €2.4M in CRM, €1.8M agreed limit in ERP. Boots UK — Net 30 in CRM, Net 45 in ERP.
**Resolution during demo:** Select SAP CRM as authoritative — ranked first by evidence (most complete, most recently updated).
**Source documents:** Doc 07 (AR Review Notes), Doc 08 (SAP ERP Export), Doc 09 (SAP CRM Export)

### Finding 2 — 67% of Orders Running Without Governance 🔴
**What it is:** Order Management SOP documents a specialty pharma distributor flow. System evidence shows 67% of actual orders arrive via retail EDI — undocumented, unowned.
**Resolution during demo:** Not resolved on the spot — flagged as a process documentation sprint (Operations lead). Stays in the output as priority action.
**Source documents:** Doc 01 (Order Management SOP), Doc 03 (O2C RACI), Doc 10 (Order Flow Export)

### Finding 3 — 6 EDI Integrations with Unverified Ownership 🟡
**What it is:** 6 of 14 retail EDI connections (Carrefour, Boots, dm) were established under Sanofi Shared Services with no carve-out transfer documentation. CS working notes reference "Sanofi IT helpdesk" as the contact for failures — the clearest evidence of non-transfer.
**Tray:** This is a strategic tension — a non-blocking finding where the evidence (Sanofi-managed connections still active) conflicts with the stated direction (consolidate + modernize means operating autonomously). It does not block the pipeline. It routes to a separate SME tray in the Discovery Copilot. The SME reviews it and chooses one of three interpretations: (1) the direction needs revisiting, (2) the finding needs verification, or (3) the tension is known and accepted (which is the case here — TSA obligations are an explicit constraint in the StrategyProfile). This finding never reaches the client without SME review.
**Resolution during demo:** Acknowledged as a known TSA constraint. SME marks it as accepted tension. Routed to Digital and Legal teams — not an AI opportunity. Flagged for TSA exit planning.
**Source documents:** Doc 04 (EDI Integration Register), Doc 11 (CS Working Notes)

---

## Discovery Copilot — Two-Tray Model (Presenter Reference)

The Discovery Copilot handles two distinct types of findings. The presenter needs to understand this distinction because Findings 1, 2, and 3 land in different trays.

| Tray | Finding type | Blocking? | Action |
|------|-------------|-----------|--------|
| **Blocking gaps tray** | Missing system-of-record; unresolvable contradiction; no authoritative source | Yes — pipeline cannot continue | SME selects from 2–3 candidate resolutions or overrides. Knowledge Graph updates. Pipeline continues. |
| **Strategic tensions tray** | Evidence conflicts with stated strategic direction — but data is present and unambiguous | No — pipeline continues | SME picks one of three interpretations: (1) direction needs revisiting, (2) finding needs verification, (3) tension is known and accepted. Tension never reaches client without SME review. |

**Where each O2C finding lands:**

| Finding | Tray | Why |
|---------|------|-----|
| Finding 1 — Customer Master conflict | Blocking gaps | No authoritative credit limit. Platform cannot proceed without a designated system of record. |
| Finding 2 — 67% EDI undocumented | Blocking gaps | Process ownership is unassigned. This is missing data, not conflicting evidence. |
| Finding 3 — Sanofi-managed EDI connections | Strategic tensions | The evidence is clear — 6 connections are outside Opella's control. The conflict is with the stated consolidate + modernize direction (which requires autonomous operation). TSA constraints are already in the StrategyProfile, so SME marks this as accepted tension. |

**During the demo:** The presenter does not need to use the word "tray" or explain this model in narration. Show the Copilot surface, resolve Finding 1 on screen, indicate Findings 2 and 3 are routed differently. The distinction will come out in Q&A if the audience asks how the platform handles issues that aren't blocking.

---

## The Output Suite — 6 Deliverables

The output suite is what the platform produces. All six deliverables are shown on screen. Walk through them in order after Finding resolution.

### ① Current State Assessment (8:00–9:30)
Three panels: Domain Map (two O2C flows — documented 33% vs. actual EDI 67%), System Context (five systems with ownership), Ownership Map (RACI per process step with EDI credit review row blank).

### ② Pain Points & Opportunity Report (9:30–11:00)
Four items with business impact figures:
- **€600K+** — customer master credit over-exposure
- **34 incidents/yr** — EDI exception handling burden on CS
- **6 of 14 EDI** — TSA-exposed connections (Legal/Digital action)
- **5,665 orders/yr** — no credit check on 67% of EDI volume

Each item includes a feasibility read.

### ③ Transformation Recommendation (11:00–12:00)
A value/feasibility 2×2 matrix with each opportunity plotted by business impact and delivery complexity. Supported by:
- Opportunity ratings table — score bars, rationale, intervention type, quadrant placement
- Sequencing rationale — why certain opportunities must precede others; which run in parallel
- Dependencies — what must be true before each can begin
- Strategic Readiness Assessment — the gap between Opella's current state and what their stated consolidate + modernize direction requires to execute

The Strategic Readiness Assessment is informed by the Strategic Alignment Score produced during analysis and by any resolved strategic tensions. This is shaped by the StrategyProfile — present it as specific to Opella's direction, not a generic readiness view.

This is the bridge to the portfolio. Spend 60 seconds on the matrix placement, name the Strategic Readiness Assessment, then move.

### ④ AI Opportunity Portfolio (12:00–16:00) — PRIMARY
Three reference opportunities with full per-opportunity documentation. Important framing notes for the presenter:

- These three are reference examples for the demo. In an actual engagement, the portfolio contains 5–15 opportunities across a domain — the depth of documentation is identical regardless of scale.
- Before/after process documentation is elaborated in full, not summarised — every step, actor, system, and failure point is written out. If the audience questions whether this is comprehensive, the detail on screen is the answer.
- The portfolio is direction-agnostic. Every opportunity the platform identifies appears here regardless of Opella's stated StrategyProfile. Use this to distinguish it from the Roadmap: "The portfolio shows every opportunity we found. The roadmap is where Opella's direction determines what happens first."

Per-opportunity structure on screen: Opportunity Overview, Before Process, After Process, Business Impact (with derivation), Implementation Approach, System Integrations, Success Metrics, Dependencies, Risks.

| Opportunity | Type | Impact | Sequence |
|-------------|------|--------|----------|
| Customer Master Reconciliation | HITL Workflow | €600K+ exposure | Resolve first |
| EDI Exception Pipeline | Automation Pipeline | 34 incidents/yr, ~370 orders miss SLA per cluster | Run in parallel |
| AI Credit Decisioning Agent | AI Agent | 5,665 orders/yr unchecked | After Opp 1 |

### ⑤ Transformation Roadmap (16:00–17:00)
H1 (0–6 months): Opp 1 (Customer Master Reconciliation) + Opp 2 (EDI Exception Pipeline) + TSA Connection Ownership Transfer.
H2 (6–18 months): Opp 3 (AI Credit Decisioning Agent) + EDI middleware assessment.
H3 (18+ months): Application rationalization — CRM consolidation, EDI middleware modernisation, ERP credit module upgrade.

The sequencing is shaped by two things: the dependencies the platform identified AND Opella's confirmed StrategyProfile. Consolidate + modernize with H1 tactical / H3 app rationalization is why the roadmap is structured this way. A client with a different direction (stabilize, for example) would see a different roadmap from the same portfolio. Name this explicitly — it makes the roadmap feel purpose-built rather than generic.

### ⑥ Supporting Artefacts (17:00–17:30)
Six navigable artefacts: process map, data flow diagram, application dependency chart, decision rationale, source documents, RACI analysis. Name them. Don't walk through them unless asked.

---

## The Three Portfolio Opportunities — Source Derivation

### Opportunity 1 — Customer Master Reconciliation (HITL Workflow)

**Business impact:** €600K+
**Derivation:**
- Doc 07 (AR Review Notes): names Carrefour FR discrepancy — "CRM shows €2.4M, ERP agreed limit is €1.8M"
- Doc 08 (SAP ERP Customer Master Export): 340 rows, includes €1.8M Carrefour FR credit limit
- Doc 09 (SAP CRM Customer Export): 318 rows (22 fewer than ERP), includes €2.4M Carrefour FR limit
- Delta = €600K uninstructed exposure. 22 accounts present in ERP, absent in CRM.
- Doc 07 also names Boots UK Net 30/Net 45 payment term mismatch.

**Prerequisite for:** Opportunity 3 (the credit agent needs a single authoritative limit per customer)

### Opportunity 2 — EDI Exception Pipeline (Automation Pipeline)

**Business impact:** 34 CS interventions/yr, ~370 orders miss SLA per cluster
**Derivation:**
- Doc 06 (CS Escalation Log 2025): 34 entries tagged "EDI order not processed — manual intervention required"
- Doc 10 (Order Flow Export): SLA stable at 94%, drops to 61% during Apr–May and Oct–Nov clusters. 67.3% of 8,420 orders = 5,665 EDI orders/yr. ~472/month. 2-month cluster × 39% miss rate = ~370 orders per cluster event.
- Doc 11 (CS Working Notes): re-entry process documented informally, reference to Sanofi IT helpdesk
- Doc 04 (EDI Integration Register): 14 connections, 6 flagged as Sanofi-established

**Independent of Opportunity 1** — can run in parallel from day one.

### Opportunity 3 — AI Credit Decisioning Agent (AI Agent)

**Business impact:** 5,665 orders/yr (67.3%) with no credit check
**Derivation:**
- Doc 02 (Credit Management Policy): defines credit review process for Tier 1–3 accounts — applies to manual and email orders only. EDI channel not mentioned.
- Doc 03 (O2C Process RACI): no row for EDI credit review — no owner, no escalation path
- Doc 10 (Order Flow Export): 8,420 total orders × 67.3% = 5,665 EDI orders/yr, avg 1.2h processing time — no credit gate in that flow

**Requires Opportunity 1 first** — the agent reads against the reconciled customer master. Conflicting limits from two systems = undefined behaviour.

---

## Language Rules

### Never say
- Pipeline, agents, blocks
- Knowledge Graph
- Evidence Synthesis
- Gap detected / gap resolved
- Nodes and edges
- Technical architecture

### Say instead
- "The platform is reading your landscape"
- "Your operational map"
- "Here's what it found"
- "A finding that needed a quick answer"
- "How your processes connect"
- "What your business actually looks like"

---

## Discussion Preparation — Expected Questions

### "Is the €600K exposure figure real?"
Navigate to Opportunity 1 sources. Open Doc 07 → Doc 08 → Doc 09. The discrepancy is named in the AR notes and confirmed in both system exports. "The platform read all three and computed the gap. This is what the documents say."

### "How did you find the undocumented EDI flow?"
Open Doc 10 (Order Flow Export) — 67.3% of orders via EDI. Open Doc 01 (Order Management SOP) — EDI flow absent. "The SOP describes one business. The data shows another. The platform found the mismatch between them."

### "Is the TSA finding based on the actual integration register?"
Open Doc 04 (EDI Integration Register) — 6 connections marked as Sanofi-established. Open Doc 11 (CS Working Notes) — Sanofi IT helpdesk number is in the notes as the contact for connection failures. "This is the clearest evidence the connections were never formally transferred."

### "What data do we give you for the pilot?"
Same categories as these 12 inputs. Live SAP ERP and CRM customer exports, actual EDI integration register, CS escalation log, order flow data, credit management policy, process documentation. Your team collates. We run the platform. Two weeks.

### "Can we see the demand planning connection?"
Navigate to Current State Assessment — cross-domain pattern. "When the demand forecast underruns, the O2C escalation queue spikes 12–15 days later. Your CS team is absorbing a demand planning failure. That pattern is in the map."

---

## Fallback Protocol

If live discovery stalls, switch to pre-compiled output without breaking the narrative:

> "Let me show you the complete output suite from a run we prepared — same documents, same process."

Jump directly to the **AI Opportunity Portfolio** (section 7 in the timeline). Three opportunities pre-populated. Before/after process visible. Impact figures on screen.

The live run is sacrificed. The findings — and the business case — are not.

---

## Related Files

| File | Purpose |
|------|---------|
| `docs/superpowers/specs/html/demo-script-o2c.html` | The demo script (this guide's HTML) |
| `docs/superpowers/specs/html/synthetic-inputs-o2c.html` | The 12 synthetic input artefacts |
| `docs/superpowers/specs/2026-06-01-o2c-tactical-output-design.md` | Design spec — 20-min structure, all 6 deliverables |
| `docs/superpowers/plans/2026-06-01-o2c-synthetic-inputs-generation.md` | Implementation plan for generating the 12 inputs |
| `Agentic Discovery Platform/Opella - Autonomous Discovery Platform.md` | Full platform design doc — defines the 6-deliverable output suite |
