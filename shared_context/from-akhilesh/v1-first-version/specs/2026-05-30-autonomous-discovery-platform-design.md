# AuroPro Autonomous Discovery Platform — High-Level Design

**Date:** 2026-05-30
**Status:** Draft
**Context:** Opella engagement — accelerated enterprise discovery for a 1000+ application post-merger landscape

---

## Problem

Enterprise discovery currently takes 2–3 months of business stakeholder time — interviews, workshops, and manual documentation review. Opella cannot afford that. The platform compresses this to days by automating pattern detection across all input types, with human involvement limited to reviewing high-confidence findings and resolving ambiguous gaps.

---

## System Overview

A four-block agentic pipeline that ingests all available organisational knowledge, constructs a knowledge graph, runs analysis in parallel, surfaces gaps for SME resolution, performs domain-centric analysis, and generates a full suite of tactical and strategic outputs.

The system ships in two forms:
- **Demo / Early Engagement (Approach A):** Linear pipeline with explicit phase gates. Simpler to build, predictable to demo, easy to reason about. See [Approach A — Linear Pipeline Design](./2026-05-30-approach-a-linear-pipeline-design.md).
- **Production (Approach B):** Hierarchical Orchestrator model. Same agents promoted to stateless workers, controlled by a central Orchestrator that owns pipeline state, gap routing, and audit trail. Upgraded without rewrites — the agents don't change, only the control model does. See [Approach B — Hierarchical Orchestrator Design](./2026-05-30-approach-b-orchestrator-design.md).

---

## Pipeline Architecture

```
Block 1          Block 2               Block 3              Block 4
─────────────    ─────────────────     ────────────────     ──────────────────
Ingest &    →   Analysis Pipeline  →  Domain Analysis  →   Report Generation
Knowledge        (parallel agents)    (multi-agent,         (synthesises all
Construction     + Gap Gate           DDD-motivated)         block outputs)
```

---

## Block 1 — Ingestion & Knowledge Construction

Accepts all five input categories: structured documents, semi-structured inputs, unstructured/conversational, system-level signals, and comparative inputs (same process described across multiple sources or teams).

Each document is classified by type (SOP, org chart, transcript, log, etc.) based on its content — not its filename or metadata. Entities, events, actors, systems, decision points, and handoffs are extracted and used to construct a **Knowledge Graph** — the shared data plane for all downstream agents.

---

## Block 2 — Analysis Pipeline

Two agents run in parallel:

- **Evidence Synthesis Agent** — detects cross-source patterns, sequences process events, maps handoff chains, surfaces workarounds and exceptions, and flags contradictions between sources.
- **Technology Landscape Assessment Agent** — constructs the application inventory, maps functional surface area, identifies integration topology and system-to-process bindings, and detects overlap and redundancy.

**Gap handling (severity-split model):**

- The **Gap Scorer** automatically classifies every detected gap as high-severity or low-severity based on business impact and verifiability.
- **High-severity gaps** (missing system-of-record for a critical process, unresolvable contradictions) block Block 3. They are surfaced to the **SME** (the AuroPro discovery specialist, not the client) via the Discovery Copilot, where the agent proposes 2–3 candidate resolutions and the SME selects or overrides. Resolution can happen via any channel — direct knowledge, email, chat, targeted app crawl, or stakeholder clarification.
- **Low-severity gaps** (ambiguous ownership, minor inconsistencies) carry forward automatically as amber-tiered nodes in the Knowledge Graph. Block 3 runs against them at reduced confidence. If the SME resolves them later, confidence scores update.

Once all high-severity gaps are cleared, Block 2 produces a **Verified Cohort** — a confidence-tiered snapshot of the Knowledge Graph — and passes it to Block 3.

---

## Block 3 — Domain Analysis

A DDD-motivated multi-agent framework. **Handoff topology is the primary signal for domain boundary discovery** — where a process crosses a team or system, that is a candidate boundary. Sub-agents run in parallel across identified domains:

