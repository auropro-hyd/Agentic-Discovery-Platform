import { z } from "zod";
import {
  Synthesis,
  DiscoveryDoc,
  // re-derive the leaf shapes via the schema object below
} from "./synthesis.schema";

/* All UI types are INFERRED from the one zod schema, so they cannot drift from what is
 * validated at load. Components import these — never re-declare a data shape locally. */
export type Synthesis = z.infer<typeof Synthesis>;
export type DiscoveryDoc = z.infer<typeof DiscoveryDoc>;

export type PainPoint = Synthesis["pain_points"][number];
export type Opportunity = Synthesis["opportunities"][number];
export type PlanningAssumption = Synthesis["planning_assumptions"][number];
export type RoadmapHorizon = Synthesis["roadmap"][number];
export type RoadmapItem = RoadmapHorizon["items"][number];
export type RiskRow = Synthesis["risk_register"][number];
export type EvidenceRow = Synthesis["evidence_register"][number];
export type TraceRow = Synthesis["traceability"][number];
export type MetricRow = Synthesis["metrics_framework"][number];
export type SourceIndexRow = Synthesis["source_index"][number];
export type ChartSpec = Synthesis["charts"][number];
export type DataTable = NonNullable<NonNullable<Synthesis["current_state"]>["data_tables"]>[number];
export type NumberRef = PainPoint["quantified"][number];
export type SourceRef = PainPoint["sources"][number];

export type FactStore = NonNullable<Synthesis["fact_store"]>;
export type FactQuant = NonNullable<FactStore["quant"]>[number];
export type FactQuote = NonNullable<FactStore["quotes"]>[number];
export type FactEntity = NonNullable<FactStore["entities"]>[number];

export type Tier = "verified" | "amber" | "gap" | string;

/* ── the GROUNDING BRAND ──────────────────────────────────────────────────────────────────
 * A FactValue is the ONLY shape <GroundedNumber> will render. It is minted in exactly one
 * place (lib/store.ts `fact()`), straight from parsed JSON. Because the `__fact` brand is a
 * private symbol-like literal, no view-layer code can fabricate one — passing a raw computed
 * number to <GroundedNumber> is a COMPILE error. This is grounding enforced by the type system. */
declare const FACT_BRAND: unique symbol;
export interface FactValue {
  readonly [FACT_BRAND]: true;
  readonly value: number | string;
  readonly unit?: string;
  readonly label?: string;
  readonly sources?: string[];
  readonly tier?: Tier;
}

export const SeverityOrder: Record<string, number> = { high: 0, critical: 0, medium: 1, lower: 2, low: 2 };
export const QuadrantLabel: Record<string, string> = {
  do_first: "Do first",
  plan_for: "Plan for",
  consider: "Consider",
  deprioritise: "Deprioritise",
};
export const PatternLabel: Record<string, string> = {
  hitl_workflow: "Human-in-the-loop workflow",
  automation: "Automation",
  modernisation: "Modernisation",
  ai_agent: "AI agent",
};
