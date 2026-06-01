# Approach A — Linear Pipeline Design

**Date:** 2026-05-30
**Status:** Draft
**Role:** Demo and early engagement delivery model
**Parent doc:** [Autonomous Discovery Platform — High-Level Design](./2026-05-30-autonomous-discovery-platform-design.md)

---

## Summary

A fixed-phase pipeline where each block completes before the next begins, with defined parallel slots within blocks. The control model is simple: blocks are functions, not services. No central coordinator — each block is invoked in sequence by the runner. Gap handling is an explicit gate between Block 2 and Block 3.

Designed to ship for the Opella demo and carry through the pilot. Upgrade path to Approach B requires no agent rewrites — only the control model changes.

---

## Execution Model

```
Runner
  │
  ├─► Block 1: Ingest & Knowledge Construction  (sequential internal steps)
  │         └─► emits: Knowledge Graph (initial, untiered)
  │
  ├─► Block 2: Analysis Pipeline  (parallel internal agents)
  │         ├─► Evidence Synthesis Agent        ─┐
  │         └─► Landscape Assessment Agent       ─┴─► Gap Scorer
  │                                                      │
  │                                          ┌───────────┴───────────┐
  │                                   High-severity?           Low-severity?
  │                                          │                       │
  │                                   SME Copilot            Carry forward (amber)
  │                                   (blocking gate)
  │                                          │
  │                                   Resolved → unblock
  │                                          │
  │         └─► emits: Verified Cohort (confidence-tiered KG snapshot)
  │
  ├─► Block 3: Domain Analysis  (parallel sub-agents per domain)
  │         ├─► Bounded Context Mapper
  │         ├─► Context Map Builder
  │         ├─► Domain Event Cataloguer
  │         ├─► Automation Opportunity Ranker
  │         ├─► App Rationalization Scorer
  │         └─► Transformation Roadmap Planner
  │         └─► emits: Structured domain analysis payload
  │
  └─► Block 4: Report Generation  (single agent, sequential)
            └─► emits: Full deliverable suite (tactical + strategic)
```

---

## Phase Gates

### Block 1 → Block 2
No gate. Block 2 begins as soon as the Knowledge Graph is constructed. Block 1 is complete when all documents are ingested, classified, and extracted into the KG.

### Block 2 → Block 3 (Gap Gate)
Block 3 is held until all high-severity gaps are resolved. The runner polls gap status after each SME resolution. Once the high-severity gap queue is empty, the Verified Cohort is assembled and Block 3 is invoked.

Low-severity gaps do not block this gate. They are carried forward as amber-tiered nodes in the KG.

### Block 3 → Block 4
No gate. Block 4 begins as soon as all Block 3 sub-agents have completed. Block 3 sub-agents run in parallel; the slowest domain determines when Block 4 starts.

---

## Gap Handling Detail

The Gap Scorer runs as a post-processing step after both Block 2 agents complete.

**Severity classification (agent-driven, SME can override):**

| Signal | Severity |
|---|---|
| Process has no system-of-record | High |
| Critical process contradicted across two or more sources | High |
| Ownership unresolvable across all input types | High |
| Ambiguous ownership with at least one candidate | Low |
| Minor cross-source inconsistency (naming, volume) | Low |
| Domain boundary unclear but handoff evidence exists | Low |

**SME Copilot interaction (Model B — current):**
For each high-severity gap, the agent surfaces:
- A description of the gap and which sources it was detected from
- 2–3 candidate resolutions ranked by evidence strength
- The SME selects a resolution or provides a free-text override
- Resolution is written back to the KG; affected nodes are re-tiered

**Resolution channels:** Direct SME knowledge, email thread, chat, targeted app crawl, stakeholder clarification. The channel is irrelevant — only the outcome is recorded.

---

## State Model

The runner maintains a simple state object for the pipeline run:

```
PipelineRun {
  run_id
  status: RUNNING | BLOCKED_ON_GAPS | COMPLETED | FAILED
  blocks: {
    block1: PENDING | RUNNING | COMPLETE
    block2: PENDING | RUNNING | BLOCKED | COMPLETE
    block3: PENDING | RUNNING | COMPLETE
    block4: PENDING | RUNNING | COMPLETE
  }
  knowledge_graph: KnowledgeGraph
  gaps: {
    high_severity: Gap[]      // blocking queue
    low_severity: Gap[]       // informational, carried forward
    resolved: ResolvedGap[]
  }
  cohort: VerifiedCohort | null
  outputs: DeliverableSuite | null
}
```

---

## Upgrade Path to Approach B

Approach A is designed so that the upgrade to B requires no changes to any agent. The only change is replacing the runner with an Orchestrator Agent.

| Component | Approach A | Approach B |
|---|---|---|
| Runner | Procedural script | Orchestrator Agent |
| Block agents | Invoked directly | Invoked as stateless workers |
| Gap routing | Hardcoded in runner | Orchestrator decision |
| Audit trail | Log file | Orchestrator event log |
| State | In-memory run object | Orchestrator-managed persistent state |

**Prerequisite for upgrade:** Each block agent must accept a well-defined input contract and return a well-defined output contract. This must be enforced in Approach A — it is what makes the promotion to B a structural change rather than a rewrite.

---

## Constraints

- Block 1 must fully complete before Block 2 starts. Streaming ingestion is out of scope for Approach A.
- The gap gate is synchronous — the pipeline is paused, not cancelled, while waiting for SME resolution.
- Block 3 sub-agents share the same KG read snapshot (the Verified Cohort). They do not write back to the KG — their outputs are collected and passed to Block 4 as a payload.
- Approach A does not support mid-run document addition. New documents require a pipeline restart.
