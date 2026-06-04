import { z } from "zod";

/* The ONE schema, authored against the ACTUAL engine output (v1/out/discovery-*.json).
 * All client data lives under the top-level `synthesis` key; `domain_label` sits at the root.
 * z.infer (see types.ts) generates every TS type from this, so runtime validation and the
 * compile-time types cannot drift. Validation runs at load (loadSynthesis.ts); a failure shows
 * a "data contract changed" banner rather than a blank screen.
 *
 * The schema is deliberately LENIENT on optional/nullable/empty fields the LLM-emitted JSON
 * varies on (charts:[], opportunity_id:null, addresses_pain_point:'', empty quote/locator),
 * and uses .passthrough() at the synthesis root so a newly-added pipeline field never breaks
 * the SPA — only the fields the UI actually reads are constrained. */

const SourceRef = z
  .object({
    doc_id: z.string().default(""),
    quote: z.string().default(""),
    locator: z.string().default(""),
  })
  .partial()
  .passthrough();

// `sources` appears in two shapes across the engine output: a bare doc_id string list (on
// fact_store.quant and on quantified NumberRefs) OR a list of SourceRef objects (on data_tables
// and detail_tables). Accept either, everywhere, so the SPA tolerates both without per-field rules.
const SourceList = z.array(z.union([z.string(), SourceRef])).default([]);

// Tier stays string-typed: the data is LLM-emitted and may drift. Real domain (documented, NOT
// enforced — never tighten to z.enum without .catch(""), or drift would fail the whole load):
//   "verified" | "amber" | "gap"
const Tier = z.string().default("");

const FactQuant = z
  .object({
    label: z.string().default(""),
    value: z.union([z.number(), z.string()]),
    unit: z.string().default(""),
    sources: z.array(z.string()).default([]),
    tier: Tier,
  })
  .passthrough();

const FactQuote = z
  .object({
    text: z.string().default(""),
    doc_id: z.string().default(""),
    locator: z.string().default(""),
    tier: Tier,
  })
  .passthrough();

const FactEntity = z
  .object({
    kind: z.string().default(""),
    name: z.string().default(""),
    attributes: z.record(z.string(), z.any()).default({}),
    sources: z.array(z.string()).default([]),
    tier: Tier,
  })
  .passthrough();

const FactStore = z
  .object({
    quant: z.array(FactQuant).default([]),
    quotes: z.array(FactQuote).default([]),
    entities: z.array(FactEntity).default([]),
    relations: z.array(z.any()).default([]),
  })
  .partial()
  .passthrough();

// a quantified figure attached to a pain point / opportunity impact
const NumberRef = z
  .object({
    value: z.union([z.number(), z.string()]).optional(),
    unit: z.string().default(""),
    label: z.string().default(""),
    text: z.string().default(""),
    sources: SourceList,
  })
  .passthrough();

const DataTable = z
  .object({
    title: z.string().default(""),
    caption: z.string().default(""),
    columns: z.array(z.string()).default([]),
    rows: z.array(z.array(z.union([z.string(), z.number(), z.null()]))).default([]),
    note: z.string().default(""),
    sources: SourceList,
  })
  .passthrough();

const ProcessStep = z
  .object({
    actor: z.string().default(""),
    description: z.string().default(""),
    step: z.string().default("").optional(),
  })
  .passthrough();

const BaselineStat = z
  .object({
    label: z.string().default(""),
    value: z.union([z.number(), z.string()]).optional(),
    sublabel: z.string().default(""),
  })
  .passthrough();

const PainPoint = z
  .object({
    id: z.string(),
    title: z.string().default(""),
    description: z.string().default(""),
    category: z.string().default(""),
    failure_pattern: z.string().default(""),
    impact_rank: z.number().optional(),
    severity: z.string().default(""), // high | medium | lower
    quantified: z.array(NumberRef).default([]),
    root_cause: z.string().default(""),
    business_consequence: z.string().default(""),
    detail_table: DataTable.optional().nullable(),
    opportunity_signal: z.string().default(""),
    from_finding: z.string().default(""),
    sources: z.array(SourceRef).default([]),
  })
  .passthrough();

const BusinessImpact = z
  .object({
    narrative: z.string().default(""),
    quantified: z.array(NumberRef).default([]),
    derivation: z.string().default(""),
  })
  .partial()
  .passthrough();

const Opportunity = z
  .object({
    id: z.string(),
    title: z.string().default(""),
    overview: z.string().default(""),
    // kept string for LLM drift-tolerance. Real domain (documented, not enforced):
    //   "hitl_workflow" | "automation" | "modernisation" | "ai_agent"
    pattern: z.string().default(""),
    addresses_pain_point: z.string().default(""), // a PainPoint id (or "")
    business_impact: BusinessImpact.optional().nullable(),
    before_process: z.array(ProcessStep).default([]),
    after_process: z.array(ProcessStep).default([]),
    value_rating: z.string().default(""),
    value_score: z.number().optional(),
    feasibility_rating: z.string().default(""),
    feasibility_score: z.number().optional(),
    // kept string for LLM drift-tolerance. Real domain (documented, not enforced):
    //   "do_first" | "plan_for" | "consider" | "deprioritise"
    matrix_quadrant: z.string().default(""),
    technical_complexity: z.string().default(""),
    data_readiness: z.string().default(""),
    operational_readiness: z.string().default(""),
    implementation_approach: z.string().default(""),
    expected_behaviour: z.string().default(""),
    escalation: z.string().default(""),
    personas: z.array(z.string()).default([]),
    knowledge_sources: z.array(z.string()).default([]),
    required_integrations: z.array(z.string()).default([]),
    document_formats: z.array(z.string()).default([]),
    success_metrics: z.array(z.string()).default([]),
    risks: z.array(z.string()).default([]),
    dependencies: z.array(z.string()).default([]),
    prerequisite_for: z.array(z.string()).default([]),
    sources: z.array(SourceRef).default([]),
  })
  .passthrough();