| Sub-Agent | Responsibility |
|---|---|
| Bounded Context Mapper | Proposes domain boundaries from handoff chains; boundaries start amber-tiered until confirmed in output review |
| Context Map Builder | Maps relationships between domains (upstream/downstream, shared kernel, ACL) |
| Domain Event Cataloguer | Catalogs every discrete event per domain, tagged by trigger, actor, system, outcome |
| Automation Opportunity Ranker | Scores automation and agent workflow candidates by effort-to-impact ratio |
| App Rationalization Scorer | Scores consolidation candidates within each domain |
| Transformation Roadmap Planner | Sequences initiatives across three horizons per domain |

Block 3 output is a structured domain analysis payload passed directly to Block 4.

---

## Block 4 — Report Generation

A single Report Generation Agent synthesises all block outputs into the full deliverable suite:

**Tactical outputs:**
- Current State Assessment (domain boundaries, process inventory, system mapping, ownership)
- Event catalog and handoff map (DDD context map)
- Exception and workaround register
- Automation and agent workflow candidates (with HITL insertion points)
- Process redesign blueprints for top 3–5 candidates

**Strategic outputs:**
- Application overlap matrix and consolidation scenarios
- Build-vs-buy-vs-configure recommendations per domain
- Transformation Roadmap across three horizons (0–6 months, 6–18 months, 18+ months)
- Governance model recommendation (agentic layer ownership, drift/hallucination management)
- Strategic KPI framework (baseline, target state, leading indicators)

---

## Discovery Copilot — SME Interface

The human-in-the-loop surface for Block 2 gap resolution. The SME only sees high-severity gaps that are actively blocking Block 3.

**Resolution model — B now, C later:**
- **Current (B):** For each gap, the agent proposes 2–3 candidate resolutions based on available evidence. The SME selects one or provides a free-text override.
- **Upgrade (C):** Resolution becomes action-triggered — "run app crawl on System X", "send clarification to [client contact]", "mark as out of scope". Each action type has a defined outcome and feeds directly back into the Knowledge Graph.

The Copilot is a communication hub, not a meeting scheduler. Resolution happens through whatever channel is fastest — the SME records the outcome and the pipeline proceeds.

---

## Knowledge Graph

Shared data plane accessed by all agents across all blocks. Confidence tier is a first-class attribute on every node and edge — not a post-hoc annotation.

**Nodes:** Process, System/Application, Actor (team/role), Domain Event, Decision Point, Domain Boundary

**Edges:** `handoff_to`, `triggers`, `owned_by`, `runs_on`, `conflicts_with`, `belongs_to_domain`

**Confidence tiers:**
- 🟢 **Verified** — supported by document evidence AND non-prod app crawl
- 🟡 **Amber** — document evidence only, or low-severity gap carried forward
- 🔴 **Gap** — mentioned but unverifiable, contradicted, or missing system-of-record

---

## Deployment Strategy

| Phase | Approach | Description |
|---|---|---|
| Demo | A | AuroPro-hosted, synthetic FMCH data, one domain end-to-end |
| Pilot | A | AuroPro-hosted, one real Opella domain under NDA |
| Engagement | A → B | Full domain-by-domain sprints; Orchestrator model introduced as volume scales |
| Platform | B | Multi-engagement, multi-client, Orchestrator as control plane |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Orchestration model | A (demo) → B (production) | Ship fast, upgrade without rewrites. See individual approach docs. |
| Gap handling | Severity-split | High-severity blocks; low-severity carries forward at reduced confidence |
| Gap scoring | Agent auto-classifies, SME reviews only high-severity | Minimises SME cognitive load |
| Domain boundary signal | Handoff topology (primary) | Observable in all input types; directly maps to DDD context maps |
| Gap resolution UX | B → C upgrade path | Start guided, graduate to structured actions as taxonomy matures |
| Confidence tiering | First-class on KG nodes/edges | Visible to client; drives SME prioritisation |

---

## Open Questions

- What graph store backs the Knowledge Graph in the demo? (In-memory vs. lightweight persistent — Neo4j, Kuzu, or JSON-backed)
- What is the confidence scoring function for gap severity? (Rule-based heuristics vs. LLM-scored vs. hybrid)
- What does the Discovery Copilot UI look like as a product surface? (Separate app, embedded in report, CLI-first for demo?)
- Which synthetic FMCH domain for the Opella demo? (Consumer Safety & Pharmacovigilance vs. Regulatory Submissions & Product Lifecycle)
