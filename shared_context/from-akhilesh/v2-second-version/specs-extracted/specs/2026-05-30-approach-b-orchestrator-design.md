# Approach B — Hierarchical Orchestrator Design

**Date:** 2026-05-30
**Status:** Draft
**Role:** Production and multi-engagement delivery model
**Parent doc:** [Autonomous Discovery Platform — High-Level Design](./2026-05-30-autonomous-discovery-platform-design.md)
**Prerequisite:** [Approach A — Linear Pipeline Design](./2026-05-30-approach-a-linear-pipeline-design.md) (agents built in A are reused without modification)

---

## Summary

The Orchestrator Agent replaces the procedural runner from Approach A. It owns the full pipeline state, decides when to unblock phases, routes gaps to the Discovery Copilot, maintains an audit log of every decision, and manages the lifecycle of all sub-agent workers. Sub-agents are stateless — they accept inputs, return outputs, and have no knowledge of pipeline state.

This model is introduced once pipeline volume (document count, domain count, or concurrent engagement count) makes the procedural runner insufficient, or when audit and explainability requirements demand a first-class decision log.

---

## Control Architecture

```
                        ┌─────────────────────────────────────┐
                        │         Orchestrator Agent           │
                        │                                      │
                        │  - Owns: PipelineState               │
                        │  - Decides: phase transitions        │
                        │  - Routes: gaps → Copilot            │
                        │  - Emits: AuditEvent per decision    │
                        │  - Monitors: worker health + timeout │
                        └──────────┬──────────────────────────┘
                                   │ dispatches work to
           ┌───────────────────────┼────────────────────────────┐
           ▼                       ▼                            ▼
   ┌───────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
   │  Block 1      │    │  Block 2             │    │  Block 3 + 4         │
   │  Workers      │    │  Workers             │    │  Workers             │
   │               │    │                      │    │                      │
   │  Classifier   │    │  Evidence Synthesis  │    │  Domain Analysts ×N  │
   │  Extractor    │    │  Landscape Assess.   │    │  Report Generator    │
   │  KG Builder   │    │  Gap Scorer          │    │                      │
   └───────────────┘    │  SME Copilot         │    └──────────────────────┘
                        └──────────────────────┘
```

---

## Orchestrator Responsibilities

### Phase Management
The Orchestrator decides when each block begins and when it is considered complete. It does not assume sequential completion — it evaluates readiness conditions:

| Transition | Readiness Condition |
|---|---|
| Start Block 2 | Block 1 emits `KG_READY` |
| Unblock Block 3 | Block 2 emits `COHORT_READY` AND `high_severity_gap_queue.length === 0` |
| Start Block 4 | Block 3 emits `DOMAIN_ANALYSIS_COMPLETE` for all domains |

### Gap Routing
The Orchestrator receives gap events from the Gap Scorer and routes them based on severity:
- High-severity → placed on `blocking_gap_queue`, Copilot notified
- Low-severity → written directly to KG as amber-tiered, `informational_gap_log` updated

When the SME resolves a gap via the Copilot, the Orchestrator:
1. Writes the resolution to the KG
2. Re-tiers affected nodes
3. Checks if `blocking_gap_queue` is now empty
4. If empty: assembles Verified Cohort and emits `COHORT_READY`

### Audit Log
Every Orchestrator decision is appended to an append-only `AuditLog`:

```
AuditEvent {
  event_id
  timestamp
  event_type: PHASE_STARTED | PHASE_COMPLETED | GAP_DETECTED
              | GAP_ROUTED | GAP_RESOLVED | BLOCK_UNBLOCKED
              | WORKER_DISPATCHED | WORKER_COMPLETED | WORKER_FAILED
  payload: {}   // event-specific data
  decision_rationale: string  // why the Orchestrator made this decision
}
```

The audit log is the primary explainability surface for client-facing output review. Every confidence-tiered finding in the final report is traceable to an audit event.

---

## Worker Contract

All sub-agents built in Approach A are reused without modification. The contract they must satisfy:

```
Worker {
  input:  WorkerInput   // defined per worker type, passed by Orchestrator
  output: WorkerOutput  // defined per worker type, returned to Orchestrator
  // no access to PipelineState
  // no side effects outside of returning WorkerOutput
  // idempotent: same input always produces same output
}
```

The Orchestrator is responsible for writing worker outputs to the Knowledge Graph or passing them downstream. Workers do not write to the KG directly.

---

## Discovery Copilot Integration

### Model B (current) — Guided Resolution
The Orchestrator dispatches a `CopilotGapResolutionTask` to the Copilot worker for each high-severity gap. The Copilot worker:
1. Retrieves evidence context from the KG for the gap
2. Generates 2–3 candidate resolutions ranked by evidence strength
3. Surfaces the gap card to the SME interface
4. Awaits SME selection or free-text override
5. Returns a `ResolvedGap` to the Orchestrator

### Model C (upgrade) — Action-Triggered Resolution
The Copilot worker is extended to emit structured `ResolutionAction` objects instead of free-text:

```
ResolutionAction {
  action_type: RUN_APP_CRAWL | SEND_CLIENT_CLARIFICATION
               | MARK_OUT_OF_SCOPE | ACCEPT_CANDIDATE | MANUAL_OVERRIDE
  target: string        // system, contact, or scope boundary
  expected_outcome: string
  triggered_by: sme_id
}
```

Each action type has a defined handler in the Orchestrator. The handler executes the action, captures the result, and writes the resolution back to the KG. This upgrade is isolated to the Copilot worker and the Orchestrator's action handlers — no other agents change.

---

## State Model

The Orchestrator maintains persistent pipeline state (survives restarts, supports long-running engagements):

```
PipelineState {
  run_id
  engagement_id
  status: INITIALISING | BLOCK_1_RUNNING | BLOCK_2_RUNNING
          | BLOCKED_ON_GAPS | BLOCK_3_RUNNING | BLOCK_4_RUNNING
          | COMPLETED | FAILED
  knowledge_graph_ref: KGReference
  blocks: {
    block1: BlockState
    block2: BlockState
    block3: BlockState    // includes per-domain sub-states
    block4: BlockState
  }
  gaps: {
    blocking_queue: Gap[]
    informational_log: Gap[]
    resolved: ResolvedGap[]
  }
  cohort_ref: CohortReference | null
  audit_log: AuditEvent[]
  outputs: DeliverableSuite | null
}
```

Unlike Approach A's in-memory run object, this state is persisted. Long-running engagements (where SME gap resolution may take hours or days) do not lose state on restart.

---

## Differences from Approach A

| Concern | Approach A | Approach B |
|---|---|---|
| Control model | Procedural runner script | Orchestrator Agent |
| State persistence | In-memory (lost on restart) | Persisted (survives restarts) |
| Gap routing | Hardcoded gate in runner | Orchestrator decision with audit event |
| Audit trail | Log file | Structured AuditEvent log, traceable to outputs |
| Worker lifecycle | Direct invocation | Orchestrator dispatches and monitors |
| Copilot integration | Direct call | Orchestrator-dispatched CopilotTask |
| Multi-engagement support | One run at a time | Orchestrator can manage concurrent runs |
| Mid-run document addition | Not supported | Supported — Orchestrator re-triggers Block 1 workers |

---

## When to Introduce Approach B

Introduce Approach B when any of the following are true:
- A single engagement spans more than 3 domains and gap resolution extends across multiple working days
- Multiple concurrent engagements run on the same platform instance
- Client or regulatory requirements demand a structured audit trail per finding
- Mid-run document additions become a regular occurrence
- The Copilot is upgraded to Model C (action-triggered) — the action handler architecture requires the Orchestrator
