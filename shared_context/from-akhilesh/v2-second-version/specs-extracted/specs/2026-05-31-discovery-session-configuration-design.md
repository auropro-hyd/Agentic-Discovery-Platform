# Discovery Session Configuration — Design Spec

**Date:** 2026-05-31
**Status:** Draft
**Context:** Extension to the AuroPro Autonomous Discovery Platform — adds per-BU strategic direction configuration as a first-class pipeline input
**Parent doc:** [Autonomous Discovery Platform — High-Level Design](./2026-05-30-autonomous-discovery-platform-design.md)

---

## Problem

The existing pipeline produces tactical and strategic outputs from ingested inputs, but both output types are generated without knowledge of where the business unit is actually headed. Tactical outputs (automation candidates, agent workflows, process redesign) are direction-agnostic — that is correct. Strategic outputs (transformation roadmap, app rationalization, build-vs-buy recommendations) are not direction-agnostic — they need to be aimed at something specific, and that something differs by BU.

Without a declared strategic direction, the platform can only describe the current state and surface generic opportunities. With a declared direction, it can assess readiness, sequence toward a specific outcome, and flag where reality conflicts with intent.

---

## Design Decision

**Approach: Per-BU Strategy Profiles with Phase-Aware Application**

Strategy profiles are defined per BU at session configuration time. Blocks 1 & 2 operate on a merged signal (all BUs' directions inform what to surface and flag). Block 3 applies per-domain splits — each domain sub-agent set is initialized with its BU's specific StrategyProfile. Block 4 generates per-BU strategic sections shaped by each direction, while tactical sections remain direction-agnostic.

A single-BU engagement (demo, pilot) is identical to a simple pipeline-level annotation — no additional complexity until multi-BU is needed.

---

## Session Configuration Step (Pre-Block 1)

A new step that runs before Block 1. Produces confirmed StrategyProfiles locked into PipelineState.

### StrategyProfile — Structured Template

| Field | Type | Purpose |
|---|---|---|
| `direction_type` | Enum | Primary strategic move: `consolidate` / `modernize` / `divest` / `stabilize` / `acquire` / `exit` |
| `horizon` | Enum | Execution window: `0–6 months` / `6–18 months` / `18+ months` |
| `strategic_constraints` | Free text | What cannot be recommended (budget caps, TSA obligations, regulatory, political) |
| `stakeholder_priorities` | List of strings | What the BU lead cares most about from this engagement |
| `out_of_scope` | Free text | Explicit exclusions (e.g., "do not recommend greenfield builds") |
| `success_definition` | Free text | How the BU lead defines a successful engagement outcome |

### Confirmation Flow

1. AuroPro SME populates the StrategyProfile per BU from intake materials (pre-engagement conversations, existing documents, prior context)
2. The Discovery Copilot generates a structured confirmation document (rendered as a shareable artifact — PDF or web form in later phases; a structured doc for demo/pilot) for the client BU lead to review
3. Client BU lead reviews, edits if needed, and confirms
4. Confirmed profiles are locked into `PipelineState` — profiles cannot change mid-pipeline; changes require a new session

The confirmation document is the **first formal alignment artifact** of the engagement. Its standalone value: it forces explicit articulation of strategic direction before discovery begins, and frequently surfaces misalignment between stakeholders before the platform has run a single analysis.

---

## Pipeline Flow — How StrategyProfile Is Applied

### Block 1 — Ingestion & Knowledge Construction

Agents receive the **merged strategy signal** (union of all BUs' confirmed profiles).

- **Priority weighting:** Document types most relevant to the stated directions get higher ingestion priority. `consolidate` → tech assessments, integration docs, system-of-record references. `divest` → ownership docs, contractual dependencies, TSA obligations.
- **Strategy relevance tagging:** Each extracted KG node receives a `strategy_relevance` attribute indicating how closely it connects to one or more stated directions. This attribute is used by downstream agents to focus analysis.

### Block 2 — Analysis Pipeline

Both agents work with the merged strategy signal.

- **Evidence Synthesis Agent:** Actively sequences patterns that confirm or challenge stated directions, not just patterns in general. A `consolidate` direction focuses event sequencing around system overlap, duplicate ownership, and handoff friction.
- **Technology Landscape Assessment Agent:** Evaluates the app landscape against directions. `consolidate` triggers identification of survivability candidates and dependency chains that would block consolidation.

A new event class is introduced here: **strategic tension** — where discovered evidence conflicts with the stated direction. Strategic tensions are distinct from gaps (missing/ambiguous information) and are routed to the Orchestrator as `strategy_tension` events.

### Block 3 — Domain Analysis

Per-BU split fully activates. Each domain sub-agent set is initialized with its BU's specific StrategyProfile, not the merged signal.

- **Transformation Roadmap Planner:** Sequences initiatives toward the stated direction. `horizon` and `direction_type` are primary constraints. A `0–6 month / stabilize` profile produces a different roadmap than `18+ months / modernize`.
- **App Rationalization Scorer:** Applies `direction_type` as a scoring constraint. `consolidate` → score by survivability and integration dependency reduction. `modernize` → score by technical debt and extensibility. `divest` → score by operational separability.
- **New output per domain:** Strategic Alignment Score — how well the current state positions this BU to execute its stated direction. Key input to Block 4.

### Block 4 — Report Generation

Tactical/strategic split is explicit in the output structure:

- **Tactical outputs** (automation candidates, agent workflow candidates, process redesign blueprints) are generated consistently across all BUs. They are not filtered or shaped by strategic direction — the automation opportunity is the opportunity regardless of where the BU is headed.
- **Strategic outputs** are fully shaped by the BU's StrategyProfile. Roadmap horizons are oriented toward the stated direction. Build-vs-buy-vs-configure recommendations respect `out_of_scope` constraints. Governance model recommendations account for `stakeholder_priorities`.
- **New section — Strategic Readiness Assessment:** The gap between current state and what the stated direction requires to execute. Informed by the Strategic Alignment Score from Block 3 and by resolved strategic tensions.

---

## Strategic Tension Handling

### What a Strategic Tension Is

A strategic tension is a detected conflict between the stated strategic direction and discovered evidence. Examples:
- Direction is `consolidate`, but discovered evidence shows the BU has 4 active vendor negotiations underway for new point solutions
- Direction is `modernize`, but discovered evidence shows 3 critical processes have no documentation and no system-of-record — the foundation for modernization is missing
- Direction is `divest`, but discovered evidence shows deep operational entanglement that contradicts separability

### Non-Blocking Design

Strategic tensions do **not** block the pipeline. Unlike high-severity gaps (which block Block 3 until resolved), a tension between stated direction and reality is a finding — not missing data. Blocking on it would stall the pipeline waiting for a strategic decision that lives outside the discovery process.

### Orchestrator Changes

New queue: `strategy_tension_queue` alongside the existing `blocking_gap_queue`.

New event types added to the AuditLog:

| Event | Trigger |
|---|---|
| `STRATEGY_PROFILE_LOADED` | Session config confirmed, profiles locked into PipelineState |
| `STRATEGY_TENSION_DETECTED` | Block 2 or Block 3 agent surfaces a direction conflict |
| `STRATEGY_TENSION_ROUTED` | Tension sent to Copilot for SME review |
| `STRATEGY_TENSION_RESOLVED` | SME records a resolution decision |

### Discovery Copilot Changes

The SME sees tensions in a separate tray from gaps — same surface, different priority track. For each tension, the system proposes three candidate interpretations:

1. **The direction needs revisiting** — evidence suggests the stated direction may be infeasible or outdated
2. **The finding needs verification** — tension is based on low-confidence evidence; SME should investigate before treating it as real
3. **The tension is known and accepted** — the BU lead is aware of this friction; proceed and flag it in the output

The SME selects one or provides a free-text override. Resolution writes back to the KG, updates `strategy_relevance` attributes on affected nodes, and adds a tension-resolution entry that Block 4 uses in the Strategic Readiness Assessment.

Tensions never reach the client without the SME seeing them first.

---

## Updated Pipeline Architecture

```
Session Config (new)
──────────────────
StrategyProfile per BU
→ confirmed by client BU lead
→ locked into PipelineState

Block 1          Block 2               Block 3              Block 4
─────────────    ─────────────────     ────────────────     ──────────────────
Ingest &    →   Analysis Pipeline  →  Domain Analysis  →   Report Generation
Knowledge        (merged strategy      (per-BU profile       (tactical: constant
Construction     signal; tensions      applied per           strategic: shaped
(priority        detected here)        domain sub-agent      by StrategyProfile)
weighted by                            set)
merged signal)
```

---

## Updated Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Strategic direction scope | Per-BU StrategyProfile | Different BUs within one engagement have different directions; one config per engagement would produce averaged-down strategic outputs |
| Profile confirmation flow | AuroPro drafts, client BU lead confirms | Creates a formal alignment artifact before the platform runs; surfaces stakeholder misalignment early |
| Tactical output variation | None — tactical outputs are direction-agnostic | Automation and agent workflow opportunities don't change based on strategic direction; separating the two prevents the strategic config from distorting tactical findings |
| Strategic tension handling | Non-blocking, SME-routed | Tensions are findings, not missing data; blocking the pipeline stalls for strategic decisions that live outside the discovery process |
| Tension resolution authority | SME only | Tensions never reach the client without SME review; maintains AuroPro as the quality gate |

---

## Deployment Fit

| Phase | Approach | Session Config Behaviour |
|---|---|---|
| Demo | A | Single BU, single StrategyProfile. Merged signal = per-BU profile. No routing complexity. |
| Pilot | A | Single real BU under NDA. Confirmation flow is live with actual client BU lead. |
| Engagement | A → B | Multi-BU. Orchestrator routes domain sub-agents to their BU's profile. `strategy_tension_queue` becomes a real operational queue. |
| Platform | B | Multiple concurrent engagements, each with isolated BU profiles. Confirmation flow is a structured onboarding step for every new BU. |

---

## Open Questions

- What is the UI surface for the StrategyProfile confirmation document? (Structured web form vs. PDF review vs. shared document)
- Should `direction_type` be multi-select? (A BU may be simultaneously consolidating some systems and modernizing others)
- What is the minimum set of fields required to run the pipeline? (If a BU lead only fills in `direction_type` and `horizon`, is that sufficient for Block 3?)
- Should Strategic Alignment Scores be visible to the client in the output, or internal-only for SME context?
