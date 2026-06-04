import { FACT_BRAND } from "./types";
import type {
  Synthesis,
  PainPoint,
  Opportunity,
  FactValue,
  FactQuant,
  NumberRef,
} from "./types";

/* The derived store for one domain. Built once per domain load. Holds:
 *  - id maps (painPointById / opportunityById) for O(1) cross-link resolution
 *  - oppByPainPoint: reverse index opportunity.addresses_pain_point -> opportunities[]
 *  - factByLabel: fact_store.quant indexed by lowercased label (for SourceCite provenance)
 *  - factFrom*(): the SOLE mints of the FactValue brand (the grounding chokepoint)
 */

/* A "source row" is the only thing a fact can be minted FROM — a shape that exists in the parsed
 * JSON (a fact_store quant row or a pain-point/opportunity NumberRef). Because the mint takes a row
 * (with its own `value`), not a bare number, a page cannot mint `fact(x * y)`: there is no public
 * function that accepts a number. This is what makes the brand real rather than cosmetic. */
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

export interface DomainStore {
  domain: string;
  domainLabel: string;
  clientDisplay: string; // the client name to show on screen (neutral when suppressed)
  synthesis: Synthesis;
  painPointById: Map<string, PainPoint>;
  opportunityById: Map<string, Opportunity>;
  oppByPainPoint: Map<string, Opportunity[]>;
  factByLabel: Map<string, FactQuant>;
}

export function buildStore(
  domain: string,
  domainLabel: string,
  clientDisplay: string,
  s: Synthesis,
): DomainStore {
  const painPointById = new Map<string, PainPoint>();
  for (const pp of s.pain_points) if (pp.id) painPointById.set(pp.id, pp);

  const opportunityById = new Map<string, Opportunity>();
  const oppByPainPoint = new Map<string, Opportunity[]>();
  for (const opp of s.opportunities) {
    if (opp.id) opportunityById.set(opp.id, opp);
    const target = (opp.addresses_pain_point || "").trim(); // OPP6 (o2c) has "" — guarded
    if (target) {
      const list = oppByPainPoint.get(target) ?? [];
      list.push(opp);
      oppByPainPoint.set(target, list);
    }
  }

  const factByLabel = new Map<string, FactQuant>();
  for (const q of s.fact_store?.quant ?? []) {
    const key = (q.label || "").trim().toLowerCase();
    if (key && !factByLabel.has(key)) factByLabel.set(key, q);
  }

  return {
    domain,
    domainLabel,
    clientDisplay,
    synthesis: s,
    painPointById,
    opportunityById,
    oppByPainPoint,
    factByLabel,
  };
}
