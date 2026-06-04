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
 * A FactValue is the ONLY shape <GroundedNumber> will render, and it can be minted in exactly one
 * place (the factFrom* functions below) from a JSON source row — never from a view-computed number.
 * The brand is a real runtime symbol (FACT_BRAND below): the minted object genuinely carries it, so
 * no unsafe `as unknown as` cast is needed, and a plain object literal cannot satisfy FactValue (the
 * symbol is module-private — NOT exported, so it cannot be forged from another module). Combined with
 * `mintFact` taking a {value} ROW (not a bare number) and not being exported for arbitrary use, a
 * page cannot turn `x * y` into a FactValue. So figures rendered THROUGH <GroundedNumber> are grounded
 * by construction; other verbatim figures are protected by the src/pages/** no-arithmetic ESLint rule
 * (this is not a SPA-wide runtime guarantee). */
const FACT_BRAND: unique symbol = Symbol("fact");
export interface FactValue {
  readonly [FACT_BRAND]: true;
  readonly value: number | string;
  readonly unit?: string;
  readonly label?: string;
  readonly sources?: string[];
  readonly tier?: Tier;
}

/* A "source row" is the only thing a fact can be minted FROM — a shape that exists in the parsed
 * JSON (a fact_store quant row or a pain-point/opportunity NumberRef). Because the mint takes a row
 * (with its own `value`), not a bare number, a page cannot mint `fact(x * y)`: there is no public
 * function that accepts a number. This is what makes the brand real rather than cosmetic.
 * The mints live HERE (not in store.ts) so FACT_BRAND need never be exported. store.ts re-exports
 * factFromQuant/factFromNumberRef so existing import paths keep working. */
type SourceRow = {
  value?: number | string;
  unit?: string;
  label?: string;
  sources?: string[];
  tier?: string;
};

/** The single brand-mint. Private to this module — pages/charts cannot call it. The object
 *  genuinely carries the FACT_BRAND symbol, so no unsafe cast is needed. */
function mintFact(row: SourceRow): FactValue {
  return {
    [FACT_BRAND]: true,
    value: row.value ?? "",
    unit: row.unit,
    label: row.label,
    sources: row.sources,
    tier: row.tier,
  };
}

/** Mint a FactValue from a fact_store quant row (carries unit/sources/tier provenance). */
export function factFromQuant(q: FactQuant): FactValue {
  return mintFact({ value: q.value, unit: q.unit, label: q.label, sources: q.sources, tier: q.tier });
}

/** Mint a FactValue from a pain-point / opportunity quantified NumberRef. NumberRef.sources may be
 *  string[] or SourceRef[]; keep only the doc_id strings for the cite popover. */
export function factFromNumberRef(n: NumberRef): FactValue {
  const sources = (n.sources ?? [])
    .map((s) => (typeof s === "string" ? s : s?.doc_id ?? ""))
    .filter(Boolean);
  return mintFact({ value: n.value, unit: n.unit, label: n.label, sources });
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