// A planning assumption is prose only — it intentionally has NO value/sources fields, so it can
// never be minted into a FactValue or rendered as a grounded fact (it surfaces via <PlanningBadge>/
// <PlanningRow> instead). Do not add a numeric `value` here.
const PlanningAssumption = z
  .object({
    statement: z.string().default(""),
    kind: z.string().default(""), // date|owner|sla|threshold|cadence|cost|sequence
    basis: z.string().default(""),
  })
  .passthrough();

const RoadmapItem = z
  .object({
    title: z.string().default(""),
    rationale: z.string().default(""),
    opportunity_id: z.string().nullable().default(null),
    depends_on: z.array(z.string()).default([]),
  })
  .passthrough();

const RoadmapHorizon = z
  .object({
    horizon: z.string().default(""),
    theme: z.string().default(""),
    window: z.string().default(""),
    items: z.array(RoadmapItem).default([]),
  })
  .passthrough();

const RiskRow = z
  .object({
    risk: z.string().default(""),
    likelihood: z.string().default(""),
    impact: z.string().default(""),
    mitigation: z.string().default(""),
    owner: z.string().default(""),
  })
  .passthrough();

const EvidenceRow = z
  .object({
    finding: z.string().default(""),
    data_point: z.string().default(""),
    evidence_type: z.string().default(""),
    source: z.string().default(""),
    confidence: z.string().default(""),
  })
  .passthrough();

const TraceRow = z
  .object({
    pain_point: z.string().default(""),
    opportunity: z.string().default(""),
    recommendation: z.string().default(""),
    expected_outcome: z.string().default(""),
    horizon: z.string().default(""),
    severity: z.string().default(""),
    summary: z.string().default(""),
  })
  .passthrough();

const MetricRow = z
  .object({
    name: z.string().default(""),
    definition: z.string().default(""),
    target: z.string().default(""),
  })
  .passthrough();

const SourceIndexRow = z
  .object({
    doc_id: z.string().default(""),
    business_name: z.string().default(""),
    doc_type: z.string().default(""),
    what_we_read: z.string().default(""),
    supported_findings: z.array(z.string()).default([]),
  })
  .passthrough();

const ChartSpec = z
  .object({
    key: z.string().default(""),
    kind: z.string().default(""), // donut | bar
    title: z.string().default(""),
    unit: z.string().default(""),
    segments: z
      .array(
        z
          .object({ label: z.string().default(""), value: z.union([z.number(), z.string()]).optional() })
          .passthrough(),
      )
      .default([]),
  })
  .passthrough();

const CurrentState = z
  .object({
    domain_overview: z.string().default(""),
    process_summary: z.string().default(""),
    baseline_stats: z.array(BaselineStat).default([]),
    data_tables: z.array(DataTable).default([]),
    process_flow: z.array(z.any()).default([]),
    process_detail: z.array(z.any()).default([]),
    process_inventory: z.array(z.any()).default([]),
    ownership_map: z.array(z.any()).default([]),
    system_inventory: z.array(z.any()).default([]),
    system_profiles: z.array(z.any()).default([]),
    handoff_catalogue: z.array(z.any()).default([]),
    format_taxonomy: z.array(z.any()).default([]),
  })
  .partial()
  .passthrough();

const ExecutiveSummary = z
  .object({
    headline: z.string().default(""),
    situation: z.string().default(""),
    opportunity: z.string().default(""),
  })
  .partial()
  .passthrough();

const StrategyProfile = z
  .object({ posture: z.string().default(""), notes: z.string().default("") })
  .partial()
  .passthrough();

export const Synthesis = z
  .object({
    executive_summary: ExecutiveSummary.optional(),
    current_state: CurrentState.optional(),
    pain_points: z.array(PainPoint).default([]),
    opportunities: z.array(Opportunity).default([]),
    planning_assumptions: z.array(PlanningAssumption).default([]),
    roadmap: z.array(RoadmapHorizon).default([]),
    risk_register: z.array(RiskRow).default([]),
    evidence_register: z.array(EvidenceRow).default([]),
    traceability: z.array(TraceRow).default([]),
    metrics_framework: z.array(MetricRow).default([]),
    source_index: z.array(SourceIndexRow).default([]),
    fact_store: FactStore.optional(),
    charts: z.array(ChartSpec).default([]),
    strategy_profile: StrategyProfile.optional(),
    cross_process_patterns: z.array(z.any()).default([]),
    target_state: z.string().default(""),
    strategic_readiness: z.string().default(""),
    sequencing_rationale: z.string().default(""),
    dependency_notes: z.string().default(""),
  })
  .passthrough();

// the root document the engine writes (we only constrain what the UI reads).
// The sync step writes a top-level `client_display` string (the neutral label to show in the
// header/cover) into the SHIPPED doc and no longer emits `_confidential`. We read client_display
// only. `_confidential` is still tolerated via .passthrough() so a raw (pre-sync) engine file can
// also parse, but the UI never reads it — a suppressed client name must never reach the client view.
export const DiscoveryDoc = z
  .object({
    domain: z.string().default(""),
    domain_label: z.string().default(""),
    client_display: z.string().optional(),
    synthesis: Synthesis,
  })
  .passthrough();
